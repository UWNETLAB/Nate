import spacy
from spacy.pipeline import merge_entities
from .mp_helpers import mp
from tok import sent_tokenize
from gensim.models.phrases import Phrases, Phraser
from itertools import chain

def get_spacy_text(text, model="en_core_web_sm"):
    nlp = spacy.load(model)
    nlp.add_pipe(merge_entities)
    nlp.add_pipe(spacy_component, name="filter_lemmatize", last=True) 
    return mp(text, spacy_process, nlp)

def get_spacy_sentences(text, model="en_core_web_sm"):
    nlp = spacy.load(model)
    nlp.add_pipe(merge_entities)
    return mp(text, spacy_process, nlp)


# Everything from this point down was moved from the `text_helpers` module

def spacy_process(nlp, text):
    processed_list = [doc for doc in nlp.pipe(text)]
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
