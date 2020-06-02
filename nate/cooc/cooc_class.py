"""Definition of the `Cooc` pipeline, for co-occurence analysis.

This module defines the `Cooc` pipeline, [description of cooc pipeline functionality].
"""
from typing import Dict, Union, List
from ..edgeburst.burst_mixin import BurstMixin
from nate.edgeburst.burst_class import Bursts


class Cooc(BurstMixin):
    """The main object in the `Cooc` pipeline.

    Attributes:
        offset_dict (Dict): A dictionary with term-term pairs as keys and a list
            of times when they occur as values.
        lookup (Dict): A dictionary with the integer representation of a term as
            key and the string representation as value.
        minimum_offsets (int): The minimum number of 'offsets' - or occurrences
            in the dataset - a given token/term pair must have had in order to
            be retained.
        from_svo (Bool): A flag to be passed to future steps in the pipeline
            marking whether the data descended from an SVO class. 
            [Should be removed on future development.]
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
            List: A list of named tuples, each corresponding to one row in the dataset. 
        """

        if isinstance(index, slice) or isinstance(index, int):
            return list(self.offset_dict.items())[index]
        else:
            return self.offset_dict[index]


    def cooc_to_burst(self, s=2, gamma=1):
        """Returns an instance of the `Bursts` class.
        
        Args:
            s (float, optional): s parameter for tuning Kleinberg algorithm.
                Higher values make it more difficult for bursts to move up the
                burst hierarchy. Defaults to 2.
            gamma (float, optional): gamma parameter for tuning Kleinberg
                algorithm. Higher values make it more difficult for activity to
                be considered a burst. Defaults to 1.
        
        Returns:
            Bursts: An instance of the `Bursts` class containing data from the
                instance of the `Cooc` class it was called from.
        """
        offset_dict_strings, edge_burst_dict_strings, s, gamma, from_svo, lookup = self.burst_detection(
            s, gamma)

        return Bursts(offset_dict_strings, edge_burst_dict_strings, s, gamma,
                      from_svo, lookup)
