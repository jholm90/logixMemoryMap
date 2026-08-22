// Replaces the old PowerShell Assembly.LoadFrom approach (James, 2026-08-22):
// that threw ReflectionTypeLoadException, almost certainly because loading
// the raw NuGet-cache DLL directly doesn't resolve ITS OWN dependencies
// (Google.Protobuf, gRPC, etc. -- see LogixDesigner.cs's own `using
// Google.Protobuf;`), which live in sibling package folders that plain
// PowerShell reflection has no reason to search. A real project reference
// (this file) resolves the full dependency graph correctly at build time
// via the generated deps.json, then a compile-time `typeof(LogixProject)`
// needs no runtime assembly-loading gymnastics at all.
//
// Purpose: answer definitively whether the installed Logix Designer SDK
// exposes any offline compile/verify/build method on LogixProject that
// needs no communication path and no controller -- James has ruled out
// FactoryTalk Logix Echo (won't buy it) and this is a no-download project,
// so DownloadAsync (which the ra-logix-cicd reference CI/CD pattern relies
// on to force a real compile) is off the table too. This is the check for
// whether something else on LogixProject already does that job offline.

using System.Reflection;
using RockwellAutomation.LogixDesigner;

Type[] types;
try
{
    types = typeof(LogixProject).Assembly.GetTypes();
}
catch (ReflectionTypeLoadException ex)
{
    Console.WriteLine("GetTypes() partially failed -- some referenced type couldn't load. Loader exceptions:");
    foreach (var le in ex.LoaderExceptions)
        Console.WriteLine($"  - {le?.Message}");
    Console.WriteLine();
    Console.WriteLine("Continuing with the types that DID load successfully (ex.Types, nulls filtered):");
    types = ex.Types.Where(t => t != null).Cast<Type>().ToArray();
}

var logixProjectType = types.FirstOrDefault(t => t.Name == "LogixProject");
if (logixProjectType is null)
{
    Console.WriteLine("LogixProject type not found even after fallback. Assembly location:");
    Console.WriteLine($"  {typeof(LogixProject).Assembly.Location}");
    return 1;
}

Console.WriteLine($"Assembly: {logixProjectType.Assembly.Location}");
Console.WriteLine($"Assembly version: {logixProjectType.Assembly.GetName().Version}");
Console.WriteLine();

var methods = logixProjectType.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static)
    .Select(m => m.Name)
    .Distinct()
    .OrderBy(n => n)
    .ToList();

Console.WriteLine("=== All public methods on LogixProject ===");
foreach (var name in methods)
    Console.WriteLine(name);

Console.WriteLine();
Console.WriteLine("=== Methods matching Memory|Verify|Build|Compile|Usage|Propert|Controller|Error|Check|Offline ===");
var filtered = methods.Where(n =>
        n.Contains("Memory", StringComparison.OrdinalIgnoreCase) ||
        n.Contains("Verify", StringComparison.OrdinalIgnoreCase) ||
        n.Contains("Build", StringComparison.OrdinalIgnoreCase) ||
        n.Contains("Compile", StringComparison.OrdinalIgnoreCase) ||
        n.Contains("Usage", StringComparison.OrdinalIgnoreCase) ||
        n.Contains("Propert", StringComparison.OrdinalIgnoreCase) ||
        n.Contains("Controller", StringComparison.OrdinalIgnoreCase) ||
        n.Contains("Error", StringComparison.OrdinalIgnoreCase) ||
        n.Contains("Check", StringComparison.OrdinalIgnoreCase) ||
        n.Contains("Offline", StringComparison.OrdinalIgnoreCase))
    .ToList();
foreach (var name in filtered)
    Console.WriteLine(name);

Console.WriteLine();
Console.WriteLine("=== Nested types/enums on LogixProject (e.g. ControllerMode, RequestedControllerMode) ===");
foreach (var nested in logixProjectType.GetNestedTypes(BindingFlags.Public).OrderBy(t => t.Name))
{
    Console.WriteLine(nested.Name + (nested.IsEnum ? $" (enum: {string.Join(", ", Enum.GetNames(nested))})" : ""));
}

return 0;
