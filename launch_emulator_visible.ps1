param(
    [string]$AvdName = "phone_vulkan"
)

$ErrorActionPreference = "Stop"

$EmulatorExe = "C:\Users\Donov\AppData\Local\BeeWare\briefcase\Cache\tools\android_sdk\emulator\emulator.exe"

# Kill existing emulator instances to avoid stale/off-screen windows.
Get-Process emulator, qemu-system-x86_64, qemu-system-i386 -ErrorAction SilentlyContinue |
    ForEach-Object {
        $proc = $_
        try {
            Stop-Process -Id $proc.Id -Force -ErrorAction Stop
        } catch {
            $pname = if ($proc.ProcessName) { $proc.ProcessName } else { "unknown" }
            Write-Warning ("Could not stop process {0} ({1}); continuing." -f $pname, $proc.Id)
        }
    }

$existing = Get-Process emulator -ErrorAction SilentlyContinue
if (-not $existing) {
    Start-Process $EmulatorExe -ArgumentList "-avd $AvdName -no-snapshot -no-boot-anim -gpu swiftshader_indirect"
} else {
    Write-Host "Emulator process already running; skipping fresh start."
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class WinApi {
  public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int maxCount);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
}
"@

$screen = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
$targetWidth = [Math]::Min(900, [Math]::Max(700, [int]($screen.Width * 0.55)))
$targetHeight = [Math]::Min(1600, [Math]::Max(900, $screen.Height - 40))
$x = 0
$y = 0

$SW_RESTORE = 9
$SWP_NOZORDER = 0x0004
$SWP_NOACTIVATE = 0x0010
$flags = $SWP_NOZORDER -bor $SWP_NOACTIVATE

$moved = $false
for ($i = 0; $i -lt 120; $i++) {
    Start-Sleep -Milliseconds 500
    [WinApi]::EnumWindows({
        param($hWnd, $lParam)
        if (-not [WinApi]::IsWindowVisible($hWnd)) { return $true }
        $sb = New-Object System.Text.StringBuilder 512
        [void][WinApi]::GetWindowText($hWnd, $sb, $sb.Capacity)
        $title = $sb.ToString()
        if ($title -match "Android Emulator" -or $title -match [Regex]::Escape($AvdName)) {
            [WinApi]::ShowWindow($hWnd, $SW_RESTORE) | Out-Null
            [WinApi]::SetWindowPos($hWnd, [IntPtr]::Zero, $x, $y, $targetWidth, $targetHeight, $flags) | Out-Null
            [WinApi]::SetForegroundWindow($hWnd) | Out-Null
            $script:moved = $true
            return $false
        }
        return $true
    }, [IntPtr]::Zero) | Out-Null

    if ($moved) { break }
}

if ($moved) {
    Write-Host "Emulator '$AvdName' launched and positioned on-screen."
} else {
    Write-Warning "Emulator launched, but window handle was not found for repositioning."
}
