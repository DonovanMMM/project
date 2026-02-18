param(
    [string]$AvdName = "phone_vulkan"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$adb = "C:\Users\Donov\AppData\Local\BeeWare\briefcase\Cache\tools\android_sdk\platform-tools\adb.exe"

# Hard reset emulator stack to avoid stale/hung state.
Get-Process emulator, qemu-system-x86_64, qemu-system-i386, adb, java, javaw -ErrorAction SilentlyContinue |
    Stop-Process -Force -ErrorAction SilentlyContinue

& "$root\launch_emulator_visible.ps1" -AvdName $AvdName

& $adb wait-for-device | Out-Null

for ($i = 0; $i -lt 120; $i++) {
    $boot = (& $adb shell getprop sys.boot_completed 2>$null).Trim()
    if ($boot -eq "1") { break }
    Start-Sleep -Seconds 2
}

# Keep the device awake, but do not toggle power (keyevent 26).
& $adb shell settings put global stay_on_while_plugged_in 3 2>$null | Out-Null
& $adb shell settings put system screen_off_timeout 2147483647 2>$null | Out-Null
& $adb shell settings put secure screensaver_enabled 0 2>$null | Out-Null
& $adb shell settings put secure doze_enabled 0 2>$null | Out-Null

# Lightweight unlock and Home, no app launch.
& $adb shell input keyevent 82 2>$null | Out-Null
& $adb shell wm dismiss-keyguard 2>$null | Out-Null
cmd /c """$adb"" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME >nul 2>nul" | Out-Null

Write-Host "Emulator ready on Home screen (minimal-safe mode)."
