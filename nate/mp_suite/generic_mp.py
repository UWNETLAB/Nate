from joblib import Parallel, delayed, cpu_count
# from toolz import partition_all
from itertools import chain
from spacy.util import minibatch
from functools import partial
# from spacy.pipeline import merge_entities

def mp(items, function, *args):
    """
    This is a docstring.
    """

    cpu = int(cpu_count()) - 1

    if cpu <= 0:
        cpu = 1

    batch_size = round(len(items)/cpu)
    partitions = minibatch(items, size=batch_size)
    executor = Parallel(n_jobs=cpu, backend="multiprocessing", prefer="processes")
    do = delayed(partial(function, *args))
    tasks = (do(batch) for batch in partitions)
    temp = executor(tasks)
    if isinstance(temp[0], dict):
        results = {}
        for batch in temp:
            for key, value in batch.items():
                results.setdefault(key, []).extend(value)
    elif isinstance(temp[0], (list, tuple)):
        results = list(chain(*temp))

    return results

