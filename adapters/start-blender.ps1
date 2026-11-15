param([string]$Config = (Join-Path $PSScriptRoot '../tools.local.json'))
$ErrorActionPreference = 'Stop'
$settings = Get-Content -Raw -LiteralPath $Config | ConvertFrom-Json
$root = Split-Path (Resolve-Path -LiteralPath $Config).Path
if (Get-NetTCPConnection -LocalPort $settings.blender_port -State Listen -ErrorAction SilentlyContinue) {
    throw 'Configured port already has a listener. Inspect and reuse that instance; do not start a duplicate.'
}
$logs = Join-Path $root 'audit/logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$arguments = @('--factory-startup', '--python', ('"' + (Join-Path $PSScriptRoot 'blender_start.py') + '"'), '--', ('"' + (Resolve-Path -LiteralPath $Config).Path + '"'))
$process = Start-Process -FilePath $settings.blender_executable -ArgumentList $arguments -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs 'blender-start.stdout.log') -RedirectStandardError (Join-Path $logs 'blender-start.stderr.log') -PassThru
$process.Id | Set-Content (Join-Path $root 'audit/blender-session.pid')
Write-Output "Isolated Blender PID $($process.Id); no preferences saved; 127.0.0.1:$($settings.blender_port)"
