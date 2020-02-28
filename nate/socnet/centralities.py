from importlib.util import find_spec
from collections import namedtuple
import igraph as ig


cent_tuple = namedtuple('centralities', ['vertex', 'betweenness', 'closeness', 'eigenvector'])


def compute_centralities(tuples, force_igraph = False):
    """
    This is a docstring
    """ 

    if find_spec('graph_tool') != None and force_igraph == False:
        print("using graph-tool")
        return gt_cents(tuples)

    elif find_spec('igraph') != None:
        print("using igraph")
        return igraph_cents(tuples)

    else:
        raise Exception("Please ensure that either graph_tool or python_igraph are installed.")


def gt_cents(tuples):
    """
    This is a docstring
    """ 
    author_lookup = {}
    author_number = 0

    for entry in tuples:
        for i in range(2):
            if entry[i] not in author_lookup:
                author_lookup[entry[i]] = author_number 
                author_number += 1

    import graph_tool as gt
    from graph_tool.centrality import betweenness, closeness, eigenvector

    G = gt.Graph(directed=False)

    for edge in tuples:
        G.add_edge(author_lookup[edge[0]], author_lookup[edge[1]], add_missing=True)

    betweenness_vertex, _ = betweenness(G)
    closeness_vertex = closeness(G)
    _, eigenvector_vertex = eigenvector(G)

    return_list = []

    for k, v in author_lookup.items():
        cent = cent_tuple(
            k,
            betweenness_vertex[v],
            closeness_vertex[v],
            eigenvector_vertex[v]
        )
        return_list.append(cent)

    return return_list


def igraph_cents(tuples):
    """
    This is a docstring
    """ 
    G = ig.Graph.TupleList(tuples, directed = False)

    vertex_list = G.vs()
    between_list = G.betweenness(directed=False)
    close_list = G.closeness(normalized=True)
    eigen_list = G.eigenvector_centrality(directed=False, scale=True)

    return_list = []

    for i in range(len(vertex_list)):
        cent = cent_tuple(
            vertex_list[i]['name'], 
            between_list[i], 
            close_list[i], 
            eigen_list[i]
        )
        return_list.append(cent)

    return return_list
