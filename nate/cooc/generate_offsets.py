import spacy
import pandas as pd
from spacy.pipeline import merge_entities
from time import time as marktime
from typing import List
from ..utils.mp_helpers import mp
from ..utils.nlp_helpers import spacy_process, spacy_component, bigram_process
from itertools import groupby, chain, combinations
import pickle
from collections import defaultdict


def generate_offsets(processed_list:List, time:List, minimum_offsets, save_spacy_path = None, bigrams = False, custom_spacy_component = False):
    """
    This is a docstring.
    """
    print("Generating Offsets:")

    start = marktime()

    # nlp = spacy.load('en_core_web_sm', disable=['parser'])
    # nlp.add_pipe(merge_entities)  #merges named entities into single tokens
    # if custom_spacy_component != False:
    #     nlp.add_pipe(custom_spacy_component, name="custom_component", last=True)  #custom component
    # else:
    #     nlp.add_pipe(spacy_component, name="filter_lemmatize", last=True)  #standard component
    
    # print("finished preliminary preparation in {} seconds".format(round(marktime() - start)))
    
    # if bigrams == True:
    #     print("Detecting bigrams...")
    #     texts = bigram_process(texts, tokenized = False)
    #     print("Finished bigram detection.")
    
    
    # Spacy Pipeline
    # print("commencing spacy pipeline...")

    # processed_list = mp(texts, spacy_process, nlp)

    # if save_spacy_path != None:
    #     with open(save_spacy_path, "wb") as stream:
    #         pickle.dump(processed_list, stream)
    
    word_ints, lookup = text_to_int(processed_list)
    
    offset_dict = mp(word_ints, cooc, time)

    offsets= {k: v for k, v in offset_dict.items() if len(v) >= minimum_offsets}
    
    print("Finished offset generation in {} seconds".format(round(marktime() - start)))
    print("Commencing timestamp deduplication...")

    for item in offsets.keys():
        offsets[item].sort()
        offsets[item] = [g + i * 0.001 for k, group in groupby(offsets[item]) for i, g in enumerate(group)]

    print("finished timestamp deduplication in {} seconds".format(round(marktime() - start)))

    print("Finished Generating Offsets. Returning offset dictionary.")

    return offsets, lookup 


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

def cooc(time, word_ints):
    """
    This is a docstring.
    """
    offset_dict = defaultdict(list)
    
    for text, timestamp in zip(word_ints, time):
        keys = list(combinations(text,2))
        for key in keys:
            offset_dict[key].append(timestamp)
    
    return offset_dict
