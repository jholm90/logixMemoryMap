<#
.SYNOPSIS
  Proof-of-concept only (James, 2026-08-22: "lets see if we can do ocr on
  an object") -- NOT the real validator yet. Captures a screenshot (full
  screen by default, or a specific window by process name) and runs it
  through Windows' built-in OCR engine (Windows.Media.Ocr -- no install
  needed, ships with Windows 10/11), dumping every recognized text line
  plus its screen coordinates to the console and to a text file.

  Purpose: confirm OCR actually reads Studio 5000's Verify/Build result
  text (status bar message, Error List pane, whatever it turns out to be)
  clearly enough to parse automatically, and capture the REAL text shape
  so the real parser regex can be built against actual output instead of
  a guess. Once you've run this against a real Verify result and we know
  what the text looks like, the real batch tool (open file -> wait for you
  to Verify -> capture -> parse pass/fail -> log -> next file, same
  semi-attended pattern as batch_memory_capture.ps1) is a quick follow-up.

.PARAMETER ProcessName
  If given, captures only that process's main window instead of the full
  screen (e.g. -ProcessName "Logix Designer" -- exact name TBD, run
  Get-Process to find it if unsure). Omit to capture the full screen.

.PARAMETER OutDir
  Where to save the screenshot PNG and the OCR text dump. Defaults to a
  scratch folder next to this script.

.EXAMPLE
  ./ocr_test.ps1
  ./ocr_test.ps1 -ProcessName "LogixDesigner"
#>
param(
    [string]$ProcessName,
    [string]$OutDir = (Join-Path $PSScriptRoot "ocr_test_output")
)

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$pngPath = Join-Path $OutDir "capture_$timestamp.png"
$txtPath = Join-Path $OutDir "ocr_text_$timestamp.txt"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# --- Native calls needed to find & capture a specific window, if requested ---
Add-Type @"
using System;
using System.Runtime.InteropServices;
public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
public class Native {
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
}
"@

function Get-CaptureRect {
    param([string]$ProcName)
    if (-not $ProcName) {
        $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        return New-Object RECT -Property @{ Left = $screen.Left; Top = $screen.Top; Right = $screen.Right; Bottom = $screen.Bottom }
    }
    $proc = Get-Process -Name $ProcName -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if (-not $proc) {
        Write-Error "No process named '$ProcName' with a visible main window found. Run Get-Process to check the real name."
        exit 1
    }
    [Native]::SetForegroundWindow($proc.MainWindowHandle) | Out-Null
    Start-Sleep -Milliseconds 300  # let it come to front before capturing
    $rect = New-Object RECT
    [Native]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
    return $rect
}

$rect = Get-CaptureRect -ProcName $ProcessName
$width = $rect.Right - $rect.Left
$height = $rect.Bottom - $rect.Top
Write-Host "Capturing region: ($($rect.Left),$($rect.Top)) ${width}x${height}"

$bitmap = New-Object System.Drawing.Bitmap $width, $height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, (New-Object System.Drawing.Size $width, $height))
$bitmap.Save($pngPath, [System.Drawing.Imaging.ImageFormat]::Png)
Write-Host "Saved screenshot: $pngPath"

# --- Windows.Media.Ocr via WinRT interop (no extra install required) ---
[Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime] | Out-Null

Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
})[0]
function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

$ocrEngine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
if (-not $ocrEngine) {
    Write-Error "Could not create an OCR engine -- check Windows Settings > Time & Language > Language > installed OCR language pack for English."
    exit 1
}

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($pngPath)) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$softwareBitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$ocrResult = Await ($ocrEngine.RecognizeAsync($softwareBitmap)) ([Windows.Media.Ocr.OcrResult])

$lines = @()
foreach ($line in $ocrResult.Lines) {
    $lines += $line.Text
}

Write-Host ""
Write-Host "=== OCR recognized $($lines.Count) line(s) ==="
$lines | ForEach-Object { Write-Host "  $_" }

($lines -join "`n") | Out-File -FilePath $txtPath -Encoding utf8
Write-Host ""
Write-Host "Full text dump: $txtPath"
Write-Host "Screenshot: $pngPath"
Write-Host ""
Write-Host "Next: trigger a Verify/Build in Studio 5000 (one with errors, one clean if you"
Write-Host "can), run this script right after each, and share back what lines show up for"
Write-Host "the result message -- that's what the real parser regex gets built against."
