---
name: new-tool
description: Put a tool on DHV-med GitHub - start a new tool, or move an existing folder of scripts into its own private repo built from the team starter repo. Use on /new-tool, "put this on GitHub", "share this tool with the team", "create a repo for this", "start a new tool".
---

The user is not a developer; do every step for them and explain in one line what each is for.

## 1. Tools present
`git --version` and `gh auth status`. If git or the GitHub CLI is missing, install it with
`winget install --id Git.Git -e` / `winget install --id GitHub.cli -e`. If gh is not logged in,
ask the user to run `gh auth login` themselves (it opens the browser; you never handle passwords).
Then `gh api user/memberships/orgs/DHV-med --jq .state` must say `active`. If it fails, stop: the
person needs a GitHub account in the DHV-med organization, and Dan Ofek adds people. Say so in one line.

## 2. Name and description
Ask for, or propose from the code:
- a repo name: lowercase words joined by hyphens, saying what it does (`odor-data-extraction`,
  not `script2`). Check it is free: `gh repo view DHV-med/<name>` should fail.
- a one-sentence description a colleague understands.
- the owner (default: the user).

## 3. Create from the starter repo
    gh repo create DHV-med/<name> --private --template DHV-med/tool-template --description "<sentence>"

The starter repo brings the ignore list, the automatic check, the plugin settings and a README
skeleton.

## 4. Existing folder
Clone the new repo to a temporary folder and copy its files into the user's folder without
overwriting their own files (if they already have a README or .gitignore, merge the starter
content into them). Then in their folder: `git init -b main` (skip if it is already a git repo),
`git remote add origin https://github.com/DHV-med/<name>.git`, `git pull origin main`.

New tool with no folder yet: `gh repo clone DHV-med/<name>` into a sensible place (ask where they
keep their work) and continue there.

## 5. Fill in and upload
Write the README from the code (what it does, how to run it), fill `Owner:`, leave `Status: draft`.
Ask where the client data lives. Then run `/ship-check`, which checks nothing sensitive is included
and uploads.

## 6. Tell the user
The repo link, and one line: *"Dan will see it in the team tool list tomorrow; it stays 'draft' until he approves it."*
