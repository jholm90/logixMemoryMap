<#
.SYNOPSIS
    One-time setup of the L5X Memory Analyzer UI on a Windows machine that has nothing
    installed. Double-click Setup.cmd in the repository root, which runs it.

.DESCRIPTION
    1. Uses a Python 3.10+ already on the machine, or downloads the official Python
       installer from python.org, checks its Python Software Foundation signature and
       installs it for the current user only: no administrator rights.
    2. Creates .venv in the repository folder and installs the analyzer into it
       (`pip install .`, as the README does). Nothing is installed system-wide apart
       from Python itself.
    3. Self-check: loads the sizing model and builds the UI application.
    4. Puts an "L5X Memory Analyzer" shortcut on the desktop (runs
       scripts\LaunchUI.pyw, no console window) and starts the UI.

    Needs internet access for the Python download and the pip packages. Safe to run
    again: every step that is already done is skipped or repeated harmlessly.

.PARAMETER NoLaunch
    Do not start the UI at the end.
.PARAMETER NoShortcut
    Do not create the desktop shortcut.
.PARAMETER PythonVersion
    Python to install when none is found. Default 3.12.10.
#>
param(
    [switch]$NoLaunch,
    [switch]$NoShortcut,
    [string]$PythonVersion = '3.12.10'
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # Windows PowerShell 5.1 downloads 10x slower with the progress bar
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

$Repo = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $Repo '.venv'
$VenvPy = Join-Path $Venv 'Scripts\python.exe'
$VenvPyw = Join-Path $Venv 'Scripts\pythonw.exe'
$Launcher = Join-Path $Repo 'scripts\LaunchUI.pyw'

function Step([string]$Message) { Write-Host "==> $Message" -ForegroundColor Cyan }

# Native programs are run with ErrorActionPreference Continue: under Windows PowerShell 5.1,
# 'Stop' turns any line a program writes to stderr (a pip warning) into a fatal error.
function Invoke-Checked([string]$Exe, [string[]]$Arguments, [string]$What) {
    $ErrorActionPreference = 'Continue'
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$What failed (exit code $LASTEXITCODE)." }
}

function Test-Python([string]$Exe) {
    $ErrorActionPreference = 'Continue'
    # The Microsoft Store "python.exe" alias in WindowsApps only opens the Store.
    if (-not $Exe -or -not (Test-Path $Exe) -or $Exe -like '*\WindowsApps\*') { return $false }
    try { $v = & $Exe -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null } catch { return $false }
    if ($LASTEXITCODE -ne 0 -or -not $v) { return $false }
    $major, $minor = "$v".Trim().Split('.')
    return ([int]$major -eq 3 -and [int]$minor -ge 10)
}

function Find-Python {
    $ErrorActionPreference = 'Continue'
    $tag = ($PythonVersion.Split('.')[0..1] -join '')
    $candidates = @(Join-Path $env:LOCALAPPDATA "Programs\Python\Python$tag\python.exe")
    foreach ($name in 'python', 'python3') {
        Get-Command $name -All -ErrorAction SilentlyContinue | ForEach-Object { $candidates += $_.Source }
    }
    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        try {
            $p = & $launcher.Source -3 -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $p) { $candidates += "$p".Trim() }
        } catch { }
    }
    foreach ($c in $candidates) { if (Test-Python $c) { return $c } }
    return $null
}

function Install-Python {
    $url = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"
    $installer = Join-Path $env:TEMP "python-$PythonVersion-amd64.exe"
    Step "Downloading Python $PythonVersion from python.org"
    Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
    $sig = Get-AuthenticodeSignature -FilePath $installer
    if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'Python Software Foundation') {
        Remove-Item $installer -ErrorAction SilentlyContinue
        throw "The downloaded Python installer is not validly signed by the Python Software Foundation ($($sig.Status)). Not running it."
    }
    Step "Installing Python $PythonVersion for this user (no administrator rights needed)"
    $installArgs = @('/quiet', 'InstallAllUsers=0', 'PrependPath=1', 'Include_launcher=1',
                     'InstallLauncherAllUsers=0', 'Include_test=0', 'Include_doc=0', 'Shortcuts=0')
    $proc = Start-Process -FilePath $installer -ArgumentList $installArgs -Wait -PassThru
    Remove-Item $installer -ErrorAction SilentlyContinue
    if ($proc.ExitCode -ne 0) { throw "The Python installer exited with code $($proc.ExitCode)." }
}

try {
    if (-not (Test-Path (Join-Path $Repo 'pyproject.toml'))) {
        throw "pyproject.toml not found in $Repo. Double-click Setup.cmd in the root of the extracted repository."
    }

    Step 'Looking for Python 3.10 or newer'
    $python = Find-Python
    if ($python) {
        Write-Host "    using $python"
    } else {
        Install-Python
        $python = Find-Python
        if (-not $python) { throw 'Python was installed but cannot be found. Sign out and back in, then run this again.' }
        Write-Host "    installed $python"
    }

    if (-not (Test-Python $VenvPy)) {
        Step "Creating the virtual environment $Venv"
        Invoke-Checked $python @('-m', 'venv', $Venv) 'Creating the virtual environment'
    }

    Step 'Installing the analyzer and its dependencies (Flask, waitress, PyYAML, openpyxl)'
    Invoke-Checked $VenvPy @('-m', 'pip', 'install', '--disable-pip-version-check', '--upgrade', 'pip') 'Upgrading pip'
    Invoke-Checked $VenvPy @('-m', 'pip', 'install', '--disable-pip-version-check', $Repo) 'Installing the analyzer'

    Step 'Self-check: loading the sizing model and building the UI'
    $check = 'import waitress, openpyxl; ' +
             'from l5x_memory_analyzer.sizing.constants import load_memory_model; ' +
             'from l5x_memory_analyzer.ui.server import create_app; ' +
             'load_memory_model(); create_app(None); print(''self-check ok'')'
    Invoke-Checked $VenvPy @('-c', $check) 'The self-check'

    if (-not $NoShortcut) {
        Step 'Creating the desktop shortcut "L5X Memory Analyzer"'
        $lnk = Join-Path ([Environment]::GetFolderPath('Desktop')) 'L5X Memory Analyzer.lnk'
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($lnk)
        $shortcut.TargetPath = $VenvPyw
        $shortcut.Arguments = "`"$Launcher`""
        $shortcut.WorkingDirectory = $Repo
        $shortcut.Description = 'L5X Memory Analyzer -- opens in your browser'
        $shortcut.Save()
        Write-Host "    $lnk"
    }

    Write-Host ''
    Write-Host 'Setup complete.' -ForegroundColor Green
    Write-Host 'Start it from the desktop shortcut. It opens in your browser at http://127.0.0.1:8765'
    Write-Host 'From a command prompt:  .venv\Scripts\l5x-memory-analyzer ui'

    if (-not $NoLaunch) {
        Step 'Starting the UI'
        Start-Process -FilePath $VenvPyw -ArgumentList "`"$Launcher`"" -WorkingDirectory $Repo
    }
    exit 0
}
catch {
    Write-Host ''
    Write-Host "SETUP FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
