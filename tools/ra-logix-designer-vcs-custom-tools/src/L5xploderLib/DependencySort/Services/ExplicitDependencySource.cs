using System.Xml.Linq;
using L5xploderLib.DependencySort.Enum;
using L5xploderLib.DependencySort.Interfaces;

namespace L5xploderLib.DependencySort.Services;

/// <summary>
/// Reads the explicit &lt;Dependencies&gt; block that Logix Designer emits when an L5X is exported
/// with the Dependencies option (SDK 2.2 and newer). This is the only source that can see inside
/// encoded (source-protected) definitions, so it is authoritative wherever it is present. An empty
/// &lt;Dependencies /&gt; block is a positive statement that the definition has no dependencies.
/// </summary>
public sealed class ExplicitDependencySource : IDependencySource
{
    public DependencyOrigin Origin => DependencyOrigin.Declared;

    public bool CanResolve(XElement definition) => definition.Element("Dependencies") != null;

    /// <summary>
    /// The Dependency Type attribute is deliberately ignored. A DataType dependency is exactly the
    /// link that leads to Add-On Instructions nested inside a UDT, so dropping those entries would
    /// hide the indirect dependencies this source exists to expose.
    /// </summary>
    public IEnumerable<string> GetDependencyNames(XElement definition) =>
        definition.Element("Dependencies")?
            .Elements("Dependency")
            .Select(dependency => dependency.Attribute("Name")?.Value)
            .Where(name => !string.IsNullOrEmpty(name))
            .Select(name => name!)
        ?? [];
}
