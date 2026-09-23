using System.Xml.Linq;

namespace L5xploderLib.DependencySort.Services;

/// <summary>
/// Recovers the Add-On Instruction order that the source L5X had when it was exploded.
///
/// Exploded AOIs are stored one directory per instruction and come back in file-name order, so the
/// original order is carried in ephemeral <see cref="Constants.OriginalOrderingHintElement"/> hints
/// that each record the AOI that preceded it. The hints are only a preference: where they are
/// absent, or the chain has been broken by a merge that added or removed AOIs, the current document
/// order stands in for the affected instructions.
/// </summary>
internal static class OriginalAoiOrder
{
    /// <summary>
    /// Maps each AOI element to its preferred position. Every supplied element gets a position, and
    /// positions are unique, so the result is a total order usable as a deterministic tiebreaker.
    /// </summary>
    public static Dictionary<XElement, int> Resolve(IReadOnlyList<(string Name, XElement Element)> aois)
    {
        var byName = new Dictionary<string, XElement>(StringComparer.Ordinal);
        foreach (var (name, element) in aois)
        {
            byName.TryAdd(name, element);
        }

        var successors = new Dictionary<XElement, XElement>();
        var hasPredecessor = new HashSet<XElement>();

        foreach (var (_, element) in aois)
        {
            var previousName = element.Element(Constants.OriginalOrderingHintElement)?.Attribute("Name")?.Value;

            // Ignore a hint whose target is gone, is the element itself, or is already spoken for by
            // another element; keeping the first claim leaves the rest of the chain intact.
            if (string.IsNullOrEmpty(previousName)
                || !byName.TryGetValue(previousName, out var previous)
                || previous == element
                || successors.ContainsKey(previous))
            {
                continue;
            }

            successors[previous] = element;
            hasPredecessor.Add(element);
        }

        var order = new Dictionary<XElement, int>();
        var position = 0;

        // Walk each chain from its head. Heads are taken in document order so AOIs added since the
        // last explode, and fragments left by a broken chain, land in a stable, predictable place.
        foreach (var (_, head) in aois)
        {
            if (hasPredecessor.Contains(head))
            {
                continue;
            }

            XElement? current = head;
            while (current != null && !order.ContainsKey(current))
            {
                order[current] = position++;
                current = successors.TryGetValue(current, out var successor) ? successor : null;
            }
        }

        // Anything still unplaced sits in a hint cycle; document order is the best remaining guess.
        foreach (var (_, element) in aois)
        {
            if (!order.ContainsKey(element))
            {
                order[element] = position++;
            }
        }

        return order;
    }
}
