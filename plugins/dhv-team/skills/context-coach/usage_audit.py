#!/usr/bin/env python
"""Claude Code usage audit. Standard library only; it never calls a model, so running it costs no tokens.

  python usage_audit.py collect            on the person's own PC: reads the chat logs, writes ONE file of
                                           numbers and names (no prompt text, file names, commands or replies)
  python usage_audit.py report FILE        on the reviewer's PC: verdict + deep report from a collected file
  python usage_audit.py card               short card for the /context-coach skill (same findings, as fixes)

Every finding is priced as "what the same work would have cost done the trained way" (a counterfactual),
never as a count against a fixed line. Tier 1 = certain waste, tier 2 = probable (tested in context),
tier 3 = not judged, listed as questions. fix_by says who can remove it: habit (the person), setup (rules,
settings, the kit) or tool (Claude's own behaviour).
"""
import argparse, collections, datetime, glob, hashlib, io, json, os, platform, re, sys

SCHEMA = 1
# ---- tunables. These decide what counts; the trust test (tests/ + labelled chats) is what justifies them.
NOTES = 3_000              # tokens a handoff note adds to a fresh chat
BREAK_SEC = 3600           # a real break: with notes, a fresh chat is the trained way
COLD_MIN_CTX = 40_000      # below this a re-store is too cheap to matter
LEAN_START = 55_000        # a lean starting size (Claude Code's floor plus a short rules file)
DUMP = 8_000               # one command answering with this many tokens should have gone to a file
DUMP_KEPT = 500            # what the trained way keeps in the chat (counts + path)
BIG_READ = 20_000
SWITCH_MIN_CTX = 80_000    # a task switch only costs when the old task's chat is big
WORD_OVERLAP = 0.15        # share of a new message's words already seen in the task
LIGHT_OUT, LIGHT_TOOLS = 800, 2   # a light turn: short answer, at most two tool calls, no edits
LIGHT_SHARE = 0.8
LIGHT_GROWTH = 20_000      # a quick-questions chat grows less than this over its whole life
RETRY, REREAD = 3, 3
IDLE_CAP = 300             # seconds; longer gaps do not count as active time

PRICES = {  # $ per 1M tokens: (input, 1-hour cache write, cache read, output). List prices 2026-10.
    "fable-5":   (10.0, 20.0, 0.25, 50.0),   # the 5-minute write is 1.25x input, computed below
    "opus-5-5":  (4.0, 8.0, 0.2, 20.0),
    "opus":      (5.0, 10.0, 0.5, 25.0),
    "sonnet-5":  (2.0, 4.0, 0.2, 10.0),
    "sonnet":    (3.0, 6.0, 0.3, 15.0),
    "haiku-5-5": (0.1, 0.2, 0.01, 0.5),
    "haiku":     (1.0, 2.0, 0.1, 5.0),
}
CHEAPER = {"fable-5": "opus-5-5", "opus-5-5": "sonnet-5", "opus": "sonnet"}   # the next tier down
TOP = "fable-5"            # the costliest tier; working chats on it are a question, never counted as waste

def price_key(model):
    m = (model or "").lower()
    return next((k for k in PRICES if k in m), "opus-5-5")      # unknown models priced as Opus 5.5
def rates(model, key=None):
    i, w1, r, o = PRICES[key or price_key(model)]
    return dict(i=i / 1e6, w5=i * 1.25 / 1e6, w1=w1 / 1e6, r=r / 1e6, o=o / 1e6)
def step_cost(s, key=None):
    p = rates(s["model"], key)
    return s["i"] * p["i"] + s["cw5"] * p["w5"] + s["cw1"] * p["w1"] + s["cr"] * p["r"] + s["out"] * p["o"]

# ---- size estimate: characters per token by source, measured against the real tokenizer (context-coach v3)
DIV = {"read": 3.59, "other": 3.05, "shell": 2.58, "listing": 2.48, "mcp": 2.27}
def est(text, bucket="other"):
    heb = sum(1 for ch in text if "֐" <= ch <= "ۿ")   # Hebrew/Arabic are denser per character
    return round((len(text) - heb) / DIV.get(bucket, 3.05) + heb / 1.9)

def bucket(name, inp):
    cmd = str(inp.get("command", ""))
    if name.startswith("mcp__"): return "mcp"
    if name == "Read": return "read"
    if name in ("Bash", "PowerShell"):
        if re.search(r"^\s*(cd [^&]*&&\s*)?(cat|sed -n|head|tail|type|Get-Content)\b", cmd): return "read"
        if re.search(r"\bls\b|\bfind\b|\bdir\b|Get-ChildItem", cmd): return "listing"
        return "shell"
    return "other"

def text_of(c, box):
    if isinstance(c, str): return c
    out = []
    for x in c or []:
        if isinstance(x, dict):
            if x.get("type") == "text": out.append(x.get("text", ""))
            elif x.get("type") == "tool_result": out.append(text_of(x.get("content"), box))
            elif x.get("type") == "image": box[0] += 1
        elif isinstance(x, str): out.append(x)
    return "\n".join(out)

STOP = set("this that with from have what when your will would could should there their about into then them "
           "they please just like also make need want does done here which were been than some more only".split())
def words(text):
    """Content words of a typed message. Used on this PC only, to compare messages; never written out."""
    out = set()
    for w in re.findall(r"[^\W\d_]{4,}", text.lower()):
        if "֐" <= w[0] <= "׿" and len(w) > 4 and w[0] in "והבלמשכ": w = w[1:]   # Hebrew one-letter prefixes
        if w not in STOP: out.add(w)
    return out

def ts(o):
    try: return datetime.datetime.fromisoformat(str(o.get("timestamp", "")).replace("Z", "+00:00"))
    except Exception: return None
def h(x): return hashlib.sha1(x.encode("utf-8", "ignore")).hexdigest()[:12]
NOT_TYPED = ("<local-command", "<task-notification", "<system-reminder", "[SYSTEM NOTIFICATION", "<side-sessions", "<agent-message", "<ci-monitor")
EDITS = ("Edit", "Write", "MultiEdit", "NotebookEdit")

def scan(path):
    """One chat log -> steps (one per model reply, usage counted once), turns (one per typed message), events."""
    S = dict(steps=[], turns=[], results=[], cwd=None, entry=collections.Counter(), versions=set(),
             interrupts=0, rejects=0, tool_errors=0, limit_hits=[], compact_at=[], clears=0, hook_blocks=0,
             lines=(0, 0), exts=collections.Counter(), changed=set(), reads=collections.defaultdict(list),
             errs=collections.Counter(), skills=collections.Counter(), mcp=collections.Counter(), names=set())
    by_id, uses, turn = {}, {}, None
    if os.name == "nt" and len(path) >= 250 and not path.startswith("\\\\?\\"):
        path = "\\\\?\\" + os.path.abspath(path)         # Windows refuses paths over 260 characters without this
    with io.open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            try: o = json.loads(line)
            except Exception: continue                   # a log being written right now has a torn last line
            if not isinstance(o, dict): continue
            t = o.get("type"); m = o.get("message") if isinstance(o.get("message"), dict) else {}
            if S["cwd"] is None and o.get("cwd"): S["cwd"] = o["cwd"]
            if o.get("entrypoint"): S["entry"][o["entrypoint"]] += 1
            if o.get("version"): S["versions"].add(o["version"])
            if t == "assistant":
                u = m.get("usage") or {}
                if o.get("isApiErrorMessage"):
                    if "limit" in text_of(m.get("content"), [0]).lower(): S["limit_hits"].append(ts(o))
                elif u and m.get("model") != "<synthetic>" and (u.get("input_tokens") is not None):
                    key = m.get("id") or o.get("uuid")
                    g = lambda k: u.get(k, 0) or 0
                    cc = u.get("cache_creation") or {}
                    cw = g("cache_creation_input_tokens"); cw5 = cc.get("ephemeral_5m_input_tokens", 0) or 0
                    s = by_id.get(key)
                    if s is None:
                        s = by_id[key] = dict(t=ts(o), turn=len(S["turns"]) - 1); S["steps"].append(s)
                        if o.get("attributionSkill"): S["skills"][o["attributionSkill"]] += 1
                        if o.get("attributionMcpServer"): S["mcp"][o["attributionMcpServer"]] += 1
                    s.update(model=m.get("model"), effort=o.get("effort"), i=g("input_tokens"), cw5=min(cw5, cw),
                             cw1=cw - min(cw5, cw), cr=g("cache_read_input_tokens"), out=g("output_tokens"),
                             think=(u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0)
                    s["ctx"] = s["i"] + cw + s["cr"]
                for c in m.get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        name, inp = c.get("name", "?"), c.get("input") or {}
                        uses[c.get("id")] = (name, inp)
                        if turn is not None: turn["tools"] += 1
                        fp = inp.get("file_path") or inp.get("notebook_path")
                        if fp:
                            fp = str(fp).replace("\\", "/").lower(); S["names"].add(os.path.basename(fp))
                            if turn is not None: turn["files"].add(fp)
                            if name in EDITS:
                                S["changed"].add(fp); S["exts"][os.path.splitext(fp)[1] or "(none)"] += 1
                                if turn is not None: turn["edits"] += 1
            elif t == "user":
                ct = m.get("content")
                blocks = ct if isinstance(ct, list) else []
                results = [x for x in blocks if isinstance(x, dict) and x.get("type") == "tool_result"]
                for c in results:
                    name, inp = uses.get(c.get("tool_use_id"), ("?", {}))
                    b = bucket(name, inp); box = [0]
                    size = est(text_of(c.get("content"), box), b) + box[0] * 1500
                    S["results"].append(dict(at=len(S["steps"]), size=size, bucket=b))
                    sig = h(name + json.dumps(inp, sort_keys=True, default=str))
                    if c.get("is_error"): S["tool_errors"] += 1; S["errs"][sig] += 1
                    if b == "read" and inp.get("file_path"): S["reads"][h(str(inp["file_path"]).lower())].append((len(S["steps"]), size))
                pd = o.get("permissionDecision") or {}
                if pd.get("decision") == "reject" and str(pd.get("source", "")).startswith("user"): S["rejects"] += 1
                if o.get("isCompactSummary"): S["compact_at"].append(len(S["steps"])); continue
                if results or o.get("isMeta"): continue
                # the app may put its own reminder blocks in front of what the person typed: judge block by block
                parts = [ct] if isinstance(ct, str) else [x.get("text", "") for x in blocks if isinstance(x, dict) and x.get("type") == "text"]
                if any("[Request interrupted" in x for x in parts): S["interrupts"] += 1; continue
                mine = [x.strip() for x in parts if x.strip() and not x.strip().startswith(NOT_TYPED)]
                if not mine and not any(isinstance(x, dict) and x.get("type") == "image" for x in blocks): continue
                slash = bool(mine) and mine[0].startswith("<command-")      # a slash command: a human turn, no wording to compare
                turn = dict(t=ts(o), words=set() if slash else words("\n".join(mine)), files=set(), tools=0, edits=0)
                S["turns"].append(turn)
            elif t == "attachment":
                at = o.get("attachment") or {}        # a message typed while Claude was still working is queued, not a user record
                if at.get("type") == "queued_command" and at.get("humanTurn") and isinstance(at.get("prompt"), str):
                    turn = dict(t=ts(o), words=words(at["prompt"]), files=set(), tools=0, edits=0)
                    S["turns"].append(turn)
            elif t == "system":
                sub = o.get("subtype")
                if sub == "local_command" and (o.get("commandRun") or {}).get("command") == "clear": S["clears"] += 1
                elif sub == "informational" and ((o.get("promptSubmitEnding") or {}).get("ending") or {}).get("kind") == "blocked_by_hook":
                    S["hook_blocks"] += 1
                elif sub == "compact_boundary": S["compact_at"].append(len(S["steps"]))
            elif t == "cost-state":
                S["lines"] = (o.get("totalLinesAdded", 0) or 0, o.get("totalLinesRemoved", 0) or 0)
    S["steps"] = [s for s in S["steps"] if "ctx" in s and s["ctx"]]
    return S

def subagent_files(path):
    return sorted(glob.glob(os.path.join(os.path.splitext(path)[0], "subagents", "*.jsonl")))

def judge(S):
    """Price one chat's waste. Returns (findings {key: usd}, notes {key: numbers}, per-chat facts)."""
    steps, turns = S["steps"], S["turns"]
    F, N = collections.Counter(), collections.Counter()
    n = len(steps); first = steps[0]["ctx"]
    for s in steps: s["cost"] = step_cost(s)
    cost = sum(s["cost"] for s in steps)
    compact = sorted(set(S["compact_at"]) | {k for k in range(1, n) if steps[k]["ctx"] < 0.6 * steps[k - 1]["ctx"] and steps[k - 1]["ctx"] > 60_000})
    def carried(at):           # how many later steps re-read something that entered the chat at step `at`
        end = next((c for c in compact if c > at), n)
        return max(0, end - at - 1)
    # -- cache lifetime actually in force, per step (5 minutes or 1 hour), carried forward from the last store
    ttl = 3600; short_gap_usd = 0.0; cw5_total = restored = 0
    for k, s in enumerate(steps):
        if s["cw5"] or s["cw1"]: ttl_now = 300 if s["cw5"] > s["cw1"] else 3600
        else: ttl_now = ttl
        p = rates(s["model"]); cw = s["cw5"] + s["cw1"]; cw5_total += s["cw5"]
        if k and s["t"] and steps[k - 1]["t"]:
            gap = (s["t"] - steps[k - 1]["t"]).total_seconds()
            if gap > ttl and s["ctx"] >= COLD_MIN_CTX and cw >= 0.5 * s["ctx"]:
                wp = p["w5"] if s["cw5"] > s["cw1"] else p["w1"]
                if gap > BREAK_SEC:        # a real break: notes + a fresh chat would have stored only the start
                    F["cold_return"] += max(0, cw - first - NOTES) * wp; N["cold_return"] += 1
                else:                      # a short pause that outlived a 5-minute cache: a setting, not a habit
                    short_gap_usd += cw * (wp - p["r"]); restored += cw; N["short_cache"] += 1
        ttl = ttl_now
    if N["short_cache"]:
        p0 = rates(steps[0]["model"])
        # with the 1-hour cache those re-stores become reads, but every remaining store costs the higher rate
        net = short_gap_usd - (cw5_total - restored) * (p0["w1"] - p0["w5"])
        if net > 0: F["short_cache"] = net
        else: del N["short_cache"]
    # -- standing size above a lean start, stored once and re-read on every step
    if first > LEAN_START:
        p = rates(steps[0]["model"])
        F["heavy_start"] = (first - LEAN_START) * (p["w1"] + p["r"] * (n - 1)); N["heavy_start"] = 1
    # -- walls of text from commands, carried for the rest of the chat
    for r in S["results"]:
        if r["at"] == 0 or r["at"] >= n: continue      # never sent to the model: no step followed it
        p = rates(steps[r["at"]]["model"]); keep = carried(r["at"])   # stored on the next step, re-read after it
        if r["bucket"] in ("shell", "listing") and r["size"] > DUMP:
            F["dumps"] += (r["size"] - DUMP_KEPT) * (p["w1"] + p["r"] * keep); N["dumps"] += 1
        elif r["bucket"] == "read" and r["size"] > BIG_READ: N["q_big_reads"] += 1
        elif r["bucket"] == "mcp" and r["size"] > DUMP: N["q_connector_walls"] += 1
    # -- the same failing call repeated, and the same file read again and again (Claude's habits)
    avg = cost / n
    for sig, c in S["errs"].items():
        if c >= RETRY: F["retries"] += (c - 2) * avg; N["retries"] += c - 2
    for sig, rs in S["reads"].items():
        if len(rs) >= REREAD:
            for at, size in rs[2:]:
                if at >= n: continue
                p = rates(steps[at]["model"])
                F["rereads"] += size * (p["w1"] + p["r"] * carried(at)); N["rereads"] += 1
    # -- task switch inside a big chat: the old task's chat is re-read on every step of the new one
    seen_w, seen_f, seen_n, dead, switches = set(), set(), 0, 0, 0
    starts = collections.defaultdict(list)
    for k, s in enumerate(steps): starts[s["turn"]].append(k)
    for j, tu in enumerate(turns):
        ks = starts.get(j, [])
        before = steps[ks[0] - 1]["ctx"] if ks and ks[0] > 0 else 0
        dirs = {os.path.dirname(f) for f in tu["files"]}
        can_f, can_w = len(tu["files"]) >= 1, len(tu["words"]) >= 6
        # both kinds of evidence must exist and both must say "new": other folders AND other wording.
        # One alone is how a normal follow-up looks ("now write the mail about this").
        if before >= SWITCH_MIN_CTX and can_f and can_w and len(seen_w) >= 6 and seen_n >= 2:
            new_f = not (dirs & seen_f)
            new_w = len(tu["words"] & seen_w) / len(tu["words"]) < WORD_OVERLAP
            if new_f and new_w:
                switches += 1; dead = max(0, before - first); seen_w, seen_f, seen_n = set(), set(), 0
        seen_w |= tu["words"]; seen_f |= dirs; seen_n += len(tu["files"])
        for k in ks:
            if dead and steps[k]["ctx"] < 0.6 * (dead + first): dead = 0      # compacted: the old task is gone
            if dead: F["task_switch"] += dead * rates(steps[k]["model"])["r"]
    if switches: N["task_switch"] = switches
    else: F.pop("task_switch", None)
    # -- a chat of light turns only, run on a top model
    main = collections.Counter(price_key(s["model"]) for s in steps).most_common(1)[0][0]
    light = 0
    for j, tu in enumerate(turns):
        out = sum(steps[k]["out"] for k in starts.get(j, []))
        if tu["edits"] == 0 and tu["tools"] <= LIGHT_TOOLS and out <= LIGHT_OUT: light += 1
    grew = max(s["ctx"] for s in steps) - first          # quick questions barely grow a chat; loaded material does
    is_light = bool(turns) and light / len(turns) >= LIGHT_SHARE and not S["changed"] and grew < LIGHT_GROWTH
    if is_light and main in CHEAPER:
        alt = sum(step_cost(s, CHEAPER[main]) for s in steps if price_key(s["model"]) == main)
        F["light_on_top_model"] = sum(s["cost"] for s in steps if price_key(s["model"]) == main) - alt
        N["light_on_top_model"] = 1
    facts = dict(cost=cost, first=first, peak=max(s["ctx"] for s in steps), main=main, light=is_light,
                 switches=switches, compactions=len(compact))
    return {k: v for k, v in F.items() if v > 0.005}, dict(N), facts

FINDINGS = {  # key: (tier, fix_by, plain description)
    "cold_return":        (1, "habit", "big chat picked up again after a break of over an hour; notes and a fresh chat would have stored only the start"),
    "short_cache":        (1, "setup", "pauses of 5-60 minutes outlived a 5-minute cache; the 1-hour cache setting removes this"),
    "heavy_start":        (1, "setup", "every chat starts above a lean size (rules files, skills, connectors), re-read on every step"),
    "dumps":              (1, "setup", "commands answered with a wall of text that stayed in the chat; a house rule sends it to a file"),
    "retries":            (1, "tool",  "the same failing call repeated three or more times"),
    "rereads":            (1, "tool",  "the same file read three or more times"),
    "task_switch":        (2, "habit", "a new, unrelated task started inside a big chat (files and wording both changed)"),
    "light_on_top_model": (2, "habit", "a chat of short questions only, run on a top model"),
}

def active_seconds(times):
    times = sorted(x for x in times if x); return sum(min((b - a).total_seconds(), IDLE_CAP) for a, b in zip(times, times[1:]))

def collect(a):
    home = a.home or os.path.expanduser("~")
    pdir = os.path.join(home, ".claude", "projects")
    logs = glob.glob(os.path.join(pdir, "*", "*.jsonl"))
    if not logs: sys.exit("No chat logs found under " + pdir + ". Claude Code has not been used on this PC, or the logs were cleared.")
    now = datetime.datetime.now().timestamp(); cutoff = now - a.days * 86400
    files = sorted((f for f in logs if os.path.getmtime(f) >= cutoff), key=os.path.getmtime)   # first cut; the real test is the last step's time
    rows, forbidden = [], set()
    T = collections.defaultdict(float); tok = collections.Counter()
    by = {k: collections.Counter() for k in ("model", "project", "effort", "skill", "connector", "entry", "cache", "ext", "day", "fix", "finding")}
    fcount = collections.Counter(); qs = collections.Counter(); times_by_day = collections.defaultdict(list)
    limit_days, changed, versions = set(), 0, set()
    for f in files:
        S = scan(f)
        if not S["steps"]: continue
        last = S["steps"][-1]["t"]
        if last and last.timestamp() < cutoff: continue      # an old chat whose file was only touched (moved, synced)
        F, N, facts = judge(S)
        sub_cost = sub_steps = 0
        for sf in subagent_files(f):
            ss = scan(sf)["steps"]; sub_steps += len(ss); sub_cost += sum(step_cost(s) for s in ss)
        project = os.path.basename((S["cwd"] or os.path.dirname(f)).rstrip("\\/")) or "?"
        forbidden |= S["names"]; versions |= S["versions"]
        day = (S["steps"][-1]["t"] or datetime.datetime.fromtimestamp(os.path.getmtime(f))).astimezone().date().isoformat()
        typed = len(S["turns"]); auto = typed == 0
        for s in S["steps"]:
            by["model"][re.sub(r"^claude-", "", s["model"] or "?")] += s["cost"]
            by["effort"][s["effort"] or "?"] += s["cost"]
            by["cache"]["5m" if s["cw5"] > s["cw1"] else "1h" if s["cw1"] else "none"] += 1
            for k in ("i", "cw5", "cw1", "cr", "out", "think"): tok[k] += s[k]
            if s["t"]: times_by_day[s["t"].astimezone().date().isoformat()].append(s["t"])
        for tu in S["turns"]:
            if tu["t"]: times_by_day[tu["t"].astimezone().date().isoformat()].append(tu["t"])
        total = facts["cost"] + sub_cost
        by["project"][project] += total; by["day"][day] += total
        for k, v in S["skills"].items(): by["skill"][k] += v
        for k, v in S["mcp"].items(): by["connector"][k] += v
        for k, v in S["entry"].items(): by["entry"][k] += v
        for k, v in S["exts"].items(): by["ext"][k] += v
        for k, v in F.items(): by["finding"][k] += v; by["fix"][FINDINGS[k][1]] += v; fcount[k] += 1
        for k, v in N.items():
            if k.startswith("q_"): qs[k] += v
        T["usd"] += total; T["sub"] += sub_cost; T["auto"] += total if auto else 0
        T["steps"] += len(S["steps"]); T["typed"] += typed; T["interrupts"] += S["interrupts"]; T["rejects"] += S["rejects"]
        T["tool_errors"] += S["tool_errors"]; T["clears"] += S["clears"]; T["hook_blocks"] += S["hook_blocks"]
        T["added"] += S["lines"][0]; T["removed"] += S["lines"][1]; changed += len(S["changed"])
        T["edits"] += sum(tu["edits"] for tu in S["turns"]); T["tools"] += len(S["results"])
        for x in S["limit_hits"]:
            if x: limit_days.add(x.astimezone().date().isoformat())
        T["limit_hits"] += len(S["limit_hits"])
        if facts["peak"] > 200_000 and not facts["switches"]: qs["q_long_one_task"] += 1
        if facts["main"] == TOP and not facts["light"] and not auto: qs["q_top_model_working_chats"] += 1
        rows.append(dict(id=os.path.basename(f)[:8], day=day, project=project, usd=round(total, 3), steps=len(S["steps"]),
                         typed=typed, model=facts["main"], start=facts["first"], peak=facts["peak"],
                         helpers_usd=round(sub_cost, 3), edits=sum(tu["edits"] for tu in S["turns"]), files_changed=len(S["changed"]),
                         automated=auto, light=facts["light"], compactions=facts["compactions"],
                         waste={k: round(v, 3) for k, v in F.items()}, counts={k: v for k, v in N.items()}))
    if not rows: sys.exit(f"Chat logs exist, but none from the last {a.days} days had a usable step.")
    if a.hide_projects:
        alias = {p: f"Project {n + 1}" for n, (p, _) in enumerate(by["project"].most_common())}
        for r in rows: r["project"] = alias[r["project"]]
        by["project"] = collections.Counter({alias[p]: v for p, v in by["project"].items()})
    days = sorted(times_by_day)
    active = sum(active_seconds(v) for v in times_by_day.values())
    entry = by["entry"].most_common(1)[0][0] if by["entry"] else "?"
    seat = "gateway" if entry.endswith("-3p") else "subscription"
    try: seat = json.load(io.open(os.path.join(home, ".claude", "dhv-kit.json"), encoding="utf-8")).get("seat") or seat
    except Exception: pass
    r2 = lambda c, n=40: {k: round(v, 2) for k, v in c.most_common(n)}
    findings = [dict(key=k, tier=FINDINGS[k][0], fix_by=FINDINGS[k][1], usd=round(v, 2), share=round(v / T["usd"], 4),
                     chats=fcount[k], what=FINDINGS[k][2]) for k, v in by["finding"].most_common()]
    starts = sorted(r["start"] for r in rows)
    doc = dict(
        schema=SCHEMA, tool="usage-audit", generated=datetime.datetime.now().isoformat(timespec="minutes"), window_days=a.days,
        privacy="Numbers, dates and names of projects, models, skills and connectors only. No prompt text, replies, file names or commands.",
        not_visible=["chats in claude.ai or the desktop app outside the Code tab (no logs on the PC)", "other devices",
                     f"chat logs older than {a.days} days or already cleaned up by Claude Code"],
        machine=dict(os=platform.system(), claude_code=sorted(versions)[-3:], app=dict(by["entry"]), seat=seat,
                     cache_stores=dict(by["cache"]), logs_on_disk=len(logs),
                     oldest_log=datetime.date.fromtimestamp(min(os.path.getmtime(x) for x in logs)).isoformat()),
        totals=dict(usd_list_price=round(T["usd"], 2), chats=len(rows), steps=int(T["steps"]), tokens=dict(tok),
                    helpers_usd=round(T["sub"], 2), automated_usd=round(T["auto"], 2), by_model=r2(by["model"]),
                    by_project=r2(by["project"]), by_effort=r2(by["effort"]), steps_by_skill=r2(by["skill"]),
                    steps_by_connector=r2(by["connector"]), by_day=r2(collections.Counter(dict(sorted(by["day"].items()))), 400)),
        demand=dict(active_days=len(days), active_hours=round(active / 3600, 1), typed_messages=int(T["typed"]),
                    projects=len(by["project"]), most_chats_in_a_day=max(collections.Counter(r["day"] for r in rows).values()),
                    edits=int(T["edits"]), files_changed=changed, lines_added=int(T["added"]), lines_removed=int(T["removed"]),
                    tool_calls=int(T["tools"]), files_changed_by_type=r2(by["ext"], 15),
                    limit_hits=int(T["limit_hits"]), days_with_a_limit_hit=len(limit_days), interruptions=int(T["interrupts"]),
                    refused_actions=int(T["rejects"]), failed_tool_calls=int(T["tool_errors"]), clears=int(T["clears"]),
                    stops_by_house_rules=int(T["hook_blocks"]), median_start=starts[len(starts) // 2]),
        findings=findings, waste_by_fixer=r2(by["fix"]), not_judged=dict(qs), chats=rows)
    text = json.dumps(doc, indent=1, ensure_ascii=False)
    # privacy self-check: no file name seen in the logs may appear as a value or a key anywhere in the file
    leaves = set()
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items(): leaves.add(str(k).lower()); walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
        elif isinstance(x, str): leaves.add(x.lower())
    walk(doc)
    allowed = {x.lower() for x in list(by["project"]) + list(by["skill"]) + list(by["connector"])}
    leaked = [n for n in forbidden if n in leaves and n not in allowed]
    if leaked: sys.exit(f"Refusing to write: {len(leaked)} file name(s) would appear in the report. This is a bug; nothing was saved.")
    return doc, text

def summary(doc):
    t, d = doc["totals"], doc["demand"]
    out = [f"Usage report, last {doc['window_days']} days: {t['chats']} chats on {d['active_days']} days, {d['active_hours']} active hours, {d['typed_messages']} messages typed.",
           "What is in the file: numbers, dates, and the names of projects, models, skills and connectors.",
           "What is NOT in it: anything you typed, anything Claude wrote, file names, commands.",
           "Not visible to this check: " + "; ".join(doc["not_visible"]) + "."]
    return "\n".join(out)

# ------------------------------------------------------------------ report (reviewer's side)
def verdict(doc, budget=None):
    usd = doc["totals"]["usd_list_price"] or 1e-9
    f = doc["findings"]
    t1h = sum(x["usd"] for x in f if x["tier"] == 1 and x["fix_by"] == "habit")
    t1s = sum(x["usd"] for x in f if x["tier"] == 1 and x["fix_by"] == "setup")
    t1t = sum(x["usd"] for x in f if x["tier"] == 1 and x["fix_by"] == "tool")
    t2 = sum(x["usd"] for x in f if x["tier"] == 2)
    monthly = usd * 30 / doc["window_days"]; k = monthly / usd
    lean_hi, lean_lo = (usd - t1h - t1s) * k, (usd - t1h - t1s - t2) * k      # usage once certain / certain+probable waste is gone
    d = doc["demand"]; conf = []
    if doc["totals"]["chats"] < 10: conf.append("fewer than 10 chats")
    if d["active_days"] < 7: conf.append("fewer than 7 active days")
    if not d["limit_hits"]: conf.append("no limit hit recorded in these logs")
    conf.append("claude.ai chat use is not visible")
    v = dict(monthly=monthly, certain_habit=t1h * k, certain_setup=t1s * k, tool=t1t * k, probable=t2 * k,
             lean_range=(lean_lo, lean_hi), budget=budget, caveats=conf)
    cert, prob = (t1h + t1s) / usd, t2 / usd
    if budget:
        if monthly <= budget: v["call"], v["why"] = "within allowance", f"this PC's usage (${monthly:.0f}/month at list price) is under the ${budget:.0f} allowance; the overrun is elsewhere (chat, another device) or in another period"
        elif lean_hi <= budget: v["call"], v["why"] = ("fix setup first" if t1s > t1h else "train first"), f"removing certain waste alone brings ${monthly:.0f} down to ${lean_hi:.0f}, inside the ${budget:.0f} allowance"
        elif lean_lo > budget: v["call"], v["why"] = "needs more", f"even with every certain and probable waste removed, usage is ${lean_lo:.0f}-${lean_hi:.0f} against a ${budget:.0f} allowance"
        else: v["call"], v["why"] = "borderline", f"certain waste removed leaves ${lean_hi:.0f} (over ${budget:.0f}); probable waste removed too leaves ${lean_lo:.0f} (under)"
    else:   # no allowance in money (a subscription seat): the call rests on shares, which is weaker; say so
        conf.append("no money allowance for this seat, so the call rests on waste shares")
        if cert >= 0.25: v["call"], v["why"] = ("fix setup first" if t1s > t1h else "train first"), f"{cert:.0%} of usage is certain waste"
        elif cert + prob <= 0.12: v["call"], v["why"] = "needs more", f"only {cert + prob:.0%} of usage is certain or probable waste"
        else: v["call"], v["why"] = "borderline", f"{cert:.0%} certain and {prob:.0%} probable waste"
    return v

def report(doc, budget=None, base=None):
    v = verdict(doc, budget); t, d = doc["totals"], doc["demand"]; usd = t["usd_list_price"] or 1e-9
    pct = lambda x: f"{x / usd:.0%}"
    L = [f"# Usage audit: {doc['generated'][:10]}, last {doc['window_days']} days", "",
         f"**Verdict: {v['call'].upper()}.** {v['why'][0].upper() + v['why'][1:]}.", "",
         f"- Usage: ${v['monthly']:.0f} a month at list price ({doc['machine']['seat']} seat" + (f", allowance ${budget:.0f}" if budget else "") + ")",
         f"- Certain waste the person can stop: ${v['certain_habit']:.0f} a month · fixable by setup: ${v['certain_setup']:.0f} · Claude's own habits: ${v['tool']:.0f}",
         f"- Probable waste: ${v['probable']:.0f} a month",
         f"- Usage once trained: ${v['lean_range'][0]:.0f}-${v['lean_range'][1]:.0f} a month",
         f"- Confidence notes: {'; '.join(v['caveats'])}", "",
         "## Workload (the demand side)", "",
         "| measure | this person |" + (" baseline |" if base else ""), "|---|---|" + ("---|" if base else "")]
    bd, bt = (base["demand"], base["totals"]) if base else ({}, {})
    def row(name, val, bval=None): L.append(f"| {name} | {val} |" + (f" {bval} |" if base else ""))
    per = lambda tt, dd: f"${tt['usd_list_price'] / max(dd['active_hours'], 0.1):.2f}"
    row("active days / hours", f"{d['active_days']} / {d['active_hours']}", f"{bd.get('active_days')} / {bd.get('active_hours')}" if base else None)
    row("chats / messages typed", f"{t['chats']} / {d['typed_messages']}", f"{bt.get('chats')} / {bd.get('typed_messages')}" if base else None)
    row("cost per active hour", per(t, d), per(bt, bd) if base else None)
    row("cost per typed message", f"${usd / max(d['typed_messages'], 1):.2f}", f"${bt['usd_list_price'] / max(bd['typed_messages'], 1):.2f}" if base else None)
    row("projects", d["projects"], bd.get("projects"))
    row("files changed / edits", f"{d['files_changed']} / {d['edits']}", f"{bd.get('files_changed')} / {bd.get('edits')}" if base else None)
    row("typical starting size", f"{d['median_start'] / 1000:.0f}k", f"{bd.get('median_start', 0) / 1000:.0f}k" if base else None)
    row("limit hits (days)", f"{d['limit_hits']} ({d['days_with_a_limit_hit']})", f"{bd.get('limit_hits')} ({bd.get('days_with_a_limit_hit')})" if base else None)
    row("interruptions / failed tool calls", f"{d['interruptions']} / {d['failed_tool_calls']}", f"{bd.get('interruptions')} / {bd.get('failed_tool_calls')}" if base else None)
    row("automated runs (no typed message)", pct(t["automated_usd"]), f"{bt['automated_usd'] / (bt['usd_list_price'] or 1e-9):.0%}" if base else None)
    row("helper agents", pct(t["helpers_usd"]), f"{bt['helpers_usd'] / (bt['usd_list_price'] or 1e-9):.0%}" if base else None)
    L += ["", "## Waste, priced against the trained way", "", "| finding | certainty | who fixes it | share of usage | chats | what happened |", "|---|---|---|---|---|---|"]
    for x in doc["findings"]:
        L.append(f"| {x['key'].replace('_', ' ')} | {'certain' if x['tier'] == 1 else 'probable'} | {x['fix_by']} | {x['share']:.1%} | {x['chats']} | {x['what']} |")
    if not doc["findings"]: L.append("| none found | | | | | |")
    q = doc["not_judged"]
    L += ["", "## Not judged: ask the person", ""]
    asks = [("q_long_one_task", "chats that grew past 200k on what looks like one continuous task. What were they?"),
            ("q_top_model_working_chats", "working chats (edits, many tool calls) on a top model. Did the work need it?"),
            ("q_big_reads", "very large files read into a chat. Was the whole file needed?"),
            ("q_connector_walls", "large answers from connectors (mail, browser, boards). Not the person's doing; a setup question.")]
    L += [f"- {q[k]} {text}" for k, text in asks if q.get(k)] or ["- nothing"]
    L += ["", "## Where the usage went", "",
          "By model: " + ", ".join(f"{k} {pct(x)}" for k, x in t["by_model"].items()),
          "", "By effort level: " + ", ".join(f"{k} {pct(x)}" for k, x in t["by_effort"].items()),
          "", "By project: " + ", ".join(f"{k} {pct(x)}" for k, x in list(t["by_project"].items())[:8]),
          "", "Cache in force (stores): " + ", ".join(f"{k}: {n}" for k, n in doc["machine"]["cache_stores"].items()),
          "", "## The ten costliest chats", "", "| day | project | share | typed | start | peak | waste found |", "|---|---|---|---|---|---|---|"]
    for r in sorted(doc["chats"], key=lambda r: -r["usd"])[:10]:
        w = ", ".join(k.replace("_", " ") for k in r["waste"]) or ("automated run" if r["automated"] else "none")
        L.append(f"| {r['day']} | {r['project']} | {pct(r['usd'])} | {r['typed']} | {r['start'] / 1000:.0f}k | {r['peak'] / 1000:.0f}k | {w} |")
    L += ["", "## Not visible to this audit", ""] + [f"- {x}" for x in doc["not_visible"]]
    return "\n".join(L) + "\n", v

FIX = {  # what the coach offers for each finding, in the person's terms
    "cold_return": "before a break of an hour or more, ask for notes and come back to a new chat",
    "short_cache": "switch on the one-hour memory setting, so a coffee break no longer re-stores the chat",
    "heavy_start": "trim what loads at the start of every chat (rules file, unused skills and connectors)",
    "dumps": "add the house rule that sends long command output to a file",
    "task_switch": "new task, new chat",
    "light_on_top_model": "quick questions go to the lighter model",
}
def card(doc, prev=None):
    usd = doc["totals"]["usd_list_price"] or 1e-9
    L = [f"USAGE CARD  last {doc['window_days']} days  {doc['totals']['chats']} chats  seat: {doc['machine']['seat']}",
         f"start size (typical): {doc['demand']['median_start'] / 1000:.0f}k   limit hits: {doc['demand']['limit_hits']}", "FIXES, largest first (share of usage it would free):"]
    fx = [x for x in doc["findings"] if x["key"] in FIX and x["share"] >= 0.01]     # under 1% is not worth anyone's attention
    for x in fx[:5]:
        L.append(f"  {x['share']:.0%}  [{x['key']}] {'certain' if x['tier'] == 1 else 'probable'}, in {x['chats']} of {doc['totals']['chats']} chats: {FIX[x['key']]}")
    if not fx: L.append("  nothing worth changing was found")
    rec = sum(x["usd"] for x in fx) / usd
    L.append(f"recoverable in total: {rec:.0%}")
    if prev:
        pr = sum(x["usd"] for x in prev["findings"] if x["key"] in FIX) / (prev["totals"]["usd_list_price"] or 1e-9)
        L.append(f"SINCE LAST RUN ({prev['generated'][:10]}): recoverable {pr:.0%} -> {rec:.0%}, start size {prev['demand']['median_start'] / 1000:.0f}k -> {doc['demand']['median_start'] / 1000:.0f}k")
        for x in fx:
            was = next((y["share"] for y in prev["findings"] if y["key"] == x["key"]), 0)
            if abs(was - x["share"]) >= 0.02: L.append(f"  {x['key']}: {was:.0%} -> {x['share']:.0%}")
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("collect", "card"):
        c = sub.add_parser(name)
        c.add_argument("--days", type=int, default=30); c.add_argument("--home", help="another user folder (tests)")
        c.add_argument("--hide-projects", action="store_true", help="write Project 1, 2, 3 instead of folder names")
        c.add_argument("--out", help="where to save the file")
    r = sub.add_parser("report")
    r.add_argument("file"); r.add_argument("--budget", type=float, help="the seat's monthly allowance in dollars, if it has one")
    r.add_argument("--baseline", help="a collected file to compare against (a trained user)"); r.add_argument("--out")
    a = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        try: s.reconfigure(encoding="utf-8")
        except Exception: pass
    if a.cmd == "report":
        doc = json.load(io.open(a.file, encoding="utf-8"))
        base = json.load(io.open(a.baseline, encoding="utf-8")) if a.baseline else None
        budget = a.budget or (15.0 if doc["machine"]["seat"] == "gateway" else None)
        text, v = report(doc, budget, base)
        out = a.out or os.path.splitext(a.file)[0] + "-report.md"
        io.open(out, "w", encoding="utf-8").write(text)
        print(f"Verdict: {v['call']} - {v['why']}\nReport: {out}")
        return
    doc, text = collect(a)
    home = a.home or os.path.expanduser("~")
    if a.cmd == "collect":
        out = a.out or os.path.join(home, f"claude-usage-report-{datetime.date.today():%Y%m%d}.json")
        io.open(out, "w", encoding="utf-8").write(text)
        print(summary(doc)); print(f"\nSaved: {out}\nOpen it to see exactly what it holds, then send that one file.")
    else:
        runs = os.path.join(home, ".claude", "context-coach", "runs"); os.makedirs(runs, exist_ok=True)
        old = sorted(glob.glob(os.path.join(runs, "audit-*.json")))
        prev = json.load(io.open(old[-1], encoding="utf-8")) if old else None
        print(card(doc, prev))
        io.open(a.out or os.path.join(runs, f"audit-{datetime.datetime.now():%Y%m%d-%H%M}.json"), "w", encoding="utf-8").write(text)

if __name__ == "__main__":
    main()
