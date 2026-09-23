<#
.SYNOPSIS
  Builds the vendored l5xgit CLI and prints the path to l5xgit.exe.

  The source lives in tools/ra-logix-designer-vcs-custom-tools (see
  tools/README.md for the pinned upstream commit). batch_l5x_to_acd.ps1 calls
  this automatically when -L5xGitPath is not given, so a fresh clone needs no
  separate checkout of the Rockwell repository.

  Only the executable path goes to the output stream; all build chatter goes
  to the host, so a caller can capture the path with $exe = & build_l5xgit.ps1.

.PARAMETER Configuration
  dotnet build configuration. Default Release.

.PARAMETER Force
  Rebuild even if l5xgit.exe already exists -- use after updating the vendored
  source.

.PREREQS
  - .NET 10 SDK
  - Studio 5000 Logix Designer + Logix Designer SDK 2.2+, whose local NuGet
    folder supplies RockwellAutomation.LogixDesigner.CSClient

.EXAMPLE
  ./scripts/build_l5xgit.ps1
  ./scripts/build_l5xgit.ps1 -Force
#>
param(
    [string]$Configuration = "Release",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path $PSScriptRoot -Parent
$toolRoot = Join-Path $repoRoot "tools\ra-logix-designer-vcs-custom-tools"
$project = Join-Path $toolRoot "src\l5xgit\l5xgit.csproj"
$exe = Join-Path $toolRoot "artifacts\bin\$Configuration\l5xgit.exe"

if ((Test-Path $exe) -and -not $Force) {
    Write-Output $exe
    return
}

if (-not (Test-Path $project)) {
    throw "Vendored l5xgit source not found at $toolRoot. It is committed to this repository; check the clone is complete."
}

if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    throw "dotnet not found. Install the .NET 10 SDK: https://dotnet.microsoft.com/download/dotnet/10.0"
}
$sdks = & dotnet --list-sdks
if (-not ($sdks | Where-Object { $_ -match '^10\.' })) {
    throw "No .NET 10 SDK installed (found: $($sdks -join '; ')). Install it from https://dotnet.microsoft.com/download/dotnet/10.0"
}

# The Logix Designer SDK's package folder, as named in the vendored nuget.config.
# Without it restore fails with a bare "unable to find package" that does not
# say the SDK install is what is missing.
$sdkFeed = "C:\Users\Public\Documents\Studio 5000\Logix Designer SDK\dotnet"
if (-not (Test-Path $sdkFeed)) {
    throw "Logix Designer SDK package folder not found at '$sdkFeed'. Install Studio 5000 Logix Designer and the Logix Designer SDK 2.2+ first."
}

Write-Host "Building l5xgit ($Configuration) from $toolRoot ..."
& dotnet build $project -c $Configuration --nologo | Out-Host
if ($LASTEXITCODE -ne 0) {
    throw "dotnet build failed (exit $LASTEXITCODE)."
}
if (-not (Test-Path $exe)) {
    throw "Build reported success but $exe does not exist."
}
Write-Host "Built $exe"
Write-Output $exe
