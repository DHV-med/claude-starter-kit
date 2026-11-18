---
name: start
description: Set up the DHV kit for this person - a short welcome, up to five questions so Claude knows them, their reply language, and the kit's on/off switches. Use on /start, /start undo, /start settings, "set me up", "what does this kit do", "turn off the long-chat stop", "התחלה", "הגדרות", "לכבות".
argument-hint: (nothing) | undo | settings
---

Reply in Hebrew unless the person writes in English or picks English below. Plain words; no talk of
tokens, prices or hooks.

## Places this skill writes (only these, and only after the person says yes)
- **About-me block:** `~/.claude/CLAUDE.md`, between these two lines, which belong to the kit:
  `<!-- dhv-kit:start -->` and `<!-- dhv-kit:end -->`. Nothing outside them is ever changed.
- **Switches:** `~/.claude/dhv-kit.json`, for example
  `{"language": "he", "handoff_stop": true, "cold_hold": true, "seat": "team"}`.
  Defaults when the file is missing: Hebrew, both on, `team`.
Before changing an existing file, copy it next to itself with `.bak-dhv` added to the name. If that
backup is already there, leave it: it holds the file as it was before the kit ever touched it. Show
what will be saved before saving it.

If you cannot write files here (a plain chat), you write nothing: show the block and tell the person to
paste it into the app's personal preferences (in claude.ai: Settings > Profile, "What personal
preferences should Claude consider in responses?"). The switches only matter where the kit's automatic
parts run (the Code tab), so in a plain chat skip them. In a plain chat the team rules do not load by
themselves, so end the block with these four lines:

    - Reply in Hebrew unless I write in another language. Plain words; explain any technical term.
    - When I say send, publish or share a document or code, offer /check once before it goes out.
    - When I start something unrelated to this chat, suggest once that I open a new chat for it.
    - Client names, measurements and passwords never go into code or anything uploaded.

## Which seat (never a question about "gateways")
The long-chat stop comes earlier for a colleague on the company's pay-per-use set-up (a small monthly
budget) than for one on a Claude Team account. Work it out; ask only if you cannot tell:
1. Where you can run a command: if the `ANTHROPIC_BASE_URL` environment variable, or `env.ANTHROPIC_BASE_URL`
   in `~/.claude/settings.json`, holds an address that is not anthropic.com, the seat is `gateway`.
2. Otherwise ask one multiple-choice question, last: "How do you sign in to Claude?" - with my work
   email on a Claude Team account (`team`) / through the company set-up with a monthly budget
   (`gateway`) / not sure (`team`).
Save it as `seat` in the switches file. Never say "seat" or "gateway" to the person.

## /start undo
Remove the about-me block and its two marker lines from `~/.claude/CLAUDE.md` (back up first). Leave the
rest of the file exactly as it was. Then ask once whether to also reset the switches (delete
`~/.claude/dhv-kit.json`). Say what was removed, in one line.

## /start settings
Show the three settings in plain words, with their current values, and change the ones the person picks:
1. Reply language: Hebrew / English.
2. Long-chat stop (in the Code tab: when a chat grows long, Claude saves notes and suggests a fresh chat): on / off.
3. Cold-chat hold (in the Code tab: the first message to a long chat that sat idle is held back once,
   with a warning; sending again goes through): on / off.
Write `~/.claude/dhv-kit.json` with all three keys, keeping any other key already in it (such as
`seat`). Changes apply from the next message.

## /start (no argument)
1. **Welcome.** Say this, in the person's language, in your own short words:
   - The kit gives Claude DHV's team rules, answers in Hebrew, keeps long chats from eating the usage
     limit, and checks work before it is sent (`/check`).
   - It changes nothing of yours without asking, and everything it adds comes off in one step
     (`/start undo`, or remove the plugin).
   - The company's Claude admin can see how much you use and nothing else.
2. **Already set up?** If the marker block exists, show it and ask what to change; skip the questions
   that need no change.
3. **Up to five questions,** one at a time, multiple choice where possible (use the question tool if this
   app has one):
   1. Reply language: Hebrew / English.
   2. Your role, in a line (for example "environmental engineer, writes odour reports for clients").
   3. What you mainly use Claude for (several allowed): client reports and documents / emails / Excel
      and data / meeting summaries / scripts and tools / other.
   4. Answer style: short or detailed; explain technical terms or not.
   5. Anything Claude should always or never do (optional; "nothing" is fine).
4. **The block.** At most ~15 lines, in English (Claude reads it; it costs less), written as plain
   instructions: role, main uses, language, answer style, always/never. No client names, no personal
   details beyond what the person typed. Show it and ask: save?
5. **Save** on yes (see "Places this skill writes"). Append the block at the end of `~/.claude/CLAUDE.md`
   (create the file if missing); running `/start` again replaces only the block. Then the switches
   file: if it exists, change only `language` and `seat` and keep the person's switches as they are; if
   not, write it with the chosen language, both switches on, and the seat.
6. **Close** in three lines: what was saved and where, how to switch parts off (`/start settings`) or undo
   (`/start undo`), and `/guide` for how to use Claude well.

<!-- Maintainer: the admin line in step 1 is Dan's wording (2026-11-18). Say nothing about messages being seen
     or sent: it is not true and it worries people. tests/test_gate.py checks the line. -->
