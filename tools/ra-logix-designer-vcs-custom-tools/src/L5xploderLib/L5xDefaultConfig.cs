using System.Xml.Linq;
using L5xploderLib.Serialization;
using L5xploderLib.Transformation;

namespace L5xploderLib;

public static class L5xDefaultConfig
{
    public static IEnumerable<L5xExploderConfig> DefaultConfig { get; } =
    [
        new L5xExploderConfig
        {
            XPath = @"Controller/DataTypes/*",
            FolderGenerator = element => "DataTypes",
            BaseFileNameGenerator = DefaultNameGenerator,
        },
        new L5xExploderConfig
        {
            XPath = @"Controller/Modules/*",
            FolderGenerator = element => "Modules",
            BaseFileNameGenerator = DefaultNameGenerator,
            SortFunction = SortModules,
        },
        new L5xExploderConfig
        {
            XPath = @"Controller/AddOnInstructionDefinitions/*",
            FolderGenerator = element => "AddOnInstructionDefinitions",
            BaseFileNameGenerator = DefaultNameGenerator,
            // No SortFunction: AOI ordering depends on DataTypes too, so L5xImploder resolves it
            // over the whole document via AddOnInstructionOrderer once every config has run.
            PreExplodeTransform = AddOriginalOrderingHints,
            ChildConfigs =
            [
                // We purposely do not break apart the Parameters and Local Tags because
                // the order they are in can impact the packing of structs. We'd rather not
                // potentially mutate the original order of these elements. This is a problem
                // because instances of this AOI may have stored values persisted elsewhere in
                // the L5x which no longer match the order of the parameters/tags in the AOI definition.
                // Not breaking them apart does not solve the problem if the AOI is manually modified,
                // but it does prevent this tool itself from breaking this parameter/tag struct.
                //
                // new L5xExploderConfig
                // {
                //     XPath = @"Parameters/*",
                //     FolderGenerator = element => "Parameters",
                //     BaseFileNameGenerator = DefaultNameGenerator,
                // },
                // new L5xExploderConfig
                // {
                //     XPath = @"LocalTags/*",
                //     FolderGenerator = element => "LocalTags",
                //     BaseFileNameGenerator = DefaultNameGenerator,
                // },
                new L5xExploderConfig
                {
                    XPath = @"Routines/*",
                    FolderGenerator = element => "Routines",
                    BaseFileNameGenerator = DefaultNameGenerator,
                    CustomSerializers = [
                        new StructuredTextSerializer(),
                    ],
                    Transformers = [
                        new LadderLogicLineNumberTransformer(),
                    ],
                },

            ],
        },
        new L5xExploderConfig
        {
            XPath = @"Controller/AlarmDefinitions/*",
            FolderGenerator = element => "AlarmDefinitions",
            BaseFileNameGenerator = DefaultNameGenerator,
        },
        new L5xExploderConfig
        {
            XPath = @"Controller/Tags/*",
            FolderGenerator = element => "Tags",
            BaseFileNameGenerator = DefaultNameGenerator,
        },
        new L5xExploderConfig
        {
            XPath = @"Controller/Programs/*",
            FolderGenerator = element => "Programs",
            BaseFileNameGenerator = DefaultNameGenerator,
            ChildConfigs = 
            [
                new L5xExploderConfig
                {
                    XPath = @"Tags/*",
                    FolderGenerator = element => "Tags",
                    BaseFileNameGenerator = DefaultNameGenerator,
                },
                new L5xExploderConfig
                {
                    XPath = @"Routines/*",
                    FolderGenerator = element => "Routines",
                    BaseFileNameGenerator = DefaultNameGenerator,
                    CustomSerializers = [
                        new StructuredTextSerializer(),
                    ],
                    Transformers = [
                        new LadderLogicLineNumberTransformer(),
                    ],
                }
            ],
        },
        new L5xExploderConfig
        {
            XPath = @"Controller/Tasks/*",
            FolderGenerator = element => "Tasks",
            BaseFileNameGenerator = DefaultNameGenerator,
        },
        new L5xExploderConfig
        {
            XPath = @"Controller/Trends/*",
            FolderGenerator = element => "Trends",
            BaseFileNameGenerator = DefaultNameGenerator,
        },
        new L5xExploderConfig
        {
            XPath = @"Controller/DataLogs/*",
            FolderGenerator = element => "DataLogs",
            BaseFileNameGenerator = DefaultNameGenerator,
        }
    ];

    private static readonly char[] InvalidFileNameChars = Path.GetInvalidFileNameChars();

    private static string DefaultNameGenerator(XElement element)
    {
        var baseName = element.Attribute("Name")?.Value;
        if (string.IsNullOrEmpty(baseName))
        {
            return "unnamed_element";
        }

        foreach (var invalidChar in InvalidFileNameChars)
        {
            baseName = baseName.Replace(invalidChar, '_');
        }

        return baseName;
    }

    /// <summary>
    /// Adds L5XGitPrevAOI hint elements to each AOI to record the original ordering
    /// from the source L5X file. This runs during explode before elements are persisted.
    /// Hints are only added when UnsafeSkipDependencyCheck is enabled in the serialization options,
    /// which indicates the L5X was exported without the Dependencies option.
    /// </summary>
    private static void AddOriginalOrderingHints(IList<XElement> elements, L5xSerializationOptions options)
    {
        if (!options.UnsafeSkipDependencyCheck)
        {
            return;
        }

        for (int i = 1; i < elements.Count; i++)
        {
            var prevName = elements[i - 1].Attribute("Name")?.Value;
            if (!string.IsNullOrEmpty(prevName))
            {
                // Remove any existing hint (in case of re-explode)
                elements[i].Element(Constants.OriginalOrderingHintElement)?.Remove();

                // Insert the hint as the first child element so it's easy to find
                // and clearly not part of the Logix Designer schema
                elements[i].AddFirst(new XElement(Constants.OriginalOrderingHintElement, new XAttribute("Name", prevName)));
            }
        }
    }

    private static IList<XElement> SortModules(IEnumerable<XElement> modules)
    {
        // Build a dependency graph and unnamed modules list
        // The element which is the key depends on the elements in the value list.
        var dependencies = new Dictionary<XElement, IList<XElement>>();
        var unnamedModules = new List<XElement>();

        foreach (var module in modules)
        {
            var moduleName = module.Attribute("Name")?.Value;
            var parentModuleName = module.Attribute("ParentModule")?.Value;

            // If the module has no name, add it to the unnamed list to be appended last
            // Nothing can take a dependency on unnamed modules because there is no name to reference
            if (string.IsNullOrEmpty(moduleName))
            {
                unnamedModules.Add(module);
                continue;
            }

            // If the module isn't yet in the dependencies map, initialize an entry for it.
            if (!dependencies.ContainsKey(module))
            {
                dependencies[module] = new List<XElement>();
            }

            // Find the parent module in the list
            var parentModule = modules.FirstOrDefault(m =>
                m.Attribute("Name")?.Value == parentModuleName);

            // If the parentModule differs from the current module, it is a dependency
            if (parentModule != null && parentModule != module)
            {
                // And finally, add the dependency to the map
                dependencies[module].Add(parentModule);
            }
        }

        var sortedModules = TopologicalSort(dependencies);
        sortedModules.AddRange(unnamedModules);

        return sortedModules;
    }

    private static List<XElement> TopologicalSort(IDictionary<XElement, IList<XElement>> dependencies)
    {
        var sorted = new List<XElement>();
        var visited = new HashSet<XElement>();
        var visiting = new HashSet<XElement>();

        void Visit(XElement node)
        {
            if (visited.Contains(node)) return;
            if (visiting.Contains(node))
            {
                throw new InvalidOperationException("Cyclic dependency detected.");
            }

            visiting.Add(node);

            if (dependencies.ContainsKey(node))
            {
                foreach (var child in dependencies[node])
                {
                    Visit(child);
                }
            }

            visiting.Remove(node);
            visited.Add(node);

            sorted.Add(node);
        }

        foreach (var node in dependencies.Keys)
        {
            Visit(node);
        }

        return sorted;
    }
}
