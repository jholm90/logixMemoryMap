namespace L5xploderLib;

/// <summary>
/// Version of the on-disk layout produced by <see cref="L5xExploder"/>, stamped into the exploded
/// directory's options file so that a tool built against an older layout refuses to implode a newer
/// one instead of silently producing an incorrect L5X. Imploding older layouts stays supported.
/// </summary>
public readonly record struct ExplodedSchemaVersion(int Value)
{
    /// <summary>
    /// Increment this whenever the exploded layout changes in a way that a tool built against a
    /// previous version would implode incorrectly.
    /// 1: Original layout (unstamped).
    /// 2: Structured text routines persist their Routine element (comments/descriptions) alongside the .st files.
    /// </summary>
    public static ExplodedSchemaVersion Current => new(2);

    /// <summary>
    /// Version assumed for exploded directories written before the schema version was stamped.
    /// </summary>
    public static ExplodedSchemaVersion Unstamped => new(1);

    /// <summary>
    /// The single place that applies the "an absent stamp means <see cref="Unstamped"/>" rule.
    /// </summary>
    public static ExplodedSchemaVersion From(L5xSerializationOptions options) =>
        new(options.SchemaVersion ?? Unstamped.Value);

    public bool IsSupported => Value <= Current.Value;

    public bool IsOlderThanCurrent => Value < Current.Value;

    /// <summary>
    /// Throws when this layout was written by a tool using a newer schema than this one understands.
    /// </summary>
    public void EnsureSupported(string explodedSubDir)
    {
        if (IsSupported)
        {
            return;
        }

        throw new InvalidDataException(
            $"The exploded directory '{explodedSubDir}' was created using schema version {Value}, " +
            $"but the version of this tool you are running only supports up to version {Current.Value}. " +
            "Imploding it may produce an incorrect L5X." +
            Environment.NewLine +
            "Update to a matching version of this tool.");
    }

    public override string ToString() => Value.ToString();
}
