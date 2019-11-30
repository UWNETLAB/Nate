from nate.helpers import window_text, search_entities
from itertools import chain, combinations
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
nlp = spacy.load('en')
import re


class Text():
"""
First pass only accepts text data in the form of a list.
Will need to expand on this later.
"""
    def __init__(self, source, window=None, towin='sentences'):
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

        if type(window) is int:
            # prepare text for windowing
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

            self.concatenated = [" ".join(ttw)]

            # window text
            self.windows = window_text(self.concatenated[0].lower(), window_lr=window)

        else:
            pass


    def window_corpus(self, window=4, towin='sentences'):
        """
        Construct sliding windows for text in a corpus if the windows were
        not constructed when the Corpus was first initialized.
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

        self.concatenated = [" ".join(ttw)]

        # window text
        self.windows = window_text(self.concatenated[0].lower(), window_lr=window)


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
            text = self.source
        elif context is 'sentences':
            text = self.sentences
        elif context is 'noun_chunks':
            text = [i for sublist in self.noun_chunks for i in sublist]
        elif type(context) is int:
            text = self.source
        else:
            ValueError("Expected source, sentences, or noun_chunks for context.")

        # if windowed, search and construct windows
        if type(context) is int:
            contexts = []
            for each in text:
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
            for each in text:
                if search in each:
                    excerpts.append(each)
            return excerpts

# NOT INCLUDING THE NETWORK CONSTRUCTORS. THEY BELONG IN ANOTEHR FILE??? -- JM
