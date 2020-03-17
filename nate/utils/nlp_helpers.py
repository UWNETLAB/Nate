import spacy
from spacy.pipeline import merge_entities
from .mp_helpers import mp
from tok import sent_tokenize
from gensim.models.phrases import Phrases, Phraser
from itertools import chain
from ..svonet.svonet_class import process_svo

# Everything from this point down was moved from the `text_helpers` module

def spacy_process(nlp, texts, sub_tags = False, obj_tags = False):
    if 'svo_component' in nlp.pipe_names:
        processed_list = [doc for doc in nlp.pipe(texts, {'svo_component': [sub_tags, obj_tags]})]
    else:
        processed_list = [doc for doc in nlp.pipe(texts)]
    return processed_list
    
def default_filter_lemma(doc):  # to do: make this user-configurable
    """
    This is a docstring.
    """
    doc = [token.lemma_.lower() for token in doc if token.is_stop == False and len(token) > 2 and token.is_alpha and token.is_ascii]
    return doc
    
def custom_spacy_component(doc):
    return [token.lemma_.lower() for token in doc if token.is_stop == False and token.is_ascii]
    
def svo_component(doc, sub_tags, obj_tags):
    doc = process_svo(sub_tags, obj_tags, doc)
    return doc

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
