---
name: goal-draft
description: Turn what the person wants done into a ready-to-paste /goal line that Claude can finish alone and the goal check can confirm from the chat. Use on /goal-draft, "help me word a goal", "write me a /goal", before setting a /goal for a long task, "נסח לי מטרה", "תכין לי goal", "איך מנסחים /goal".
argument-hint: what you want done, in your own words
---

`/goal` makes a second model read the conversation at every stop and block it until the goal sentence is
true. It sees only the goal text and the chat. A goal such as "when done, draft an email to her" can be
read as "sent", which only the person can approve, so it blocks again and again.

Input: the argument. Empty: ask "What should be true when this is done?" and stop.

1. **Test the wording four ways.** A good goal is:
   1. **Reachable alone.** No step needs the person (send, share, publish, delete, pay, approve) or
      someone else (a client answers, a review comes back). Turn each into a ready state plus who acts:
      "draft saved, not sent; sending is mine".
   2. **Visible in the chat.** The checker confirms only what shows in the transcript: a command output,
      a file written, a read-back. Name the proof: "report.docx opened and the totals re-added".
   3. **One finish line.** The end state, not the steps. Steps go in the prompt after the goal is set.
   4. **Specific nouns.** Which file, table, mail, person.
2. **Ask only what you cannot fill in:** at most two questions in one message, each with your guess in
   brackets so the person can answer "yes".
3. **Return only:**
   - the line in its own `text` block, starting `/goal ` and under about 40 words, ready to paste;
   - one line per change from the person's wording, naming the test it fixes;
   - if the wording already passes, say so in one line and return it unchanged.

Never run `/goal` or start the work yourself: the person pastes the line. Reply in the person's
language; the goal line stays in the language the person used.
