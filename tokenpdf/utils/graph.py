import networkx as nx
from typing import Any, Callable, List, Sequence

def largest_connected_component(
        items: Sequence[Any],
        is_connected: Callable[[Any, Any], bool]
) -> List[Any]:
    """Finds the largest connected component in a graph of items.
    The graph is constructed here, so this function is not suitable
    for large graphs.

    Args:
      items: A sequence of items to be connected.
      is_connected: A function that returns True if two items are connected.

    Returns:
      : A list of items in the largest connected component.

    """
    graph = nx.Graph()
    graph.add_nodes_from(items)
    for i, item1 in enumerate(items):
        for item2 in items[i+1:]:
            if is_connected(item1, item2):
                graph.add_edge(item1, item2)
    components = list(nx.connected_components(graph))
    return max(components, key=len) if components else []
