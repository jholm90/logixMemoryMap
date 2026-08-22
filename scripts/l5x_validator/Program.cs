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
// against known-bad AND known-good negative-control fixtures. Both bad
// fixtures must FAIL and the good one must come back ok, or this mechanism
// isn't actually catching what it needs to and no "ok" from `validate` mode
// can be trusted.
//
// CONFIRMED DEAD END on James's environment (2026-08-22): first self-test run
// showed both bad fixtures failing with the identical "Operation not
// supported on Logix Designer version 35.5" -- looked like a pass (both
// failed) but was actually a universal failure, not real ladder-logic
// detection. Adding a KNOWN_GOOD_ fixture caught it immediately: it failed
// with the exact same message. DefaultTarget does not work on Designer 35.5
// -- no public doc pins the exact minimum version, but the SDK client
// (2.2.1109) and the Designer application version independently, and 35.5
// is old relative to that SDK. The other two RequestedBuildTarget values
// (PhysicalController, EchoController) both need exactly what's been ruled
// out (a controller, Echo). This tool's Open/Build/timing harness is kept
// as reusable infrastructure, but `validate` mode should not be trusted
// until `selftest` genuinely passes against whatever mechanism replaces
// DefaultTarget.

using RockwellAutomation.LogixDesigner;
using RockwellAutomation.LogixDesigner.Logging;
using System.Diagnostics;

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
    string? convertLogPath = null;
    for (int a = 3; a < args.Length; a++)
    {
        if (args[a] == "--limit" && a + 1 < args.Length && int.TryParse(args[a + 1], out var l))
        { limit = l; a++; }
        else if (args[a] == "--convert-log" && a + 1 < args.Length)
        { convertLogPath = args[a + 1]; a++; }
    }

    return await RunValidateAsync(inputDir, logPath, limit, convertLogPath);
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
    Console.WriteLine("  dotnet run -- validate <inputDir> <logCsvPath> [--convert-log <path>] [--limit N]");
    Console.WriteLine("      Recursively finds every *.L5X under inputDir, opens each and runs");
    Console.WriteLine("      BuildAsync(DefaultTarget) -- offline compile, no download, no Echo --");
    Console.WriteLine("      logs pass/fail + real SDK error text to logCsvPath.");
    Console.WriteLine("      Resumable: files already logged 'ok' are skipped on re-run.");
    Console.WriteLine("      --convert-log points at an existing batch_l5x_to_acd.ps1 convert_log.csv:");
    Console.WriteLine("      when a file has a status=ok row there, this opens the already-converted");
    Console.WriteLine("      .ACD instead of re-importing the raw .L5X (saves the import/convert time");
    Console.WriteLine("      per file if that's where BuildAsync's cost actually is -- unconfirmed,");
    Console.WriteLine("      worth comparing a timed run with and without this flag on a small -Limit).");
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
    var badFiles = files.Where(f => Path.GetFileName(f).StartsWith("KNOWN_BAD_")).ToList();
    var goodFiles = files.Where(f => Path.GetFileName(f).StartsWith("KNOWN_GOOD_")).ToList();
    var unclassified = files.Except(badFiles).Except(goodFiles).ToList();
    if (files.Length == 0)
    {
        Console.WriteLine($"No .L5X files found in {fixturesDir}.");
        return 1;
    }
    if (unclassified.Count > 0)
    {
        Console.WriteLine("Fixture file(s) not prefixed KNOWN_BAD_ or KNOWN_GOOD_, skipping: " +
            string.Join(", ", unclassified.Select(Path.GetFileName)));
    }

    // Two-sided on purpose (James, 2026-08-22, after the first version's
    // false pass): BuildAsync failing on a known-bad file only means
    // something. It could mean the mechanism doesn't work AT ALL on this
    // Designer version -- the exact failure mode hit here (both fixtures
    // came back "Operation not supported on Logix Designer version 35.5",
    // identical text, nothing about ladder content) -- so a known-GOOD file
    // has to independently come back "ok" or this whole approach is a false
    // positive machine, not a validator.
    Console.WriteLine($"=== SELF-TEST: {badFiles.Count} known-bad + {goodFiles.Count} known-good fixture(s) ===");
    Console.WriteLine("Bad fixtures MUST come back FAILED. Good fixture(s) MUST come back ok.");
    Console.WriteLine("If a bad fixture fails with the SAME error text a good fixture also gets,");
    Console.WriteLine("that's not ladder-logic detection -- it's the mechanism failing on everything.");
    Console.WriteLine();

    if (!File.Exists(logPath))
        File.WriteAllText(logPath, "l5x_path,status,error_count,messages,elapsed_ms,opened_as_acd\n");

    bool ok = true;
    var allMessages = new List<(string file, bool expectedBad, ValidationResult result)>();
    int i = 0;
    int total = badFiles.Count + goodFiles.Count;
    foreach (var (f, expectedBad) in badFiles.Select(f => (f, true)).Concat(goodFiles.Select(f => (f, false))))
    {
        i++;
        Console.WriteLine($"[{i}/{total}] {Path.GetFileName(f)} (expect {(expectedBad ? "FAILED" : "ok")})");
        var result = await ValidateOneFileAsync(f, f);
        LogResult(logPath, result);
        allMessages.Add((f, expectedBad, result));
        Console.WriteLine($"  -> {result.Status} ({result.ErrorCount} error event(s), {FormatElapsed(result.ElapsedMs)})");
        foreach (var msg in result.Messages.Take(5))
            Console.WriteLine($"     {msg}");

        bool asExpected = expectedBad ? result.Status == "FAILED" : result.Status == "ok";
        if (!asExpected)
            ok = false;
    }

    // Specifically check for the false-positive pattern that bit the first
    // version of this tool: a bad fixture and a good fixture failing with
    // the exact same message text means the mechanism isn't discriminating
    // on content at all.
    var badMessages = allMessages.Where(m => m.expectedBad).SelectMany(m => m.result.Messages).ToHashSet();
    var goodFailures = allMessages.Where(m => !m.expectedBad && m.result.Status == "FAILED").ToList();
    bool sharedFailureText = goodFailures.Any(g => g.result.Messages.Any(gm => badMessages.Contains(gm)));

    Console.WriteLine();
    if (ok && badFiles.Count > 0 && goodFiles.Count > 0)
    {
        Console.WriteLine("SELF-TEST PASSED: bad fixture(s) FAILED, good fixture(s) came back ok.");
        Console.WriteLine("Open -> BuildAsync(DefaultTarget) is discriminating real ladder-logic errors,");
        Console.WriteLine("not just failing universally. Safe to proceed with validate mode.");
        return 0;
    }

    Console.WriteLine("SELF-TEST FAILED.");
    if (goodFiles.Count == 0)
        Console.WriteLine("  No KNOWN_GOOD_ fixture present -- can't rule out a universal-failure false positive.");
    if (sharedFailureText)
        Console.WriteLine("  A good fixture failed with the SAME message text as a bad one -- looks like a universal failure, not real detection.");
    Console.WriteLine("Do NOT trust 'ok' results from validate mode until this is understood.");
    return 1;
}

static async Task<int> RunValidateAsync(string inputDir, string logPath, int? limit, string? convertLogPath)
{
    if (!Directory.Exists(inputDir))
    {
        Console.WriteLine($"Input directory not found: {inputDir}");
        return 1;
    }

    var acdByL5x = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
    if (convertLogPath is not null)
    {
        if (!File.Exists(convertLogPath))
        {
            Console.WriteLine($"--convert-log path not found: {convertLogPath}");
            return 1;
        }
        int usable = 0;
        foreach (var line in File.ReadLines(convertLogPath).Skip(1))
        {
            var parts = line.Split(',');
            if (parts.Length >= 3 && parts[2] == "ok" && File.Exists(parts[1]))
            {
                acdByL5x[parts[0]] = parts[1];
                usable++;
            }
        }
        Console.WriteLine($"Loaded {usable} usable L5X->ACD mapping(s) from {convertLogPath}.");
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
        File.WriteAllText(logPath, "l5x_path,status,error_count,messages,elapsed_ms,opened_as_acd\n");
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
    var results = new List<ValidationResult>();
    var batchSw = Stopwatch.StartNew();
    foreach (var f in todo)
    {
        i++;
        string openPath = acdByL5x.TryGetValue(f, out var acdPath) ? acdPath : f;
        Console.WriteLine($"[{i}/{todo.Count}] {Path.GetFileName(f)}{(openPath != f ? " (opening existing .ACD)" : "")}");
        var result = await ValidateOneFileAsync(f, openPath);
        LogResult(logPath, result);
        results.Add(result);
        if (result.Status == "ok")
        {
            Console.WriteLine($"  -> ok ({FormatElapsed(result.ElapsedMs)})");
        }
        else
        {
            failCount++;
            Console.WriteLine($"  -> FAILED ({result.ErrorCount} error event(s), {FormatElapsed(result.ElapsedMs)})");
            foreach (var msg in result.Messages.Take(5))
                Console.WriteLine($"     {msg}");
        }
    }
    batchSw.Stop();

    Console.WriteLine();
    Console.WriteLine($"Done this pass. {todo.Count - failCount} ok, {failCount} FAILED. Full log: {logPath}");

    if (results.Count > 0)
    {
        double avgMs = results.Average(r => r.ElapsedMs);
        Console.WriteLine($"Batch: {FormatElapsed(batchSw.ElapsedMilliseconds)} total for {results.Count} file(s), avg {FormatElapsed((long)avgMs)}/file.");

        var acdResults = results.Where(r => r.OpenedAsAcd).ToList();
        var l5xResults = results.Where(r => !r.OpenedAsAcd).ToList();
        if (acdResults.Count > 0)
            Console.WriteLine($"  Opened from .ACD: {acdResults.Count} file(s), avg {FormatElapsed((long)acdResults.Average(r => r.ElapsedMs))}/file.");
        if (l5xResults.Count > 0)
            Console.WriteLine($"  Opened from .L5X: {l5xResults.Count} file(s), avg {FormatElapsed((long)l5xResults.Average(r => r.ElapsedMs))}/file.");
    }

    return 0;
}

static void LogResult(string logPath, ValidationResult r)
{
    string Escape(string s) => s.Replace(",", ";").Replace("\r", " ").Replace("\n", " ");
    string joined = Escape(string.Join(" | ", r.Messages));
    File.AppendAllText(logPath, $"{Escape(r.L5xPath)},{r.Status},{r.ErrorCount},{joined},{r.ElapsedMs},{r.OpenedAsAcd}\n");
}

static async Task<ValidationResult> ValidateOneFileAsync(string l5xPath, string openPath)
{
    var collector = new ErrorCollector();
    var result = new ValidationResult
    {
        L5xPath = l5xPath, Status = "FAILED", ErrorCount = 0, Messages = new List<string>(),
        ElapsedMs = 0, OpenedAsAcd = !string.Equals(openPath, l5xPath, StringComparison.OrdinalIgnoreCase),
    };

    var sw = Stopwatch.StartNew();
    try
    {
        var project = await LogixProject.OpenLogixProjectAsync(openPath, collector, CancellationToken.None);
        await project.BuildAsync(LogixProject.RequestedBuildTarget.DefaultTarget, CancellationToken.None);
        project.Dispose();
    }
    catch (Exception ex)
    {
        collector.Errors.Add((openPath, $"[exception] {ex.GetType().Name}: {ex.Message}"));
    }
    sw.Stop();

    result.ElapsedMs = sw.ElapsedMilliseconds;
    result.ErrorCount = collector.Errors.Count;
    result.Messages = collector.Errors.Select(e => $"{Path.GetFileName(e.file)}: {e.msg}").ToList();
    result.Status = result.ErrorCount == 0 ? "ok" : "FAILED";
    return result;
}

static string FormatElapsed(long ms) => ms >= 1000 ? $"{ms / 1000.0:F1}s" : $"{ms}ms";

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
    public required long ElapsedMs { get; set; }
    public required bool OpenedAsAcd { get; set; }
}
