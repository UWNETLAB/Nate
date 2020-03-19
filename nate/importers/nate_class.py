"""Definition for the `nate` class, the common ancestor of all `nate` pipelines.

This module defines the `nate` class, which serves as a shared terminus for all 
of this package's importer functions, and as a point of common departure for each
of the package's many pipelines. Typically, users will instantiate `nate` via 
one of the importer functions. The `nate` class can be directly instantiated, 
but this should only be done by experienced users who have taken pains to 
format their input data so as to comply with `nate`'s internal standard.
"""

from pprint import pprint

import spacy
from spacy.pipeline import merge_entities

from ..cooc.cooc_class import Cooc
from ..cooc.cooc_offsets import cooc_offsets
from ..socnet.socnet import SOCnet
from ..svonet.svonet_class import process_svo, SVOnet
from ..utils import nlp_helpers
from ..utils.mp_helpers import mp, mp2
from .edgelist_importers import EdgelistMixin
from collections import namedtuple
from typing import List, NamedTuple


class Nate(EdgelistMixin):
    """The `nate` package's eponymous base class. 
    
    Each of the `nate` package's importer functions returns a populated instance
    of the `nate` class. This class contains the data and methods necessary to 
    initialize any of the subsidary pipelines for network analysis with text.

    Calling an instance of this class directly is functionally identical to 
    calling the `head()` method with no arguments - both return the first
    5 'rows' of the dataset. 

    Attributes:
        data: A list of `NamedTuples` containing the project's formatted dataset.
        texts: A list of text documented, derived from the `data` attribute.
        time: A list of epoch times, derived from the `data` attribute.

    """
    
    def __init__(self, data: List[NamedTuple]):
        """Inits `nate`. See `nate` class docstring.
        """ 
        self.data: List[NamedTuple] = data
        self.texts = self.list_texts()
        self.time = self.list_time()

    def __call__(self, start: int = 0, end: int = 5):
        """[summary]
        
        Args:
            start (int, optional): [description]. Defaults to 0.
            end (int, optional): [description]. Defaults to 5.
        """
        pprint(self.data[start:end])

    def __getitem__(self, index):
        """[summary]
        
        Args:
            index ([type]): [description]
        
        Returns:
            [type]: [description]
        """
        return self.data[index]
        
    def preprocess(self, bigrams = False, custom_filter = False, model="en_core_web_sm"):
        """[summary]
        
        Args:
            bigrams (bool, optional): [description]. Defaults to False.
            custom_filter (bool, optional): [description]. Defaults to False.
            model (str, optional): [description]. Defaults to "en_core_web_sm".
        """
        self.bigrams = bigrams
        self.model = model
        self.custom_filter = custom_filter

        if custom_filter:
            # note that for mp on Windows, custom_filter must be defined in a python file and imported
            self.nlp = spacy.load(self.model, disable=['parser'])
            self.nlp.add_pipe(merge_entities)
            self.nlp.add_pipe(custom_filter, name="custom_filter", last=True)
            if bigrams == True:
                self.texts = nlp_helpers.bigram_process(self.texts, tokenized = False)
            self.post_nlp = mp(self.texts, custom_filter, nlp_helpers.spacy_process, self.nlp)
        else:
            self.nlp = spacy.load(self.model, disable=['parser'])
            self.nlp.add_pipe(merge_entities)
            self.nlp.add_pipe(nlp_helpers.default_filter_lemma, name="filter_lemmatize", last=True)
            if bigrams == True:
                self.texts = nlp_helpers.bigram_process(self.texts, tokenized = False)
            self.post_nlp = mp(self.texts, nlp_helpers.spacy_process, self.nlp)

    def head(self, start:int = 0, end:int = 5):
        """[summary]
        
        Args:
            start (int, optional): [description]. Defaults to 0.
            end (int, optional): [description]. Defaults to 5.
        """
        pprint(self.data[start:end])

    def list_texts(self, start:int = None, end:int = None):
        """[summary]
        
        Args:
            start (int, optional): [description]. Defaults to None.
            end (int, optional): [description]. Defaults to None.
        
        Returns:
            [type]: [description]
        """
        return [str(i.text) for i in self.data[start:end]]

    def list_time(self, start:int = None, end:int = None):
        """[summary]
        
        Args:
            start (int, optional): [description]. Defaults to None.
            end (int, optional): [description]. Defaults to None.
        
        Returns:
            [type]: [description]
        """
        return [i.time for i in self.data[start:end]]

    def list_ids(self, start:int = None, end:int = None): 
        """[summary]
        
        Args:
            start (int, optional): [description]. Defaults to None.
            end (int, optional): [description]. Defaults to None.
        
        Returns:
            [type]: [description]
        """
        return [i.unique_id for i in self.data[start:end]]

    def list_column(self, column_name:str, start:int = None, end:int = None): 
        """[summary]
        
        Args:
            column_name (str): [description]
            start (int, optional): [description]. Defaults to None.
            end (int, optional): [description]. Defaults to None.
        
        Returns:
            [type]: [description]
        """
        return [getattr(i, column_name) for i in self.data[start:end]]

    def cooc_pipeline(self, minimum_offsets = 20, custom_filter = False): 
        """[summary]
        
        Args:
            minimum_offsets (int, optional): [description]. Defaults to 20.
            custom_filter (bool, optional): [description]. Defaults to False.
        
        Returns:
            [type]: [description]
        """
            
        offset_dict, lookup = cooc_offsets(self.post_nlp, self.time, minimum_offsets)
        
        return Cooc(offset_dict, lookup, minimum_offsets)

    def socnet_pipeline(self, subset:int = None):
        """[summary]

        Returns an instance of the 'socnet_pipe' class, initialized with the relevant data contained.
        The 'Subset' parameter allows users to specify the maximum number of edges to calculate.
        
        Args:
            subset (int, optional): [description]. Defaults to None.
        
        Returns:
            [type]: [description]
        """
        return SOCnet(self.data, self.edgelist[slice(subset)])

    def svo_pipeline(self, sub_tags=False, obj_tags=False, bigrams = False, model="en_core_web_sm"):
        """[summary]
        
        Args:
            sub_tags (bool, optional): [description]. Defaults to False.
            obj_tags (bool, optional): [description]. Defaults to False.
            bigrams (bool, optional): [description]. Defaults to False.
            model (str, optional): [description]. Defaults to "en_core_web_sm".
        
        Returns:
            [type]: [description]
        """

        # add error check for custom_filter, which cannot be applied in this step for svo
        self.model = model
        
        if bigrams == True:
            self.texts = nlp_helpers.bigram_process(self.texts, tokenized = False)
            
        self.nlp = spacy.load(self.model)
        self.nlp.add_pipe(merge_entities)
        self.nlp.add_pipe(nlp_helpers.svo_component, name="svo_component", last=True)
        
        self.post_svo = mp(self.texts, nlp_helpers.spacy_process, self.nlp, sub_tags, obj_tags)
        
        sentences = [x[0] for x in self.post_svo]
        svo_items = [x[1] for x in self.post_svo]
        
        return SVOnet(sentences, svo_items, self.time)
