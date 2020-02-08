# CREDIT CHAIN OF DEVS FOR THIS... INCLUDING MALCOLM... 

'''
This module implements the disparity filter to compute a significance score of edge weights in networks.
Forked from: https://github.com/aekpalakorn/python-backbone-network/blob/master/backbone.py
With the following changes:
 - formatted to pylint standards
 - architected as a module with no code that runs on load
 - broke large functions into smaller ones
 - copy all nodes so that completely disconnected nodes aren't removed and so that node attributes are not removed
 - copy all the original edge attributes so that they are not removed
 - bug fix: changed G.in_degree(G.successors(u)[0]) to G.in_degree(list(G.successors(u))[0])
'''
 
import networkx as nx
import numpy as np
from scipy import integrate


def get_graph_backbone(G, alpha_t=0.8):
    '''Gets the backbone of a given graph `G`.'''
    G_disp = compute_disparity_filter(G)
    G_backbone = apply_disparity_filter(G_disp, alpha_t, cut_mode='or')
    return G_backbone


def compute_disparity_filter(G, weight='weight'):
    ''' Compute significance scores (alpha) for weighted edges in G as defined in Serrano et al. 2009
        Args
            G: Weighted NetworkX graph
        Returns
            Weighted graph with a significance score (alpha) assigned to each edge
        References
            M. A. Serrano et al. (2009) Extracting the Multiscale backbone of complex weighted networks. PNAS, 106:16, pp. 6483-6488.
    '''
    return compute_disparity_filter_directed(G, weight) \
           if nx.is_directed(G) else \
           compute_disparity_filter_undirected(G, weight)


def compute_disparity_filter_directed(G, weight='weight'):
    '''See docstring for `compute_disparity_filter`.'''
    N = nx.DiGraph()
    N.add_nodes_from(G.nodes(data=True))
    for u in G:

        k_out = G.out_degree(u)
        k_in = G.in_degree(u)

        if k_out > 1:
            sum_w_out = sum(np.absolute(G[u][v][weight]) for v in G.successors(u))
            for v in G.successors(u):
                w = G[u][v][weight]
                p_ij_out = float(np.absolute(w))/sum_w_out
                alpha_ij_out = 1 - (k_out-1) * integrate.quad(lambda x: (1-x)**(k_out-2), 0, p_ij_out)[0] # pylint: disable=cell-var-from-loop
                N.add_edge(u, v, alpha_out=float('%.4f' % alpha_ij_out))
                N[u][v].update(G[u][v])

        elif k_out == 1 and G.in_degree(list(G.successors(u))[0]) == 1:
            #we need to keep the connection as it is the only way to maintain the connectivity of the network
            v = list(G.successors(u))[0]
            N.add_edge(u, v, alpha_out=0., alpha_in=0.)
            N[u][v].update(G[u][v])
            #there is no need to do the same for the k_in, since the link is built already from the tail

        if k_in > 1:
            sum_w_in = sum(np.absolute(G[v][u][weight]) for v in G.predecessors(u))
            for v in G.predecessors(u):
                w = G[v][u][weight]
                p_ij_in = float(np.absolute(w))/sum_w_in
                alpha_ij_in = 1 - (k_in-1) * integrate.quad(lambda x: (1-x)**(k_in-2), 0, p_ij_in)[0] # pylint: disable=cell-var-from-loop
                N.add_edge(v, u, alpha_in=float('%.4f' % alpha_ij_in))
                N[v][u].update(G[v][u])
    return N


def compute_disparity_filter_undirected(G, weight='weight'):
    '''See docstring for `compute_disparity_filter`.'''
    B = nx.Graph()
    B.add_nodes_from(G.nodes(data=True))
    for u in G:
        k = len(G[u])
        if k > 1:
            sum_w = sum(np.absolute(G[u][v][weight]) for v in G[u])
            for v in G[u]:
                w = G[u][v][weight]
                p_ij = float(np.absolute(w))/sum_w
                alpha_ij = 1 - (k-1) * integrate.quad(lambda x: (1-x)**(k-2), 0, p_ij)[0] # pylint: disable=cell-var-from-loop
                B.add_edge(u, v, alpha=float('%.4f' % alpha_ij))
                B[u][v].update(G[u][v])
    return B


def apply_disparity_filter(G, alpha_t=0.8, cut_mode='or'):
    ''' Performs a cut of the graph previously filtered through the disparity_filter function.
        Args
        ----
        G: Weighted NetworkX graph
        alpha_t: double (default='0.4')
            The threshold for the alpha parameter that is used to select the surviving edges.
            It has to be a number between 0 and 1.
        cut_mode: string (default='or')
            Possible strings: 'or', 'and'.
            It applies only to directed graphs. It represents the logic operation to filter out edges
            that do not pass the threshold value, combining the alpha_in and alpha_out attributes
            resulting from the disparity_filter function.
        Returns
        -------
        B: Weighted NetworkX graph
            The resulting graph contains only edges that survived from the filtering with the alpha_t threshold
        References
        ---------
        .. M. A. Serrano et al. (2009) Extracting the Multiscale backbone of complex weighted networks. PNAS, 106:16, pp. 6483-6488.
    '''
    return apply_disparity_filter_directed(G, alpha_t, cut_mode) \
           if nx.is_directed(G) else \
           apply_disparity_filter_undirected(G, alpha_t)


def apply_disparity_filter_directed(G, alpha_t=0.8, cut_mode='or'):
    '''See the docstring for the `apply_disparity_filter` function.'''
    B = nx.DiGraph()
    B.add_nodes_from(G.nodes(data=True))
    for u, v, w in G.edges(data=True):
        try:
            alpha_in = w['alpha_in']
        except KeyError: #there is no alpha_in, so we assign 1. It will never pass the cut
            alpha_in = 1
        try:
            alpha_out = w['alpha_out']
        except KeyError: #there is no alpha_out, so we assign 1. It will never pass the cut
            alpha_out = 1

        if cut_mode == 'or':
            if alpha_in < alpha_t or alpha_out < alpha_t:
                B.add_edge(u, v)
                B[u][v].update(G[u][v])
        elif cut_mode == 'and':
            if alpha_in < alpha_t and alpha_out < alpha_t:
                B.add_edge(u, v)
                B[u][v].update(G[u][v])
    return B


def apply_disparity_filter_undirected(G, alpha_t=0.8):
    '''See the docstring for the `apply_disparity_filter` function.'''
    B = nx.Graph()
    B.add_nodes_from(G.nodes(data=True))
    for u, v, w in G.edges(data=True):

        try:
            alpha = w['alpha']
        except KeyError: #there is no alpha, so we assign 1. It will never pass the cut
            alpha = 1

        if alpha < alpha_t:
            B.add_edge(u, v)
            B[u][v].update(G[u][v])
    return B
