namespace L5xploderLib.DependencySort.Models;

/// <summary>
/// One Add-On Instruction's dependencies: the tree as declared, plus the AOIs that tree resolves to.
/// </summary>
/// <param name="DirectAois">AOIs this instruction declares a dependency on itself.</param>
/// <param name="IndirectAois">
/// The remaining AOIs that must still be defined first, reached through a DataType or through
/// another AOI. These are the ones a naive AOI-only sort misses, and they constrain the import order
/// just as much as the direct ones.
/// </param>
public sealed record AoiDependencies(
    string Name,
    IReadOnlyList<DependencyTree> Dependencies,
    IReadOnlyList<string> DirectAois,
    IReadOnlyList<string> IndirectAois);
