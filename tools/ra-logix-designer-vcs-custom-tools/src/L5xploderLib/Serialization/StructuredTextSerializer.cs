
using System.Xml.Linq;
using L5xploderLib.Models;
using L5xploderLib.Services;

namespace L5xploderLib.Serialization;

internal sealed class StructuredTextSerializer : ICustomSerializer
{
    private string fileExt => Constants.StructuredTextFileExtension;

    public IEnumerable<XElement> Deserialize(string folderPath, IEnumerable<XElement> elements)
    {
        var stFiles = Directory.GetFiles(folderPath, $"*{fileExt}");
        if (stFiles.Length == 0)
        {
            return [];
        }

        var routines = new Dictionary<string, XElement>(StringComparer.OrdinalIgnoreCase);
        foreach (var element in elements.Where(e => e.Name.LocalName == "Routine"))
        {
            var name = element.Attribute("Name")?.Value;
            if (!string.IsNullOrEmpty(name))
            {
                routines[name] = element;
            }
        }

        var synthesised = new List<XElement>();

        foreach (var routineName in stFiles.Select(GetRoutineName).Distinct())
        {
            if (!routines.TryGetValue(routineName, out var routine))
            {
                // Exploded before the routine element was persisted alongside the .st file. Rebuild
                // the little that older layouts recorded so those directories still implode.
                routine = new XElement("Routine",
                    new XAttribute("Name", routineName),
                    new XAttribute("Type", "ST"));

                routines[routineName] = routine;
                synthesised.Add(routine);
            }

            foreach (var stFile in stFiles.Where(file => GetRoutineName(file) == routineName))
            {
                var onlineEditType = GetOnlineEditType(stFile);
                var stContentElement = FindOrCreateStContent(routine, onlineEditType);

                // Line numbers are positional, so they are regenerated rather than stored.
                var lines = File.ReadAllText(stFile).Split(["\r\n", "\n"], StringSplitOptions.None);
                stContentElement.Add(lines.Select((line, index) =>
                    new XElement("Line",
                        new XAttribute("Number", index),
                        new XCData(line))));
            }
        }

        return synthesised;
    }

    private static XElement FindOrCreateStContent(XElement routine, string? onlineEditType)
    {
        var existing = routine
            .Elements("STContent")
            .FirstOrDefault(content => content.Attribute("OnlineEditType")?.Value == onlineEditType);

        if (existing != null)
        {
            return existing;
        }

        var created = new XElement("STContent");
        if (onlineEditType is not null)
        {
            created.SetAttributeValue("OnlineEditType", onlineEditType);
        }

        routine.Add(created);
        return created;
    }

    public IEnumerable<ElementFile> Serialize(XElement element, string elementBaseFile)
    {
        var results = new List<ElementFile>();
        var fileRegistry = new FilePathRegistry();

        var parentFolder = Path.GetDirectoryName(elementBaseFile) ?? string.Empty;

        // Find all <STContent> elements
        var stContentElements = element.Elements("STContent").ToList();

        // If there is no <STContent>, this is a no-op, just process the element as passed in.
        if (!stContentElements.Any())
        {
            return [new L5xElementFile { BaseFilePath = elementBaseFile, Element = element }];
        }

        foreach (var stContentElement in stContentElements)
        {
            // It's possible to have multiple <STContent> elements if it was edited online.
            var onlineEditType = stContentElement.Attribute("OnlineEditType")?.Value;

            // Generate the file path and name for the .st file
            var filePath = onlineEditType == null
                ? $"{elementBaseFile}"
                : $"{elementBaseFile}.{onlineEditType}";
            var fileName = Path.GetFileName(filePath);

            // Ensure the file path is unique, if not throw.  We cannot rename these to make them unique
            // because the file name is meaningful.
            if (fileRegistry.IsReserved(filePath))
            {
                throw new InvalidDataException(
                    $"The file path {filePath} is already used and cannot be used for structured text content."
                );
            }

            fileRegistry.Reserve(filePath);

            // If any line elements are missing a line number or out of order, throw an error.
            int lineNumber = 0;
            foreach (var line in stContentElement.Elements("Line"))
            {
                if (!(line.Attribute("Number")?.Value == lineNumber.ToString()))
                {
                    throw new InvalidDataException(
                        $"Line number mismatch in <STContent> element {elementBaseFile}. Expected line number {lineNumber}, but found {line.Attribute("Number")?.Value ?? "missing"}."
                    );
                }
                lineNumber++;
            }

            // Extract the content from <Line> elements now that we know they are well-ordered.
            var lines = stContentElement.Elements("Line")
                .Select(line => line.Value)
                .ToList();

            // Only the lines move out to the .st file. Everything else on the routine and on
            // <STContent> stays in the element file, so descriptions, attributes and any other
            // children survive the round trip without this serializer needing to know about them.
            stContentElement.Elements("Line").Remove();

            // Create the .st file with the content
            results.Add(
                new CustomElementFile
                {
                    BaseFilePath = filePath,
                    FileExt = fileExt,
                    Content = string.Join(Environment.NewLine, lines),
                }
            );
        }

        results.Add(new L5xElementFile { BaseFilePath = elementBaseFile, Element = element });

        return results;
    }

    private static string? GetOnlineEditType(string filePath)
    {
        // Extract the online edit type from the file name if it exists
        var fileName = Path.GetFileNameWithoutExtension(filePath);
        var parts = fileName.Split('.');

        return parts != null && parts.Length > 1 ? parts[1] : null;
    }
    
    private static string GetRoutineName(string filePath)
    {
        // Extract the routine name from the file name
        var fileName = Path.GetFileNameWithoutExtension(filePath);
        var parts = fileName.Split('.');

        return parts.Length > 0 ? parts[0] : throw new InvalidDataException($"Invalid structured text file name: {filePath}");
    }
}