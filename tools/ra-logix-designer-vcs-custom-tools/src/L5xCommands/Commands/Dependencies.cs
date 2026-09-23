using System.CommandLine;
using System.Xml.Linq;
using L5xploderLib;
using L5xploderLib.DependencySort.Enum;
using L5xploderLib.DependencySort.Models;
using L5xploderLib.DependencySort.Services;

namespace L5xCommands.Commands;

public static class Dependencies
{
    public static Command Command
    {
        get
        {
            var command = new Command("dependencies", "Print the dependency graph of every Add-On Instruction that has dependencies");
            command.Aliases.Add("deps");

            var l5xOption = CommandOptions.L5xInputFile();
            l5xOption.Required = true;

            command.Options.Add(l5xOption);

            command.SetAction(parseResult =>
            {
                var l5xPath = parseResult.GetValue(l5xOption) ?? throw new ArgumentNullException(nameof(l5xOption));

                try
                {
                    Execute(l5xPath);
                    return 0;
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"Error: {ex.Message}");
                    return 1;
                }
            });

            return command;
        }
    }

    private static void Execute(string l5xFile)
    {
        var rootElement = XDocument.Load(l5xFile).Root
            ?? throw new InvalidDataException($"'{l5xFile}' is empty.");

        var aoiCount = rootElement
            .Element("Controller")?
            .Element("AddOnInstructionDefinitions")?
            .Elements()
            .Count() ?? 0;

        if (!L5xExportOptions.FromRootElement(rootElement).HasDependencies)
        {
            Console.WriteLine(
                "Note: this L5X was exported without the 'Dependencies' option, so dependencies are " +
                "inferred from parameter, local tag and member data types. Dependencies hidden inside " +
                "encoded Add-On Instructions cannot be seen.");
            Console.WriteLine();
        }

        var report = AoiDependencyReport.Build(rootElement);

        if (report.Any(aoi => ContainsInferred(aoi.Dependencies)))
        {
            Console.WriteLine(
                "Entries marked (inferred) were worked out from data type references because the " +
                "definition that uses them declares no dependencies. Unmarked entries were declared " +
                "by Logix Designer.");
            Console.WriteLine();
        }

        foreach (var aoi in report)
        {
            Console.WriteLine(aoi.Name);

            var mustPrecede = aoi.DirectAois
                .Concat(aoi.IndirectAois.Select(name => $"{name} (indirect)"));

            if (aoi.DirectAois.Count + aoi.IndirectAois.Count > 0)
            {
                Console.WriteLine($"  must be preceded by: {string.Join(", ", mustPrecede)}");
            }

            PrintTree(aoi.Dependencies, depth: 1);
            Console.WriteLine();
        }

        Console.WriteLine($"{report.Count} of {aoiCount} add-on instruction(s) have dependencies.");
    }

    private static bool ContainsInferred(IReadOnlyList<DependencyTree> dependencies) =>
        dependencies.Any(dependency =>
            dependency.Origin == DependencyOrigin.Inferred || ContainsInferred(dependency.Dependencies));

    private static void PrintTree(IReadOnlyList<DependencyTree> dependencies, int depth)
    {
        foreach (var dependency in dependencies)
        {
            var kind = dependency.IsAoi ? "AOI" : "DataType";
            var origin = dependency.Origin == DependencyOrigin.Inferred ? " (inferred)" : string.Empty;
            var truncated = dependency.Truncated ? " (shown above)" : string.Empty;

            Console.WriteLine($"{new string(' ', depth * 2)}- {dependency.Name} [{kind}]{origin}{truncated}");
            PrintTree(dependency.Dependencies, depth + 1);
        }
    }
}
