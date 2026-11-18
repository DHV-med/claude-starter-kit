---
name: check
description: Check a document or code before it is sent, published or shared - numbers traced to a source, client and confidential details, invented references, AI-sounding wording, right-to-left layout; for code, secrets and client data. Use on /check, "check before I send", "is this ready to send", "בדוק לפני שליחה", "תבדוק את המסמך", "אפשר לשלוח?".
argument-hint: the file or text to check (default: what this chat just produced)
---

A last look before something leaves the person's hands. Read-only: report, then fix only what the
person says yes to. Reply in the person's language.

## What to check
The argument if given, else the document or code this chat produced or edited last. Unsure which →
ask in one line and stop.

## A document (report, letter, mail, presentation, table)
Check each; report only real findings.
1. **Numbers.** Every figure traced to its source (a file, a table, a calculation shown in this chat).
   A number you cannot trace is a finding: say where it appears and that its source is unknown. Re-add
   totals and percentages yourself.
2. **Who it goes to.** Another client's name, project, site or figures left over from a template;
   confidential details (prices, internal notes, personal phone numbers, comments, tracked changes,
   hidden sheets or slides) that the recipient should not see.
3. **References.** Standards, regulations, laws, articles and links: real, and do they say what the
   text claims? One you cannot confirm is marked "not verified", never assumed.
4. **Reads like AI.** Empty openers and closers, "not only X but Y", lists of exactly three, inflated
   words, one-line summaries at the end of every paragraph, dashes everywhere; in Hebrew too, including
   word-for-word translations from English and stiff, over-formal phrasing. Quote the line, offer a
   plainer one.
5. **Hebrew layout** (Word, PowerPoint, PDF in Hebrew). Text runs right-to-left, tables and bullets on
   the right side, numbers, dates and English words inside Hebrew lines in the right order, page numbers
   and headers correct.

## Code or a script
1. **Secrets:** passwords, API keys, tokens or connection strings in the code or in any file about to be
   uploaded. One that was ever committed must be changed; deleting it is not enough.
2. **Client data:** Excel, CSV, exports or anything with client names or measurements headed into git.
3. Then run the built-in `/security-review` if it exists here.
4. Inside a DHV-med tool repo (the tool-repo rules are loaded): run `/ship-check` instead of steps 1-3; it
   covers them and uploads.

## Report
- **Verdict:** ready to send / fix first.
- **Findings,** most serious first, each: where (page, paragraph, sheet), what is wrong, the fix.
- **Not checked:** whatever you could not look at, by name: tracked changes, comments or hidden sheets
  in a file you only saw as text, a link that did not open, a source file you were not given, layout
  you could not see rendered. "Ready" covers only what you checked; with anything on this list the
  verdict reads "ready, except not checked: ...".
- Nothing found → one line: "Checked numbers, recipient details, references, wording and layout: ready."
  (name only the parts you really checked).
Then offer to fix what you found; change nothing until the person says yes.
