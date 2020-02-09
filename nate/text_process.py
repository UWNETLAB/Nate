import spacy
import pandas as pd
import numpy as np
import os
from spacy.pipeline import merge_entities
from joblib import dump, load, Parallel, delayed, cpu_count
from toolz import partition_all
import itertools


def main():   #execute all functions within main to protect against multiprocessing infinite feedback loop
    
        if cpu_count() >= 8:   #to avoid overtaxing Brad, save some cores
            cpu = 10
        else:
            cpu = cpu_count()
            
        nlp = spacy.load('en', disable=['parser'])
        nlp.add_pipe(merge_entities)
        
        df = pd.read_csv('../data/test.csv')
        texts = df['content'].tolist()
        times = df['publish_date'].tolist()
        
        texts = texts[:10000]
        
        
        processed_list = mp(texts, spacy_process, cpu, nlp)
        print(len(processed_list))
        
def spacy_process(texts, nlp):
    processed_list = []
    for doc in nlp.pipe(texts):  # nlp.pipe sends texts to spacy_process in batches for efficiency. Default is 128 (should experiment)
        processed = []
        for token in doc:
            if token.is_stop == False and len(token) > 1:  # don't bother with single char tokens
                processed.append(token.lemma_.lower())  # keeping lemmatized version of each NOUN and PROPN
        processed_list.append(processed) # add the doc's processed words to the list of processed documents
    return processed_list
    
    
def mp(items, function, cpu, *args):
    batch_size = round(len(items)/cpu)
    partitions = partition_all(batch_size, items)
    temp = Parallel(n_jobs=cpu, max_nbytes=None)(delayed(function)(v, *args) for v in partitions)
    results = list(itertools.chain(*temp))
    return results
    
if __name__ == '__main__':
    main()