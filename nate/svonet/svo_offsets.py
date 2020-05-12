"""
This is a MODULE docstring
"""
from time import time as marktime
from typing import List
from itertools import groupby
from collections import defaultdict


def generate_svo_offsets(svo_list: List, time: List, minimum_offsets):
    """
    This is a docstring. Create offset dictionary and int-to-string lookup for text in SVO format.
    """
    print("Generating Offsets:")

    start = marktime()

    svo_dict = defaultdict(list)
    for i, svo in enumerate(svo_list):
        svo_dict[svo].append(time[i])

    svo_int_dict, lookup = text_to_int(svo_dict)

    # prune SVOs, excluding those with fewer occurrences than specified by minimum_offsets
    offsets = {
        k: v for k, v in svo_int_dict.items() if len(v) >= minimum_offsets
    }

    print("Finished offset generation in {} seconds".format(
        round(marktime() - start)))
    print("Commencing timestamp deduplication...")

    # increment simultaneous occurrences by 1 millisecond to satisfy Kleinberg requirements
    for item in offsets.keys():
        offsets[item].sort()
        offsets[item] = [
            g + i * 0.001
            for k, group in groupby(offsets[item])
            for i, g in enumerate(group)
        ]

    print("finished timestamp deduplication in {} seconds".format(
        round(marktime() - start)))

    print("Finished Generating Offsets. Returning offset dictionary.")

    return offsets, lookup


def text_to_int(svo_dict):
    """
    This is a docstring. Converts SVO terms to integers for memory and processing efficiency but also
    to remain consistent with other pipelines
    """
    svo_int_dict = defaultdict(list)
    lookup_dict = defaultdict(tuple)
    i = 0
    for k, v in svo_dict.items():
        svo_int_dict[i] = v
        lookup_dict[i] = k
        i = i + 1

    return svo_int_dict, lookup_dict
