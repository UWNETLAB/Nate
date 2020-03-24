"""
This is a MODULE docstring
"""
from joblib import Parallel, delayed, cpu_count
from itertools import chain
from spacy.util import minibatch
from functools import partial
from typing import Union, List, Dict


# note: functions must now accept `*args` first and batched `items` come last
def mp(items, function, *args) -> Union[List, Dict]:
    """
    This is a docstring.
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


# for fuctions that return two lists (does not work for dictionaries yet)
def mp2(items, function, *args):
    """
    This is a docstring.
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
