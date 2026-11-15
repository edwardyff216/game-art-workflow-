param([ValidateSet('import','initial','diagnostics','stills','video','seams-before','seams-after')][string]$Mode = 'stills')
$ErrorActionPreference = 'Stop'
$config = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot '../tools.session.json') | ConvertFrom-Json
$project = Join-Path $PSScriptRoot 'project'
$reports = Join-Path $PSScriptRoot 'reports'
if ($Mode.StartsWith('seams-')) {
    $reports = Join-Path $PSScriptRoot '../seam-review/reports'
}
New-Item -ItemType Directory -Path $reports -Force | Out-Null
$argsList = @('--path', ('"' + $project + '"'))
if ($Mode -eq 'import') {
    $argsList += @('--headless','--editor','--import')
} else {
    $argsList += @('--disable-vsync','--', $Mode)
}
$process = Start-Process -FilePath $config.godot_executable -ArgumentList $argsList -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $reports "$Mode.log") `
    -RedirectStandardError (Join-Path $reports "$Mode.stderr.log")
if (-not $process.WaitForExit(180000)) {
    Stop-Process -Id $process.Id
    throw "$Mode timed out"
}
Get-Content -LiteralPath (Join-Path $reports "$Mode.log") -Tail 12
$stderr = Join-Path $reports "$Mode.stderr.log"
Get-Content -LiteralPath $stderr
if ($process.ExitCode -ne 0 -or (Select-String -LiteralPath $stderr -Pattern 'SCRIPT ERROR|^ERROR:' -Quiet)) {
    exit 1
}
