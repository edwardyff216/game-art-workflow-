[CmdletBinding()]
param(
    [ValidateSet('Open','Check','Rebuild')][string]$Mode = 'Check',
    [string]$OutputDirectory,
    [string]$ConfigPath = (Join-Path $PSScriptRoot '../../../tools.local.json'),
    [string]$Python = 'python',
    [string]$Ffmpeg = 'ffmpeg'
)
$ErrorActionPreference = 'Stop'

$config = Get-Content -Raw -LiteralPath $ConfigPath | ConvertFrom-Json
$sample = Split-Path $PSScriptRoot -Parent
$project = (Resolve-Path -LiteralPath (Join-Path $sample 'godot-review/project')).Path
$baseline = Join-Path $sample 'source/frontier-relay-07-seams-v09.blend'
if ($Mode -ne 'Open') {
    if (-not $OutputDirectory) {
        $OutputDirectory = Join-Path $PSScriptRoot ('previews/' + [guid]::NewGuid().ToString('N'))
    }
    $OutputDirectory = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputDirectory)
    if (Test-Path -LiteralPath $OutputDirectory) {
        throw "Choose a new output directory: $OutputDirectory"
    }
    $null = New-Item -ItemType Directory -Path $OutputDirectory
    Write-Host "Evidence: $OutputDirectory"
}

function Invoke-NativeChecked {
    param([string]$Tool, [string[]]$Arguments)
    & $Tool @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Tool exited with code $LASTEXITCODE" }
}

function Invoke-GodotChecked {
    param([string]$Label, [string[]]$ExtraArguments)
    $arguments = @('--path', ('"' + $project + '"')) + $ExtraArguments
    $stdout = Join-Path $OutputDirectory "$Label.log"
    $stderr = Join-Path $OutputDirectory "$Label.stderr.log"
    $process = Start-Process -FilePath $config.godot_executable -ArgumentList $arguments `
        -WindowStyle Hidden -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if (-not $process.WaitForExit(180000)) {
        Stop-Process -Id $process.Id
        throw "Godot timed out: $Label"
    }
    if ($process.ExitCode -ne 0 -or (Select-String -LiteralPath $stderr -Pattern 'SCRIPT ERROR|^ERROR:' -Quiet)) {
        Get-Content -LiteralPath $stdout,$stderr -Tail 25
        throw "Godot failed: $Label"
    }
}

if ($Mode -eq 'Rebuild') {
    $maps = Join-Path $OutputDirectory 'textures'
    $blend = Join-Path $OutputDirectory 'frontier-relay-07-finish-v10.blend'
    $glb = Join-Path $OutputDirectory 'frontier-relay-07-v10.glb'
    Invoke-NativeChecked $Python @((Join-Path $PSScriptRoot 'make_finish_maps.py'), $maps)
    Invoke-NativeChecked $config.blender_executable @(
        '--background','--factory-startup',$baseline,'--python-exit-code','1',
        '--python',(Join-Path $PSScriptRoot 'build_finish.py'),'--',$maps,$blend,$glb
    )
    Invoke-NativeChecked $Python @((Join-Path $PSScriptRoot 'verify_final.py'), $OutputDirectory, '--export-only', '--rebuilt', $glb)
} elseif ($Mode -eq 'Open') {
    $process = Start-Process -FilePath $config.godot_executable -Wait -PassThru -WindowStyle Hidden `
        -ArgumentList @('--headless','--editor','--path',('"' + $project + '"'),'--import')
    if ($process.ExitCode -ne 0) { throw 'Godot import failed.' }
    Start-Process -FilePath $config.godot_executable -ArgumentList @('--path', ('"' + $project + '"'))
} else {
    Invoke-GodotChecked 'godot-import' @('--headless','--editor','--import')
    Invoke-GodotChecked 'godot-capture' @('--disable-vsync','--script','res://final_capture.gd','--',('"' + $OutputDirectory + '"'))
    Invoke-NativeChecked $Python @((Join-Path $PSScriptRoot 'verify_final.py'), $OutputDirectory)
    Invoke-NativeChecked $Ffmpeg @('-hide_banner','-loglevel','error','-n','-framerate','24',
        '-i',(Join-Path $OutputDirectory 'frames/frame-%04d.jpg'),'-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2',
        '-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',
        (Join-Path $OutputDirectory '06-orbit.mp4'))
}
