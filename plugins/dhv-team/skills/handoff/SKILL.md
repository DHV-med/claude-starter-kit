---
name: handoff
description: Save where this work got to so a fresh chat can carry on from it (HANDOFF.md, plus the open-items and decisions files; or a paste-ready summary in chat). Use on /handoff, "save notes", "start fresh", "this chat is getting long", "סכם", "שמור סיכום", "צ'אט חדש", or when a hook says the handoff line was crossed.
argument-hint: what the next chat should focus on (optional)
---

Save the state of this work so a chat that has none of this conversation can carry on.
Write the notes in the person's language; file names and code stay as they are.

## Where the notes go
First work out whether this chat has a **work folder**. It does not when the current folder is any of
these, or when the chat's opening rules said "This chat has no work folder":
- a temp or scratch folder (anything under `AppData\Local\Temp`, `%TEMP%`, a scratchpad);
- the person's home folder itself, or Desktop, Documents or Downloads themselves (a subfolder is fine);
- the app's own folder (`.claude`), a drive root, a system or program folder.

Then:
- **A work folder you can write to** (Claude Code, Cowork): `HANDOFF.md` in it - inside a git repo, in
  the repo's top folder. A fresh chat opened anywhere in that folder is handed the file automatically.
  Overwrite any existing HANDOFF.md.
- **No work folder, but you can write files.** Never write the notes here: a temp folder is cleared
  without warning and the next chat would not find them. Tell the person in one plain line, in their
  language: this chat is not tied to a work folder, so the notes cannot be saved where a new chat would
  pick them up. Then offer the two ways on, and do the one they pick:
  1. **Pick a folder for this work.** In the desktop app open the folder picker (`request_directory`
     with no path), write `HANDOFF.md` there, and say in one line that the next chat must be opened in
     that folder to carry on. Elsewhere, ask for the folder's path.
  2. **Take the notes along.** Show them in one block to paste as the first message of a new chat.
  If the person does not answer (a hook asked for this handoff), give the block.
- **You cannot write files** (a plain chat): if the chat is inside a Project with memory, save the notes
  there. Otherwise show them in one block and tell the person, in one line: open a new chat and paste
  this block as the first message.

## What goes in (under 40 lines)
1. **Current state** - what is true now. A short table: piece / where it lives / state.
2. **Decisions** - anything chosen that the files do not explain, one line each, with the why (and,
   when it was written up below, the month file and heading).
3. **Next step** - the single next action, concrete enough to start on.
4. **Open items** - only what blocks the next step; point at `OPEN.md` for the rest.

## Open items: `OPEN.md`, next to HANDOFF.md
The lasting list of what is unresolved, so it is not retyped at the end of every reply and does not
quietly rot. Only in a work folder; create it the first time there is an open item. Four sections,
always under these English headings, the rows in the person's language:
`## Blocked` (waiting on someone: say who) · `## Decide` (the person's own call; work continues) ·
`## Parked` (deliberately not now) · `## Closed` (dated one-liners).
Each section is a table `| # | item | trigger |`: `#` counts 1, 2, 3 within the section, `item` is a
**bold short title** plus one line of detail, `trigger` is what makes it actionable again. An item
with no trigger is done now or dropped.
- **Check before carrying.** Look at the actual file or state for each row. Already done: move it to
  Closed with today's date. Never take the previous list's word for it.
- Add what this chat surfaced, each with its trigger.

## Decisions: `DECISIONS.md` and `docs/decisions/YYYY-MM.md`
When this chat chose something the files do not explain (an approach, a number, a wording the client
approved), write it up in this month's file, `docs/decisions/YYYY-MM.md`, under its own `## ` heading:
what was tried, what was rejected, what was chosen and why. `DECISIONS.md`, next to HANDOFF.md, is
only the index: one line per entry (date, heading, month file). Add the lines that are missing. Only
in a work folder; nothing was decided in this chat: skip this step and create nothing.

## For all three files
Do not restate what the files, the git history or the README already say - point at the file and
section instead. No history of this chat. Inside a git repo: no client names or measurements (the notes are saved
with the code). In a client's own folder on the shared drive, name the client and the project plainly:
notes that hide them are no use to the next chat.
If $ARGUMENTS says what the next chat should focus on, shape the notes toward that.

## Chat title
Where you can rename this chat (`set_session_title`, session "self"; if the tool is listed but not
loaded yet, load it first), set its title to what the chat achieved: project + outcome, under 7 words,
in the person's language. Skip it if the title already says that.

## Closing line
End your reply with the line in the person's language, exactly, alone, as the last line.
Hebrew:
🛑 **הסיכום נשמר ב-HANDOFF.md - הקלידו /clear כדי לפתוח צ'אט חדש; הוא ימשיך מהסיכום לבד.**
English:
🛑 **Notes saved to HANDOFF.md - type /clear to start a fresh chat; it picks the notes up by itself.**
When the notes were given as a block to paste (no work folder, or a plain chat), end instead with:
"🛑 פתחו צ'אט חדש והדביקו את הסיכום" / "🛑 Open a new chat and paste the notes."
When the notes were saved to a folder the person just picked, use the HANDOFF.md line and add before
it, in one line, which folder to open the next chat in.
