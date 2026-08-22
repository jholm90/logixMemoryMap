// Batch L5X validator, no-download version (James, 2026-08-22: "I dont have
// echo. I'm not buying echo. I told you this is a no-download project from
// the start"). The first version of this tool used FactoryTalk Logix Echo +
// Download, matching Rockwell's own CI/CD reference pattern -- scrapped
// entirely once that constraint was restated.
//
// Real path found via scripts/dump_ldsdk_api.ps1 (run against James's actual
// installed SDK, 2026-08-22): LogixProject.BuildAsync(RequestedBuildTarget
// target, CancellationToken) exists, and RequestedBuildTarget has a
// DefaultTarget value alongside PhysicalController/EchoController --
// DefaultTarget needs no comm path, no controller, no Echo. Build errors are
// NOT returned from BuildAsync (it's a bare Task) -- they come through the
// SDK's own event-handler mechanism: IOperationEvent.Error(projectFile, msg),
// registered via the operationEventHandler parameter on OpenLogixProjectAsync.
//
// PREREQ before trusting any "ok" result: run `selftest` first. It runs this
// exact Open -> BuildAsync(DefaultTarget) -> check-for-Error-events pipeline
// against two files this project already knows are broken (the real pre-fix
// CPS array-subscript bug and the T_ADD-called-as-native-instruction bug
// James caught by hand). Both must come back FAILED with real error text, or
// this mechanism isn't actually catching what it needs to and no "ok" from
// `validate` mode can be trusted.

using RockwellAutomation.LogixDesigner;
using RockwellAutomation.LogixDesigner.Logging;

if (args.Length == 0)
{
    PrintUsage();
    return 1;
}

string mode = args[0].ToLowerInvariant();

if (mode == "selftest")
{
    string selfTestLog = args.Length > 1 ? args[1] : Path.Combine(AppContext.BaseDirectory, "selftest_log.csv");
    return await RunSelfTestAsync(selfTestLog);
}
else if (mode == "validate")
{
    if (args.Length < 3)
    {
        PrintUsage();
        return 1;
    }
    string inputDir = args[1];
    string logPath = args[2];
    int? limit = null;
    if (args.Length > 3 && args[3] == "--limit" && args.Length > 4 && int.TryParse(args[4], out var l))
        limit = l;

    return await RunValidateAsync(inputDir, logPath, limit);
}
else
{
    PrintUsage();
    return 1;
}

static void PrintUsage()
{
    Console.WriteLine("Usage:");
    Console.WriteLine("  dotnet run -- selftest [logCsvPath]");
    Console.WriteLine("      Runs the validation pipeline against two known-bad negative-control");
    Console.WriteLine("      fixtures. RUN THIS FIRST. Both must come back FAILED with real error");
    Console.WriteLine("      text, or 'ok' results from validate mode can't be trusted.");
    Console.WriteLine();
    Console.WriteLine("  dotnet run -- validate <inputDir> <logCsvPath> [--limit N]");
    Console.WriteLine("      Recursively finds every *.L5X under inputDir, opens each and runs");
    Console.WriteLine("      BuildAsync(DefaultTarget) -- offline compile, no download, no Echo --");
    Console.WriteLine("      logs pass/fail + real SDK error text to logCsvPath.");
    Console.WriteLine("      Resumable: files already logged 'ok' are skipped on re-run.");
}

static async Task<int> RunSelfTestAsync(string logPath)
{
    string fixturesDir = Path.Combine(AppContext.BaseDirectory, "negative_control_fixtures");
    if (!Directory.Exists(fixturesDir))
        fixturesDir = Path.Combine(Directory.GetCurrentDirectory(), "negative_control_fixtures");
    if (!Directory.Exists(fixturesDir))
    {
        Console.WriteLine($"Could not find negative_control_fixtures/ (looked under {AppContext.BaseDirectory} and {Directory.GetCurrentDirectory()}).");
        return 1;
    }

    var files = Directory.GetFiles(fixturesDir, "*.L5X");
    if (files.Length == 0)
    {
        Console.WriteLine($"No .L5X files found in {fixturesDir}.");
        return 1;
    }

    Console.WriteLine($"=== SELF-TEST: validating {files.Length} known-bad fixture(s) ===");
    Console.WriteLine("Every one of these MUST come back FAILED. If any comes back 'ok', this");
    Console.WriteLine("tool is not catching what it's meant to -- stop before running validate.");
    Console.WriteLine();

    if (!File.Exists(logPath))
        File.WriteAllText(logPath, "l5x_path,status,error_count,messages\n");

    bool allFailed = true;
    int i = 0;
    foreach (var f in files)
    {
        i++;
        Console.WriteLine($"[{i}/{files.Length}] {Path.GetFileName(f)}");
        var result = await ValidateOneFileAsync(f);
        LogResult(logPath, result);
        Console.WriteLine($"  -> {result.Status} ({result.ErrorCount} error event(s))");
        foreach (var msg in result.Messages.Take(5))
            Console.WriteLine($"     {msg}");
        if (result.Status == "ok")
            allFailed = false;
    }

    Console.WriteLine();
    if (allFailed)
    {
        Console.WriteLine("SELF-TEST PASSED: both known-bad fixtures came back FAILED.");
        Console.WriteLine("Open -> BuildAsync(DefaultTarget) is catching this class of error.");
        Console.WriteLine("Safe to proceed with: dotnet run -- validate <inputDir> <logCsvPath>");
        return 0;
    }
    else
    {
        Console.WriteLine("SELF-TEST FAILED: at least one known-bad fixture came back 'ok'.");
        Console.WriteLine("Do NOT trust 'ok' results from validate mode until this is understood.");
        return 1;
    }
}

static async Task<int> RunValidateAsync(string inputDir, string logPath, int? limit)
{
    if (!Directory.Exists(inputDir))
    {
        Console.WriteLine($"Input directory not found: {inputDir}");
        return 1;
    }

    var alreadyDone = new HashSet<string>();
    if (File.Exists(logPath))
    {
        foreach (var line in File.ReadLines(logPath).Skip(1))
        {
            var parts = line.Split(',');
            if (parts.Length >= 2 && parts[1] == "ok")
                alreadyDone.Add(parts[0]);
        }
    }
    else
    {
        File.WriteAllText(logPath, "l5x_path,status,error_count,messages\n");
    }

    var allFiles = Directory.GetFiles(inputDir, "*.L5X", SearchOption.AllDirectories);
    var todo = allFiles.Where(f => !alreadyDone.Contains(f)).ToList();
    if (limit.HasValue)
        todo = todo.Take(limit.Value).ToList();

    Console.WriteLine($"Found {allFiles.Length} L5X file(s) under {inputDir}; {alreadyDone.Count} already validated ok; {todo.Count} to run this pass.");
    Console.WriteLine("Ctrl+C is safe at any point -- only fully-completed files are logged.");
    Console.WriteLine();

    int i = 0;
    int failCount = 0;
    foreach (var f in todo)
    {
        i++;
        Console.WriteLine($"[{i}/{todo.Count}] {Path.GetFileName(f)}");
        var result = await ValidateOneFileAsync(f);
        LogResult(logPath, result);
        if (result.Status == "ok")
        {
            Console.WriteLine("  -> ok");
        }
        else
        {
            failCount++;
            Console.WriteLine($"  -> FAILED ({result.ErrorCount} error event(s))");
            foreach (var msg in result.Messages.Take(5))
                Console.WriteLine($"     {msg}");
        }
    }

    Console.WriteLine();
    Console.WriteLine($"Done this pass. {todo.Count - failCount} ok, {failCount} FAILED. Full log: {logPath}");
    return 0;
}

static void LogResult(string logPath, ValidationResult r)
{
    string Escape(string s) => s.Replace(",", ";").Replace("\r", " ").Replace("\n", " ");
    string joined = Escape(string.Join(" | ", r.Messages));
    File.AppendAllText(logPath, $"{Escape(r.L5xPath)},{r.Status},{r.ErrorCount},{joined}\n");
}

static async Task<ValidationResult> ValidateOneFileAsync(string l5xPath)
{
    var collector = new ErrorCollector();
    var result = new ValidationResult { L5xPath = l5xPath, Status = "FAILED", ErrorCount = 0, Messages = new List<string>() };

    try
    {
        var project = await LogixProject.OpenLogixProjectAsync(l5xPath, collector, CancellationToken.None);
        await project.BuildAsync(LogixProject.RequestedBuildTarget.DefaultTarget, CancellationToken.None);
        project.Dispose();
    }
    catch (Exception ex)
    {
        collector.Errors.Add((l5xPath, $"[exception] {ex.GetType().Name}: {ex.Message}"));
    }

    result.ErrorCount = collector.Errors.Count;
    result.Messages = collector.Errors.Select(e => $"{Path.GetFileName(e.file)}: {e.msg}").ToList();
    result.Status = result.ErrorCount == 0 ? "ok" : "FAILED";
    return result;
}

class ErrorCollector : IOperationEvent
{
    public List<(string file, string msg)> Errors { get; } = new();

    public void Error(string projectFile, string msg) => Errors.Add((projectFile, msg));
    public void Status(string projectFile, string msg) { }
    public void Progress(string projectFile, int value) { }
    public void LogError(bool logErrorNew) { }
    public void LogProgress(bool logProgressNew) { }
    public void LogStatus(bool logStatusNew) { }
}

class ValidationResult
{
    public required string L5xPath { get; set; }
    public required string Status { get; set; }
    public required int ErrorCount { get; set; }
    public required List<string> Messages { get; set; }
}
