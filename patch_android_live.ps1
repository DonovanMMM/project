param(
    [string]$AppId = "org.donov.mobile_app",
    [switch]$SkipUpdate,
    [switch]$SkipBuild,
    [switch]$NoLaunch
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$adb = "C:\Users\Donov\AppData\Local\BeeWare\briefcase\Cache\tools\android_sdk\platform-tools\adb.exe"
$apkPath = Join-Path $root "build\mobile_app\android\gradle\app\build\outputs\apk\debug\app-debug.apk"

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"

function Invoke-External {
    param(
        [scriptblock]$Command,
        [string]$FailureMessage
    )
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$FailureMessage (exit code $LASTEXITCODE)"
    }
}

function Repair-BuildPathState {
    $pythonBuildPath = Join-Path $root "build\mobile_app\android\gradle\app\src\main\python"
    $mobileModulePath = Join-Path $pythonBuildPath "mobile_app"

    if (Test-Path $pythonBuildPath) {
        icacls $pythonBuildPath /inheritance:r | Out-Null
        $u = whoami
        icacls $pythonBuildPath /grant:r "$u`:(OI)(CI)F" "SYSTEM:(OI)(CI)F" "Administrators:(OI)(CI)F" /T /C | Out-Null
        icacls $pythonBuildPath /remove:d Everyone /T /C | Out-Null
        attrib -R "$pythonBuildPath\*" /S /D 2>$null
    }

    if (Test-Path $mobileModulePath) {
        try {
            Remove-Item -Recurse -Force $mobileModulePath -ErrorAction Stop
        } catch {
            # Retry path handles follow-up failure.
        }
    }
}

function Require-RunningEmulator {
    $devicesRaw = (& $adb devices) -join "`n"
    if ($devicesRaw -notmatch "emulator-\d+\s+device") {
        throw "No running emulator detected. Start emulator first with .\run_android_stable.ps1"
    }
}

Require-RunningEmulator

if (-not $SkipUpdate) {
    try {
        Invoke-External -Command { briefcase update android } -FailureMessage "briefcase update failed"
    } catch {
        Repair-BuildPathState
        Invoke-External -Command { briefcase update android } -FailureMessage "briefcase update failed after retry"
    }
}

& "$root\scripts\apply_android_gradle_workaround.ps1" -ProjectRoot $root

if (-not $SkipBuild) {
    Invoke-External -Command { briefcase build android } -FailureMessage "briefcase build failed"
}

if (-not (Test-Path $apkPath)) {
    throw "APK not found at $apkPath"
}

# Replace app in-place on the running emulator; no emulator restart required.
& $adb shell am force-stop $AppId 2>$null | Out-Null
& $adb install -r $apkPath

if ($LASTEXITCODE -ne 0) {
    throw "adb install failed."
}

if (-not $NoLaunch) {
    & $adb shell monkey -p $AppId -c android.intent.category.LAUNCHER 1 | Out-Null
    Write-Host "Patched and relaunched $AppId on running emulator."
} else {
    Write-Host "Patched $AppId on running emulator (launch skipped)."
}
