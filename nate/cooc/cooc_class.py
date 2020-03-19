"""
This is a MODULE docstring
"""
from typing import Dict
from ..edgeburst.burst_mixin import BurstMixin

class Cooc(BurstMixin):
    """
    This is a docstring
    """
    def __init__(self, offset_dict: Dict, lookup: Dict, minimum_offsets: int = 20):
        self.offset_dict = offset_dict
        self.lookup = lookup
        self.minimum_offsets = minimum_offsets
        self.from_svo = False

