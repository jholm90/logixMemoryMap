$sdkDir = "C:\Users\Public\Documents\Studio 5000\Logix Designer SDK\dotnet"
$dll = Get-ChildItem -Path $sdkDir -Recurse -Filter "RockwellAutomation.LogixDesigner*.dll" |
    Where-Object { $_.FullName -notmatch "\\ref\\" } | Select-Object -First 1
if (-not $dll) { Write-Host "DLL not found under $sdkDir -- adjust path and retry."; exit 1 }
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
