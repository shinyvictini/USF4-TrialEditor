$ErrorActionPreference = "Stop"

Set-Location "$PSScriptRoot\tools"

python -m pip install pyinstaller

if ($LASTEXITCODE -ne 0) {
    throw "Dependency installation failed."
}

$buildArgs = @(
    "--noconfirm"
    "--clean"
    "--onefile"
    "--windowed"
    "--name", "USF4-TrialEditor"
    "--version-file", "version_info.txt"
    "--add-data", "../patches/trial_tasks.gfx.bsdiff;patches"
    "--add-data", "../patches/ultra_trial_menu.gfx.bsdiff;patches"
)

if (Test-Path "icon.ico") {
    $buildArgs += @(
        "--icon", "icon.ico"
        "--add-data", "icon.ico;."
    )
}

python -m PyInstaller @buildArgs editor_v1.py

if ($LASTEXITCODE -ne 0) {
    throw "Build failed."
}

Write-Host "Build complete: tools\dist\USF4-TrialEditor.exe"