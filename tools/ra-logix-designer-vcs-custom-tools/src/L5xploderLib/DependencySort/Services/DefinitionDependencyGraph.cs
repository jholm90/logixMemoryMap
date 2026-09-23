using System.Xml.Linq;
using L5xploderLib.DependencySort.Enum;
using L5xploderLib.DependencySort.Interfaces;
using L5xploderLib.DependencySort.Models;

namespace L5xploderLib.DependencySort.Services;

/// <summary>
/// A dependency graph covering every DataType and Add-On Instruction definition in a controller.
/// Both containers must be in one graph because UDTs and AOIs share a single Logix type-name
/// namespace and reference each other freely: an AOI can depend on another AOI purely through a UDT
/// member, and that indirection is invisible to anything that only looks at the AOI container.
/// </summary>
internal sealed class DefinitionDependencyGraph
{
    private sealed class Node
    {
        public required string Name { get; init; }
        public required bool IsAoi { get; init; }
        public required XElement Element { get; init; }

        /// <summary>How the edges in <see cref="Dependencies"/> were established.</summary>
        public DependencyOrigin Origin { get; set; }

        public List<Node> Dependencies { get; } = [];
    }

    private readonly Dictionary<string, Node> _nodes = new(StringComparer.Ordinal);

    private DefinitionDependencyGraph()
    {
    }

    /// <summary>
    /// The dependency sources in the order they are consulted: explicit information wherever Logix
    /// Designer recorded it, inference from type references everywhere else.
    /// </summary>
    public static IReadOnlyList<IDependencySource> DefaultSources { get; } =
    [
        new ExplicitDependencySource(),
        new TypeReferenceDependencySource(),
    ];

    /// <summary>
    /// Builds the graph from the controller's DataTypes and AddOnInstructionDefinitions. Each
    /// definition's edges come from the first supplied source that can resolve it, so a document
    /// that only partially carries explicit dependency information still resolves as well as it can.
    /// </summary>
    public static DefinitionDependencyGraph Build(XElement controller, IReadOnlyList<IDependencySource> sources)
    {
        var graph = new DefinitionDependencyGraph();

        graph.AddDefinitions(controller.Element("DataTypes"), isAoi: false);
        graph.AddDefinitions(controller.Element("AddOnInstructionDefinitions"), isAoi: true);

        foreach (var node in graph._nodes.Values)
        {
            var source = sources.FirstOrDefault(candidate => candidate.CanResolve(node.Element));
            if (source == null)
            {
                continue;
            }

            var linked = new HashSet<string>(StringComparer.Ordinal) { node.Name };
            node.Origin = source.Origin;

            foreach (var dependencyName in source.GetDependencyNames(node.Element))
            {
                // Names that are not in the graph are built-in Logix types and need no ordering.
                if (linked.Add(dependencyName) && graph._nodes.TryGetValue(dependencyName, out var dependency))
                {
                    node.Dependencies.Add(dependency);
                }
            }
        }

        return graph;
    }

    /// <summary>
    /// Every Add-On Instruction that must be defined before the named one, following the graph all
    /// the way through both DataTypes and other AOIs. Definition cycles cannot loop the walk because
    /// each definition is expanded at most once.
    /// </summary>
    public IReadOnlyList<string> GetRequiredAois(string aoiName)
    {
        var required = new List<string>();
        if (!_nodes.TryGetValue(aoiName, out var start))
        {
            return required;
        }

        var expanded = new HashSet<string>(StringComparer.Ordinal) { aoiName };
        var pending = new Queue<Node>();
        pending.Enqueue(start);

        while (pending.Count > 0)
        {
            foreach (var dependency in pending.Dequeue().Dependencies)
            {
                if (!expanded.Add(dependency.Name))
                {
                    continue;
                }

                if (dependency.IsAoi)
                {
                    required.Add(dependency.Name);
                }

                pending.Enqueue(dependency);
            }
        }

        return required;
    }

    /// <summary>
    /// The full dependency tree rooted at the named definition. Each definition is expanded at most
    /// once per tree; a repeat appears as a leaf flagged <see cref="DependencyTree.Truncated"/>, so
    /// shared subgraphs and cycles cannot make the tree explode.
    /// </summary>
    public IReadOnlyList<DependencyTree> Describe(string name) =>
        _nodes.TryGetValue(name, out var node)
            ? Expand(node, new HashSet<string>(StringComparer.Ordinal) { name })
            : [];

    private static List<DependencyTree> Expand(Node node, HashSet<string> expanded)
    {
        var children = new List<DependencyTree>();

        foreach (var dependency in node.Dependencies)
        {
            // The origin belongs to the edge, so it comes from the node that declared or implied it.
            children.Add(expanded.Add(dependency.Name)
                ? new DependencyTree(dependency.Name, dependency.IsAoi, node.Origin, Truncated: false, Expand(dependency, expanded))
                : new DependencyTree(dependency.Name, dependency.IsAoi, node.Origin, dependency.Dependencies.Count > 0, []));
        }

        return children;
    }

    private void AddDefinitions(XElement? container, bool isAoi)
    {
        if (container == null)
        {
            return;
        }

        foreach (var element in container.Elements())
        {
            var name = element.Attribute("Name")?.Value;
            if (!string.IsNullOrEmpty(name) && !_nodes.ContainsKey(name))
            {
                _nodes[name] = new Node { Name = name, IsAoi = isAoi, Element = element };
            }
        }
    }
}
