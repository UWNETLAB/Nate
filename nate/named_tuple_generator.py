from collections import namedtuple
from typing import List, Tuple, NamedTuple


# Define Named Tuple

def define_named_tuple(observation_name:str, attribute_names:List[str]) -> NamedTuple:
    
    output_tuple:NamedTuple = namedtuple(observation_name, attribute_names)

    return output_tuple






