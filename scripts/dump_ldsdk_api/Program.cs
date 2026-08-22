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

static IEnumerable<Type> SafeGetTypes(Assembly asm)
{
    try { return asm.GetTypes(); }
    catch (ReflectionTypeLoadException ex) { return ex.Types.Where(t => t != null)!; }
    catch { return Enumerable.Empty<Type>(); }
}

// Scan every DLL sitting alongside LogixProject's own assembly in the build
// output, not just that one assembly -- the SDK package ships several
// assemblies together (this DLL plus whatever it depends on), and a type
// like IOperationEvent or StdOutEventLogger, referenced by name in
// Rockwell's own reference code but not obviously part of LogixProject
// itself, could live in any of them.
string sdkDir = Path.GetDirectoryName(typeof(LogixProject).Assembly.Location)!;
var loadedAssemblies = new List<Assembly> { typeof(LogixProject).Assembly };
foreach (var dll in Directory.GetFiles(sdkDir, "*.dll"))
{
    if (loadedAssemblies.Any(a => string.Equals(a.Location, dll, StringComparison.OrdinalIgnoreCase)))
        continue;
    try { loadedAssemblies.Add(Assembly.LoadFrom(dll)); }
    catch { /* not a loadable managed assembly, or already loaded under a different identity -- skip */ }
}

var types = loadedAssemblies.SelectMany(SafeGetTypes).ToArray();
Console.WriteLine($"Scanned {loadedAssemblies.Count} assembl{(loadedAssemblies.Count == 1 ? "y" : "ies")} under {sdkDir}, found {types.Length} total types.");

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

static string Sig(MethodInfo m)
{
    string TypeName(Type t)
    {
        if (!t.IsGenericType) return t.Name;
        string baseName = t.Name.Substring(0, t.Name.IndexOf('`'));
        string args = string.Join(", ", t.GetGenericArguments().Select(TypeName));
        return $"{baseName}<{args}>";
    }
    string ps = string.Join(", ", m.GetParameters().Select(p => $"{TypeName(p.ParameterType)} {p.Name}"));
    string mods = m.IsStatic ? "static " : "";
    return $"{mods}{TypeName(m.ReturnType)} {m.Name}({ps})";
}

var allMethods = logixProjectType.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static)
    .Where(m => !m.IsSpecialName) // drop property get_/set_ noise
    .OrderBy(m => m.Name)
    .ToList();

Console.WriteLine("=== All public methods on LogixProject (full signatures) ===");
foreach (var m in allMethods)
    Console.WriteLine(Sig(m));

Console.WriteLine();
Console.WriteLine("=== Full signatures: BuildAsync, ChangeControllerModeAsync, ChangeControllerTypeAsync, GoOfflineAsync, GoOnlineAsync, ReadControllerModeAsync, OpenLogixProjectAsync, DownloadAsync, UploadAsync ===");
var namesOfInterest = new[] { "BuildAsync", "ChangeControllerModeAsync", "ChangeControllerTypeAsync", "GoOfflineAsync",
    "GoOnlineAsync", "ReadControllerModeAsync", "OpenLogixProjectAsync", "DownloadAsync", "UploadAsync" };
foreach (var m in allMethods.Where(m => namesOfInterest.Contains(m.Name)))
    Console.WriteLine(Sig(m));

Console.WriteLine();
Console.WriteLine("=== Nested types/enums on LogixProject (e.g. ControllerMode, RequestedControllerMode) ===");
foreach (var nested in logixProjectType.GetNestedTypes(BindingFlags.Public).OrderBy(t => t.Name))
{
    Console.WriteLine(nested.Name + (nested.IsEnum ? $" (enum: {string.Join(", ", Enum.GetNames(nested))})" : ""));
}

// BuildAsync (found 2026-08-22 -- RequestedBuildTarget.DefaultTarget looks
// like exactly the no-download, no-Echo offline compile/verify path James
// needs) returns bare Task with no result object, so however build errors
// get reported, it's either (a) an exception on failure, or (b) delivered
// through the SDK's own event-handler mechanism -- AddEventHandler(IOperationEvent)
// is a real method, and the ra-logix-cicd reference code passes a
// StdOutEventLogger to it that isn't defined in that repo's own source, so
// it must ship in the SDK itself. Dump both types so the actual validator
// tool can be built against real signatures instead of guessing.
Console.WriteLine();
Console.WriteLine("=== IOperationEvent interface members ===");
var opEventType = types.FirstOrDefault(t => t.Name == "IOperationEvent");
if (opEventType is null)
{
    Console.WriteLine("(not found in this assembly -- may live in a different assembly the SDK pulls in)");
}
else
{
    foreach (var m in opEventType.GetMethods().OrderBy(m => m.Name))
        Console.WriteLine(Sig(m));
}

Console.WriteLine();
Console.WriteLine("=== StdOutEventLogger (used by Rockwell's own ra-logix-cicd reference code) ===");
var loggerType = types.FirstOrDefault(t => t.Name == "StdOutEventLogger");
if (loggerType is null)
{
    Console.WriteLine("(not found in this assembly -- check other assemblies loaded alongside it)");
}
else
{
    Console.WriteLine($"Full name: {loggerType.FullName}");
    Console.WriteLine($"Implements: {string.Join(", ", loggerType.GetInterfaces().Select(i => i.Name))}");
    foreach (var ctor in loggerType.GetConstructors())
        Console.WriteLine($"  ctor({string.Join(", ", ctor.GetParameters().Select(p => $"{p.ParameterType.Name} {p.Name}"))})");
}

// Also list every type in the assembly whose name mentions Event/Error/Log
// /Result/Message -- BuildAsync's actual error-reporting shape (event
// stream vs. exception vs. a result object elsewhere) is the one open
// question left before this can be trusted for a real validation run.
Console.WriteLine();
Console.WriteLine("=== All types in this assembly matching Event|Error|Log|Result|Message|Diagnostic ===");
foreach (var t in types.Where(t => t.Name.Contains("Event") || t.Name.Contains("Error") || t.Name.Contains("Log")
             || t.Name.Contains("Result") || t.Name.Contains("Message") || t.Name.Contains("Diagnostic"))
         .OrderBy(t => t.Name))
{
    Console.WriteLine(t.FullName);
}

return 0;
