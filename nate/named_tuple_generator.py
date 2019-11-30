from collections import namedtuple
from typing import List, Tuple, NamedTuple


# Define Named Tuple

def define_named_tuple(observation_name, attribute_names:List[str]) -> NamedTuple:
    
    output_tuple:NamedTuple = namedtuple(observation_name, attribute_names)

    return output_tuple


def create_observation_list(observation_name:str, **kwargs) -> List[NamedTuple]:

    custom_named_tuple = define_named_tuple(observation_name,  list(kwargs.keys()))
    
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
    