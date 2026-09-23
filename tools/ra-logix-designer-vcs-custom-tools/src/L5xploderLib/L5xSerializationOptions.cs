using L5xploderLib.Enum;
using YamlDotNet.Serialization;

namespace L5xploderLib;

public sealed class L5xSerializationOptions
{
    /// <summary>
    /// Version of the exploded on-disk layout. Null when read from a directory that predates
    /// schema stamping; always written as <see cref="ExplodedSchemaVersion.Current"/>.
    /// Prefer <see cref="ExplodedSchemaVersion.From"/> over reading this directly.
    /// </summary>
    [YamlMember(Alias = "schema_version", Order = -1)]
    public int? SchemaVersion { get; init; }

    [YamlMember(Alias = "serialization_format")]
    public L5xSerializationFormat Format { get; init; }

    [YamlMember(Alias = "xml_attribute_per_line")]
    public bool PrettyXmlAttributes { get; init; }

    [YamlMember(Alias = "omit_export_date")]
    public bool OmitExportDate { get; init; }

    /// <summary>
    /// When true, bypasses the safety check for missing AOI dependency information and
    /// includes ordering hints (L5XGitPrevAOI) to preserve the original AOI order from
    /// Logix Designer. This is needed when the L5X was exported without the "Dependencies"
    /// export option, as encrypted/encoded AOIs may have invisible inter-AOI dependencies
    /// that can only be inferred from the original export ordering. This inferred implicit
    /// dependency info is imperfect and can cause issues when merging, removing or adding AOIs.
    /// </summary>
    [YamlMember(Alias = "unsafe_skip_dependency_check")]
    public bool UnsafeSkipDependencyCheck { get; init; }

    public static L5xSerializationOptions DefaultOptions => new()
    {
        PrettyXmlAttributes = false,
        Format = L5xSerializationFormat.Xml,
        OmitExportDate = true,
    };

    public void Save(string filePath)
    {
        var serializer = new SerializerBuilder()
            .WithIndentedSequences()
            .Build();

        var yaml = serializer.Serialize(WithCurrentSchemaVersion());
        File.WriteAllText(filePath, yaml);
    }

    private L5xSerializationOptions WithCurrentSchemaVersion() => new()
    {
        SchemaVersion = ExplodedSchemaVersion.Current.Value,
        Format = Format,
        PrettyXmlAttributes = PrettyXmlAttributes,
        OmitExportDate = OmitExportDate,
        UnsafeSkipDependencyCheck = UnsafeSkipDependencyCheck,
    };

    /// <summary>
    /// Loads the options stamped into an exploded directory, or null when the directory holds no
    /// exploded content. Every explode writes this file, so its absence means "nothing here"
    /// rather than "an old layout".
    /// </summary>
    public static L5xSerializationOptions? LoadFromExplodedDir(string explodedDir) =>
        LoadFromFile(Paths.GetOptionsFilePath(explodedDir));

    public static L5xSerializationOptions? LoadFromFile(string filePath)
    {
        if (!File.Exists(filePath))
        {
            return null;
        }

        var yaml = File.ReadAllText(filePath);
        var deserializer = new DeserializerBuilder()
            .IgnoreUnmatchedProperties()
            .Build();
        return deserializer.Deserialize<L5xSerializationOptions>(yaml);
    }
}