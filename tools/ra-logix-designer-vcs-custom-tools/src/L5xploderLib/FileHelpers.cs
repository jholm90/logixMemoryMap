namespace L5xploderLib;

public static class FileHelpers
{
    /// <summary>
    /// Creates the directory that will contain the given file, including any missing parent levels.
    /// Does nothing if it already exists.
    /// </summary>
    public static void CreateDirectoryForFile(string filePath)
    {
        var directory = Path.GetDirectoryName(filePath);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }
    }
}
