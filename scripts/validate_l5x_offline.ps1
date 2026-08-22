<#
.SYNOPSIS
  Batch-validates .L5X files with a real offline compile -- no download, no
  FactoryTalk Logix Echo. James, 2026-08-22: "I dont have echo. I'm not
  buying echo. I told you this is a no-download project from the start" --
  and separately: "All of your data samples need 100% validation or you can
  consider your entire data sample moot."

  Uses LogixProject.BuildAsync(RequestedBuildTarget.DefaultTarget), found by
  running dump_ldsdk_api.ps1 against the actual installed SDK. This forces a
  real offline compile of the project; build errors surface through the
  SDK's own IOperationEvent.Error callback, not l5x2acd's "did it open"
  check (which convert_log.csv already proved does NOT catch ladder-logic
  errors -- every file with the 2026-08-22 arr0/T_ADD bugs showed "ok").

.USAGE
  ALWAYS run -SelfTest first. It validates two files this project already
  knows are broken (pre-fix CPS array-subscript bug, T_ADD misclassification)
  and requires both come back FAILED with real error text. If it doesn't,
  don't trust any "ok" result from a full run.

.EXAMPLE
  ./validate_l5x_offline.ps1 -SelfTest
  ./validate_l5x_offline.ps1 -InputDir ..\samples\generated -LogPath C:\l5x_scratch\validate_log.csv -Limit 10
  ./validate_l5x_offline.ps1 -InputDir ..\samples\generated -LogPath C:\l5x_scratch\validate_log.csv -ConvertLog C:\l5x_scratch\acd\convert_log.csv
#>
param(
    [switch]$SelfTest,
    [string]$InputDir,
    [string]$LogPath,
    [int]$Limit,
    [string]$ConvertLog,
    [string]$SelfTestLogPath = (Join-Path $PSScriptRoot "l5x_validator\selftest_log.csv")
)

$projectDir = Join-Path $PSScriptRoot "l5x_validator"
if (-not (Test-Path (Join-Path $projectDir "LogixValidator.csproj"))) {
    Write-Error "Expected LogixValidator.csproj under $projectDir -- run this from a checkout of the repo."
    exit 1
}

Write-Host "Building validator..."
Push-Location $projectDir
try {
    dotnet build -c Release *>&1 | Tee-Object -Variable buildOutput | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host $buildOutput
        Write-Error "Build failed -- see output above."
        exit 1
    }

    if ($SelfTest) {
        dotnet run -c Release --no-build -- selftest $SelfTestLogPath
        $exitCode = $LASTEXITCODE
    } else {
        if (-not $InputDir -or -not $LogPath) {
            Write-Error "For a real run, -InputDir and -LogPath are required (or pass -SelfTest alone)."
            exit 1
        }
        $argList = @("run", "-c", "Release", "--no-build", "--", "validate", $InputDir, $LogPath)
        if ($ConvertLog) { $argList += @("--convert-log", $ConvertLog) }
        if ($Limit) { $argList += @("--limit", $Limit) }
        dotnet @argList
        $exitCode = $LASTEXITCODE
    }
} finally {
    Pop-Location
}

if (-not $SelfTest -and $LogPath -and (Test-Path $LogPath)) {
    $repoRoot = Split-Path $PSScriptRoot -Parent
    $repoLogPath = Join-Path $repoRoot "samples\validate_log.csv"
    Copy-Item -Path $LogPath -Destination $repoLogPath -Force
    . (Join-Path $PSScriptRoot "_autopush.ps1")
    Push-RepoFile -RepoRoot $repoRoot -FilePath $repoLogPath -CommitMessage "Log offline L5X BuildAsync validation results"
}

exit $exitCode
