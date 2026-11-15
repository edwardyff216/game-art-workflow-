param(
    [string]$Config = (Join-Path $PSScriptRoot '../tools.local.json'),
    [string]$Sample = (Join-Path $PSScriptRoot '../samples/technical-prop')
)
$ErrorActionPreference = 'Stop'
$settings = Get-Content -Raw -LiteralPath $Config | ConvertFrom-Json
$samplePath = (Resolve-Path -LiteralPath $Sample).Path
$spec = Get-Content -Raw -LiteralPath (Join-Path $samplePath 'asset.params.json') | ConvertFrom-Json
$engineProject = Join-Path $samplePath 'godot'
$logs = Join-Path $samplePath 'reports'
& $settings.blender_executable --background --factory-startup --python-exit-code 1 --python (Join-Path $samplePath 'verify_blender.py') *> (Join-Path $logs 'blender-roundtrip.log')
if ($LASTEXITCODE -ne 0) { throw 'Blender round trip failed; inspect reports/blender-roundtrip.log' }
Copy-Item -LiteralPath (Join-Path $samplePath ('exports/' + $spec.id + '.glb')) -Destination (Join-Path $engineProject ('assets/' + $spec.id + '.glb'))
Copy-Item -LiteralPath (Join-Path $samplePath 'asset.params.json') -Destination (Join-Path $engineProject 'asset.params.json')
function Invoke-SampleGodot([string[]]$Arguments, [string]$Label) {
    $process = Start-Process -FilePath $settings.godot_executable -ArgumentList $Arguments -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs "$Label.log") -RedirectStandardError (Join-Path $logs "$Label.stderr.log") -PassThru
    if (-not $process.WaitForExit(60000)) {
        Stop-Process -Id $process.Id
        throw "$Label timed out; this is a failure even if an import file exists."
    }
    if ($process.ExitCode -ne 0) { throw "$Label exited $($process.ExitCode)" }
    if (Select-String -LiteralPath (Join-Path $logs "$Label.stderr.log") -Pattern 'ERROR|SCRIPT ERROR' -Quiet) { throw "$Label reported errors" }
}
Invoke-SampleGodot @('--headless','--path',('"'+$engineProject+'"'),'--editor','--import') 'godot-import'
Invoke-SampleGodot @('--path',('"'+$engineProject+'"')) 'godot-run'
foreach ($name in @('blender-roundtrip.json','godot-validation.json')) {
    $report = Get-Content -Raw -LiteralPath (Join-Path $logs $name) | ConvertFrom-Json
    if (-not $report.passed) { throw "$name did not pass" }
}
Write-Output 'TECHNICAL_CHECKS_PASS — inspect the actual previews separately; this does not approve art style or performance.'
