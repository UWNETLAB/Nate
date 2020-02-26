import pandas as pd
import numpy as np
import os
import spacy
import pickle
from joblib import dump, load, Parallel, delayed, cpu_count
from joblib import parallel_backend
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models.phrases import Phrases, Phraser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from toolz import partition_all
import itertools
import time
from tqdm import tqdm
from gensim.utils import simple_preprocess

from scipy.sparse import vstack

from numpy.lib.stride_tricks import as_strided    # for removing the diagonal (self-self comparison) in a matrix

from sklearn.metrics.pairwise import linear_kernel  # equal to cosine_similarity for L2 normalized data

from sklearn import preprocessing

from yaml import load
 


def mp(items, function, cpu, *args):
    batch_size = round(len(items)/cpu)  # split the list of items so that each CPU receives one batch
    partitions = partition_all(batch_size, items)
    temp = Parallel(n_jobs=cpu, max_nbytes=None)(delayed(function)(v, *args) for v in partitions) #executes the function on each batch
    results = list(itertools.chain(*temp)) # joblib.delayed returns a list of lists (ie. list of each batch result), concatenate them
    return results

# same as above, but when 2 lists of results are needed
def mp2(items, function, cpu, *args):
    batch_size = round(len(items)/cpu)
    partitions = partition_all(batch_size, items)
    temp = Parallel(n_jobs=cpu, max_nbytes=None)(delayed(function)(v, *args) for v in partitions)
    results1, results2 = zip(*temp)
    results1 = list(itertools.chain(*results1))
    results2 = list(itertools.chain(*results2))
    return results1, results2

# ibid
def mp3(items, function, cpu, *args):
    batch_size = round(len(items)/cpu)
    partitions = partition_all(batch_size, items)
    temp = Parallel(n_jobs=cpu, max_nbytes=None)(delayed(function)(v, *args) for v in partitions)
    results1, results2, results3 = zip(*temp)
    results1 = list(itertools.chain(*results1))
    results2 = list(itertools.chain(*results2))
    results3 = list(itertools.chain(*results3))
    return results1, results2, results3
    
def mp_shared(items, function, cpu, *args):
    batch_size = round(len(items)/cpu)  # split the list of items so that each CPU receives one batch
    partitions = partition_all(batch_size, items)
    temp = Parallel(n_jobs=cpu, require='sharedmem', max_nbytes=None)(delayed(function)(v, *args) for v in partitions) #executes the function on each batch
    results = list(itertools.chain(*temp)) # joblib.delayed returns a list of lists (ie. list of each batch result), concatenate them
    return results
    
def mp2_shared(items, function, cpu, *args):
    batch_size = round(len(items)/cpu)
    partitions = partition_all(batch_size, items)
    temp = Parallel(n_jobs=cpu, require='sharedmem', max_nbytes=None)(delayed(function)(v, *args) for v in partitions)
    results1, results2 = zip(*temp)
    results1 = list(itertools.chain(*results1))
    results2 = list(itertools.chain(*results2))
    return results1, results2
    
def mp3_shared(items, function, cpu, *args):
    batch_size = round(len(items)/cpu)
    partitions = partition_all(batch_size, items)
    temp = Parallel(n_jobs=cpu, require='sharedmem', max_nbytes=None)(delayed(function)(v, *args) for v in partitions)
    results1, results2, results3 = zip(*temp)
    results1 = list(itertools.chain(*results1))
    results2 = list(itertools.chain(*results2))
    results3 = list(itertools.chain(*results3))
    return results1, results2, results3
    

    
    
def dissim_rba(auth_list, auth_alt_dict, auth_alt_dict_2, auth_vectors):
    rb_avg_dissims = []
    ring_avg_dissims = []
    bridge_avg_dissims = []
    for batch_list in batch(auth_list, 50):
        comp_list = []
        for author in batch_list:
            comp_list += [author]
            comp_list += auth_alt_dict[author]
            comp_list += auth_alt_dict_2[author]
        comp_list = sorted(list(set(comp_list)))
        comp_dict = {k: v for v, k in enumerate(comp_list)}
        comp_vectors = []
        for member in comp_list:
            comp_vectors.append(auth_vectors[member])
        v_array = vstack(comp_vectors)
        dissim_matrix = v_array @ v_array.T
        dissim_matrix = dissim_matrix.todense()

        
        for author in batch_list:

            rb_dissims = []
            ring_dissims = []
            bridge_dissims = []
            if len(auth_alt_dict[author]) > 0:
                alter_list = auth_alt_dict[author]

                for alter in alter_list:
                    if len(auth_alt_dict[alter]) > 1:
                        alter_2_list = auth_alt_dict[alter]
                        ring_list = list_common(alter_list, alter_2_list)
                        bridge_list = list_difference(alter_2_list, alter_list)
                        alter_2_list_trim = [x for x in alter_2_list if x != author]
                        bridge_list_trim = [x for x in bridge_list if x != author]
                        if len(alter_2_list_trim) > 0:
                            alter_dissim = create_average_dissim(alter, alter_2_list_trim, comp_dict, dissim_matrix)
                            rb_dissims.append(1 - alter_dissim)
                        if len(ring_list) > 0:
                            alter_dissim = create_average_dissim(alter, ring_list, comp_dict, dissim_matrix)
                            ring_dissims.append(1 - alter_dissim)                        
                        if len(bridge_list_trim) > 0:
                            alter_dissim = create_average_dissim(alter, bridge_list_trim, comp_dict, dissim_matrix)
                            bridge_dissims.append(1 - alter_dissim)

            if len(rb_dissims) > 0:
                rb_avg_dissims.append(np.round(np.average(rb_dissims), 3))
            else:
                rb_avg_dissims.append('NA')

            if len(ring_dissims) > 0:
                ring_avg_dissims.append(np.round(np.average(ring_dissims), 3))
            else:
                ring_avg_dissims.append('NA')

            if len(bridge_dissims) > 0:
                bridge_avg_dissims.append(np.round(np.average(bridge_dissims), 3))
            else:
                bridge_avg_dissims.append('NA')

    return (rb_avg_dissims, ring_avg_dissims, bridge_avg_dissims)
    
    
def group_avg_dissim(members, vectors):
    member_vectors = []
    for member in members:
        member_vectors.append(vectors[member])
    v_array = vstack(member_vectors)
    group_dissim = 1 - linear_kernel(v_array)
    m = group_dissim.shape[0]
    s0,s1 = group_dissim.strides
    dissim_avg = np.round(np.average(as_strided(group_dissim.ravel()[1:], shape=(m-1,m), strides=(s0+s1,s1)).reshape(m,-1)), 3)

    return dissim_avg    


# perform NLP on a list of texts, requires NLP object from main() function (note for future work: NLP object can't be pickled using
# python's pickle module (fast), so there may be performance gains possible by sorting this out re: disabling Loky in mp() functions)
def spacy_process(texts, nlp):
    processed_list = []
    copyright_stops = ['elsevier', 'right', 'rights', '(c)', 'ltd']   # domain specific stop words to remove
    allowed_postags=['NOUN', 'PROPN']   # parts of speech to keep 
    for doc in nlp.pipe(texts):  # nlp.pipe sends texts to spacy_process in batches for efficiency. Default is 128 (should experiment)
        processed = []
        for token in doc:
            if token.is_stop == False and len(token) > 1:  # don't bother with single char tokens
                if token.text not in copyright_stops and token.pos_ in allowed_postags:
                    processed.append(token.lemma_)  # keeping lemmatized version of each NOUN and PROPN
        processed = ' '.join(processed)   # concat the tokens of the document with whitespace between
        processed_list.append(processed) # add the doc's processed words to the list of processed documents
    return processed_list


# same as above, but with a small batch size for memory constraints
def spacy_process_large(texts, nlp):
    processed_list = []
    copyright_stops = ['elsevier', 'right', 'rights', '(c)', 'ltd']
    allowed_postags=['NOUN', 'PROPN']    
    for doc in nlp.pipe(texts, batch_size=1):
        processed = []
        for token in doc:
            if token.is_stop == False and len(token) > 1:
                if token.text not in copyright_stops and token.pos_ in allowed_postags:
                    processed.append(token.lemma_)
        processed = ' '.join(processed)
        processed_list.append(processed)
    return processed_list



# bigram detection on a list of texts using sklearn's Phrases module. Note: test whether creating trigrams is as simple as calling 
# this process on the text again
def bigram_process(texts):
    words = [simple_preprocess(x, deacc=False) for x in texts]  # very efficient preprocessing into tokens based on white space only
    phrases = Phrases(words, min_count=1, threshold=0.8, scoring='npmi') # bigram model training
    bigram = Phraser(phrases) # creates a leaner specialized version of the bigram model
    bigrams = list(bigram[words]) # concatenate words into bigrams (ie. word1_word2)
    bigrams = [' '.join(words) for words in bigrams]
    return bigrams



def list_difference(list1, list2):
    return (list(set(list1) - set(list2)))

def list_common(list1, list2):
    return (list(set(list1).intersection(list2)))

#not used for now


def batch(batch_list, n=1):
    l = len(batch_list)
    for ndx in range(0, l, n):
        yield batch_list[ndx:min(ndx + n, l)]
        
def create_average_dissim(ego, alters, index_dict, matrix):
    dissims = []
    ego_idx = index_dict[ego]
    for alter in alters:
        alter_idx = index_dict[alter]
        
        dissim = matrix[ego_idx, alter_idx]

        dissims.append(dissim)
    dissim_avg = np.round(np.average(dissims), 3)
    return dissim_avg


def dissim_alters(auth_list, auth_alt_dict, auth_alt_dict_2, auth_vectors):
    alters_avg_dissims = []
    alters_2_avg_dissims = []
    for batch_list in batch(auth_list, 4):
        comp_list = []
        for author in batch_list:
            comp_list += [author]
            if author in auth_alt_dict and len(auth_alt_dict[author]) > 0:
                comp_list += auth_alt_dict[author]
            if author in auth_alt_dict and len(auth_alt_dict_2[author]) > 0:
                comp_list += auth_alt_dict_2[author]
        comp_list = sorted(list(set(comp_list)))
        comp_dict = {k: v for v, k in enumerate(comp_list)}
        comp_vectors = []
        for member in comp_list:
            comp_vectors.append(auth_vectors[member])
        v_array = vstack(comp_vectors)
        dissim_matrix = v_array @ v_array.T
        dissim_matrix = dissim_matrix.todense()
        
        for author in batch_list:
            if author in auth_alt_dict and len(auth_alt_dict[author]) > 0:
                alter_list = auth_alt_dict[author]
                alter_dissim = create_average_dissim(author, alter_list, comp_dict, dissim_matrix)
                alters_avg_dissims.append(1 - alter_dissim)
            else:
                alters_avg_dissims.append('NA')
            if author in auth_alt_dict_2 and len(auth_alt_dict_2[author]) > 0:
                alter_list = auth_alt_dict_2[author]
                alter_dissim = create_average_dissim(author, alter_list, comp_dict, dissim_matrix)
                alters_2_avg_dissims.append(1 - alter_dissim)
            else:
                alters_2_avg_dissims.append('NA')

    return (alters_avg_dissims, alters_2_avg_dissims)

def single_avg_dissim(ego, alter_list, vectors):
    ego_vector = vectors[ego]
    alter_vectors = []
    if len(alter_list) > 1:
        for alter in alter_list:    # create list of word vectors for each alter in the list
            alter_vectors.append(vectors[alter])
        v_array = vstack(alter_vectors)  # stack the list of vectors into a numpy array of shape 1 x the number of alters
        ego_dissim = 1 - linear_kernel(ego_vector, v_array)  # pairwise comparison of author vector to all  vectors in the array
        dissim_avg = np.round(np.average(ego_dissim), 3) # average the above results
    else:
        alter = alter_list[0] # if author has only 1 alter, no vstack is needed
        dissim_avg = np.round(np.average(1 - linear_kernel(ego_vector, vectors[alter])), 3)
    return dissim_avg

#not used for now
# def group_avg_dissim(members, vectors):
#     member_vectors = []
#     for member in members:
#         member_vectors.append(vectors[member])
#     v_array = vstack(member_vectors)
#     group_dissim = 1 - linear_kernel(v_array)
#     m = group_dissim.shape[0]
#     s0,s1 = group_dissim.strides
#     dissim_avg = np.round(np.average(as_strided(group_dissim.ravel()[1:], shape=(m-1,m), strides=(s0+s1,s1)).reshape(m,-1)), 3)

#     return dissim_avg    
    
def main():   #execute all functions within main to protect against multiprocessing infinite feedback loop
    
        if cpu_count() >= 8:   #to avoid overtaxing Brad, save some cores
            cpu = 10
        else:
            cpu = cpu_count()
            
        with open('../input/generated_meta_strings.pkl', "rb") as pkl:   # dictionary with authors as keys and their strings as values 
            auth_strings = pickle.load(pkl)

        with open('../input/alter_lists.pkl', "rb") as pkl:  # dataframe with author column, alters column, and alters_2 column
            alter_lists = pickle.load(pkl)


        auth_alt_dict = dict(zip(alter_lists.author, alter_lists.alter)) # dict of {auth:alter list}
        auth_alt_dict_2 = dict(zip(alter_lists.author, alter_lists.alter_2)) # dict of {auth: alter_2 list}
        auth_list = sorted(list(auth_strings.keys()))[:] # list of author names

            
        abs_list = [] # list of author strings to process
        
        # NOTE: this is only safe because the auth_strings dict hasn't been modified. Should be modified for posterity
        for author in auth_list: 
            abs_list.append(auth_strings[author]["meta_string"])

        del auth_strings

        bigram_text = bigram_process(abs_list)  # find and concatenate bigrams in the author string list

        # load spacy model, disable unnecessary parser and named entity recog for performance
        #spacy.require_gpu()
        nlp = spacy.load('en', disable=['parser', 'ner'])   
        
        #nlp.max_length = 10000000   # community strings are very large, may cause memory problems on modest PCs - needs rethinking
        
        # send bigrammed text and spacy function + its required variables to multiprocess function for execution
        processed_list = mp(bigram_text, spacy_process, cpu, nlp)  
        vectorizer = TfidfVectorizer(max_df=0.5, min_df=3, stop_words='english', norm='l2')  
        matrix = vectorizer.fit_transform(processed_list) # Tfidf vectors for each author string
        auth_vectors = dict(zip(auth_list, matrix)) # creat a dict of {author : tfidf vector}
        

        #create a dataframe by sending list of authors and the dissim function + its required variables to multiprocess function 
        sim_df = pd.DataFrame()
        sim_df['author'] = pd.Series(auth_list)
        sim_df['dissim_alters'], sim_df['dissim_alters_2'] = pd.Series(mp2_shared(auth_list, dissim_alters, cpu, auth_alt_dict, auth_alt_dict_2, auth_vectors)).array
        sim_df['alter_dissim_avg'], sim_df['bridge_dissim_avg'], sim_df['first_ring_dissim_avg'] =\
            pd.Series(mp3_shared(auth_list, dissim_rba, cpu, auth_alt_dict, auth_alt_dict_2, auth_vectors)).array

        sim_df.to_csv('../output/sim_scores.csv', index=False)
        
if __name__ == '__main__':
    main()

