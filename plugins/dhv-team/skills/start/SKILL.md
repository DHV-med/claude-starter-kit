---
name: start
description: Set up the DHV kit with this person as a guided tour - get to know their work, save it, connect their tools (Outlook, Teams, SharePoint), set up a work folder, do one real task together, and keep going for as long as they want; picks up where they stopped. Also the kit's on/off switches. Use on /start, /start undo, /start settings, "set me up", "what does this kit do", "what next", "continue the tour", "turn off the long-chat stop", "התחלה", "הגדרות", "לכבות", "מה עכשיו".
argument-hint: (nothing) | undo | settings
---

Reply in Hebrew unless the person writes in English or picks English below. Plain words; no talk of
tokens, prices or hooks. This is a conversation, not a form: one question at a time, react to what they
say, and never print a block of instructions or settings at them.

## Places this skill writes (only these)
- **About-me block:** `~/.claude/CLAUDE.md`, between these two lines, which belong to the kit:
  `<!-- dhv-kit:start -->` and `<!-- dhv-kit:end -->`. Nothing outside them is ever changed.
- **Switches and tour progress:** `~/.claude/dhv-kit.json`, for example
  `{"language": "he", "handoff_stop": true, "cold_hold": true, "short_replies": true, "auto_save": true,
  "seat": "team", "tour": {"done": ["about", "tools"], "connected": ["Outlook"], "folder": "...",
  "tried": "..."}}`.
  Defaults when the file is missing: Hebrew, all four switches on, `team`, no tour progress.
- **Starter files in a work folder the person picked** (stage 3), after a yes.
Before changing an existing file, copy it next to itself with `.bak-dhv` added to the name. If that
backup is already there, leave it: it holds the file as it was before the kit ever touched it.

**Save without asking, and never show the block.** The block is written for Claude, not for the
person: a wall of instructions in English reads as something gone wrong. Do not ask "save?", do not
print the block or the JSON, do not narrate the backup. Say it is saved and link the folder: the link
text is the full path of their own `.claude` folder, the target is that same path as a `file:///`
address. Show the block only when the person asks to see what was saved. If a save failed, say that
instead, plainly, with what went wrong; never say "saved" on a guess.

If you cannot write files here (a plain chat), you write nothing: show the block and tell the person to
paste it into the app's personal preferences (in claude.ai: Settings > Profile, "What personal
preferences should Claude consider in responses?"). The switches only matter where the kit's automatic
parts run (the Code tab), so in a plain chat skip them and stages 3 and 5. In a plain chat the team
rules do not load by themselves, so end the block with these four lines:

    - Reply in Hebrew unless I write in another language. Plain words; explain any technical term.
    - When I say send, publish or share a document or code, offer /check once before it goes out.
    - When I start something unrelated to this chat, suggest once that I open a new chat for it.
    - Client names, measurements and passwords never go into code or anything uploaded.

## Which seat (never a question about "gateways")
The long-chat stop comes earlier for a colleague on the company's pay-per-use set-up (a small monthly
budget) than for one on a Claude Team account. Work it out; ask only if you cannot tell:
1. Where you can run a command: if the `ANTHROPIC_BASE_URL` environment variable, or `env.ANTHROPIC_BASE_URL`
   in `~/.claude/settings.json`, holds an address that is not anthropic.com, the seat is `gateway`.
2. Otherwise ask one multiple-choice question, last in stage 1: "How do you sign in to Claude?" - with my
   work email on a Claude Team account (`team`) / through the company set-up with a monthly budget
   (`gateway`) / not sure (`team`).
Save it as `seat` in the switches file. Never say "seat" or "gateway" to the person.

## /start undo
Remove the about-me block and its two marker lines from `~/.claude/CLAUDE.md` (back up first). Leave the
rest of the file exactly as it was. Then ask once whether to also reset the switches and the tour
progress (delete `~/.claude/dhv-kit.json`). Files in their work folders stay. Say what was removed, in
one line.

## /start settings
Show the settings in plain words, with their current values, and change the ones the person picks:
1. Reply language: Hebrew / English.
2. Long-chat stop (in the Code tab: when a chat grows long, Claude saves notes and suggests a fresh chat): on / off.
3. Cold-chat hold (in the Code tab: the first message to a long chat that sat idle is held back once,
   with a warning; sending again goes through): on / off.
4. Short answers (`short_replies`: answers kept to what you need, with a bottom line when long): on / off.
5. Save points (`auto_save`: in a folder that already uses git, each file Claude edits is saved locally
   so a bad edit can be undone; nothing leaves the computer): on / off.
Write `~/.claude/dhv-kit.json` with all the keys, keeping any other key already in it (such as `seat`
and `tour`). Changes apply from the next message.

## /start (no argument): the tour
Read `~/.claude/dhv-kit.json` first.
- **No tour progress:** welcome, then stage 1.
- **Some progress:** one line on what is already done, in their words ("last time we got you connected
  to Outlook"), then offer the next stage, the "what next" menu, or settings. Never repeat a finished
  stage unless they ask.

**Welcome.** Say this, in the person's language, in your own short words:
- The kit gives Claude DHV's team rules, answers in Hebrew, keeps long chats from eating the usage
  limit, and checks work before it is sent (`/check`).
- It saves a short note about you so Claude knows who it is working with, touches nothing else of
  yours, and everything it adds comes off in one step (`/start undo`, or remove the plugin).
- The company's Claude admin can see how much you use and nothing else.
- This is a tour in a few short stages. Every stage can be skipped, and they can stop at any point and
  carry on another day.

After every stage: write the progress to `tour` in the switches file, say in one line what is now set
up, and offer the next stage and "stop here". "Skip" moves on without nagging.

### Stage 1 - your work (`about`)
Get to know the work itself, not a job title. One question at a time, multiple choice where it helps
(use the question tool if this app has one), and **follow up on what they answer**: someone who says
"odour reports" is asked who reads them and what takes longest. There is no fixed number of questions:
stop when you could describe their week to a stranger, usually six to ten, or sooner when they say
enough. Cover:
1. Reply language: Hebrew / English.
2. What they do, and what they hand over in a normal week (reports, tables, mails, drawings), and to whom.
3. Which programs the work lives in (Word, Excel, Outlook, Teams, SharePoint, AutoCAD, GIS, other).
4. What repeats every week and eats time. What they would hand to an assistant tomorrow.
5. What went wrong the last time they used Claude or another AI tool, if anything.
6. Answer style: short or fuller; explain technical terms or not. (Fuller: set `short_replies` to false.)
7. Anything Claude should always or never do (optional; "nothing" is fine).
Then build the block: at most ~15 lines, in English (Claude reads it; it costs less), written as plain
instructions: role, what they produce and for whom, programs, the repeating work, language, answer
style, always/never. No client names, no personal details beyond what the person typed. Save it
straight away (see "Save without asking"). Append it at the end of `~/.claude/CLAUDE.md` (create the
file if missing); a later `/start` replaces only the block. Then the switches file: if it exists,
change only `language`, `short_replies` and `seat` and keep the person's other switches; if not, write
it with the chosen language, the switches on, and the seat. Say "Saved" with the folder link, in one
line, and go on to stage 2.

### Stage 2 - your tools (`tools`)
Claude is far more useful when it can find a mail, a meeting or a file itself instead of the person
pasting it. From stage 1 you know which programs they use. For each, say in one line what connecting
it gives them, in their own work ("find the client's last mail about the Holit report"), then:
- Where this app lets you see or suggest connectors, check what is already connected and offer the
  rest one at a time. Microsoft 365 (Outlook, Teams, SharePoint) first: most of DHV's work is there.
- Otherwise give the steps: in the Claude app, Settings > Connectors, choose the tool, Connect, and
  sign in with the work account. They sign in themselves; never ask for or type a password.
- Only tools that appear in their connector list. One that is missing has not been switched on for the
  company: say so, do not look for a way around it, and tell them the kit's maintainer (Dan Ofek) is
  the one to ask.
- After each connection, prove it with one small real look-up they choose ("your next meeting", "the
  last mail from X") and show the result in a line.
- **Add-ons.** Where this app has a plugin or skill search, look for what fits their work (Hebrew Word
  documents, meeting summaries, Excel) and offer at most three, each with one line on what it does.
  Install only on a yes. If Anthropic's own guided set-up skill is available here, it may be used for
  this part.
Record what got connected or added in `tour.connected`.

### Stage 3 - a work folder (`folder`)
In one line: Claude works best inside the folder of one piece of work; its files and its notes live
there, and a new chat carries on from them. Ask which piece of work they are on now and where its
folder is. Open the folder picker where the app has one. Never a temp folder, the home folder, or
Desktop, Documents or Downloads themselves: a subfolder for this one piece of work.
Then ask once: lay Claude's three note files here? On a yes, create only the ones that are missing:
`HANDOFF.md`, `OPEN.md` (sections `## Blocked`, `## Decide`, `## Parked`, `## Closed`, each a table
`| # | item | trigger |`), `DECISIONS.md` (an index) and `docs/decisions/YYYY-MM.md`. No git set-up
unless they ask for it. Say in one line what each file is for. Record the folder in `tour.folder`.
Client data stays where it is; nothing is copied or uploaded.

### Stage 4 - one real task, together (`task`)
Pick, with them, one small real thing from their own answers that fits in about fifteen minutes: a
mail to draft, a table to tidy, a report section to tighten, a meeting to summarise. Do it properly
and let them see the habits while it happens, each named in half a line the moment it is used:
- finding the source through a connected tool instead of pasting;
- `/check` before anything goes out;
- `/handoff` at the end, and the three note files filling in.
It is their work: they decide what goes out; you never send. Record in `tour.tried` what was done.

### Stage 5 - what is on the screen (`screen`)
Two minutes, no lecture:
- The row above the prompt: the clock shows how long Claude still remembers this chat cheaply, and how
  full the chat is. Cold or nearly full means: notes, then a new chat. If the row is not there, offer
  to add it (the `dhv-band` plugin from the same `dhv-med` source as the kit); add it only on a yes,
  and say it shows after the app is restarted. `/band hide` puts it away.
- The four commands worth remembering: `/handoff`, `/check`, `/guide`, `/start`.
- The one habit: a new task gets a new chat.

### What next (after any stage, and whenever `/start` is run again with the tour done)
Offer two to four choices that fit this person, never a fixed list, plus "stop here". Draw on:
another tool to connect; another real task; a weekly chore from stage 1 turned into something
repeatable (`/kickoff`); where their usage goes (`/context-coach`); a plan they want pressure-tested
(`/bulletproof`); searching for an existing product before building (`/market-scan`); the guide
(`/guide`); changing a setting. Keep going for as long as they pick something.

### Closing summary (whenever they stop)
A super brief summary of everything that was set up, in their language, five lines at most and
nothing else:
1. Saved: a note about you and your preferences - with the folder link.
2. Connected: the tools that now work (or "nothing yet").
3. Work folder: its name and the folder as a link (or "not yet").
4. Tried: the task you did together (or "not yet").
5. Next time: `/start` picks up from here; `/start settings` changes things; `/start undo` removes them.
Only what really happened: a stage that was skipped or failed is said as such, never as done.

<!-- Maintainer: the admin line in the welcome is Dan's wording (2026-11-18). Say nothing about messages being
     seen or sent: it is not true and it worries people. tests/test_gate.py checks the line. -->
