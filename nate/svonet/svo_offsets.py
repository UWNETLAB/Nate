"""
This is a MODULE docstring
"""
import pandas as pd
from time import time as marktime
from typing import List
from ..utils.mp_helpers import mp
from itertools import groupby, combinations
import pickle
from collections import defaultdict


def generate_svo_offsets(svo_list:List, time:List, minimum_offsets):
    """
    This is a docstring.
    """
    print("Generating Offsets:")

    start = marktime()
    
    svo_dict = defaultdict(list)
    for i, svo in enumerate(svo_list):
        svo_dict[svo].append(time[i])
            
    svo_int_dict, lookup = text_to_int(svo_dict)

    offsets = {k: v for k, v in svo_int_dict.items() if len(v) >= minimum_offsets}
    
    print("Finished offset generation in {} seconds".format(round(marktime() - start)))
    print("Commencing timestamp deduplication...")

    for item in offsets.keys():
        offsets[item].sort()
        offsets[item] = [g + i * 0.001 for k, group in groupby(offsets[item]) for i, g in enumerate(group)]

    print("finished timestamp deduplication in {} seconds".format(round(marktime() - start)))

    print("Finished Generating Offsets. Returning offset dictionary.")

    return offsets, lookup 


def text_to_int(svo_dict):
    """
    This is a docstring.
    """
    svo_int_dict = defaultdict(list)
    lookup_dict = defaultdict(tuple)
    i = 0
    for k, v in svo_dict.items():
        svo_int_dict[i] = v
        lookup_dict[i] = k
        i = i + 1
    
    return svo_int_dict, lookup_dict    

