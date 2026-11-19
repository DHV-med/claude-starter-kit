# A short guide: working well with Claude without running out of usage

## Which tool for which job
| The work | Where |
|---|---|
| A question, an idea, a draft email, a pasted document to read | Chat |
| Work on files on your computer (a folder, Excel, Word, slides), scripts, tools, code | The Code tab |
| Standing documents you keep asking about (procedures, templates) | A Project holding only those documents |

## Three habits
1. **New task → notes, then a new chat.** In the Code tab: type `/handoff`, then open a new chat. In Chat:
   ask "summarise what we did for a new chat" and paste the summary into a new chat. A question about what
   was just done is not a new task.
2. **Same task → keep going.** In the Code tab the kit tells you when the chat has grown too long. In Chat:
   when it holds files, runs very long, or your usage in Settings → Usage climbs fast, move to a new chat
   with a summary.
3. **Before a break of an hour or more → notes.** Come back to a new chat that starts from them.

## More ways to save usage
- **Model:** Sonnet for routine work, Opus when the work needs judgement. Pick it when you open the chat,
  not halfway through. Fable uses far more: only with a reason.
- **Effort, in the Code tab:** low or medium for routine work.
- **Heavy tools only when needed:** Research, web search, file creation, connectors (links to other
  services).
- **Attach little:** only the file or pages you need. Text beats a screenshot unless the look matters.
- **Fix, don't pile on:** an answer went the wrong way? Edit your earlier message and send it again (in the Code tab: `/rewind`).

## What the kit does by itself (in the Code tab)
- Gives Claude the team rules in every chat: replies in your language, keeps client data and passwords out of shared code,
  explains terms.
- Gives chats clear titles in the app, so you can find them again.
- Offers `/check` before you send something out.
- When Python is on the computer: stops a chat that has grown long and saves notes, and
  holds back the first message to a long chat that sat for a long time (sending again goes through).
- Tells you when a chat has no work folder, so your notes are never saved somewhere they get lost.
- Keeps answers short and to the point, with a bottom line when they run long (switch it off in `/start`).
- Reminds Claude to look for what already exists before building something new.
- In a folder that already uses git: saves each file Claude edits, on your computer only, so a bad edit can be undone.
- Shows a row above the prompt: how long Claude still remembers the chat cheaply, and how full the chat is.
- Saves a short note about you when you run `/start`, and touches nothing else of yours.
- The company's Claude admin can see how much you use and nothing else.

## What stays with you
Picking the model, opening a new chat in time, and checking yourself whatever goes to a client.

## The commands
The commands work in the Code tab.

| Command | What it does |
|---|---|
| `/start` | A guided tour: your work, your tools (Outlook, Teams, SharePoint), a work folder, a first task; also switches parts of the kit on or off |
| `/guide` | This guide |
| `/handoff` | Notes for a new chat, and the lists of open items and decisions |
| `/check` | A check before sending: numbers, client details, sources, wording |
| `/bulletproof` | Find the holes in a plan before building it |
| `/context-coach` | Where your usage goes, and up to three fixes |
| `/kickoff` | Start a new piece of work: what already exists, the smallest version, a rough plan |
| `/market-scan` | Who already sells this? A wide look before building anything |
| `/qa` | A careful check of the work in front of you: against the request, Hebrew layout, Excel and Word, counts |
| `/humanizer` | Rewrite text that sounds like AI so it reads like you |
| `/tired` | Very short answers for the rest of the chat |
| `/goal-draft` | Word a goal Claude can finish on its own |

## Switching off, removing, feedback
- Switch part of the kit off: `/start` and choose what to turn off. Undo the introduction: `/start undo`.
- Remove it completely: in the Code tab type `/plugin`, and remove dhv-team and dhv-band.
- Feedback, a problem or an idea: write to Dan Ofek.
