---
name: handoff
description: Save where this work got to so a fresh chat can carry on from it (HANDOFF.md, or a paste-ready summary in chat). Use on /handoff, "save notes", "start fresh", "this chat is getting long", "סכם", "שמור סיכום", "צ'אט חדש", or when a hook says the handoff line was crossed.
argument-hint: what the next chat should focus on (optional)
---

Save the state of this work so a chat that has none of this conversation can carry on.
Write the notes in the person's language; file names and code stay as they are.

## Where the notes go
- **A project folder you can write to** (Claude Code, Cowork): `HANDOFF.md` in the project root. A fresh
  chat in this folder is handed the file automatically. Overwrite any existing HANDOFF.md.
- **A chat with no folder** (you cannot write files): if the chat is inside a Project with memory, save the
  notes there. Otherwise show them in one block and tell the person, in one line: open a new chat and
  paste this block as the first message.

## What goes in (under 40 lines)
1. **Current state** - what is true now. A short table: piece / where it lives / state.
2. **Decisions** - anything chosen that the files do not explain, one line each, with the why.
3. **Next step** - the single next action, concrete enough to start on.
4. **Open items** - anything unresolved, each with what would make it actionable.

Do not restate what the files, the git history or the README already say - point at the file and
section instead. No history of this chat. Inside a git repo: no client names or measurements (the notes are saved
with the code). In a client's own folder on the shared drive, name the client and the project plainly:
notes that hide them are no use to the next chat.
If $ARGUMENTS says what the next chat should focus on, shape the notes toward that.

## Chat title
Where you can rename this chat (`set_session_title`, session "self"), set its title to what the chat
achieved: project + outcome, under 7 words, in the person's language. Skip it if the title already says that.

## Closing line
End your reply with the line in the person's language, exactly, alone, as the last line.
Hebrew:
🛑 **הסיכום נשמר ב-HANDOFF.md - הקלידו /clear כדי לפתוח צ'אט חדש; הוא ימשיך מהסיכום לבד.**
English:
🛑 **Notes saved to HANDOFF.md - type /clear to start a fresh chat; it picks the notes up by itself.**
In a chat with no folder, end instead with: "🛑 פתחו צ'אט חדש והדביקו את הסיכום" / "🛑 Open a new chat
and paste the notes."
