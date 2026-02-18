$ErrorActionPreference = "Stop"

$adb = "C:\Users\Donov\AppData\Local\BeeWare\briefcase\Cache\tools\android_sdk\platform-tools\adb.exe"

& $adb wait-for-device | Out-Null
& $adb shell input keyevent 82 | Out-Null
& $adb shell wm dismiss-keyguard 2>$null | Out-Null
& $adb shell settings put system screen_brightness 180 | Out-Null
& $adb shell settings put global stay_on_while_plugged_in 3 | Out-Null
& $adb shell settings put system screen_off_timeout 2147483647 2>$null | Out-Null
& $adb shell settings put secure screensaver_enabled 0 2>$null | Out-Null
& $adb shell settings put secure doze_enabled 0 2>$null | Out-Null
& $adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME | Out-Null

Write-Host "Emulator home reset complete (no power toggle / no lock_settings)."
