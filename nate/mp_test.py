import pandas as pd
from joblib import Parallel, delayed, cpu_count
from functools import partial
import spacy
from spacy.util import minibatch
from spacy.pipeline import merge_entities
import itertools

def main():
    if cpu_count() >= 8:   #to avoid overtaxing Brad, save some cores
        cpu = 10
    else:
        cpu = cpu_count()
    df = pd.read_csv('../data/sl2.csv')
    texts = df.content.tolist()
    nlp = spacy.load('en_core_web_sm')  # load spaCy model
    nlp.add_pipe(merge_entities)
    batch_size = round(len(texts)/cpu)
    partitions = minibatch(texts, size=batch_size)
    executor = Parallel(n_jobs=cpu, backend="multiprocessing", prefer="processes")
    do = delayed(partial(spacy_process, nlp))
    tasks = (do(batch) for batch in partitions)
    results = executor(tasks)
    results = list(itertools.chain(*results))
    print(len(results))
    
def spacy_process(nlp, texts):
    processed_list = [doc for doc in nlp.pipe(texts)]
    return processed_list
    
if __name__ == "__main__":
    main()
    
    
def mp(items, function, cpu, *args):
    batch_size = round(len(items)/cpu)
    partitions = minibatch(items, size=batch_size)
    executor = Parallel(n_jobs=cpu, backend="multiprocessing", prefer="processes")
    do = delayed(partial(function, *args))
    tasks = (do(batch) for batch in partitions)
    results = executor(tasks)
    results = list(itertools.chain(*temp))