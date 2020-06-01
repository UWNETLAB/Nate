"""Implements extra NamedTuple functionality."""

from collections import namedtuple
from typing import List, NamedTuple


def define_named_tuple(observation_name, attribute_names: List[str]):
    """Creates a new subclass of NamedTuple."""
    output_tuple = namedtuple(observation_name, attribute_names)

    return output_tuple


def create_observation_list(observation_name: str,
                            **kwargs) -> List[NamedTuple]:
    """Creates an observation list of NamedTuples.
    
    This function builds a new NamedTuple type from the lists passed as
    kwargs, with each field given the name of the keyword it was passed with.

    This function requires that all lists passed as kwargs are the same length.

    Args:
        observation_name (str): The name given to the new NamedTuple type.
        **kwargs: Lists containing data for each observation. The keyword
            passed with each list will become the name of that field in the
            resulting NamedTuple type.

    Returns:
        List[NamedTuple]: A list of NamedTuples, with each tuple corresponding
            to one observation.
    
    Raises:
        Exception: If the lists passed as kwargs are not the same length.
    """
    custom_named_tuple = define_named_tuple(observation_name,
                                            list(kwargs.keys()))

    #Length check: all of the lists fed in MUST be of the same length

    arg_lengths = [len(arg) for arg in kwargs.values()]
    arg_length = set(arg_lengths)

    if len(arg_length) != 1:
        raise Exception("Not all of the input data is the same length.")

    observation_list = []

    for i in range(0, arg_length.pop()):

        variables = []

        for arg in kwargs:
            variables.append(kwargs[arg][i])

        observation_list.append(custom_named_tuple(*variables))

    return observation_list


def tupleize(series_dict, tuple_name="obs"):
    """Creates an observation list of NamedTuples."""
    kwarg_dict = {}

    keys = [i for i in series_dict.keys()]

    for i in range(0, len(keys)):
        kwarg_dict[keys[i]] = list(series_dict[keys[i]])

    return create_observation_list(tuple_name, **kwarg_dict)
