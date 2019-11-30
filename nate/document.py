"""
This module accepts documents and outputs similarity networks

TODO:
    * input dataframe
    * output WELNAF
    * get these todos on GH issues... ;) 
"""

import spacy
nlp = spacy.load('en')
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Document():
    """
    Accepts a list of documents.
    Outputs a network with similarity scores as edge attributes.
    """

    def __init__(self, documents):
        """Initialize attributes"""
        self.documents = documents

        if type(self.documents) == list:
            pass
        else:
            raise TypeError("Expected data in the form of a list. Other inputs will be supported soon...")

        docs = nlp.pipe(source, batch_size=10, n_threads=4)


    def document_similarity(self, cosim_threshold=.5, tfidf=True, drop_isolates=True):
        """
        Takes in a text data in list format (should already be pre-processed)
        and returns a networkx graph where edges between texts are based on
        cosine similarity. Default threshold for similarity is .5.

        Cosine similarity is set to 0 when below threshold to avoid forming an
        edge between dissimilar documents.
        """
        vectorizer = TfidfVectorizer(norm='l2')
        matrix = vectorizer.fit_transform(self.documents)
        sim = cosine_similarity(matrix)
        adj_mat = pd.DataFrame(np.round(sim, 2))
        # set baseline sim threshold
        for col in adj_mat.columns:
            adj_mat[col][adj_mat[col] < cosim_threshold] = 0
        for col in adj_mat.columns:
            adj_mat[col][adj_mat[col] == 1] = 0  # prevent self-loops
        G = nx.from_pandas_adjacency(adj_mat)
        # get text data to add as attribute
        d = dict(enumerate(self.documents))
        # ^ dict with node id as key and original text as value
        nx.set_node_attributes(G, values=d, name='Text')
        if drop_isolates is True:
            G.remove_nodes_from(list(nx.isolates(G)))
        else:
            pass
        if nx.number_of_nodes(G) < 1:
            raise ValueError(
                'Node enough nodes remaining in network. Consider lowering similairity threshold or not dropping isolates.')
        return G
