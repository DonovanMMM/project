param(
    [string]$AvdName = "phone_vulkan",
    [switch]$AutoRunApp
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

& "$root\scripts\apply_android_gradle_workaround.ps1" -ProjectRoot $root
& "$root\launch_emulator_home_only.ps1" -AvdName $AvdName

if ($AutoRunApp) {
    $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"
    briefcase run android -d "@$AvdName"
} else {
    Write-Host "Emulator is ready on Home screen. Launch the app manually."
}
