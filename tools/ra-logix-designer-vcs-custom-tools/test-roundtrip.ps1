param(
    [Parameter(Mandatory)]
    [string]$acd
)
Set-PSDebug -Trace 1

try {
    if (-not (Test-Path -Path $acd)) { throw "The specified ACD file does not exist: $acd" }

    $root = Split-Path -Path $acd -Parent
    $originalAcdPath = (Get-Item -Path $acd).FullName
    $baseName = (Get-Item -Path $acd).BaseName
    $acd2l5xPath = Join-Path $root "ACD2L5X\$($baseName).L5X"
    $explodedDir = Join-Path $root 'Exploded'
    $reimplodedPath = Join-Path $root "Reimploded\$($baseName).L5X"
    $roundtripAcdPath = Join-Path $root "$($baseName)RoundTrip.ACD"

    # 1) ACD2L5X  — SDK-convert the original ACD to L5X
    dotnet run --project '.\src\l5xgit\l5xgit.csproj' -- acd2l5x  --acd $originalAcdPath  --l5x $acd2l5xPath

    # 2) Exploded — explode that L5X into the multi-file structure
    dotnet run --project '.\src\l5xgit\l5xgit.csproj' -- explode --l5x $acd2l5xPath --dir $explodedDir --force

    # 3) Reimploded — implode back into a single L5X
    dotnet run --project '.\src\l5xgit\l5xgit.csproj' -- implode --dir $explodedDir --l5x $reimplodedPath --force

    # 4) Roundtrip ACD
    dotnet run --project '.\src\l5xgit\l5xgit.csproj' -- l5x2acd --l5x $reimplodedPath --acd $roundtripAcdPath
} finally {
    Set-PSDebug -Trace 0
}