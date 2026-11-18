#!/usr/bin/env python
"""The dhv-team kit's hooks: team rules, notes for a fresh chat, and two gates that keep chats cheap.

    python handoff_gate.py start    # SessionStart: the team rules; a fresh chat also gets HANDOFF.md
    python handoff_gate.py stop     # Stop: past the handoff line, block once and ask for HANDOFF.md
    python handoff_gate.py prompt   # UserPromptSubmit: hold back the first message to a long chat gone
                                    # cold; after a handoff, a one-line nudge every 3rd message

Ported from Dan's own ~/.claude/hooks (handoff-gate.sh, cold-cache-gate.py). Standard library only;
every mode fails open - a hook must never break a session. State lives in ~/.claude/state, not next to
this file, because a plugin update replaces this folder. The person's switches and language come from
~/.claude/dhv-kit.json (written by /start). hooks.json calls this through run.ps1, which skips it when
Python is missing. Tests: tests/test_gate.py at the repo root.
"""
import datetime, json, os, re, sys, time

# Hook stdout is a pipe; on a Hebrew Windows locale Python would encode it as cp1255 and any dash or
# arrow in HANDOFF.md would raise, which the catch-all hides - the hook would silently do nothing.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# Fixed token lines, not a % of the window: the Stop payload does not name the model, and the model id
# in the transcript never says whether it has the 1M window. On a 200k-window model Claude Code's own
# auto-compact acts before the first line; the usage line still applies.
# Per seat: (first handoff line, then every, usage line in list-price dollars - only a weight, never
# shown to the person). A gateway seat has a small monthly budget ($15 by default, a typical chat $2-4),
# so its lines come earlier. The seat is written by /start; see seat_of().
SEAT_LINES = {"team": (200_000, 100_000, 12.0), "gateway": (100_000, 50_000, 3.0)}
NUDGE_EVERY = 3        # prompts between nudges once the gate has fired
# Claude Code caps what a hook's stdout may add to a chat at 10,000 characters; past it Claude gets a
# file path and a 2,000-character preview, which would cut the rules too (code.claude.com/docs/en/hooks,
# checked 2026-11-17). So the whole start output stays under this, rules first.
HOOK_CAP = 9_500
TAIL = 4_000_000       # bytes the cold check reads from the end of the transcript; the last step is there

# $ per million tokens, Anthropic list prices: new input, cache read, output. Storing (cache write) costs
# 2x input on the 1-hour cache and 1.25x on the 5-minute one; each step's usage says which it used.
# Source: the maintainer's price card (measured from his own logs, Oct 2026). Fable is not on that card;
# its line is the plugin's September one. Unknown ids fall back to opus. "<synthetic>" entries carry
# zero usage, so they cost nothing instead of breaking the sum.
PRICES = {"fable": (10.0, 0.25, 50.0), "opus": (4.0, 0.2, 20.0), "sonnet": (2.0, 0.2, 10.0),
          "haiku": (0.1, 0.01, 0.5)}

BANNER_LINE = {
    "en": ("\U0001F6D1 **Notes saved to HANDOFF.md - type /clear to start a fresh chat; it picks the "
           "notes up by itself.**"),
    "he": ("\U0001F6D1 **הסיכום נשמר ב-HANDOFF.md - הקלידו /clear כדי לפתוח צ'אט חדש; הוא ימשיך מהסיכום "
           "לבד.**"),
}
# Claude's own reply ends with one of these after a handoff. The last is Dan's personal banner.
BANNERS = ("\U0001F6D1 **Notes saved to HANDOFF.md", "\U0001F6D1 **הסיכום נשמר ב-HANDOFF.md",
           "\U0001F6D1 **Handoff done (")
TAG = "Handoff line crossed"   # opening words of our own block reason; found again in the transcript

HOME = os.path.expanduser("~")
STATE = os.path.join(HOME, ".claude", "state")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The person's own switches, written by /start; this hook only reads them. Missing file or key = default.
# A plugin update replaces the plugin folder, so the file lives in ~/.claude, not here.
SETTINGS_FILE = os.path.join(HOME, ".claude", "dhv-kit.json")
DEFAULTS = {"language": "he", "handoff_stop": True, "cold_hold": True, "seat": "team"}


def settings():
    s = dict(DEFAULTS)
    try:
        with open(SETTINGS_FILE, encoding="utf-8-sig") as fh:     # -sig: Notepad may add a BOM
            s.update({k: v for k, v in json.load(fh).items() if k in DEFAULTS})
    except Exception:
        pass
    if s["language"] not in BANNER_LINE:
        s["language"] = "he"
    return s


def seat_of(conf):
    """"gateway" when /start recorded it, or when this chat is sent to an address that is not Anthropic's
    (how a gateway seat is wired). The cache length no longer tells: gateway seats have the hour too."""
    if conf.get("seat") == "gateway":
        return "gateway"
    base = (os.environ.get("ANTHROPIC_BASE_URL") or "").lower()
    return "gateway" if base and "anthropic.com" not in base else "team"


def lines(conf):
    """The lines for this person, in tokens and dollars: first, every, usage, cold. The DHV_* environment
    variables (thousands of tokens) override the seat's token lines; the cold line follows the first."""
    first, every, usage = SEAT_LINES[seat_of(conf)]

    def env_k(name, default):
        try:
            return int(os.environ[name]) * 1000
        except Exception:
            return default
    first = env_k("DHV_HANDOFF_FIRST_K", first)
    return {"first": first, "every": env_k("DHV_HANDOFF_EVERY_K", every), "usage": usage,
            "cold": env_k("DHV_COLD_K", first)}


# What the person reads, per language. The Stop reason is addressed to Claude, so it stays English.
TEXT = {
    "en": {
        "minutes": "%d minutes", "hours": "%.0f hours",
        "cold_head": ("Not sent yet. This chat is long and has been idle %s, so Claude's short-term memory of "
                      "it has run out: the next message makes Claude read all of it again at full price, a big "
                      "bite of the usage limit. "),
        "cold_current": ("The notes in HANDOFF.md are up to date, so the cheaper way on is to type /clear and "
                         "ask there; the fresh chat picks the notes up. To carry on here anyway, send the "
                         "message again."),
        "cold_none": ("There are no up-to-date notes, so that cost comes whatever you do. Same work: send the "
                      "message again. Something new: send /handoff first, then /clear."),
        "nudge": ("Each message in this chat now uses several times more of your usage limit than at the "
                  "start. Your notes are saved in HANDOFF.md - type /clear whenever you are ready and the "
                  "fresh chat carries on from them."),
    },
    "he": {
        "minutes": "%d דקות", "hours": "%.0f שעות",
        "cold_head": ("ההודעה עוד לא נשלחה. הצ'אט הזה ארוך ועמד בלי שימוש %s, ולכן הזיכרון הקצר של Claude "
                      "לגביו פג: ההודעה הבאה תגרום ל-Claude לקרוא את כולו מחדש במחיר מלא, נגיסה גדולה ממכסת "
                      "השימוש. "),
        "cold_current": ("הסיכום ב-HANDOFF.md עדכני, ולכן הדרך החסכונית להמשיך היא להקליד /clear ולשאול שם; "
                         "הצ'אט החדש ימשיך מהסיכום. כדי להמשיך כאן בכל זאת, שלחו את ההודעה שוב."),
        "cold_none": ("אין סיכום עדכני, אז העלות הזו תגיע בכל מקרה. אם זו אותה עבודה: שלחו את ההודעה שוב. "
                      "אם זה משהו חדש: שלחו קודם /handoff ואחר כך /clear."),
        "nudge": ("כל הודעה בצ'אט הזה צורכת עכשיו פי כמה ממכסת השימוש מאשר בהתחלה. הסיכום שמור ב-HANDOFF.md - "
                  "הקלידו /clear כשנוח לכם, והצ'אט החדש ימשיך ממנו."),
    },
}


def longpath(p):
    # Windows refuses paths past ~260 chars unless long paths are switched on machine-wide, and chat
    # logs for deep project folders get there. The \\?\ prefix lifts the limit for absolute paths.
    p = os.path.abspath(p)
    return "\\\\?\\" + p if os.name == "nt" and len(p) > 240 and not p.startswith("\\\\?\\") else p


def levels(ctx, dollars, L):
    return (0 if ctx < L["first"] else 1 + (ctx - L["first"]) // L["every"]), int(dollars // L["usage"])


def used(u):
    """What the next step has to read: everything this step read, plus what it wrote."""
    return sum(u.get(k, 0) or 0 for k in ("input_tokens", "cache_read_input_tokens",
                                         "cache_creation_input_tokens", "output_tokens"))


def cost(u, model):
    p = next((v for k, v in PRICES.items() if k in model), PRICES["opus"])
    cc = u.get("cache_creation") or {}
    w5, w1 = cc.get("ephemeral_5m_input_tokens") or 0, cc.get("ephemeral_1h_input_tokens") or 0
    if not (w5 or w1):
        w1 = u.get("cache_creation_input_tokens") or 0      # no breakdown: assume the 1-hour cache
    return ((u.get("input_tokens") or 0) * p[0] + (w5 * 1.25 + w1 * 2) * p[0]
            + (u.get("cache_read_input_tokens") or 0) * p[1] + (u.get("output_tokens") or 0) * p[2]) / 1e6


def cache_minutes(u):
    """How long this step's cache lives: 60 on a subscription, 5 on an API key, gateway or extra usage."""
    cc = u.get("cache_creation") or {}
    if cc.get("ephemeral_1h_input_tokens"):
        return 60
    if cc.get("ephemeral_5m_input_tokens"):
        return 5
    return None


def main_step(line):
    """The usage of a main-chat model step on this transcript line, or None."""
    if '"usage"' not in line:
        return None
    try:
        o = json.loads(line)
    except Exception:
        return None                              # a live transcript can end in a torn line
    if o.get("isSidechain") or o.get("type") != "assistant":
        return None                              # subagents have their own context
    msg = o.get("message") or {}
    u = msg.get("usage") or {}
    if u.get("input_tokens") is None and u.get("cache_read_input_tokens") is None:
        return None
    return o, msg, u


def scan(path, L):
    """One pass over the transcript: context now, dollars, whether this turn already printed a handoff
    banner, and the highest levels past firings announced (so a lost marker file can never make the
    same line fire twice). Streaming repeats usage on every chunk of one reply, so usage is kept per
    message id and summed once."""
    per, last = {}, None
    last_prompt = last_banner = -1
    seen = {"ctx": 0, "cost": 0}
    with open(longpath(path), encoding="utf-8", errors="ignore") as fh:
        for i, line in enumerate(fh):
            if TAG in line:
                m = re.search(r"handoff line (\d+), usage line (\d+)", line)
                if m:
                    seen["ctx"] = max(seen["ctx"], int(m.group(1)))
                    seen["cost"] = max(seen["cost"], int(m.group(2)))
                m = re.search(r"at (\d+)k of context", line)              # wording of version 1.x
                if m:
                    seen["ctx"] = max(seen["ctx"], levels(int(m.group(1)) * 1000, 0, L)[0])
                m = re.search(r"~\$(\d+) API-equivalent", line)           # wording of version 1.x
                if m:
                    seen["cost"] = max(seen["cost"], levels(0, int(m.group(1)), L)[1])
            if '"user"' in line:
                try:
                    o = json.loads(line)
                except Exception:
                    o = {}
                if o.get("type") == "user" and not o.get("isSidechain"):
                    # Tool results are also "user" lines; only a typed prompt starts a new turn.
                    content = (o.get("message") or {}).get("content")
                    blocks = content if isinstance(content, list) else []
                    if isinstance(content, str) or not any(
                            isinstance(b, dict) and b.get("type") == "tool_result" for b in blocks):
                        last_prompt = i
            step = main_step(line)
            if not step:
                continue
            o, msg, u = step
            content = msg.get("content")
            if isinstance(content, list) and any(
                    isinstance(b, dict) and b.get("type") == "text" and any(s in b.get("text", "") for s in BANNERS)
                    for b in content):
                last_banner = i
            per[msg.get("id") or o.get("uuid")] = (u, (msg.get("model") or "").lower())
            last = u
    dollars = sum(cost(u, model) for u, model in per.values())
    return (used(last) if last else 0), dollars, last_banner > last_prompt, seen


def last_step(path):
    """(timestamp, size, cache minutes) of the last main-chat step, read from the end of the file."""
    last, minutes = None, None
    with open(longpath(path), "rb") as fh:
        fh.seek(0, 2)
        fh.seek(max(0, fh.tell() - TAIL))
        data = fh.read().decode("utf-8", "ignore")
    for line in data.splitlines():
        step = main_step(line)
        if step:
            o, _, u = step
            last = (o.get("timestamp"), used(u))
            minutes = cache_minutes(u) or minutes
    if not last or not last[0]:
        return None
    return last[0], last[1], minutes or 60     # unknown: assume the hour, the quieter choice


def own_hooks(event):
    """Commands the person already runs for this event from their own settings.json. Dan (and anyone
    who ran the context-coach installer) has a personal gate; running two would ask twice."""
    try:
        with open(os.path.join(HOME, ".claude", "settings.json"), encoding="utf-8") as fh:
            groups = (json.load(fh).get("hooks") or {}).get(event) or []
        return " ".join(h.get("command", "") for g in groups for h in g.get("hooks", []))
    except Exception:
        return ""


def safe(sid):
    return re.sub(r"[^\w-]", "", sid or "unknown")


def marker(sid):
    return os.path.join(STATE, "dhv-handoff-%s.json" % safe(sid))


def read_marker(sid):
    try:
        with open(marker(sid), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def write_marker(sid, data):
    os.makedirs(STATE, exist_ok=True)
    with open(marker(sid), "w", encoding="utf-8") as fh:
        json.dump(data, fh)


def stop(ev):
    if ev.get("stop_hook_active"):
        return                                   # this reply was already our handoff - let it end
    conf = settings()
    if not conf["handoff_stop"]:
        return                                   # switched off by the person in /start
    cmds = own_hooks("Stop")
    if "handoff-gate" in cmds or "context-coach" in cmds:
        return
    tp, sid = ev.get("transcript_path"), ev.get("session_id")
    if not tp or not os.path.isfile(longpath(tp)):
        return
    L = lines(conf)
    ctx, dollars, done, announced = scan(tp, L)
    if not ctx:
        return
    ctx_level, cost_level = levels(ctx, dollars, L)
    seen = read_marker(sid) or {"ctx": 0, "cost": 0, "prompts": 0}
    for k in ("ctx", "cost"):
        seen[k] = max(seen.get(k, 0), announced[k])
    if done:
        # A handoff (manual /handoff too) just happened: record the levels and stay quiet.
        # Only past a line: a marker is what turns on the nudges, and an early /handoff needs none.
        if ctx_level or cost_level:
            seen.update(ctx=max(seen["ctx"], ctx_level), cost=max(seen["cost"], cost_level))
            write_marker(sid, seen)
        return
    if ctx_level <= seen["ctx"] and cost_level <= seen["cost"]:
        return
    seen.update(ctx=max(seen["ctx"], ctx_level), cost=max(seen["cost"], cost_level), prompts=0)
    write_marker(sid, seen)
    reason = (
        "%s (handoff line %d, usage line %d). This chat is now long: every message re-reads all of it "
        "and uses up the person's usage limit, so the cheapest next step is a fresh chat that starts "
        "from written notes. Start nothing new. Run the handoff skill now (it writes HANDOFF.md in the "
        "project root) and end your reply with its closing line, exactly: %s"
        % (TAG, seen["ctx"], seen["cost"], BANNER_LINE[conf["language"]]))
    print(json.dumps({"decision": "block", "reason": reason}))


def dhv_repo(cwd):
    """True when cwd is inside a git repo whose remote is in the DHV-med GitHub organization."""
    d = os.path.abspath(cwd)
    while True:
        g = os.path.join(d, ".git")
        if os.path.isdir(g):
            cfg = os.path.join(g, "config")
            break
        if os.path.isfile(g):                    # a worktree: .git is a file naming the real folder
            with open(g, encoding="utf-8", errors="ignore") as fh:
                gd = fh.read().split("gitdir:", 1)[-1].strip()
            gd = gd if os.path.isabs(gd) else os.path.join(d, gd)
            common = os.path.join(gd, "commondir")
            if os.path.isfile(common):
                with open(common, encoding="utf-8") as fh:
                    gd = os.path.join(gd, fh.read().strip())
            cfg = os.path.join(gd, "config")
            break
        parent = os.path.dirname(d)
        if parent == d:
            return False
        d = parent
    try:
        with open(cfg, encoding="utf-8", errors="ignore") as fh:
            return re.search(r"github\.com[:/]+dhv-med/", fh.read(), re.I) is not None
    except Exception:
        return False


def read_rules(name):
    try:
        with open(os.path.join(ROOT, "rules", name), encoding="utf-8") as fh:
            return fh.read().strip()
    except Exception:
        return ""


def start(ev):
    try:                                         # sweep markers older than two days
        for f in os.listdir(STATE):
            p = os.path.join(STATE, f)
            if f.startswith("dhv-") and time.time() - os.path.getmtime(p) > 2 * 86400:
                os.remove(p)
    except Exception:
        pass
    cwd = ev.get("cwd") or os.getcwd()
    # Tool-repo rules only where they apply: elsewhere "git pull" or "/ship-check" would misfire.
    out = [r for r in (read_rules("core.md"), dhv_repo(cwd) and read_rules("tool-repo.md")) if r]
    lang = settings()["language"]
    out.append("This person's reply language (their kit settings): %s. If they write in another language, "
               "answer in that one." % {"he": "Hebrew", "en": "English"}[lang])
    if ev.get("source") in (None, "startup", "clear") and "context-coach" not in own_hooks("SessionStart"):
        # Only a fresh chat gets the notes: a resumed or compacted one still has its thread, and the
        # personal context-coach copy already injects them.
        path = longpath(os.path.join(cwd, "HANDOFF.md"))
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
            # the notes get what the cap leaves after the rules (about 5,000 characters; the handoff
            # skill writes under 40 lines, which fits). 500 = the sentence around them and the joins.
            room = max(1000, HOOK_CAP - sum(len(o) for o in out) - 500)
            if len(text) > room:
                text = text[:room] + "\n\n[Cut here: HANDOFF.md is longer. Read the rest of the file before acting on these notes.]"
            age_h = (time.time() - os.path.getmtime(path)) / 3600
            when = ("just now" if age_h < 1 else "%.0f hours ago" % age_h if age_h < 48
                    else "%.0f days ago" % (age_h / 24))
            out.append("The previous chat left these notes in HANDOFF.md (%s). Treat them as where the work "
                       "stands; do not re-read the file unless the notes say they were cut. If the person's first message is about this work, "
                       "open with two or three plain lines on where things stand and the next step.\n\n%s"
                       % (when, text))
    if out:
        print("\n\n".join(out))


def cold(ev):
    """Hold back the first message to a long chat whose cache expired. That message re-stores the whole
    chat at the storing price, so a Stop hook would be too late. Sending again goes through."""
    if (ev.get("prompt") or "").lstrip().startswith("/"):
        return False                             # a command or skill (/handoff too): let it through
    conf = settings()
    if not conf["cold_hold"]:
        return False                             # switched off by the person in /start
    t = TEXT[conf["language"]]
    cmds = own_hooks("UserPromptSubmit")
    if "cold-cache-gate" in cmds or "context-coach" in cmds:
        return False
    tp, sid = ev.get("transcript_path"), ev.get("session_id")
    if not tp or not os.path.isfile(longpath(tp)):
        return False
    step = last_step(tp)
    if not step or step[1] < lines(conf)["cold"]:
        return False
    stamp, _, minutes = step
    # the log stamps a step when it finishes; the cache's clock started earlier, so this errs towards warm
    then = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    idle = (datetime.datetime.now(datetime.timezone.utc) - then).total_seconds() / 60
    if idle < minutes:
        return False
    path = os.path.join(STATE, "dhv-cold-%s.txt" % safe(sid))
    try:
        with open(path, encoding="utf-8") as fh:
            if fh.read().strip() == stamp:
                return False                     # already warned for this cold spell
    except Exception:
        pass
    os.makedirs(STATE, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(stamp)
    notes = os.path.join(ev.get("cwd") or os.getcwd(), "HANDOFF.md")
    # notes written at the end of the work, not before it went on
    current = os.path.isfile(longpath(notes)) and os.path.getmtime(longpath(notes)) >= then.timestamp() - 300
    away = t["minutes"] % idle if idle < 120 else t["hours"] % (idle / 60)
    reason = t["cold_head"] % away + (t["cold_current"] if current else t["cold_none"])
    print(json.dumps({"decision": "block", "reason": reason}))
    return True


def prompt(ev):
    if cold(ev):
        return
    conf = settings()
    if not conf["handoff_stop"]:
        return                                   # the nudges belong to the long-chat stop
    sid = ev.get("session_id")
    seen = read_marker(sid)
    if not seen:
        return                                   # gate never fired in this chat
    seen["prompts"] = seen.get("prompts", 0) + 1
    write_marker(sid, seen)
    if seen["prompts"] % NUDGE_EVERY:
        return
    print(json.dumps({"systemMessage": TEXT[conf["language"]]["nudge"]}))


if __name__ == "__main__":
    try:
        mode = sys.argv[1] if len(sys.argv) > 1 else ""
        {"stop": stop, "start": start, "prompt": prompt}[mode](json.load(sys.stdin))
    except Exception:
        pass
    sys.exit(0)
