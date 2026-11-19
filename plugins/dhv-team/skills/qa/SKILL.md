---
name: qa
description: Manual QA pass on the current work before it is shared or sent - proof by running checks, review against what was asked, then Hebrew / right-to-left, Excel and Word, and count checks. Use on /qa, "check your work", "review this carefully", "בדיקת איכות", "תבדוק את העבודה", "סקור לפני שליחה".
disable-model-invocation: true
---

# Scrutiny pass

Run in order; do not skip a step because it "obviously passes". Reply in the person's language.

## 1. Evidence first
Follow `verification-before-completion`: for each claim, name the check, run it fresh, read the whole
output, and state the result with it. No "should work".

## 2. Review against the request
Re-read the original ask (HANDOFF.md, the brief, the person's message) and make a line-by-line list:
met / not met / cannot be verified. Gaps come first.

## 3. Checks by type
Apply the ones that fit the deliverable; say which you skipped and why.

**Hebrew content**
- The rendered result was looked at, not just the source: right-to-left direction, no mirrored
  brackets or punctuation, mixed Hebrew / English lines in the right order.
- Word: right-to-left paragraphs and runs are set, tables and bullets sit on the right.
- Excel: sheet direction and cell alignment right-to-left where the content is Hebrew.

**Excel / CSV**
- Row counts in and out reconcile; each dropped or added row is explained.
- Headers, units and date formats follow the source's convention.
- Formulas recalculate with no `#REF!` / `#VALUE!`; no typed number where a formula belongs.
- At least one filled sheet opened and looked at, not only read by a script.

**Anything counted or matched** (matching lists, extracting tables from PDFs, merging files)
- Matched / unmatched / ambiguous counts reported; unmatched items listed, not summarised away.
- Coordinates or units: the system stated and consistent; 3 points spot-checked against the source.
- Extraction: at least 3 records compared field by field with the source document.
- Running it twice does not duplicate anything.

**Scripts and automation**
- Errors are shown to the person, not swallowed into a log.
- No passwords, keys or webhook links written into files that get shared.
- Tested the way the person will run it (their system, their shell), not only in a sandbox.

**Skills and slash commands**
- Invoke it the way it is typed, including with no argument; an empty placeholder is the usual break.
- Run every command line in the SKILL.md once as written.
- Name and trigger phrases do not clash with another skill.

**A finding or chart**
- Method, grouping and totals re-checked; does the data really support the conclusion?

## 4. Report (one block, terse, no praise)
1. Verdict: ready / not ready.
2. Evidence: the checks run and the key output.
3. Request checklist with gaps.
4. Type checks: passed / failed / skipped (with reason).
5. Open risks for the person to decide.
