# Searches several real candidate locations rather than one guessed path
# (James, 2026-08-20: the original single hardcoded path didn't exist on his
# machine) -- NuGet always unpacks a restored package into the user's global
# packages cache regardless of which feed it came from, so that's checked
# first since ra-logix-designer-vcs-custom-tools already built successfully
# against this exact package.
$candidateRoots = @(
    (Join-Path $env:USERPROFILE ".nuget\packages\rockwellautomation.logixdesigner.csclient"),
    "C:\Users\Public\Documents\Studio 5000\Logix Designer SDK\dotnet",
    "C:\Program Files\Rockwell Software",
    "C:\Program Files (x86)\Rockwell Software",
    "C:\Program Files\Common Files\Rockwell",
    "C:\Program Files (x86)\Common Files\Rockwell"
)

$dll = $null
foreach ($root in $candidateRoots) {
    if (-not (Test-Path $root)) { continue }
    $found = Get-ChildItem -Path $root -Recurse -Filter "RockwellAutomation.LogixDesigner*.dll" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch "\\ref\\" } | Select-Object -First 1
    if ($found) { $dll = $found; break }
}

if (-not $dll) {
    Write-Host "DLL not found under any candidate root. Searched:"
    $candidateRoots | ForEach-Object { Write-Host "  $_" }
    Write-Host ""
    Write-Host "Find it directly instead, e.g.:"
    Write-Host '  Get-ChildItem -Path C:\ -Recurse -Filter "RockwellAutomation.LogixDesigner*.dll" -ErrorAction SilentlyContinue'
    exit 1
}
Write-Host "Loading: $($dll.FullName)"

$asm = [System.Reflection.Assembly]::LoadFrom($dll.FullName)
$type = $asm.GetTypes() | Where-Object { $_.Name -eq "LogixProject" }
if (-not $type) { Write-Host "LogixProject type not found in this assembly."; exit 1 }

Write-Host ""
Write-Host "=== All public methods on LogixProject ==="
$type.GetMethods([System.Reflection.BindingFlags]::Public -bor [System.Reflection.BindingFlags]::Instance -bor [System.Reflection.BindingFlags]::Static) |
    Sort-Object Name -Unique | ForEach-Object { Write-Host $_.Name }

Write-Host ""
Write-Host "=== Methods matching Memory/Verify/Build/Compile/Usage/Properties/Controller ==="
$type.GetMethods() | Where-Object { $_.Name -match "Memory|Verify|Build|Compile|Usage|Propert|Controller" } |
    Sort-Object Name -Unique | ForEach-Object { Write-Host $_.Name }
