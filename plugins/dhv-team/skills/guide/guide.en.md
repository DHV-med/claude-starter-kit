# A short guide: working well with Claude without running out of usage

## Which tool for which job
| The work | Where |
|---|---|
| A question, an idea, a draft email, a pasted document to read | Chat |
| Work on files on your computer (a folder, Excel, Word, slides), standing documents you keep coming back to (procedures, templates), scripts, tools, code | The Code tab |

## Three habits (in the Code tab)
1. **New task → notes, then a new chat.** Type `/handoff`, then open a new chat.
2. **Same task → keep going.** The kit tells you when the chat has grown too long.
3. **Before a break of an hour or more → notes.** Come back to a new chat that starts from them.

## More ways to save usage
- **Model:** Sonnet for routine work, Opus when the work needs judgement. **Pick it when you open the chat, not halfway through.**
- **Fable:** only for especially hard challenges.
- **Effort:** low or medium for routine work.

## What the kit does by itself (in the Code tab)
- Gives Claude the team rules in every chat: replies in your language, keeps client data and passwords out of shared code, explains terms.
- Gives chats clear titles in the app, so you can find them again.
- Offers `/check` before you send something out.
- When Python is on the computer: stops a chat that has grown long and saves notes, and holds back the first message to a long chat that sat for a long time (sending again goes through).
- Tells you when a chat has no work folder, so your notes are never saved somewhere they get lost.
- Keeps answers short and to the point, with a bottom line when they run long (switch it off in `/start`).
- Reminds Claude to look for what already exists before building something new.
- In a folder that already uses git: saves each file Claude edits, on your computer only, so a bad edit can be undone.
- Shows a row above the prompt: how long Claude still remembers the chat cheaply, and how full the chat is.
- Saves a short note about you when you run `/start`, and touches nothing else of yours.
- The company's Claude admin can see how much you use and nothing else.

## What stays with you
Picking the model, opening a new chat in time, **and checking yourself whatever goes to a client.**

## The commands
The commands work in the Code tab.

| Command | What it does |
|---|---|
| `/start` | A guided tour: your work, your tools (Outlook, Teams, SharePoint), a work folder, a first task; also switches parts of the kit on or off |
| `/guide` | This guide |
| `/handoff` | Notes for a new chat, and the lists of open items and decisions |
| `/check` | A check before sending: numbers, client details, sources, wording |
| `/bulletproof` | A deep check of a plan before building it: alternatives, weak points, what was forgotten |
| `/context-coach` | Use your tokens more efficiently |
| `/kickoff` | Start a new piece of work: what already exists, the smallest version, a rough plan |
| `/market-scan` | Does a solution already exist? A wide look before building anything |
| `/qa` | A careful check of the work in front of you: against the request, Hebrew layout, Excel and Word, counts |
| `/humanizer` | Rewrite text that sounds like AI so it sounds human |
| `/tired` | Very short answers for the rest of the chat |

## Switching off, removing, feedback
- Switch part of the kit off: `/start` and choose what to turn off. Undo the introduction: `/start undo`.
- Remove it completely: run `/start undo` first, then in the Code tab send Claude this message:
  "Remove the DHV team kit: run the newest `claude.exe` under `%LOCALAPPDATA%\Claude-Data\*\claude-code\`
  with `plugin uninstall dhv-team@dhv-med`, then with `plugin uninstall dhv-band@dhv-med`." Then close the
  app and open it again.
- Feedback, a problem or an idea: write to Dan Ofek.
