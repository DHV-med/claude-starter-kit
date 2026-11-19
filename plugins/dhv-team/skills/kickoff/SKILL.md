---
name: kickoff
description: Start a new project or job without rebuilding what already exists - intake, starter files in the work folder, a "does this already exist?" sweep, the smallest version that delivers, and a rough phased plan whose guesses are marked as guesses. Use on /kickoff, "new project", "kick off", "we got a new job", "פרויקט חדש", "מתחילים עבודה חדשה", "בוא נתחיל פרויקט".
argument-hint: the work, in a sentence (default - the request under discussion)
---

# Day one of a project

The costly mistakes happen on day one: building a part that already exists (in the person's own files,
in tools the company owns, or on the market), and planning as if every guess were known. This skill
catches that and writes what it finds where every later chat will see it.

**Kickoff builds nothing.** Starter files, searches and a plan only; real work starts after the report.
Reply in the person's language; file names stay English.

## 1. Intake
Read the source first (the email, meeting summary or pasted text) and fill in:

    Owner:       who asked and will judge it (name, role)
    Deliverable: what the owner holds at the end: format, language, who reads it
    Done means:  how the owner will judge it ("numbers match last year's report")
    Deadline:    date, or "none stated"
    Inputs:      data and documents it needs, and where they are now
    Goes to:     internal, or client-facing (it leaves the company)
    Checked by:  who can tell the output is right (a colleague who knows the data, or nobody yet)

Ask only the gaps, **one question per message**, the likely answer first, at most 4 questions. Never
ask what a search of the files or mailbox can answer. Show the filled brief in about 6 lines and go on.

## 2. The work folder
Ask which folder this work lives in, if the person has not said. Never use a temp or scratch folder, the
home folder itself, or Desktop, Documents or Downloads themselves (a new subfolder of them is fine;
offer to create one). Create the folder if needed, then lay these starter files in it, skipping any
that already exist (never overwrite):
- `HANDOFF.md`: the brief, current state, and the next step.
- `OPEN.md`: four sections in this order, each a table with the header `| # | item | trigger |`:
  `## Blocked` (waiting on someone: say who), `## Decide` (the person's own call; work continues),
  `## Parked` (not now), `## Closed` (dated one-liners). Every item has a trigger: what makes it
  actionable. No trigger means do it now or drop it.
- `DECISIONS.md`: an index, one line per entry: date, heading, month file.
- `docs/decisions/YYYY-MM.md` (this month): the first entry, written in step 7.
No `git init` unless the person asks.

## 3. Does it already exist?
Split the deliverable into 3-6 parts (read the inputs, clean them, calculate, write the report...).
Whole projects rarely exist off the shelf; their parts often do. For each part check, in this order:
1. **The person's own work.** Other folders, scripts and reports, above all the same owner's earlier
   work: the commonest miss is the same calculation done for a previous client.
2. **Already owned.** The company's approved-tools list if there is one, and built-in features of what
   is paid for: Excel (Power Query, pivot tables), Microsoft 365, Claude's own tools.
3. **The market,** only for product-shaped parts ("extract tables from PDFs", not "apply our emission
   factors"): run `/market-scan` for those.
If you can start a separate helper, give it the brief and the parts, not the chat (which already leans
toward building), about 25 searches, and "an empty ring is a valid answer". Result, under 30 lines:
- Per part: what covers it, how much (all / most / some), the gap left, where it is. Skip "nothing" rows.
- **Lessons from past work:** mistakes already written down in other projects' notes that apply here.

## 4. Smallest version that delivers
Per part pick one and say why in a line: **reuse**, **configure** something owned, **buy**, or
**build** (only the gap left). A method found in past work is a candidate, not an order. Then name the
floor: the dumbest version the owner would still accept (one Excel sheet before a pipeline; a manual
pass before a script for something that happens once).

## 5. Bulletproof
Skip if the whole job is under about a day. Otherwise run `/bulletproof` on the route from step 4,
telling it what step 3 already searched.

## 6. Rough plan
Put it in `HANDOFF.md`, or in `docs/PLAN.md` for a larger job. It is a forecast and says so:

    # Plan - <name> (forecast, <date>; re-plan at the first milestone)
    | # | phase | what the owner sees at the end | known or guess | rough size |
    ## Assumptions
    | assumption | how we find out | if wrong, then |

Rules: phase 1 ends in something the owner can see within about a week; every "guess" row names the
assumption it rests on; sizes are ranges in days, never hours; every unconfirmed number or date is
marked "guess". A small job gets three lines instead: first step, the guess most likely to be wrong,
what done looks like.

## 7. Fill the files
- `HANDOFF.md`: state and next step. If step 3 found anything, add a section
  `## Already exists - don't rebuild` (part, what covers it, where, all / most / some) so later chats
  check it before building.
- `OPEN.md`: questions only the owner can answer under Blocked; the person's own calls under Decide.
- `docs/decisions/YYYY-MM.md`: one entry: the brief, what step 3 searched and found, the route per part
  and why, the `/bulletproof` verdict; one index line in `DECISIONS.md`.

## 8. Report
- **Where we are:** the folder, and the one-line sweep result ("3 of 5 parts already exist: ...").
- **Needs you:** the first Blocked or Decide item, or "nothing".
- **Next:** phase 1's first step.

## Never
- Build or draft the deliverable during kickoff.
- Present a guess as known.
- Skip steps 3.1-3.2 because the project "feels new"; they take minutes and a miss costs days.
- Ask what a search can answer, or more than 4 questions.
