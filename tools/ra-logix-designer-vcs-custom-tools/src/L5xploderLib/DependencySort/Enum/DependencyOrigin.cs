namespace L5xploderLib.DependencySort.Enum;

/// <summary>
/// How a dependency between two definitions was established.
/// </summary>
public enum DependencyOrigin
{
    /// <summary>
    /// Read from an explicit &lt;Dependencies&gt; block written by Logix Designer.
    /// </summary>
    Declared,

    /// <summary>
    /// Worked out from DataType references because nothing declared it. Best effort: it cannot see
    /// inside encoded definitions.
    /// </summary>
    Inferred,
}
