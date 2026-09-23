using System.Xml.Linq;
using L5xploderLib.Models;

public interface ICustomSerializer
{
    /// <summary>
    /// Serializes select components of the given L5xElementFile to a collection of ElementFiles containing the file path and string content of the file.
    /// The file path is relative to the root document's folder.  Must use a file type other than the selected default serialization format
    /// (e.g. don't use .xml, .yaml. .json).
    /// </summary>
    IEnumerable<ElementFile> Serialize(XElement element, string elementBaseFile);

    /// <summary>
    /// Restores content that <see cref="Serialize"/> moved out into companion files, back into the
    /// elements already loaded from this folder. Working against the loaded elements is what lets
    /// the companion file hold only the extracted content, leaving everything else on the element
    /// untouched in whatever format the persistence layer uses.
    /// Returns any elements that had to be synthesised because no loaded element matched.
    /// </summary>
    IEnumerable<XElement> Deserialize(string folderPath, IEnumerable<XElement> elements);
}