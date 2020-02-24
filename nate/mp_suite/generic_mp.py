from joblib import Parallel, delayed
from itertools import chain
from functools import partial
from spacy.util import minibatch

def mp(items, function, cpu, *args):
    """
    This is a docstring.
    """
    batch_size = round(len(items)/cpu)
    partitions = minibatch(items, size=batch_size)
    executor = Parallel(n_jobs=cpu, backend="multiprocessing", prefer="processes")
    do = delayed(partial(function, *args))
    tasks = (do(batch) for batch in partitions)
    results = executor(tasks)
    results = list(itertools.chain(*temp))
    
    return results

