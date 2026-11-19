# dhv-team hook launcher.
#   powershell -NoProfile -ExecutionPolicy Bypass -File run.ps1 start|stop|prompt   (JSON event on stdin)
# With Python on the machine it hands the event to handoff_gate.py. Without Python, "start" still prints
# the team rules (and a fresh chat's HANDOFF.md), and the two gates stay off: the person gets no error.
# Keep this file ASCII: Windows PowerShell 5.1 reads a script without a BOM in the local code page.
param([string]$Mode)
$ErrorActionPreference = 'SilentlyContinue'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = $utf8
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8                          # what PowerShell uses when piping text into python
$hooks = $PSScriptRoot
$root = Split-Path -Parent $hooks
$payload = [Console]::In.ReadToEnd()

# "python" may be the Microsoft Store stub, which prints to stderr and exits 9009; the gate itself
# always exits 0. So exit code 0 = it ran; anything else = try the next name, then the fallback.
foreach ($name in @('python', 'py')) {
    if (-not (Get-Command $name -CommandType Application -ErrorAction SilentlyContinue)) { continue }
    try {
        $out = $payload | & $name "$hooks\handoff_gate.py" $Mode 2>$null
        if ($LASTEXITCODE -eq 0) {
            if ($out) { [Console]::Out.Write((@($out) -join "`n")) }
            exit 0
        }
    } catch { }
}

if ($Mode -ne 'start') { exit 0 }                # no Python: the gates stay off
try {
    $ev = $payload | ConvertFrom-Json
    $parts = @()
    $rules = Get-Content -Raw -Encoding UTF8 "$root\rules\core.md"
    if ($rules) { $parts += $rules.Trim() }
    $lang = 'Hebrew'
    $short = $true
    $conf = Join-Path $env:USERPROFILE '.claude\dhv-kit.json'    # same home Python's expanduser uses
    if (Test-Path $conf) {
        $c = Get-Content -Raw -Encoding UTF8 $conf | ConvertFrom-Json
        if ($c.language -eq 'en') { $lang = 'English' }
        if ($c.short_replies -eq $false) { $short = $false }
    }
    if ($short) {
        $style = Get-Content -Raw -Encoding UTF8 "$root\rules\reply-style.md"
        if ($style) { $parts += $style.Trim() }
    }
    $parts += "This person's reply language (their kit settings): $lang. If they write in another language, answer in that one."
    $cwd = if ($ev.cwd) { $ev.cwd } else { (Get-Location).Path }
    # A chat with no folder picked runs in a temp or catch-all place: say so, as no_work_folder() and
    # NO_FOLDER_RULE do in handoff_gate.py (keep the two wordings the same).
    $here = $cwd.TrimEnd('\', '/').ToLower()
    $homeDir = $env:USERPROFILE.TrimEnd('\').ToLower()
    $none = ($here -eq $homeDir) -or ($here.Length -le 2) -or (@("$homeDir\desktop", "$homeDir\documents", "$homeDir\downloads") -contains $here)
    foreach ($b in @($env:TEMP, $env:TMP, "$homeDir\appdata\local\temp", "$homeDir\.claude")) {
        if (-not $b) { continue }
        $b = $b.TrimEnd('\').ToLower()
        if ($here -eq $b -or $here.StartsWith($b + '\')) { $none = $true }
    }
    if ($none) {
        $parts += 'This chat has no work folder: it runs in ' + $cwd + ', a temporary or catch-all place. Files written here can be lost, and notes saved here are not found by the next chat. Never write HANDOFF.md, OPEN.md or DECISIONS.md here. When the person starts work that will produce files or outlast this chat, tell them so once, in one plain line, and offer to pick a folder for it (in the desktop app: the folder picker, `request_directory` with no path, then `change_directory` to move this chat there; elsewhere: ask them to open Claude in that folder).'
    }
    # The nearest HANDOFF.md from here up to the top of the git repo; outside a repo, this folder only.
    $notes = Join-Path $cwd 'HANDOFF.md'
    $d = $cwd
    $chain = @()
    while ($d) {
        $chain += $d
        if (Test-Path -LiteralPath (Join-Path $d '.git')) { break }
        $up = Split-Path -Parent $d
        if (-not $up -or $up -eq $d) { $chain = @($cwd); break }
        $d = $up
    }
    foreach ($f in $chain) {
        $candidate = Join-Path $f 'HANDOFF.md'
        if (Test-Path -LiteralPath $candidate) { $notes = $candidate; break }
    }
    if ((@($null, 'startup', 'clear') -contains $ev.source) -and (Test-Path -LiteralPath $notes)) {
        $text = Get-Content -Raw -Encoding UTF8 -LiteralPath $notes
        # Claude Code caps a hook's output at 10,000 characters (past it the rules would be cut too),
        # so the notes get what is left after the rules. Same rule as HOOK_CAP in handoff_gate.py.
        $used = 0
        foreach ($part in $parts) { $used += $part.Length }
        $room = [Math]::Max(1000, 9500 - $used - 500)
        if ($text.Length -gt $room) { $text = $text.Substring(0, $room) + "`n`n[Cut here: HANDOFF.md is longer. Read the rest of the file before acting on these notes.]" }
        $parts += "The previous chat left these notes in HANDOFF.md. Treat them as where the work stands; do not re-read the file unless the notes say they were cut. If the person's first message is about this work, open with two or three plain lines on where things stand and the next step.`n`n$text"
    }
    [Console]::Out.Write(($parts -join "`n`n"))
} catch { }
exit 0
