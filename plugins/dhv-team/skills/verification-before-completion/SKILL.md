---
name: verification-before-completion
description: Before saying that work is done, fixed or passing, run the check that proves it and show the result; no claim without evidence. Use before any "done", "fixed", "ready", before sending or sharing, and on "verify", "prove it", "תוודא לפני שאתה אומר גמרנו", "בדוק שזה עובד", "הוכח".
---

**No "done", "fixed" or "passing" without a check run in this message.** If you have not run it now,
you cannot say it works.

## Before any claim
1. **Name the check** that would prove it: a command, opening the file, re-adding the totals, comparing
   row counts, reading the output again.
2. **Run it fresh and in full.** An earlier run, a partial check or "it should work" does not count.
3. **Read all of the output:** errors, warnings, counts, exit status.
4. **Say what you saw.** Matches the claim: state the claim with the evidence ("34 of 34 rows match the
   source"). Does not match: state the real status, with the evidence.

## What counts as proof
| Claim | Needs | Not enough |
|---|---|---|
| The script / test passes | Its output, zero failures | A previous run, "should pass" |
| The bug is fixed | The original symptom, retried, gone | The code was changed |
| The file is correct | Opened and looked at, figures re-added | The tool said "saved" |
| Everything asked for was done | The request re-read as a checklist, each line ticked | "The main part works" |
| A helper or agent finished | You looked at what it actually changed | Its own "success" report |

## Stop and run the check when you notice
- "should", "probably", "seems to" in your own draft;
- "Done!" or "Perfect!" before a check;
- wanting to finish because the work is long;
- sending or sharing something you have not re-opened.

Anything that implies success counts as a claim, in any wording. A step that cannot be checked is
reported as "not checked", never as done. Reply in the person's language.
