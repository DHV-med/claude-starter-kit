---
name: ship-check
description: Check a DHV-med tool repo before a change counts as done - no client data or passwords in git, README with an owner, known-answer test re-run - then save and upload to GitHub. Use on /ship-check, or inside a DHV-med tool repo when the person says "is it ready", "upload this", "save to GitHub", "done with this change", or the DHV check on GitHub failed. Not for folders that are not DHV-med repos.
---

Run in the tool's repo folder. Explain each finding in plain words; the user is not a developer.

## 1. Up to date
`git pull` first. If it reports a conflict, stop and explain what clashed before touching anything.

## 2. Nothing that must not be saved
Look at what would be uploaded: `git status` and `git ls-files`.
- Client data (`.xlsx .xls .xlsm .csv .dwg .dxf .msg`) outside `samples/`: untrack it with
  `git rm --cached <file>` (the file stays on disk) and make sure `.gitignore` covers it.
- Files over 5 MB, `~$` lock files, `*.jsonl` chat logs: same treatment.
- Passwords, keys, tokens in code or config: move them to `.env` and read them from there. If one
  was already committed and uploaded, tell the user plainly that the password must be changed.
  Removing it from history needs Dan, so say so.

## 3. README
It must say what the tool does, how to run it, where the data lives, and carry an `Owner:` line
with a real name (not "Your Name"). Write any missing part from the code and ask the user only for
facts the code cannot give (the owner, where the data lives).

## 4. Known-answer test
If `samples/` has an input and an expected output, re-run the tool on the input and compare.
- Same: say so, in one line.
- Different: show the difference in plain words (which number, old and new value). Ask whether
  it is intended. Do not upload until they answer.
- No sample yet: say this is the one thing that protects their numbers, and offer to create one
  from a small real case they have already checked by hand (anonymised).

## 5. Save and upload
`git add -A`, commit with a short message saying what changed, `git push`. Then, if `gh` is
available: `gh run watch --exit-status` on the latest "DHV check" run, and report pass or fail.

## Report
Three lines at most: what was checked, what was fixed, whether the upload and the DHV check passed.
