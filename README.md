# DHV team starter kit for Claude Code

Install it once if you use Claude Code: the **Code** tab in the Claude app, or Claude in a terminal. It
keeps chats short enough that your usage limit lasts, and it carries the team's safety rules. It updates
by itself. (Claude in the browser, Excel, Word or PowerPoint doesn't use it.)

## What you get
- **Team rules** Claude reads at the start of every chat: plain words, client data and passwords never
  in git, and the three habits below. Inside a DHV-med tool repo it also gets the tool rules (owner,
  samples, `/ship-check`).
- **`/handoff`** saves where the work got to in a file called `HANDOFF.md`. The next new chat in that
  folder starts from it by itself.
- **Automatic handoff.** When a chat gets long, Claude stops, writes `HANDOFF.md` and tells you to type
  `/clear`. A fresh chat then carries on from the notes.
- **Cold-chat warning.** Come back to a very long chat after a break and your first message is held back
  once, with the cheaper way on. Send it again to carry on anyway.
- **`/start`** sets the kit up for you: a few questions so Claude knows you, your reply language
  (Hebrew by default), and switching the automatic parts on or off. `/start undo` takes it back out.
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

1. In the **Code** tab, pick any folder and type these two lines, one at a time:

       /plugin marketplace add DHV-med/claude-starter-kit
       /plugin install dhv-team@dhv-med

2. Then send Claude this message:

   > Finish setting up the DHV team kit: check that `python --version` shows Python 3 (if not, install it
   > with `winget install -e --id Python.Python.3.13`), and in `~/.claude/settings.json` set
   > `"autoUpdate": true` on the `dhv-med` marketplace entry, keeping everything else as it is.

   If Windows asks for an administrator name and password while installing, stop and call IT.
3. Close the Claude app completely and open it again, start a new chat and type `/start`. It asks up to
   five short questions (reply language, your role, what you use Claude for) and sets the kit up for you.
   Until you run it, Claude answers in Hebrew.
4. `/guide` shows how to use Claude well and every command the kit adds.

Opening a DHV-med tool repo also offers the kit by itself.

## For the maintainer
- Lines depend on the seat: a Team seat hands off first at 200k tokens, then every 100k more; a
  gateway seat (small monthly budget) at 100k, then every 50k, and its usage line is a quarter of the
  Team one. The seat is `seat` in the person's settings file (written by `/start`), or a non-Anthropic
  `ANTHROPIC_BASE_URL`. Environment variables, in thousands of tokens, override the token lines:
  `DHV_HANDOFF_FIRST_K`, `DHV_HANDOFF_EVERY_K`, `DHV_COLD_K` (cold-chat warning, follows the first
  handoff line).
- A fresh chat is handed HANDOFF.md only up to what Claude Code's 10,000-character cap on hook output
  leaves after the rules (about 5,000 characters); longer notes end with a line telling Claude to read
  the rest of the file. A usage line (list-price weight, never shown) also hands off long chats that stay
  under 200k because Claude Code compacts them on its own.
- The cold-chat warning reads how long the chat's cache lives from the chat log: one hour on a Claude
  subscription, five minutes on an API key, a gateway or paid extra usage.
- Stays off for anyone whose own settings already run a handoff or cold-chat gate (Dan's do).
- Hooks run through `hooks/run.ps1` (Windows PowerShell, ~0.25 s per hook). With Python 3 it calls
  `handoff_gate.py`; without Python the rules and a fresh chat's notes still load, the two gates stay
  off, and no error shows. Not for Mac: there is no `powershell` there.
- Per-person settings in `~/.claude/dhv-kit.json` (`language` he/en, `handoff_stop`, `cold_hold`,
  `seat` team/gateway; defaults Hebrew, on, on, team), written by `/start`. Messages the person sees follow `language`.
- `/start` writes its about-me block into `~/.claude/CLAUDE.md` between `<!-- dhv-kit:start -->` and
  `<!-- dhv-kit:end -->` only. Its welcome says only that the company's Claude admin sees how much
  you use and nothing else; never add wording about messages being seen or sent (not true, it worries people).
- (Maintainer's copy only, not in this public repo) `python tests/test_gate.py` checks the hooks (both languages, the switches, the launcher with and
  without Python) and the skill files, without starting Claude.
- Bump `version` in `plugins/dhv-team/.claude-plugin/plugin.json` on every change, so everyone's copy
  updates.
- Before anything goes to a colleague: `python tools/build_kit.py` (a dry run: tests, Claude's
  validator, the privacy line, the version, a scan for internal names, the file count). It refuses
  while any of them fails; `--build` then writes `dist/dhv-team-<version>.zip`.

Maintainer: Dan Ofek.
