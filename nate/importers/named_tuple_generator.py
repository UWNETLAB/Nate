"""
This is a MODULE docstring
"""

from collections import namedtuple
from typing import List, NamedTuple


def define_named_tuple(observation_name, attribute_names: List[str]):
    """
    This is a docstring.
    """
    output_tuple = namedtuple(observation_name, attribute_names)

    return output_tuple


def create_observation_list(observation_name: str,
                            **kwargs) -> List[NamedTuple]:
    """
    This is a docstring.
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
    """
    This is a docstring.
    """
    kwarg_dict = {}

    keys = [i for i in series_dict.keys()]

    for i in range(0, len(keys)):
        kwarg_dict[keys[i]] = list(series_dict[keys[i]])

    return create_observation_list(tuple_name, **kwarg_dict)
