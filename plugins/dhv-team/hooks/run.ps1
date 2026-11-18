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
    $conf = Join-Path $env:USERPROFILE '.claude\dhv-kit.json'    # same home Python's expanduser uses
    if (Test-Path $conf) {
        $c = Get-Content -Raw -Encoding UTF8 $conf | ConvertFrom-Json
        if ($c.language -eq 'en') { $lang = 'English' }
    }
    $parts += "This person's reply language (their kit settings): $lang. If they write in another language, answer in that one."
    $cwd = if ($ev.cwd) { $ev.cwd } else { (Get-Location).Path }
    $notes = Join-Path $cwd 'HANDOFF.md'
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
