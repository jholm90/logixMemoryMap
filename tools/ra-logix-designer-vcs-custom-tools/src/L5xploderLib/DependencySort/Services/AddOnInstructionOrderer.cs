using System.Xml.Linq;

namespace L5xploderLib.DependencySort.Services;

/// <summary>
/// Reorders an assembled L5X document's AddOnInstructionDefinitions so that every Add-On Instruction
/// appears after the instructions it depends on, which is what Logix Designer requires on import.
///
/// This runs over the whole document rather than over the AOI container alone, because a dependency
/// between two AOIs can be indirect: AOI A takes a UDT parameter, and that UDT has a member
/// of AOI C's type. Looking only at the AOI container misses A depending on C entirely.
///
/// Two concerns are kept apart:
/// <list type="bullet">
/// <item>which AOI must precede which — <see cref="DefinitionDependencyGraph"/>, resolved across the
/// controller's DataTypes and AOIs so indirect dependencies are included;</item>
/// <item>which of the many valid orders to emit — <see cref="OriginalAoiOrder"/>, so the export order
/// of the source project survives wherever the dependency graph leaves a choice.</item>
/// </list>
/// The dependency graph always wins; the original order only breaks ties. That matters because the
/// original order also encodes ordering constraints we cannot see, such as those inside encoded AOIs
/// in a project exported without dependency information.
/// </summary>
public static class AddOnInstructionOrderer
{
    public static void Order(XElement rootElement)
    {
        var controller = rootElement.Element("Controller");
        var aoiContainer = controller?.Element("AddOnInstructionDefinitions");
        if (aoiContainer == null)
        {
            return;
        }

        var aois = new List<(string Name, XElement Element)>();
        var unnamed = new List<XElement>();

        foreach (var element in aoiContainer.Elements())
        {
            var name = element.Attribute("Name")?.Value;
            if (string.IsNullOrEmpty(name))
            {
                // Nothing can reference an AOI with no name, so it cannot participate in the graph.
                unnamed.Add(element);
            }
            else
            {
                aois.Add((name, element));
            }
        }

        var graph = DefinitionDependencyGraph.Build(controller!, DefinitionDependencyGraph.DefaultSources);
        var preferredOrder = OriginalAoiOrder.Resolve(aois);
        var ordered = SortByDependencies(aois, graph, preferredOrder);

        // The ordering hints are our own scaffolding and shouldn't reach the output L5X.
        foreach (var (_, element) in aois)
        {
            element.Element(Constants.OriginalOrderingHintElement)?.Remove();
        }

        // Detach then re-attach, so any comment or whitespace nodes in the container survive.
        foreach (var (_, element) in aois)
        {
            element.Remove();
        }
        foreach (var element in unnamed)
        {
            element.Remove();
        }

        aoiContainer.Add(ordered);
        aoiContainer.Add(unnamed);
    }

    /// <summary>
    /// Kahn's algorithm over the AOI-only projection of the dependency graph, taking the
    /// lowest-numbered preferred position among the instructions whose dependencies are all placed.
    /// The projection uses each instruction's full transitive requirement set, so an AOI reached only
    /// through a DataType, or only through another AOI, constrains the order exactly like a declared
    /// one. Preferred positions are unique, so the result is deterministic.
    /// </summary>
    private static List<XElement> SortByDependencies(
        IReadOnlyList<(string Name, XElement Element)> aois,
        DefinitionDependencyGraph graph,
        IReadOnlyDictionary<XElement, int> preferredOrder)
    {
        var byName = new Dictionary<string, XElement>(StringComparer.Ordinal);
        var dependents = new Dictionary<XElement, List<XElement>>();
        var unplacedDependencies = new Dictionary<XElement, int>();

        foreach (var (name, element) in aois)
        {
            byName.TryAdd(name, element);
            dependents[element] = [];
            unplacedDependencies[element] = 0;
        }

        foreach (var (name, element) in aois)
        {
            foreach (var requiredName in graph.GetRequiredAois(name))
            {
                if (byName.TryGetValue(requiredName, out var required) && required != element)
                {
                    dependents[required].Add(element);
                    unplacedDependencies[element]++;
                }
            }
        }

        int Preference(XElement element) => preferredOrder.TryGetValue(element, out var position) ? position : int.MaxValue;

        var ready = new PriorityQueue<XElement, int>();
        foreach (var (element, count) in unplacedDependencies)
        {
            if (count == 0)
            {
                ready.Enqueue(element, Preference(element));
            }
        }

        var ordered = new List<XElement>(aois.Count);
        while (ready.TryDequeue(out var element, out _))
        {
            ordered.Add(element);

            foreach (var dependent in dependents[element])
            {
                if (--unplacedDependencies[dependent] == 0)
                {
                    ready.Enqueue(dependent, Preference(dependent));
                }
            }
        }

        if (ordered.Count != aois.Count)
        {
            var cyclic = aois
                .Where(aoi => unplacedDependencies[aoi.Element] > 0)
                .Select(aoi => aoi.Name);

            throw new InvalidOperationException(
                "Cyclic dependency detected among add-on instructions: " + string.Join(", ", cyclic) + ".");
        }

        return ordered;
    }
}
