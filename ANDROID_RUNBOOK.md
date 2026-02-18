# Android Emulator + App Runbook (Working Setup)

## Final known-good baseline (2026-02-17)

- Build/patch from `C:\dev\Book_of_Mormon_local` (not OneDrive path) to avoid Windows/OneDrive file-lock failures.
- Keep emulator launch in minimal-safe mode (home screen first), then patch app.
- Chart rendering is now:
  - Primary: remote PNG from QuickChart
  - Fallback: local offline PNG generation (pure Python)
  - Non-blocking: chart generation/fetch runs on background threads to avoid app ANR.

## What currently works

- Start emulator in safe mode (recommended daily command):
```powershell
powershell -ExecutionPolicy Bypass -File .\run_android_stable.ps1
```

- Patch app without restarting emulator (recommended for code iterations):
```powershell
powershell -ExecutionPolicy Bypass -File .\patch_android_live.ps1
```

Recommended location + command:
```powershell
cd C:\dev\Book_of_Mormon_local
powershell -ExecutionPolicy Bypass -File .\patch_android_live.ps1
```

- Update app code safely, rebuild, then start emulator on Home:
```powershell
powershell -ExecutionPolicy Bypass -File .\update_and_run_android_stable.ps1
```

These scripts do all of the following:
- Reapplies Gradle workaround: `scripts/apply_android_gradle_workaround.ps1`
- Starts emulator `phone_vulkan` with stable flags
- Waits for boot
- Brings emulator to Home screen in minimal-safe mode

Optional app autorun (only when needed):
```powershell
powershell -ExecutionPolicy Bypass -File .\run_android_stable.ps1 -AutoRunApp
```

Patch script options:
- Skip update phase: `.\patch_android_live.ps1 -SkipUpdate`
- Skip build phase: `.\patch_android_live.ps1 -SkipBuild`
- Install only (do not relaunch app): `.\patch_android_live.ps1 -NoLaunch`

Current baseline to keep:
- No System UI errors in your current working flow/session.
- Keep using `phone_vulkan` with the stable scripts.
- Launch app manually after Home screen unless you explicitly need autorun.
- For chart updates, always patch from `C:\dev\Book_of_Mormon_local`.

## Fast black-screen recovery

If emulator turns black:
```powershell
powershell -ExecutionPolicy Bypass -File .\fix_emulator_black_screen.ps1
```

If that is not enough, run full stable flow again:
```powershell
powershell -ExecutionPolicy Bypass -File .\run_android_stable.ps1
```

## Key files that made this stable

- `run_android_stable.ps1`
- `launch_emulator_home_only.ps1`
- `fix_emulator_black_screen.ps1`
- `patch_android_live.ps1`
- `launch_emulator_visible.ps1`
- `scripts/apply_android_gradle_workaround.ps1`

## Important technical notes

- Emulator launch flags that are stable here:
  - `-no-snapshot`
  - `-no-boot-anim`
  - `-gpu swiftshader_indirect`
- To avoid `System UI` hangs, do not use power toggle (`keyevent 26`) or force-disable lock settings during normal launch/recovery.
- Safe keep-awake settings used:
  - `stay_on_while_plugged_in=3`
  - `screen_off_timeout=2147483647`
  - `screensaver_enabled=0`
  - `doze_enabled=0`
- App launch issue `No module named mobile_app.__main__` was resolved by rebuilding with correct packaged Python assets.
- Gradle duplicate Kotlin class conflict is handled by excluding:
  - `org.jetbrains.kotlin:kotlin-stdlib-jdk7`
  - `org.jetbrains.kotlin:kotlin-stdlib-jdk8`
- AppCompat dependency is required for current Android theme resources.
- `matplotlib` and `Pillow` are not available in this Chaquopy package index setup, so they are not used for charts.
- If QuickChart network fetch fails, the app still renders a local offline PNG chart image.
- `briefcase update` can print a trailing `PermissionError` after successful build/install/relaunch; if APK build succeeded and `adb install -r` reports `Success`, deployment is still good.

## One-command daily workflow

Use this and avoid manual steps:
```powershell
powershell -ExecutionPolicy Bypass -File .\run_android_stable.ps1
```

If you changed app code and want a safe update + rebuild + boot flow:
```powershell
powershell -ExecutionPolicy Bypass -File .\update_and_run_android_stable.ps1
```

If emulator is already running and you only want to patch app changes:
```powershell
powershell -ExecutionPolicy Bypass -File .\patch_android_live.ps1
```

## Play Store packaging

For release packaging, use the local non-OneDrive workspace:
```powershell
cd C:\dev\Book_of_Mormon_local
powershell -ExecutionPolicy Bypass -File .\release_playstore_aab.ps1
```

This generates a release `.aab` under `dist\` and prints the SHA256 hash.
