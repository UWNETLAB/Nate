from typing import List, Union
from .named_tuple_generator import define_named_tuple
from .timestamp_process import convert_times
from .nate_class import nate


def import_text(strings):
    """
    This is a docstring
    """
    if isinstance(strings, str):
        strings = [strings]
    
    text_only_namedtuple = define_named_tuple('obs', ['text'])

    return nate([text_only_namedtuple(string) for string in strings])


def import_files(files):
    """
    Directly imports a text file (or list of text files) into `nate`. 
    """

    if isinstance(files, str):
        files = [files]
    
    obs_list = []
    text_only_namedtuple = define_named_tuple('obs', ['text'])

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as stream:
            obs_list.append(text_only_namedtuple(stream.read().replace('\n', '')))

    return nate(obs_list)


def import_dict(dictionary):
    """
    IMPLEMENT
    """
    pass


def import_lists(text:List,  time:List = None, unique_id:List = None):
    """
    IMPLEMENT
    """
    pass

