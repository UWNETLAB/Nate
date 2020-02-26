import igraph as ig

def compute_centralities(tuples):
    G = ig.Graph.TupleList(tuples, directed = False)

    constraint_list = G.constraint()

    between_list = G.betweenness(directed=False)

    close_list = G.closeness(normalized=True)

    eigen_list = G.eigenvector_centrality(directed=False, scale=True)

    return G



