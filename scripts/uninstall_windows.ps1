<#
.SYNOPSIS
    Removes what Setup.cmd installed. Double-click Uninstall.cmd in the repository root.

.DESCRIPTION
    1. Stops any analyzer server running from this folder's .venv.
    2. Deletes the "L5X Memory Analyzer" desktop shortcut.
    3. Deletes the .venv folder.
    4. Uninstalls Python only if Setup.cmd installed it (it leaves the file
       .python-installed-by-setup when it does). A Python that was already on the
       machine is left alone.

    The repository folder itself is not touched: delete it afterwards if you want it gone.
#>

$ErrorActionPreference = 'Stop'
$Repo = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $Repo '.venv'
$PythonMarker = Join-Path $Repo '.python-installed-by-setup'

function Step([string]$Message) { Write-Host "==> $Message" -ForegroundColor Cyan }

try {
    Step 'Stopping the analyzer if it is running'
    $stopped = 0
    # A venv's pythonw.exe only starts the base interpreter, so the server itself is
    # matched by its command line pointing into this folder as well as by its path.
    $procs = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe' OR Name = 'pythonw.exe'" -ErrorAction SilentlyContinue |
        Where-Object { ($_.ExecutablePath -and $_.ExecutablePath.StartsWith($Venv, [StringComparison]::OrdinalIgnoreCase)) -or
                       ($_.CommandLine -and $_.CommandLine.IndexOf($Repo, [StringComparison]::OrdinalIgnoreCase) -ge 0) })
    foreach ($p in $procs) {
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        $stopped++
    }
    Write-Host "    $stopped process(es) stopped"

    Step 'Removing the desktop shortcut'
    $desktop = [Environment]::GetFolderPath('Desktop')
    $lnk = if ($desktop) { Join-Path $desktop 'L5X Memory Analyzer.lnk' } else { '' }
    if ($lnk -and (Test-Path $lnk)) { Remove-Item $lnk -Force; Write-Host "    removed $lnk" } else { Write-Host '    none found' }

    Step "Removing $Venv"
    if (Test-Path $Venv) {
        Start-Sleep -Milliseconds 500   # let stopped processes release their files
        Remove-Item $Venv -Recurse -Force
        Write-Host '    removed'
    } else { Write-Host '    none found' }

    if (Test-Path $PythonMarker) {
        $version = (Get-Content $PythonMarker -Raw).Trim()
        Step "Uninstalling Python $version (installed by Setup.cmd)"
        $entry = Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall' -ErrorAction SilentlyContinue |
            ForEach-Object { Get-ItemProperty $_.PSPath } |
            Where-Object { $_.DisplayName -like "Python $version*" -and $_.QuietUninstallString } |
            Select-Object -First 1
        # QuietUninstallString is '"<installer>" /uninstall /quiet': run the installer
        # with its arguments rather than handing the quoted string to a shell.
        if ($entry -and $entry.QuietUninstallString -match '^\s*"([^"]+)"\s*(.*)$') {
            $proc = Start-Process -FilePath $Matches[1] -ArgumentList $Matches[2] -Wait -PassThru
            if ($proc.ExitCode -ne 0) { throw "The Python uninstaller exited with code $($proc.ExitCode)." }
            Remove-Item $PythonMarker -Force
            Write-Host '    removed'
        } else {
            Write-Host "    Python $version not found among this user's installed programs; nothing to remove."
            Remove-Item $PythonMarker -Force
        }
    } else {
        Step 'Python was not installed by Setup.cmd: left in place'
    }

    Write-Host ''
    Write-Host 'Uninstall complete. You can delete this folder now.' -ForegroundColor Green
    exit 0
}
catch {
    Write-Host ''
    Write-Host "UNINSTALL FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
