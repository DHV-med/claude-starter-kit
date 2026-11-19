# DHV team starter kit for Claude Code

Install it once if you use Claude Code: the **Code** tab in the Claude app, or Claude in a terminal. It
keeps chats short enough that your usage limit lasts, and it carries the team's safety rules. It updates
by itself. (Claude in the browser, Excel, Word or PowerPoint doesn't use it.)

**Step-by-step tutorial (Hebrew):** https://claude.ai/artifact/PHpAjVxzq87HML73NUp5ZA (open it signed in to
your DHV Claude account).

## What you get
- **Team rules** Claude reads at the start of every chat: plain words, client data and passwords never
  in git, and the three habits below. Inside a DHV-med tool repo it also gets the tool rules (owner,
  samples, `/ship-check`).
- **`/handoff`** saves where the work got to in a file called `HANDOFF.md`, and keeps the list of open
  items (`OPEN.md`) and the decisions and their reasons (`DECISIONS.md`). The next new chat in that
  folder starts from the notes by itself. A chat with no work folder is told so, and nothing is saved
  where it would get lost.
- **Automatic handoff.** When a chat gets long, Claude stops, writes `HANDOFF.md` and tells you to type
  `/clear`. A fresh chat then carries on from the notes.
- **Cold-chat warning.** Come back to a very long chat after a break and your first message is held back
  once, with the cheaper way on. Send it again to carry on anyway.
- **`/start`** is a guided tour that sets the kit up with you: it gets to know your work, connects your
  tools (Outlook, Teams, SharePoint), sets up a work folder, does a first real task with you, and carries
  on for as long as you like. Stop any time; `/start` later picks up where you left off. It also
  switches the automatic parts on or off. `/start undo` takes it back out.
- **Short answers by default**, with a bottom line when an answer runs long; a reminder to look for
  what already exists before building; and, in a folder that already uses git, a local save of every
  file Claude edits (nothing leaves your computer).
- **A row above the prompt** showing how long Claude still remembers the chat cheaply and how full the
  chat is, with a button for notes and a new chat, and a **Start** button until you have begun `/start`.
- **`/kickoff`**, **`/market-scan`**, **`/qa`**, **`/humanizer`**, **`/tired`**:
  start a piece of work without rebuilding what exists, check it, and tidy its wording.
- **`/guide`**: which tool for which job, and how to keep your usage limit for real work.
- **`/check`** before you send something: numbers traced to a source, client details, invented
  references, AI-sounding wording, Hebrew layout; for code, passwords and client data.
- **Clear chat titles** in the Claude app, so you can find a chat again.
- **`/bulletproof`** pokes holes in a plan before you build it; **`/context-coach`** shows where your
  usage goes (Code tab only).
- **`/ship-check`** and **`/new-tool`** for colleagues who build tools in the DHV-med GitHub organization.

## The three habits
1. **New task:** `/handoff`, then `/clear`. A question about what was just done isn't a new task.
2. **Same task:** keep going. The automatic handoff tells you when to stop.
3. **Before a break:** `/handoff`. Come back to a new chat.

## Install (once, about 5 minutes)
You need Claude Code working (the **Code** tab in the Claude app, or Claude Code in a terminal). No GitHub
account is needed: the kit is public.

1. In the **Code** tab, pick any folder and send Claude this message (copy it whole):

   > Install the DHV team kit. Find the newest `claude.exe` under `%LOCALAPPDATA%\Claude-Data\*\claude-code\`
   > and run it with each of these, one at a time: `plugin marketplace remove dhv-med` (an error here is
   > fine), `plugin marketplace add DHV-med/claude-starter-kit`, `plugin install dhv-team@dhv-med`,
   > `plugin install dhv-band@dhv-med`. Then check that `python --version` shows Python 3 (if not, install
   > it with `winget install -e --id Python.Python.3.13`), and in `~/.claude/settings.json` set
   > `"autoUpdate": true` on the `dhv-med` marketplace entry, keeping everything else as it is. Tell me
   > which dhv-team version is installed.

   If Windows asks for an administrator name and password while installing, stop and call IT.
   (Typing `/plugin` in the app opens its plugin screen instead; the message above is the reliable way.
   In Claude in a terminal the same four commands start with `claude`.)
2. Close the Claude app completely and open it again, start a new chat and press **Start** in the row
   above the prompt (or type `/start`). It walks you through the set-up in a few short stages; every
   stage can be skipped. Until you run it, Claude answers in Hebrew.
3. `/guide` shows how to use Claude well and every command the kit adds.

Opening a DHV-med tool repo also offers the kit by itself.

## For the maintainer
- Lines depend on the seat: a Team seat hands off first at 200k tokens, then every 100k more; a
  gateway seat (small monthly budget) at 100k, then every 50k, and its usage line is a quarter of the
  Team one. The seat is `seat` in the person's settings file (written by `/start`), or a non-Anthropic
  `ANTHROPIC_BASE_URL`. Environment variables, in thousands of tokens, override the token lines:
  `DHV_HANDOFF_FIRST_K`, `DHV_HANDOFF_EVERY_K`, `DHV_COLD_K` (cold-chat warning, follows the first
  handoff line).
- A fresh chat is handed HANDOFF.md only up to what Claude Code's 10,000-character cap on hook output
  leaves after the rules (about 3,000 characters since 3.0.0, when the rules grew; about 1,800 inside a
  tool repo); longer notes end with a line telling Claude to read the rest of the file. The notes are the
  nearest HANDOFF.md from the chat's folder up to the top of its git repo. A usage line (list-price weight, never shown) also hands off long chats that stay
  under 200k because Claude Code compacts them on its own.
- The cold-chat warning reads how long the chat's cache lives from the chat log: one hour on a Claude
  subscription, five minutes on an API key, a gateway or paid extra usage.
- Stays off for anyone whose own settings already run a handoff or cold-chat gate (Dan's do).
- Hooks run through `hooks/run.ps1` (Windows PowerShell, ~0.25 s per hook). With Python 3 it calls
  `handoff_gate.py`; without Python the rules and a fresh chat's notes still load, the two gates stay
  off, and no error shows. Not for Mac: there is no `powershell` there.
- Per-person settings in `~/.claude/dhv-kit.json` (`language` he/en, `handoff_stop`, `cold_hold`,
  `short_replies`, `auto_save`, `seat` team/gateway; defaults Hebrew, all on, team), written by `/start`,
  which also keeps its tour progress there under `tour`. Messages the person sees follow `language`.
- `rules/core.md` goes to every chat; `rules/reply-style.md` only while `short_replies` is on. Both count
  against the 10,000-character cap, so keep them tight.
- A chat with no folder picked (a temp folder, the home folder, Desktop / Documents / Downloads
  themselves, `.claude`, a drive root) is told so at its start, and the long-chat stop then asks for a
  block to paste, never a file there (`no_work_folder()` in `handoff_gate.py`, mirrored in `run.ps1`).
- Three more hooks, all needing Python: after the desktop app's wrap-up tool, a reminder of the
  short-reply test (`closing`); after an edit inside a git repo, a local commit of that one file, never
  the folder and never sent anywhere (`save`; stays off for anyone running their own `on-file-change`
  hook); and on a typed message that asks what already exists, a reminder to run `/market-scan`
  (never on background notices or long pasted text).
- `/start` writes its about-me block into `~/.claude/CLAUDE.md` between `<!-- dhv-kit:start -->` and
  `<!-- dhv-kit:end -->` only. Its welcome says only that the company's Claude admin sees how much
  you use and nothing else; never add wording about messages being seen or sent (not true, it worries people).
- `python tests/test_gate.py` checks the hooks (both languages, the switches, the launcher with and
  without Python) and the skill files, without starting Claude.
- Bump `version` in `plugins/dhv-team/.claude-plugin/plugin.json` on every change, so everyone's copy
  updates.
- Before anything goes to a colleague: `python tools/build_kit.py` (a dry run: tests, Claude's
  validator, the privacy line, the version, a scan for internal names, the file count). It refuses
  while any of them fails; `--build` then writes `dist/dhv-team-<version>.zip`.

Maintainer: Dan Ofek.

**Owner:** Dan Ofek
