"""
This is a MODULE docstring
"""
from typing import Dict
from ..edgeburst.burst_mixin import BurstMixin
from nate.edgeburst.burst_class import Bursts

class Cooc(BurstMixin):
    """
    This is a docstring
    """
    def __init__(self, offset_dict: Dict, lookup: Dict, minimum_offsets: int = 20):
        self.offset_dict = offset_dict
        self.lookup = lookup
        self.minimum_offsets = minimum_offsets
        self.from_svo = False

    def cooc_to_burst(self, s = 2, gamma = 1):
        """[summary]
        
        Args:
            s (int, optional): [description]. Defaults to 2.
            gamma (int, optional): [description]. Defaults to 1.
        
        Returns:
            [type]: [description]
        """
        offset_dict_strings, edge_burst_dict_strings, s, gamma, from_svo, lookup = self.burst_detection(s, gamma)

        return Bursts(offset_dict_strings, edge_burst_dict_strings, s, gamma, from_svo, lookup)

        

