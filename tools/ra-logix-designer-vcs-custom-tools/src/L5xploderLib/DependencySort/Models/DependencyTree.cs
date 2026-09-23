using L5xploderLib.DependencySort.Enum;

namespace L5xploderLib.DependencySort.Models;

/// <summary>
/// A definition an Add-On Instruction depends on, and the dependencies that definition brings in
/// turn. Expanding a DataType node is what reveals the AOIs reached only indirectly.
/// </summary>
/// <param name="Origin">How the edge that leads to this definition was established.</param>
/// <param name="Truncated">
/// True when this definition has dependencies of its own that are not repeated here because they
/// were already shown elsewhere in the same tree.
/// </param>
public sealed record DependencyTree(
    string Name,
    bool IsAoi,
    DependencyOrigin Origin,
    bool Truncated,
    IReadOnlyList<DependencyTree> Dependencies);
