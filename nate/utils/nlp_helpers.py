"""Utilities for NLP, mainly using spaCy."""
import spacy
from spacy.pipeline import merge_entities
from .mp_helpers import mp
from tok import sent_tokenize
from gensim.models.phrases import Phrases, Phraser
from itertools import chain
from ..svonet.svonet_class import process_svo

# Everything from this point down was moved from the `text_helpers` module


def spacy_process(nlp, joined, sub_tags, obj_tags, texts):
    """Processes texts in spaCy.

    Primary point of access to spaCy. Requires the NLP model object to be
    passed, as well as the texts to be processed. Setting joined to True
    will combine tokens into strings, separated by white space. If the
    svo_component is detected, will also accept subject tags and object
    tags to be passed to `process_svo`
    """
    if 'svo_component' in nlp.pipe_names:
        processed_list = [
            doc for doc in nlp.pipe(texts,
                                    component_cfg={
                                        'svo_component': {
                                            'sub_tags': sub_tags,
                                            'obj_tags': obj_tags
                                        }
                                    })
        ]
    elif joined == True:
        processed_list = [' '.join(doc) for doc in nlp.pipe(texts)]
    else:
        processed_list = [doc for doc in nlp.pipe(texts)]
    return processed_list


def default_filter_lemma(doc):  # to do: make this user-configurable
    """Filters spaCy pipeline.

    This is the default filter to be used in the spaCy pipeline for tasks
    that don't involve SVO.
    """
    proc = []
    for token in doc:
        if '_' in token.text and len(token) > 2 and token.is_ascii:
            proc.append(token.text)
        if token.is_alpha and len(token) >2 and token.is_stop is False and token.is_ascii:
            proc.append(token.lemma_.lower())

    return proc


def custom_spacy_component(doc):
    """
    Placeholder/example for a custom spaCy pipeline component
    """
    return [
        token.lemma_.lower()
        for token in doc
        if token.is_stop == False and token.is_ascii
    ]


def svo_component(doc, sub_tags, obj_tags):
    """Processes text in the SVO pipeline.
    
    TODO: Why does this function only wrap around process_svo? Consider
    moving wrapped function here.
    """
    doc = process_svo(sub_tags, obj_tags, doc)
    return doc


def bigram_process(texts, trigrams, bigram_threshold, tokenized=True):
    """Uses gensim to detect bigrams and trigrams.

    Expects a list of texts. See gensim documentation for explanations
    of parameters: https://radimrehurek.com/gensim/models/phrases.html
    """
    sentences = [sent_tokenize(text) for text in texts] # gensim needs documents to come in as a list of sentences
    all_sentences = list(chain(*sentences)) # flatten list of sentences for training purposes
    model = Phrases(all_sentences, min_count=1, threshold=bigram_threshold, scoring='npmi') # train the model
    bigrammer = Phraser(model) # create more efficient applicator of trained model
    bigrammed_list = [[bigrammer[sent] for sent in doc] for doc in sentences] # apply the model to the original texts
    if trigrams == True: # gensim detects trigrams by stacking bigram detection on text with detected bigrams
        trigram_model = Phrases(bigrammer[all_sentences], min_count=1, threshold=bigram_threshold, scoring='npmi')
        trigrammer = Phraser(trigram_model)
        bigrammed_list = [[trigrammer[bigrammer[sent]] for sent in doc] for doc in sentences]
    bigrammed_list = [list(chain(*x)) for x in bigrammed_list]
    # option to return text in original form, but with underscores between bigrams
    if tokenized == False:
        bigrammed_list = [' '.join(doc) for doc in bigrammed_list]

    return bigrammed_list
