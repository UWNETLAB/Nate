"""
This is a MODULE docstring
"""
from typing import Dict, Union, List
from ..edgeburst.burst_mixin import BurstMixin
from nate.edgeburst.burst_class import Bursts


class Cooc(BurstMixin):
    """
    This is a docstring
    """

    def __init__(self,
                 offset_dict: Dict,
                 lookup: Dict,
                 minimum_offsets: int = 20):
        self.offset_dict = offset_dict
        self.lookup = lookup
        self.minimum_offsets = minimum_offsets
        self.from_svo = False


    def __getitem__(self, index: Union[slice, int, tuple]):
        """Called when `Cooc` is accessed using indexing or slicing.
        
        Args:
            index (slice): A range of integers used to retrieve corresponding entries
                in the `offset_dict` attribute.
        
        Returns:
            A list of named tuples, each corresponding to one row in the dataset. 
        """

        if isinstance(index, slice) or isinstance(index, int):
            return list(self.offset_dict.items())[index]
        else:
            return self.offset_dict[index]


    def cooc_to_burst(self, s=2, gamma=1):
        """[summary]
        
        Args:
            s (int, optional): [description]. Defaults to 2.
            gamma (int, optional): [description]. Defaults to 1.
        
        Returns:
            [type]: [description]
        """
        offset_dict_strings, edge_burst_dict_strings, s, gamma, from_svo, lookup = self.burst_detection(
            s, gamma)

        return Bursts(offset_dict_strings, edge_burst_dict_strings, s, gamma,
                      from_svo, lookup)
