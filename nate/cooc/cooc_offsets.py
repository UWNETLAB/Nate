"""
This is a MODULE docstring
"""
import pandas as pd
from time import time as marktime
from typing import List
from ..utils.mp_helpers import mp
from itertools import groupby, combinations, chain
import pickle
from collections import defaultdict


def cooc_offsets(processed_list:List, time:List, minimum_offsets):
    """
    This is a docstring.
    """
    print("Generating Offsets:")

    start = marktime()
    
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
