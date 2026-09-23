using System.Xml.Linq;
using L5xploderLib.DependencySort.Enum;
using L5xploderLib.DependencySort.Interfaces;

namespace L5xploderLib.DependencySort.Services;

/// <summary>
/// Infers dependencies from the DataType attribute of a definition's members, parameters and local
/// tags, for L5X files exported without the Dependencies option. It cannot see inside encoded
/// definitions, which is why <see cref="L5xExploder"/> refuses such files unless the caller opts
/// out with the unsafe-skip-dependency-check flag.
/// </summary>
public sealed class TypeReferenceDependencySource : IDependencySource
{
    private static readonly (string Container, string Child)[] TypedChildren =
    [
        ("Members", "Member"),
        ("Parameters", "Parameter"),
        ("LocalTags", "LocalTag"),
    ];

    public DependencyOrigin Origin => DependencyOrigin.Inferred;

    public bool CanResolve(XElement definition) => true;

    public IEnumerable<string> GetDependencyNames(XElement definition) =>
        TypedChildren
            .SelectMany(typed => definition.Element(typed.Container)?.Elements(typed.Child) ?? [])
            .Select(child => child.Attribute("DataType")?.Value)
            .Where(name => !string.IsNullOrEmpty(name))
            .Select(name => name!);
}
