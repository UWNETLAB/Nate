"""
This is a MODULE docstring
"""
from typing import List, Union
from .named_tuple_generator import define_named_tuple
from .nate_class import Nate
from .timestamp_process import convert_time

text_only_namedtuple = define_named_tuple('obs', ['text'])

def import_text(strings):
    """
    This is a docstring
    """
    if isinstance(strings, str):
        strings = [strings]
    
    return Nate([text_only_namedtuple(string) for string in strings])
 

def import_files(files):
    """
    Directly imports a text file (or list of text files) into `nate`. 
    """

    if isinstance(files, str):
        files = [files]
    
    obs_list = []

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as stream:
            obs_list.append(text_only_namedtuple(stream.read().replace('\n', '')))

    return Nate(obs_list)


def import_dict_of_dicts(dictionary, text, time = None, values_to_keep = []):
    """
    Used for importing data contained in a dictionary of dictionaries, where the keys of the outer dict correspond with unique_ids. 
    
    The `values_to_keep` argument accepts a list of keys which appear in all of the dictionaries nested in the outer dictionary; the 
    values therein will be passed into the resulting `nate` object.
    """

    lookup_list = [text]
    named_list = ['unique_id', 'text']

    if time != None:
        lookup_list.append(time)
        named_list.append('time')

    lookup_list.extend(values_to_keep)
    named_list.extend(values_to_keep)

    dict_namedtuple = define_named_tuple('obs', named_list)

    obs_list = []

    for key, subdict in dictionary.items():
        filtered_values = []
        for value in lookup_list:

            value_to_append = subdict[value]

            if value == 'time':
                value_to_append = convert_time(value_to_append)

            filtered_values.append(value_to_append)

        obs_list.append(dict_namedtuple(key, *filtered_values))

    return Nate(obs_list)


def import_lists(text:List,  time:List = None, unique_id:List = None):
    """
    Not yet implemented
    """
    pass

