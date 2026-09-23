using System.Xml.Linq;
using L5xploderLib.DependencySort.Models;

namespace L5xploderLib.DependencySort.Services;

/// <summary>
/// Describes the dependencies of the Add-On Instructions in a loaded L5X document, using the same
/// resolution <see cref="AddOnInstructionOrderer"/> orders by, so the report explains the order the
/// tools actually produce. Does not modify the document.
/// </summary>
public static class AoiDependencyReport
{
    /// <summary>
    /// Every Add-On Instruction that depends on something, in document order. Instructions with no
    /// dependencies at all are omitted.
    /// </summary>
    public static IReadOnlyList<AoiDependencies> Build(XElement rootElement)
    {
        var controller = rootElement.Element("Controller");
        var aoiContainer = controller?.Element("AddOnInstructionDefinitions");
        if (aoiContainer == null)
        {
            return [];
        }

        var graph = DefinitionDependencyGraph.Build(controller!, DefinitionDependencyGraph.DefaultSources);
        var report = new List<AoiDependencies>();

        foreach (var element in aoiContainer.Elements())
        {
            var name = element.Attribute("Name")?.Value;
            if (string.IsNullOrEmpty(name))
            {
                continue;
            }

            var dependencies = graph.Describe(name);
            if (dependencies.Count == 0)
            {
                continue;
            }

            var direct = dependencies
                .Where(dependency => dependency.IsAoi)
                .Select(dependency => dependency.Name)
                .ToList();

            var indirect = graph.GetRequiredAois(name)
                .Except(direct, StringComparer.Ordinal)
                .ToList();

            report.Add(new AoiDependencies(name, dependencies, direct, indirect));
        }

        return report;
    }
}
