"""
This is a MODULE docstring
"""
from typing import List, Dict
import pickle
from ..utils.mp_helpers import mp
from ..edgeburst.burst_mixin import burst_mixin

class cooc(burst_mixin):
    """
    This is a docstring
    """
    def __init__(self, offset_dict, lookup, minimum_offsets = 20):
        self.offset_dict = offset_dict
        self.lookup = lookup
        self.minimum_offsets = minimum_offsets
        self.from_svo = False

