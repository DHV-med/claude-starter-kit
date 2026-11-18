---
name: context-coach
description: Make Claude Code usage last longer. Measures this PC's own chats (numbers only), then offers up to three fixes, largest saving first, and makes them on a yes. Run again later to see what moved. Use on /context-coach, "why do I run out so fast", "reduce my usage", "context coach", "למה נגמר לי", "לחסוך בשימוש".
effort: low
---

You are helping someone who does not know what a token, a cache or a context window is, and does not
need to. Reply in the language they write in. Say outcomes, never mechanisms; one sentence of why per
item is the ceiling. Those three words do not appear unless they use them first.

## 1. Measure

    python "<this skill's folder>/usage_audit.py" card

`<this skill's folder>` is the directory this SKILL.md lives in. It costs nothing to run and reads only
this PC's Claude Code chats. Python missing: say "install Python from python.org or the
Microsoft Store, then run this again". It prints a short card; do not paste it and do not open the chat
logs yourself.

If it finds no chat logs, the person works in chat, not in Claude Code, and nothing can be measured.
Say so in one line and give the three habits instead: a new task gets a new chat; the same task keeps
going; before a long break, ask for notes and start fresh.

## 2. Reply: a plan, not a report

Fits a phone screen. One line: how much of their usage the fixes below would free ("about a sixth"),
never dollars or token counts. Then **up to three fixes**, in the card's order, each one outcome and a
yes/no. Skip anything the card does not list.

| card line | offer |
|---|---|
| `heavy_start` | "Every chat starts heavy before you type." Ask them to run `/context`, which shows what fills it, then offer to trim the biggest piece: a rules file over ~2k tokens cut down to rules and pointers, or a skill or connector they never use switched off. |
| `short_cache` | "A short break makes Claude re-read the whole chat. One setting stretches that to an hour." Step 3. |
| `cold_return` | A habit, nothing to install: "Before a break of an hour or more, ask for notes (`/handoff`) and come back to a new chat." |
| `task_switch` | A habit: "A new task gets a new chat; the old one rides along otherwise." |
| `dumps` | "Long command output stayed in the chat." Offer one line in their rules file: output over ~40 lines goes to a file, with the counts and the path printed. If the team starter kit is installed it already has this rule: say so and skip. |
| `light_on_top_model` | A habit: "Quick questions don't need the strongest model; pick the lighter one for them." |

Then, once per person: `/usage` shows what used your allowance; `/btw` asks a quick question without
growing the chat. Close with "Nothing else needs you" or the one decision you need.

## 3. Change on yes

- **Rules file trim:** show the cut as before/after, wait for yes, keep a `.bak` next to the file.
- **One-hour setting:** copy `~/.claude/settings.json` to `settings.json.bak`, then add only
  `"promptCacheTtl": "1h"` with a JSON merge. Never touch another key or overwrite a value already set.
  On a gateway seat it may not take effect; the next run of the card shows whether it did.
- **Rules line:** add the one line, nothing else.

Say what will be different from their next chat on.

## 4. Running it again

Same command. The card's SINCE LAST RUN block is the whole story: say what moved in at most five lines,
offer a fix only for what is still listed, and stop. Nothing changed = one line.

## Never

- Paste chat content, file paths from the logs, or chat ids into the reply.
- Quote dollars or token counts: shares and counts only ("in 8 of your chats").
- Install hooks or rule blocks beyond the single line above.
- Send anything anywhere. The numbers stay on this PC; a report for someone else exists only if the
  person runs `usage_audit.py collect` and sends the file themselves.
