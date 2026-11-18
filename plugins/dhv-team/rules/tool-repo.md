## This folder is a DHV-med tool repo
- Every README has an `Owner:` line (one named person) and a `Status:` line. Status stays `draft` until
  Dan Ofek approves the tool for client work; only Dan changes it to `approved`.
- Someone else's tool: read freely, but before changing it tell the person who owns it and suggest they
  check with the owner first.
- At the start of a session, get the latest version from GitHub (`git pull`).
- Never in git, besides client data and passwords: files over 5 MB, Excel lock files (`~$...`), Claude
  chat logs (`*.jsonl`). The one exception for data is `samples/`: one small anonymised example with its
  hand-checked expected output.
- When a piece of work is done, run `/ship-check`: it checks the rules above, re-runs the known-answer
  test, then saves and uploads. Every upload runs the automatic "DHV check" on GitHub; if it fails the
  person gets an email from GitHub. Offer to fix it.
- These tools produce figures for client reports. Before calling a change done, re-run the tool on the
  sample in `samples/` and compare with the expected output. A difference is either a bug or a
  deliberate change the person must confirm.
