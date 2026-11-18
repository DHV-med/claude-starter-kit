# A short guide: working well with Claude without running out of usage

## Which tool for which job
| The work | Where |
|---|---|
| A question, an idea, a draft email, a pasted document to read | Chat |
| Work on files on your computer: a folder, Excel, Word, slides | Cowork |
| Scripts, tools, code | The Code tab |
| Standing documents you keep asking about (procedures, templates) | A Project holding only those documents |

## Three habits
1. **New task → notes, then a new chat.** Type `/handoff`, then open a new chat. A question about what
   was just done is not a new task.
2. **Same task → keep going.** In the Code tab the kit tells you when the chat has grown too long. In chat:
   when it holds files or runs many screens, or your usage bar drops fast, type `/handoff` and carry on in
   a new chat.
3. **Before a break of an hour or more → notes.** Come back to a new chat that starts from them.

## More ways to save usage
- **Model:** Sonnet for routine work, Opus when the work needs judgement. Pick it when you open the chat,
  not halfway through. Fable uses far more: only with a reason.
- **Effort:** low or medium for routine work.
- **Heavy tools only when needed:** Research, web search, file creation, connectors (links to other
  services).
- **Attach little:** only the file or pages you need. Text beats a screenshot unless the look matters.
- **Fix, don't pile on:** an answer went the wrong way? Edit your earlier message and send it again.

## What the kit does by itself
- Gives Claude the team rules in every chat: replies in your language, keeps client data and passwords out of shared code,
  explains terms.
- Gives chats clear titles in the app, so you can find them again.
- Offers `/check` before you send something out.
- In the Code tab, when Python is on the computer: stops a chat that has grown long and saves notes, and
  holds back the first message to a long chat that sat for a long time (sending again goes through).
- Changes nothing of yours without asking.
- The company's Claude admin can see how much you use and nothing else.

## What stays with you
Picking the model, opening a new chat in time, and checking yourself whatever goes to a client.

## The commands
| Command | What it does |
|---|---|
| `/start` | A short introduction, your language, and switching parts of the kit on or off |
| `/guide` | This guide |
| `/handoff` | Notes for a new chat |
| `/check` | A check before sending: numbers, client details, sources, wording |
| `/bulletproof` | Poke holes in a plan before building it |
| `/context-coach` | Where your usage goes, and three fixes (Code tab only) |

## Switching off, removing, feedback
- Switch part of the kit off: `/start` and choose what to turn off. Undo the introduction: `/start undo`.
- Remove it completely: in the app's settings, in the plugins list, remove dhv-team.
- Feedback, a problem or an idea: write to Dan Ofek.
