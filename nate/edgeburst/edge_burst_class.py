from .generate_offsets import generate_offsets
from .burst_detection import bursts
from typing import List, Dict
import pickle
from ..mp_suite.generic_mp import mp


class edge_burst():
    """
    If subset_data is set to 0 (which it is, by default), `edge_burst` will include all observations. 
    """
    def __init__(self, data):

        self.texts = data.list_texts()
        self.timestamps = data.list_timestamps()

    def generate_offset(self, minimum_offsets = 10, subset_data:int = 0, save_spacy = None):
        """
        This is a docstring
        """
        self.minimum_offsets = minimum_offsets
        self.subset_data = subset_data
        self.pickle_path = pickle_path
        self.save_spacy = save_spacy
        
        if self.subset_data > 0: # This can be used to limit the number of cases for testing purposes
            self.texts = self.texts[0:self.subset_data] 
            self.timestamps = self.timestamps[0:self.subset_data] 

        self.offset_dict, self.lookup = generate_offsets(self.texts, self.timestamps, self.minimum_offsets, self.save_spacy)


    def burst_detection(self, s:float = 2, gamma:float = 1):
        """
        Returns an object of the class `bursts_for_parameters`

        This method is used to detect bursts for _all_ of the term-term pairs in the offset dictionary generated when this class (`edge_burst`) was instantiated.
        This method is best employed as an exploratory tool for identifying unusually bursty term pairs, or groups of term pairs with correlated burst patterns.  

        Since calling this method on an entire dataset can consume significant amounts of time and memory, this method only allows for one value of s and one value of gamma.

        If you wish to detect bursts using a variety of different values for the s and gamma parameters, instead utilize the `multi_bursts` method contained in this class. 
        """
        self.s = s
        self.gamma = gamma
        bursts_instance = bursts(self.offset_dict,self.lookup,s,gamma)

        return bursts_instance


    def multi_burst(self, token_pairs:List, s:List, gamma:List) -> Dict:
        """
        The lists passed to s and gamma must be exactly the same length.

        Returns a dictionary where keys are strings containing two numbers separated by an underscore, corresponding to the s and gamma values for the run, respectively.
        The values of each entry in the dictionary consists of {SOMETHING}
        """
        assert len(s) == len(gamma)

        run_dict = {}
        offset_subset_dict = {}

        for token_pair in token_pairs:
            offset_subset_dict[token_pair] = self.offset_dict[token_pair]

        for i in range(0,len(s)):
            run_name = "{}_{}".format(str(s[i]), str(gamma[i]))
            run_result = bursts(self.offset_dict,self.lookup, s[i], gamma[i])
            run_dict[run_name] = run_result

        return run_dict
