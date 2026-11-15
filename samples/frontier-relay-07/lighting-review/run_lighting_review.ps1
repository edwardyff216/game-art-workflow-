param([ValidateSet('All','A','B','C','C-AO')][string]$Preset = 'All')
$ErrorActionPreference = 'Stop'

$config = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot '../tools.session.json') | ConvertFrom-Json
$project = Join-Path $PSScriptRoot '../godot-review/project'
$reports = Join-Path $PSScriptRoot 'reports'
New-Item -ItemType Directory -Path $reports -Force | Out-Null

$engineArgs = @('--path', ('"' + $project + '"'), '--disable-vsync', '--script', 'res://lighting_review.gd')
if ($Preset -ne 'All') {
    $engineArgs += @('--', $Preset)
}

$stdout = Join-Path $reports "$Preset.log"
$stderr = Join-Path $reports "$Preset.stderr.log"
$process = Start-Process -FilePath $config.godot_executable -ArgumentList $engineArgs -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $stdout -RedirectStandardError $stderr
if (-not $process.WaitForExit(180000)) {
    Stop-Process -Id $process.Id
    throw "Godot lighting capture timed out."
}

Get-Content -LiteralPath $stdout
Get-Content -LiteralPath $stderr
if ($process.ExitCode -ne 0 -or (Select-String -LiteralPath $stderr -Pattern 'SCRIPT ERROR|^ERROR:' -Quiet)) {
    throw "Godot lighting capture failed."
}
