<#
.SYNOPSIS
  Prints every public method on the installed Logix Designer SDK's
  LogixProject class, plus a filtered subset likely to include any
  offline compile/verify/build capability.

  Rewritten 2026-08-22 (James hit ReflectionTypeLoadException with the
  original raw Assembly.LoadFrom approach) -- that failure mode is almost
  certainly LoadFrom not resolving LogixProject's own dependencies
  (Protobuf/gRPC etc, which live in sibling NuGet package folders a bare
  PowerShell reflection call has no reason to search). This version
  builds a real, tiny console project (dump_ldsdk_api\) that references
  the SDK package properly, so .NET's own dependency resolution (via the
  generated deps.json) handles it instead of hand-rolled reflection.

.PREREQS
  - Logix Designer SDK NuGet package already restoring successfully on
    this machine (confirmed 2026-08-22: rockwellautomation.logixdesigner.
    csclient 2.2.1109, net10.0). If dump_ldsdk_api\DumpApi.csproj's pinned
    version doesn't match what's actually available, `dotnet build` will
    say so plainly -- update the PackageReference Version in that file.
  - .NET 10 SDK (same one l5xgit was built against).

.EXAMPLE
  ./dump_ldsdk_api.ps1
#>
$projectDir = Join-Path $PSScriptRoot "dump_ldsdk_api"
if (-not (Test-Path (Join-Path $projectDir "DumpApi.csproj"))) {
    Write-Error "Expected DumpApi.csproj under $projectDir -- run this from a checkout of the repo."
    exit 1
}

Push-Location $projectDir
try {
    dotnet run -c Release
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
