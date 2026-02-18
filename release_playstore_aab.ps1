param(
    [switch]$SkipUpdate
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"

Write-Host "Preparing Play Store AAB from: $root"
Write-Host "JAVA_HOME: $env:JAVA_HOME"

if (-not $SkipUpdate) {
    Write-Host "Running briefcase update android..."
    briefcase update android
}

if (Test-Path "$root\scripts\apply_android_gradle_workaround.ps1") {
    Write-Host "Applying Android Gradle workaround..."
    & "$root\scripts\apply_android_gradle_workaround.ps1" -ProjectRoot $root
}

Write-Host "Packaging Android app bundle (.aab)..."
briefcase package android

if ($LASTEXITCODE -ne 0) {
    throw "briefcase package android failed with exit code $LASTEXITCODE"
}

$aab = Get-ChildItem "$root\dist" -Filter *.aab -Recurse -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $aab) {
    throw "No .aab found under dist\\ after packaging."
}

$hash = Get-FileHash $aab.FullName -Algorithm SHA256

Write-Host ""
Write-Host "Release artifact ready:"
Write-Host "AAB: $($aab.FullName)"
Write-Host "SHA256: $($hash.Hash)"
