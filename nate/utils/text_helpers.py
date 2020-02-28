"""
As this collection of helper functions grows, we may want to organize it
into different files. Right now, I am just putting all kinds of helpers
here. So far, everthing is text related because those are the modules
I have been writing. Perhaps network-related helpers should be in a different file?
- JM 
"""

import pandas as pd
import spacy #maybe not needed
from gensim.models.phrases import Phrases, Phraser
from tok import sent_tokenize
from itertools import chain


def window_text(string_of_text, window_lr=3):
    """
    This function splits a string into tokens on each space. Then it iterates
    over each token and takes add n words to a new list where n = the number of
    ``window_lr`` * 2 + 1. This is because ``window_lr'' is the number of
    words to grab to the left AND to the right of each token in the string.
    If ``window_lr'' = 2, then it will take the token itself, 2 words to the
    left of the token, and 2 words to the right of a token. The result is a
    window of 5 words. As a result of this design decision, the smallest window
    possible is 3 words, which can be given by ``window_lr'' = 1. Finally, the
    windows at the start and end of a text string will be smaller than the rest
    because they will have fewer words at the start (nothing / less to the left)
    and at the end (nothing / less to the right). This function is designed to
    take in a string. If the string is pre-processed (which is should be), make
    sure it is receiving a string, not tokenized from another package, like
    spacy or nltk.

    The output of this function is a new list of windowed strings. It can be
    fed into functions like construct_conet() to construct a co-occurrence
    network where co-occurrence happens between words within a moving window.
    Obviouslly, this is the function that makes the windows, not the
    co-occurrence network.
    """
    tokens = string_of_text.split()
    for each in tokens:
        context = []
        for index in range(len(tokens)):
            start = max(0, index-window_lr)
            finish = min(len(tokens), index+window_lr)
            left = " ".join(tokens[start:index])
            right = " ".join(tokens[index+1:finish])
            context.append("{} {} {}".format(left, tokens[index], right))
    return context


def search_entities(raw_text_string, search):
    """
    Helper function for construct_entity_conet(). Iterates over a list
    of entities and looks to see if they are present in a given text
    string. If they are, then it will append the entity to a list for
    each text. These lists of ents appearing in texts can be used to
    construct a network of entities that co-occurr within texts.
    """
    ents = []
    for entity in search:
        if entity.lower() in raw_text_string.lower():
            ents.append(entity.lower())
    return ents


def adjmat_to_wel(adjmat, remove_self_loops=True):
    """
    Accepts an adjacency matrix and outputs a weighted edgelist.
    """
    adjmat = pd.read_csv('~/Desktop/testing/ajm.csv', index_col = 0)
    adjmat.fillna(0, inplace=True)

    if remove_self_loops is True:
        # zero out the diagonal
        for i in adjmat.index:
            adjmat.loc[i,i] = 0
    else:
        pass

    wel=[('i','j','Weight')]
    for source in adjmat.index.values:
        for target in adjmat.index.values:
            if adjmat[source][target] > 0:
                wel.append((target,source,adjmat[source][target]))
    return wel


# def detect_bigrams(text_los, bigram_threshold=10, bigram_min_count=3,custom_cuts=[]):
#     """
#     Accepts text in the form of a list of strings.
#     Does some super simple tokenization and case changes.
#     Computes bigrams then returns new list of strings with the bigrams in place
#     of the original pairs, words joined by _.
#     """
#     text = [t.translate(str.maketrans('', '', string.punctuation)).lower().split() for t in text_los]
#     # bigram_threshold is 10 by default. The higher the number, the few bigrams returned.
#     bigram = Phrases(text, min_count=bigram_min_count, threshold=bigram_threshold)
#     parsed = [bigram[line] for line in text]
#     for_spacy = [" ".join(sent) for sent in parsed]
#     return for_spacy

# def preprocess_text_with_bigrams(text_with_bigrams_los):
#     """
#     Accepts the output of the `detect_bigrams()` function.
#     Uses spacy to check tokens for
#         * stopword status
#         * alpha status
#         * longer than 1 character
#         * is not in a list of custom stopwords
#     and then appends the bigrams and anything that meets the criteria ^
#     to a list. Returns the data as a list of list of strings or a list of strings.
#     Inner list in the former represents a document.
#     """
#     cleaned = [nlp(t) for t in text_with_bigrams_los]
#     inspect = []
#     for doc in cleaned:
#         processed = []
#         for token in doc:
#             if '_' in token.text:
#                 processed.append(token.text)
#             if token.is_stop == False and token.is_alpha == True and len(token) > 1:
#                 if token.text not in custom_cuts:
#                     processed.append(token.lemma_)
#         inspect.append(processed)
#         return inspect

def write_topics(model, feature_names, no_top_words, filename='topics.txt'):
    """
    This is a docstring.
    """
    with open(filename, 'w') as f:
        for topic_idx, topic in enumerate(model.components_):
            f.write("Topic {}: ".format(topic_idx))
            f.write(" ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))
            f.write('\n')

def spacy_process(nlp, texts):
    processed_list = [doc for doc in nlp.pipe(texts)]
    return processed_list
    
def spacy_component(doc):  # to do: make this user-configurable
    """
    This is a docstring.
    """
    doc = [token.lemma_.lower() for token in doc if token.is_stop == False and len(token) > 2 and token.is_alpha and token.is_ascii]
    return doc
    
def custom_spacy_component(doc):
    return [token.lemma_.lower() for token in doc if token.is_stop == False and token.is_ascii]

def bigram_process(texts, tokenized=True):
    sentences = [sent_tokenize(text) for text in texts]
    all_sentences = list(chain(*sentences))
    model = Phrases(all_sentences, min_count=1, threshold=0.8, scoring='npmi')
    bigrammer = Phraser(model)
    bigrammed_list = [[bigrammer[sent] for sent in doc] for doc in sentences]
    bigrammed_list = [list(chain(*x)) for x in bigrammed_list]
    
    if tokenized == False:
        bigrammed_list = [' '.join(doc) for doc in bigrammed_list]
    
    return bigrammed_list
