"""Import text, and only text, directly into `Nate``."""

from typing import List, Union
from .named_tuple_generator import define_named_tuple
from .nate_class import Nate
from .timestamp_process import convert_time

text_only_namedtuple = define_named_tuple('obs', ['text'])


def import_text(strings):
    """Directly imports a string (or a list of strings) into `nate`.

    Args:
        strings (Union(str, List[str])): A string or a list of strings.

    Returns:
        Nate: An instance of the `Nate` class.
    """
    if isinstance(strings, str):
        strings = [strings]

    return Nate([text_only_namedtuple(string) for string in strings])


def import_files(files):
    """Directly imports a text file (or list of text files) into `nate`.

    Args:
        files (Union(str, List[str])): A filename or list of filenames to be
            loaded from disk.

    Returns:
        Nate: A `Nate` object containing only the text data given.
    """
    if isinstance(files, str):
        files = [files]

    obs_list = []

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as stream:
            obs_list.append(
                text_only_namedtuple(stream.read().replace('\n', ' ')))

    return Nate(obs_list)


def import_dict_of_dicts(dictionary, text, time=None, values_to_keep=[]):
    """Imports a dict of dicts into `nate`.
    
    Args:
        dictionary (Dict): A dict of dicts, with the keys of the outer dict
            corresponding to unique observation ids.
        text (str): The name of the text entry in each inner dict. 
        time (str, optional): The name of the time entry in each inner dict.
        values_to_keep (List[str], optional): A list of keys which appear in 
            all inner dicts. The values will be kept in the resulting `Nate` 
            object.

    Returns:
        Nate: An instance of the `Nate` class.
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


def import_lists(text: List, time: List = None, unique_id: List = None):
    """Imports a number of list into `nate`.
    
    [Note: it might be a good idea to add a **kwargs parameter so that
    users can pass arbitrary other lists, similar to values_to_keep above.]
    
    Args:
        text (List): A list of strings.
        time (List, optional): A list containing the times each observation
            was recorded.
        unique_id (List, optional): The list containing unique
            identifiers (e.g. a unique name or hash ID#). 
    
    Returns:
        Nate: An instance of the `Nate` class.
    """
    pass
