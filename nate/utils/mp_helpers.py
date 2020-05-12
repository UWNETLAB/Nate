"""
This is a MODULE docstring
"""
from joblib import Parallel, delayed, cpu_count
from itertools import chain
from spacy.util import minibatch
from functools import partial
from typing import Union, List, Dict


def mp(items, function, *args) -> Union[List, Dict]:
    """
    This is a convenience function for generalized multiprocessing of any function that
    deals with a list or dictionary of items.
    The functions passed to `mp` must accept the list of items to be processed at the end 
    of their function call, with optional arguments first.
    *args can be any number of optional arguments accepted by the function that will be multiprocessed.
    On Windows, functions must be defined outside of the current python file and imported, to avoid 
    infinite recursion.
    """
    if cpu_count() >= 10:  #to avoid overtaxing Brad, save some cores
        cpu = 10
    else:
        cpu = cpu_count()

    batch_size = round(len(items) / cpu)
    partitions = minibatch(items, size=batch_size)
    executor = Parallel(n_jobs=cpu,
                        backend="multiprocessing",
                        prefer="processes")
    do = delayed(partial(function, *args))
    tasks = (do(batch) for batch in partitions)
    temp = executor(tasks)

    # todo: add error catch/message for zero results

    if isinstance(temp[0], dict):
        results = {}
        for batch in temp:
            for key, value in batch.items():
                results.setdefault(key, []).extend(value)
    elif isinstance(temp[0], (list, tuple)):
        results = list(chain(*temp))

    return results


def mp2(items, function, *args):
    """
    This is the same as `mp` but used when two lists of results need to be returned. Will perhaps be
    generalized for any number of results in the future. Does not currently work for dictionaries.
    """
    if cpu_count() >= 10:  #to avoid overtaxing Brad, save some cores
        cpu = 10
    else:
        cpu = cpu_count()

    batch_size = round(len(items) / cpu)
    partitions = minibatch(items, size=batch_size)
    executor = Parallel(n_jobs=cpu,
                        backend="multiprocessing",
                        prefer="processes")
    do = delayed(partial(function, *args))
    tasks = (do(batch) for batch in partitions)
    temp = executor(tasks)
    results1, results2 = zip(*temp)
    results1 = list(chain(*results1))
    results2 = list(chain(*results2))
    return results1, results2
