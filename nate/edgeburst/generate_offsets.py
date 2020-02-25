import spacy
import pandas as pd
from os import cpu_count
from spacy.pipeline import merge_entities
from time import time as marktime
from typing import List
from ..mp_suite.generic_mp import mp
from ..helpers.helpers import spacy_process
from itertools import groupby, chain, combinations
import pickle
from collections import defaultdict


def generate_offsets(texts:List, timestamps:List, minimum_offsets = 10, save_spacy_path = None):
    """
    This is a docstring.
    """
    print("Generating Offsets:")
    print("commencing preliminary preparation...")

    start = marktime()

    nlp = spacy.load('en_core_web_sm', disable=['parser'])
    nlp.add_pipe(merge_entities)  #merges named entities into single tokens
    nlp.add_pipe(spacy_component, name="filter_lemmatize", last=True)  #custom component
    
    print("finished preliminary preparation in {} seconds".format(round(marktime() - start)))
    
    # Spacy Pipeline
    print("commencing spacy pipeline...")

    processed_list = mp(texts, spacy_process, nlp)

    if save_spacy_path != None:
        with open(save_spacy_path, "wb") as stream:
            pickle.dump(processed_list, stream)
    
    word_ints, lookup = text_to_int(processed_list)

    del processed_list    
    
    print("finished spacy pipeline in {} seconds".format(round(marktime() - start)))

    # Offset Generation
    print("commencing offset generation...")
    
    offsets = mp(word_ints, cooc, cpu, timestamps, minimum_offsets)
    
    print("finished offset generation in {} seconds".format(round(marktime() - start)))
    print("commencing timestamp deduplication...")

    for item in offsets.keys():
        offsets[item].sort()
        offsets[item] = [g + i * 0.001 for k, group in groupby(offsets[item]) for i, g in enumerate(group)]

    print("finished timestamp deduplication in {} seconds".format(round(marktime() - start)))

    print("Finished Generating Offsets. Returning offset dictionary.")

    return offsets, lookup 

def spacy_component(doc):  # to do: make this user-configurable
    """
    This is a docstring.
    """
    doc = [token.lemma_.lower() for token in doc if token.is_stop == False and len(token) > 2 and token.is_alpha and token.is_ascii]
    return doc

def text_to_int(processed_list):
    """
    This is a docstring.
    """
    sorted_texts = [sorted(set(x)) for x in processed_list]
    flat_text = sorted(set(list(chain(*sorted_texts))))
    
    del processed_list  
    
    df = pd.DataFrame({'word':flat_text})
    
    del flat_text
    
    word_dict = df.reset_index().set_index('word')['index'].to_dict()
    lookup_dict = {v: k for k, v in word_dict.items()}
        
    word_ints = [[word_dict[word] for word in text] for text in sorted_texts]

    del word_dict
    
    return word_ints, lookup_dict    

def cooc(word_ints, timestamps, minimum_offsets):
    """
    This is a docstring.
    """
    offset_dict = defaultdict(list)
    
    for text, timestamp in zip(word_ints, timestamps):
        keys = list(combinations(text,2))
        for key in keys:
            offset_dict[key].append(timestamp)
    
    offsets_pruned = {k: v for k, v in offset_dict.items() if len(v) >= minimum_offsets}
    
    return offsets_pruned
