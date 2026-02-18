param(
    [string]$AvdName = "phone_vulkan",
    [switch]$AutoRunApp
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

function Stop-AndroidTooling {
    Get-Process emulator, qemu-system-x86_64, qemu-system-i386, adb, java, javaw, gradle -ErrorAction SilentlyContinue |
        Stop-Process -Force -ErrorAction SilentlyContinue
}

function Repair-BuildPathState {
    $pythonBuildPath = Join-Path $root "build\mobile_app\android\gradle\app\src\main\python"
    $mobileModulePath = Join-Path $pythonBuildPath "mobile_app"

    if (Test-Path $pythonBuildPath) {
        # Clear inherited deny ACL patterns that can cause WinError 5 during briefcase update.
        icacls $pythonBuildPath /inheritance:r | Out-Null
        $u = whoami
        icacls $pythonBuildPath /grant:r "$u`:(OI)(CI)F" "SYSTEM:(OI)(CI)F" "Administrators:(OI)(CI)F" /T /C | Out-Null
        icacls $pythonBuildPath /remove:d Everyone /T /C | Out-Null
        attrib -R "$pythonBuildPath\*" /S /D 2>$null
    }

    # If this directory is stale/locked between runs, briefcase update can fail.
    if (Test-Path $mobileModulePath) {
        try {
            Remove-Item -Recurse -Force $mobileModulePath -ErrorAction Stop
        } catch {
            # Keep going; retry logic below handles update failures.
        }
    }
}

function Invoke-BriefcaseUpdateWithRetry {
    $env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"
    try {
        briefcase update android
        return
    } catch {
        Repair-BuildPathState
        briefcase update android
    }
}

Stop-AndroidTooling
Repair-BuildPathState
Invoke-BriefcaseUpdateWithRetry

& "$root\scripts\apply_android_gradle_workaround.ps1" -ProjectRoot $root

$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"
briefcase build android

# Only boot emulator after successful update/build to reduce black-screen/crash loops.
if ($AutoRunApp) {
    & "$root\run_android_stable.ps1" -AvdName $AvdName -AutoRunApp
} else {
    & "$root\run_android_stable.ps1" -AvdName $AvdName
}
