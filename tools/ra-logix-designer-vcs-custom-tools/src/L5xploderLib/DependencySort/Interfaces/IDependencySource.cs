using System.Xml.Linq;
using L5xploderLib.DependencySort.Enum;

namespace L5xploderLib.DependencySort.Interfaces;

/// <summary>
/// Supplies the names of the definitions that a DataType or Add-On Instruction definition depends
/// on. Different L5X exports carry dependency information in different forms, so each form is a
/// separate implementation and the graph builder picks the first one that applies per definition.
/// </summary>
public interface IDependencySource
{
    /// <summary>
    /// How much to trust what this source reports.
    /// </summary>
    DependencyOrigin Origin { get; }

    /// <summary>
    /// Whether this source can determine the dependencies of the supplied definition. A single
    /// document can mix definitions that carry explicit dependency information with ones that do
    /// not, so this is asked per definition rather than per document.
    /// </summary>
    bool CanResolve(XElement definition);

    /// <summary>
    /// The names of the definitions the supplied definition depends on. Names may repeat, may refer
    /// to built-in types, and may refer to either a DataType or an Add-On Instruction.
    /// </summary>
    IEnumerable<string> GetDependencyNames(XElement definition);
}
