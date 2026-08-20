<#
.SYNOPSIS
  Batch-converts every .L5X in a folder to .ACD using Rockwell's own l5xgit
  CLI (from RockwellAutomation/ra-logix-designer-vcs-custom-tools), so
  hundreds of samples can be compiled without opening Logix Designer by hand.

.PREREQS
  - Studio 5000 Logix Designer + Logix Designer SDK 2.2+ installed
  - l5xgit.exe built from https://github.com/RockwellAutomation/ra-logix-designer-vcs-custom-tools
    (dotnet build against .NET 10 SDK) and either on PATH or passed via -L5xGitPath

.EXAMPLE
  ./batch_l5x_to_acd.ps1 -InputDir ..\samples\generated -OutputDir C:\l5x_scratch\acd
#>
param(
    [Parameter(Mandatory = $true)][string]$InputDir,
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [string]$L5xGitPath = "l5xgit",
    [switch]$UnsafeSkipDependencyCheck
)

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$logPath = Join-Path $OutputDir "convert_log.csv"
"l5x_path,acd_path,status,message" | Out-File -FilePath $logPath -Encoding utf8

$files = Get-ChildItem -Path $InputDir -Filter *.L5X -Recurse
Write-Host "Found $($files.Count) L5X file(s) under $InputDir"

$i = 0
foreach ($f in $files) {
    $i++
    $acdPath = Join-Path $OutputDir ($f.BaseName + ".ACD")
    Write-Host "[$i/$($files.Count)] $($f.Name) -> $acdPath"

    $argList = @("l5x2acd", "--l5x", $f.FullName, "--acd", $acdPath)
    if ($UnsafeSkipDependencyCheck) { $argList += "--unsafe-skip-dependency-check" }

    $result = & $L5xGitPath @argList 2>&1
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        "$($f.FullName),$acdPath,ok," | Out-File -FilePath $logPath -Append -Encoding utf8
    } else {
        $msg = ($result -join " ") -replace ",", ";"
        "$($f.FullName),$acdPath,FAILED,$msg" | Out-File -FilePath $logPath -Append -Encoding utf8
        Write-Warning "  Conversion failed: $msg"
    }
}

Write-Host "Done. Log: $logPath"
