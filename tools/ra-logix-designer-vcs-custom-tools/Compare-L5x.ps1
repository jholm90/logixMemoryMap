<#
.SYNOPSIS
    Compares two L5X files in WinMerge, by exploding them, ignoring differences that carry no meaning.

.DESCRIPTION
    Explodes both files and opens the resulting directory trees in a WinMerge folder comparison.

    Exploding is what makes the comparison meaningful. It reserialises the XML, so indentation and
    line breaks stop mattering; it omits the volatile ExportDate; and it writes every DataType,
    Add-On Instruction, Tag, Program, Task, Module and Trend to its own file named after the
    element. Because each element lands at a path determined by its name, the order those elements
    appeared in within the source file no longer shows up as a difference.

    --pretty-attributes is used so each XML attribute sits on its own line. Without it a single
    changed attribute reports the whole element as one modified line..

.PARAMETER Left
    The baseline L5X file.

.PARAMETER Right
    The L5X file to compare against the baseline.

.PARAMETER KeepOutput
    Keep the exploded directories after WinMerge closes, and print their paths.

.PARAMETER WinMergePath
    Full path to WinMergeU.exe, if it is not on PATH or in a standard install location.

.EXAMPLE
    .\Compare-L5x.ps1 -Left original.L5X -Right roundtripped.L5X

.EXAMPLE
    .\Compare-L5x.ps1 -Left a.L5X -Right b.L5X -KeepOutput
#>
param(
    [Parameter(Mandatory)]
    [string]$Left,

    [Parameter(Mandatory)]
    [string]$Right,

    [Parameter()]
    [switch]$KeepOutput,

    [Parameter()]
    [string]$WinMergePath
)

$ErrorActionPreference = 'Stop'

function Resolve-WinMerge {
    param([string]$Explicit)

    if ($Explicit) {
        if (Test-Path -PathType Leaf $Explicit) { return (Get-Item $Explicit).FullName }
        throw "WinMergeU.exe not found at '$Explicit'."
    }

    $candidates = @(
        (Get-Command 'WinMergeU.exe' -ErrorAction SilentlyContinue).Source
        (Join-Path $env:ProgramFiles 'WinMerge\WinMergeU.exe')
        (Join-Path ${env:ProgramFiles(x86)} 'WinMerge\WinMergeU.exe')
        (Join-Path $env:LOCALAPPDATA 'Programs\WinMerge\WinMergeU.exe')
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -PathType Leaf $candidate)) { return (Get-Item $candidate).FullName }
    }

    throw "WinMergeU.exe not found. Install WinMerge or pass -WinMergePath."
}

function Invoke-Explode {
    param([string]$Source, [string]$Destination, [string[]]$ExtraArgs)

    $arguments = @('explode', '--l5x', $Source, '--dir', $Destination, '--force', '--pretty-attributes') + $ExtraArgs
    $output = & $l5xplode @arguments 2>&1
    return [PSCustomObject]@{ ExitCode = $LASTEXITCODE; Output = ($output | Out-String) }
}

function Main {
    $l5xplode = Join-Path $PSScriptRoot 'artifacts\bin\Release\l5xplode.exe'
    if (-not (Test-Path $l5xplode)) {
        throw "l5xplode.exe not found at '$l5xplode'. Run 'dotnet build -c Release' first."
    }

    foreach ($path in @($Left, $Right)) {
        if (-not (Test-Path -PathType Leaf $path)) { throw "L5X file not found: $path" }
    }

    $winMerge  = Resolve-WinMerge -Explicit $WinMergePath
    $leftPath  = (Get-Item $Left).FullName
    $rightPath = (Get-Item $Right).FullName

    $workDir   = Join-Path ([System.IO.Path]::GetTempPath()) ("l5xcompare_" + [guid]::NewGuid().ToString('N').Substring(0, 8))
    $leftDir   = Join-Path $workDir 'left'
    $rightDir  = Join-Path $workDir 'right'

    try {
        # Both sides must explode with identical flags, otherwise export-options.yaml differs and shows
        # up as a false difference. So probe the baseline first and let it decide for both.
        $extraArgs = @()

        Write-Host "Exploding left  : $leftPath"
        $probe = Invoke-Explode -Source $leftPath -Destination $leftDir -ExtraArgs $extraArgs

        if ($probe.ExitCode -ne 0 -and $probe.Output -match 'Dependencies') {
            Write-Warning 'Exported without the Dependencies option; retrying with --unsafe-skip-dependency-check.'
            Write-Warning 'That records L5XGitPrevAOI ordering hints, so AOI order WILL appear in the diff.'
            $extraArgs = @('--unsafe-skip-dependency-check')
            $probe = Invoke-Explode -Source $leftPath -Destination $leftDir -ExtraArgs $extraArgs
        }

        if ($probe.ExitCode -ne 0) {
            throw "Failed to explode '$leftPath':`n$($probe.Output)"
        }

        Write-Host "Exploding right : $rightPath"
        $rightResult = Invoke-Explode -Source $rightPath -Destination $rightDir -ExtraArgs $extraArgs
        if ($rightResult.ExitCode -ne 0) {
            throw "Failed to explode '$rightPath':`n$($rightResult.Output)"
        }

        # /r recurse, /e close on Esc, /u keep out of the MRU, /wl /wr open both sides read-only so the
        # temp copies cannot be edited by mistake.
        $winMergeArgs = @(
            '/r', '/e', '/u', '/wl', '/wr',
            '/dl', "`"$leftPath`"",
            '/dr', "`"$rightPath`"",
            "`"$leftDir`"", "`"$rightDir`""
        )

        Write-Host 'Opening WinMerge...'
        Start-Process -FilePath $winMerge -ArgumentList $winMergeArgs -Wait
    }
    finally {
        if ($KeepOutput) {
            Write-Host ''
            Write-Host "Exploded output kept at: $workDir"
        }
        elseif (Test-Path $workDir) {
            Remove-Item $workDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}
