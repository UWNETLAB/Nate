"""
This module accepts text data and outputs co-occurrence networks.

TODO:
    * accept dataframes as input
    * time stamp co-occurrences
    * location stamp co-occurrences
    * output WELNAF
    * add other network constructors (not MVP)
"""

from nate.helpers import window_text, search_entities
from helpers import window_text, search_entities
from itertools import chain, combinations
from collections import Counter
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import spacy
import networkx as nx
nlp = spacy.load('en')
import re


class Text():
    """
    First pass only accepts text data in the form of a list.
    Will need to expand on this later.
    """
    def __init__(self, source):
        """Initialize attributes"""
        self.source = source
        if type(self.source) == list:
            pass
        else:
            raise TypeError("Expected data in the form of a list.")

        docs = nlp.pipe(source, batch_size=10, n_threads=4)
        self.spacy_docs = [doc for doc in docs]

        self.sentences = []
        for doc in self.spacy_docs:
            sents = [str(t) for t in list(doc.sents)]
            self.sentences.append(sents[0])

        self.noun_chunks = []
        for doc in self.spacy_docs:
            chunks = list(doc.noun_chunks)
            nc = [str(each) for each in chunks if len(each) > 1]
            self.noun_chunks.append(nc)

        self.nouns = []
        for doc in self.spacy_docs:
            nouns_in_docs = [tok.lemma_ for tok in doc if tok.pos_ == 'NOUN']
            self.nouns.append(nouns_in_docs)

        self.verbs = []
        for doc in self.spacy_docs:
            nouns_in_docs = [tok.lemma_ for tok in doc if tok.pos_ == 'VERB']
            self.verbs.append(nouns_in_docs)

        self.adjectives = []
        for doc in self.spacy_docs:
            nouns_in_docs = [tok.lemma_ for tok in doc if tok.pos_ == 'ADJ']
            self.adjectives.append(nouns_in_docs)


    def window_corpus(self, window=4, towin='sentences'):
        """
        Construct sliding windows for text in a corpus.
        """
        if towin is 'sentences':
            ttw = self.sentences
        elif towin is 'nouns':
            text_to_window = self.nouns
            ttw = [i for sublist in text_to_window for i in sublist]
        elif towin is 'verbs':
            text_to_window = self.verbs
            ttw = [i for sublist in text_to_window for i in sublist]
        elif towin is'adjectives':
            text_to_window = self.adjectives
            ttw = [i for sublist in text_to_window for i in sublist]
        else:
            ValueError("Expected sentences, nouns, verbs, or adjectives.")

        concatenated = [" ".join(ttw)]

        # window text
        windows = window_text(concatenated[0].lower(), window_lr=window)
        self.windows = windows
        return windows

    def semantic_context(self, search, context='source', window=4):
        """
        Searches original documents, sentences, or noun chuncks for content
        of 'search'. Returns list of strings that include the search term.

        If context is int, then it will only return a window of text around
        the search term. If int is 4, it will return 4 words before and 4 words
        after the search term. Note this is not the same process as windowing
        the text in the Corpus class, which constructs a window around *all*
        tokens in the corpus.
        """
        if context is 'source':
            textdata = self.source
        elif context is 'sentences':
            textdata = self.sentences
        elif context is 'noun_chunks':
            textdata = [i for sublist in self.noun_chunks for i in sublist]
        elif type(context) is int:
            textdata = self.source
        else:
            ValueError("Expected source, sentences, or noun_chunks for context.")

        # if windowed, search and construct windows
        if type(context) is int:
            contexts = []
            for each in textdata:
                raw_text_string = each

                if " " in search:
                    mod_search = search.replace(" ", "_")
                    raw_text_string = raw_text_string.replace(search, mod_search)
                    search = mod_search
                else:
                    pass

                tokens = raw_text_string.split()
                keysearch = re.compile(search, re.IGNORECASE)
                for index in range(len(tokens)):
                    if keysearch.match(tokens[index]):
                        start = max(0, index-window)
                        finish = min(len(tokens), index+window+1)
                        left = " ".join(tokens[start:index])
                        right = " ".join(tokens[index+1:finish])
                        contexts.append("{} {} {}".format(left, tokens[index].upper(), right))
            return contexts
        else:
            excerpts = []
            for each in textdata:
                if search in each:
                    excerpts.append(each)
            return excerpts


    def network_coocurrence(self, context='sentences', stopwords=True, threshold=1, drop_isolates=True):
        """
        Construct a term-term co-occurrence network.
        More sophisticated version coming soon.
        """
        if context is 'source':
            text = self.source
        elif context is 'sentences':
            text = self.sentences
        elif context is 'noun_chunks':
            text = [i for sublist in self.noun_chunks for i in sublist]
        elif context is 'windows':
            text = self.windows
        else:
            ValueError("Expected source, sentences, noun_chunks or windows.")

        # text = [" ".join(t) for t in text if len(t) > 1]

        if stopwords is True:
            vectorizer = CountVectorizer(stop_words='english')
        else:
            vectorizer = CountVectorizer()

        matrix = vectorizer.fit_transform(text)
        m = matrix.todense()
        mt = m.transpose()
        adj_mat = mt * m
        # drop anything below the threshold
        adj_mat[adj_mat < threshold] = 0 # this is faster than the list comprehension approach I took at first

        """
        I have a function called `adjmat_to_wel()` in helpers.py that
        returns a wel from an adjacency matrix. It might be a better idea
        to invoke that here rather than construct the nx object. In keeping
        with the idea of leaving as much nx to the end as possible.

        However, currently edge alpha values and the modularity score require
        networkx objects. Perhaps they could just be computed further down the
        pipeline. This would only really matter if, for example, you wanted to
        do something with the backbone edges before returning the wel. But
        currently we don't do anything like that, so maybe it's fine.
        """

        adj_df = pd.DataFrame(adj_mat)
        words = vectorizer.get_feature_names()
        G = nx.from_pandas_adjacency(adj_df)
        d = dict(enumerate(words))
        nx.set_node_attributes(G, values=d, name='Text')

        # this is slower than adj_mat[adj_mat < threshold] = 0. Just need to test to make sure results are identical.
        # if threshold > 1:
        #     remove = [(u,v) for u,v,d in G.edges(data=True) if d['weight'] < threshold]
        #     G.remove_edges_from(remove)
        # else:
        #     pass

        if drop_isolates is True:
            G.remove_nodes_from(list(nx.isolates(G)))
        else:
            pass
        print(nx.info(G))
        return G
