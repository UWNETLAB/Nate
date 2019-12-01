"""
This module accepts networks from social, text, document, or any other source.
It uses the disparity filter approach to compute alpha scores for the edges and
assigns the alpha scores as edge attributes.

It also includes a series of methods for easily grabbing useful descriptives
and simple reports for the network.
"""

from nate.backbone import compute_disparity_filter
# ^ this is Malcolm's. He refactored another module I shared with him
# implementing Seranno et al.

# I need to ask him about whether or not he is OK with including this in Nate.
# perhaps the original author as well, although we forked a fork
# the original has no license.

import numpy as np
import networkx as nx
import pandas as pd
import numpy as np
from community import best_partition, modularity
from collections import Counter
import matplotlib.pyplot as plt

class Netplus():
    def __init__(self, WEL, NAF=None):
        """Initialize attributes"""
        self.edgelist = WEL
        self.node_attributes = NAF
        # obviously we will something better than what comes below... but as a first check
        if isinstance(WEL, pd.DataFrame):
            pass
        else:
            raise TypeError("Expected data in the form of a Pandas DataFrame.")

        self.network = nx.from_pandas_edgelist(self.edgelist, 'i', 'j', ['weight'])
        backbone_scores = compute_disparity_filter(self.network)
        self.partitions = best_partition(self.network) # or backbone?
        self.wela = nx.to_pandas_edgelist(backbone_scores)

    def info(self):
        print('Number of nodes: {}'.format(nx.number_of_nodes(self.network)))
        print('Number of edges: {}'.format(nx.number_of_edges(self.network)))
        print('Density: {}'.format(np.round(nx.density(self.network), 4)))
        print('Diameter: {}'.format(nx.diameter(self.network)))
        print('Modularity: {}'.format(np.round(modularity(self.partitions, self.network), 4)))

    def degree_distribution(self):
        degree_sequence = sorted([d for n, d in self.network.degree()], reverse=True)
        degreeCount = Counter(degree_sequence)
        self.deg, self.count = zip(*degreeCount.items())
        df = pd.DataFrame([self.deg, self.count]).T
        df.columns = ['Degree', 'Count']
        return df

    def plot_degree_histogram(self):
        plt.bar(self.deg, self.count, width=0.80, color='black')
        plt.xticks(np.arange(0, 18, step=2))
        plt.title("Degree Histogram")
        plt.ylabel("Count")
        plt.xlabel("Degree")
        plt.show()
