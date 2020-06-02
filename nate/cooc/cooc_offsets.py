"""Builds the offset dictionary for the cooc pipeline.

The dictionary is of the form {(word1, word2):[time1,time2,...], ...}.
"""

import pandas as pd
from time import time as marktime
from typing import List
from ..utils.mp_helpers import mp
from itertools import groupby, combinations, chain
from collections import defaultdict


def cooc_offsets(processed_list: List, time: List, minimum_offsets):
    """Generates the offset_dict for the `Cooc` pipeline.

    Args:
        processed_list (List): A list of lists, where each entry in the outer
            list represents a text, and the entries of each inner list are 
            the tokens found in those texts in string form.
        time (List): A list of times for when each text was written.
        minimum_offsets (int): The minimum number of 'offsets' - or occurrences
            in the dataset - a given token/term pair must have in order to
            be retained.

    Returns:
        Dict: The offset dictionary for the `Cooc` class, with word-word pairs
            in integer format as keys and a list of offsets (occurence 
            timestamps) as values.
        Dict: A lookup dictionary for each word in the corpus, with the integer
            representation as key and the string representation as value.
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
    """Converts every word in a list of texts into an integer representation.

    After conversion to the integer representation, the tokens of the text are
    no longer in the same order. This function should only be used on texts
    where the distance between tokens in the source text is not relevant. It
    should only be used on texts where token co-occurence _in the same document_
    is relevan
    
    Args:
        processed_list (List): A list of texts, where each text is a
            list of tokens (strings).

    Returns:
        List: A list of texts, where each text is a list of tokens (integers).
        Dict: A lookup dict, to convert integer representations of tokens
            to strings. It is of the form {i:s} where i is the integer
            representation of the token, and s is the string representation.
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
    """Generates co-occurence pairs from documents and their timestamps.

    Args:
        time (List): A list of of the times each text in word_ints was written.
        word_ints (List): A list of lists, where each entry in the outer list
            represents a text, and the entries of each inner list are the
            integer representations of tokens found in those texts (as
            produced by text_to_int).
    
    Returns:
        Dict: A dictionary with token-token pairs as keys and a list of 
            occurence timestamps as values.
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
