"""
This is a MODULE docstring
"""
import pandas as pd
import numpy as np
import os
import itertools
import pickle
from itertools import groupby


def df_export(bursts, offsets, lookup, from_svo = False):
    """
    This is a docstring.
    """        
    key_list =[]
    burst_list = []
    offset_list = []
    for k, v in bursts.items():
        key_list.append(k)
        burst_list.append(v)
        offset_list.append(offsets[k])
    
    if from_svo == True:
        df = pd.DataFrame()
        df['svo_#'] = key_list
        df['svo'] = df['svo_#'].map(lookup)
        
        intensities = max_intensities(burst_list)
               
    else:    
    
        df = pd.DataFrame.from_records(key_list, columns =['word1_#', 'word2_#'])
        df['word1'] = df['word1_#'].map(lookup)
        df['word2'] = df['word2_#'].map(lookup)
        
        intensities = max_intensities(burst_list)
    
    df['bursts'] = intensities
    
    full_df = flatten(df, intensities)
    return full_df
        
def max_intensities(burst_list):
    """
    This is a docstring.
    """
    max_bursts = [{(j,k):i for i,j,k in x} for x in burst_list]
    
    return max_bursts
        
def flatten(df, intensities):
    """
    This is a docstring.
    """
    term_id_list = []
    interval_start_list = []
    interval_end_list = []
    intensity_list = []
    
    for i, term in enumerate(intensities):
        for interval, intensity in term.items():
            term_id_list.append(i)
            interval_start_list.append(interval[0])
            interval_end_list.append(interval[1])
            intensity_list.append(intensity)

    temp_df = pd.DataFrame()
    temp_df['term_id'], temp_df['interval_start'], temp_df['interval_end'], temp_df['intensity'] =\
        term_id_list, interval_start_list, interval_end_list, intensity_list
        
    return_df = pd.merge(df, temp_df, left_index=True, right_on='term_id')
    
    return_df = return_df.sort_values(by=['intensity'], ascending=False)
    
    return return_df
    
def max_bursts_export(bursts, lookup, from_svo = False):
    """
    This is a docstring.
    """
    key_list =[]
    burst_list = []
    
    for k, v in bursts.items():
        key_list.append(k)
        burst_list.append(v)

    if from_svo:
        df = pd.DataFrame()
        df['svo_#'] = key_list
        df['svo'] = df['svo_#'].map(lookup)
        
        intensities = max_intensities(burst_list)
        
        max_bursts = {df['svo'][x]: intensities[x] for x in df.index}        
    else:
        
        df = pd.DataFrame.from_records(key_list, columns =['word1_#', 'word2_#'])
        df['word1'] = df['word1_#'].map(lookup)
        df['word2'] = df['word2_#'].map(lookup)

        intensities = max_intensities(burst_list)

        max_bursts = {(df['word1'][x],df['word2'][x]): intensities[x] for x in df.index}
    
    return max_bursts
    
def all_bursts_export(bursts, offsets, lookup, from_svo = False):
    """
    This is a docstring.
    """        
    key_list =[]
    burst_list = []
    
    for k, v in bursts.items():
        key_list.append(k)
        burst_list.append(v)
        
    if from_svo:
        df = pd.DataFrame()
        df['svo_#'] = key_list
        df['svo'] = df['svo_#'].map(lookup)
        
        all_bursts = {df['svo'][x]: burst_list[x] for x in df.index}        
    else:    
        df = pd.DataFrame.from_records(key_list, columns =['word1_#', 'word2_#'])
        df['word1'] = df['word1_#'].map(lookup)
        df['word2'] = df['word2_#'].map(lookup)

        all_bursts = {(df['word1'][x],df['word2'][x]): burst_list[x] for x in df.index}
    
    return all_bursts

def offsets_export(offsets, lookup, from_svo = False):
    """
    This is a docstring.
    """
    key_list = []
    offset_list = []
    
    for k, _ in offsets.items():
        key_list.append(k)
        offset_list.append(offsets[k])
    
    if from_svo:
        df = pd.DataFrame()
        df['svo_#'] = key_list
        df['svo'] = df['svo_#'].map(lookup)
        
        offsets = {df['svo'][x]: offset_list[x] for x in df.index}

    else:    
        df = pd.DataFrame.from_records(key_list, columns =['word1_#', 'word2_#'])
        df['word1'] = df['word1_#'].map(lookup)
        df['word2'] = df['word2_#'].map(lookup)
        
        offsets = {(df['word1'][x],df['word2'][x]): offset_list[x] for x in df.index}
    
    return offsets