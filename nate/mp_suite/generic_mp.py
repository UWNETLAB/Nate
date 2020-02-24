from joblib import Parallel, delayed
from toolz import partition_all
from itertools import chain


def mp(items, function, cpu, *args):
    """
    This is a docstring.
    """
    batch_size = round(len(items)/cpu)
    partitions = partition_all(batch_size, items)
    temp = Parallel(n_jobs=cpu, max_nbytes=None)(delayed(function)(v, *args) for v in partitions)
    if isinstance(temp[0], dict):
        results = {}
        for batch in temp:
            for key, value in batch.items():
                results.setdefault(key, []).extend(value)
    elif isinstance(temp[0], (list, tuple)):
        results = list(chain(*temp))
    return results
