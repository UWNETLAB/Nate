"""
This is a MODULE docstring
"""
import pandas as pd
from time import time as marktime
from typing import List
from ..utils.mp_helpers import mp
from itertools import groupby, combinations, chain
from collections import defaultdict


def cooc_offsets(processed_list: List, time: List, minimum_offsets):
    """
    This is a docstring. Takes a list of documents and a list of their timestamps, returns a dictionary with term-pairs
    as keys and a list of times when those term-pairs occur as values. Also returns a lookup dictionary, with integers
    as keys for corresponding string values
    """
    print("Generating Offsets:")

    start = marktime()

    # send list of documents to text_to_int so that cooc function can work with integers for memory and processing efficiency
    word_ints, lookup = text_to_int(processed_list)

    # multiprocess the cooc function on the list of integers
    offset_dict = mp(word_ints, cooc, time)


    # recreate the dictionary of offsets, pruning all those with a less occurrences than the minimum_offsets threshold
    offsets = {
        k: v for k, v in offset_dict.items() if len(v) >= minimum_offsets
    }

    print("Finished offset generation in {} seconds".format(
        round(marktime() - start)))
    print("Commencing timestamp deduplication...")

    # kleinberg requires that timestamps be unique - increment simultaneous occurrences by 1 millisecond.
    # Note: it's possible that some dataset will require this to be microseconds, if term pairs appear more than 999 times at once
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


def text_to_int(processed_list):
    """
    This is a docstring. Converts a list of texts (which are lists of tokens) into integer representation
    """

    # sort string tokens in each text, keeping only unique words
    sorted_texts = [sorted(set(x)) for x in processed_list]

    # create a sorted list of all unique words in the corpus, used for the lookup dictionary
    flat_text = sorted(set(list(chain(*sorted_texts))))

    del processed_list

    # create dataframe with 1 column ('word') of words in the corpus
    df = pd.DataFrame({'word': flat_text})

    del flat_text

    # use the dataframe index as the identifier for each word, casting to a dictionary
    word_dict = df.reset_index().set_index('word')['index'].to_dict()

    # invert the dictionary, making word integers the keys, and words the values
    lookup_dict = {v: k for k, v in word_dict.items()}

    # create a list (documents) of lists (words in each document) integer representation of the corpus
    word_ints = [[word_dict[word] for word in text] for text in sorted_texts]

    del word_dict

    return word_ints, lookup_dict


def cooc(time, word_ints):
    """
    This is a docstring. Takes a list of times and a list (document) of lists (word integers in each document). Returns 
    dictionary with pairs of integers as keys and a list of timestamps (occurrences) as each value
    """

    # use defaultdict so that dictionary entries are created if they don't exist already
    offset_dict = defaultdict(list)

    # iterate through each document and its timestamp
    for text, timestamp in zip(word_ints, time):
        
        # use combinations to find all word-pairs in the current document
        keys = list(combinations(text, 2))

        # add current timestamp to list of timestamps (dictionary value) for each word-pair (dictionary key) found in current document
        for key in keys:
            offset_dict[key].append(timestamp)

    return offset_dict
