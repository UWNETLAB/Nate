"""
This is a MODULE docstring
"""

from pprint import pprint

import spacy
from spacy.pipeline import merge_entities

from ..cooc.cooc_class import cooc
from ..cooc.cooc_offsets import cooc_offsets
from ..socnet.socnet import socnet_pipe
from ..svonet.svonet_class import process_svo, svonet
from ..utils import nlp_helpers
from ..utils.mp_helpers import mp, mp2
from .edgelist_importers import edgelist_mixin


class nate(edgelist_mixin):
    """
    This is the `nate` package's base class. Each of the importer functions the `nate` package loads into namespace returns a populated instance of the `nate` class.

    Calling this class directly is functionally identical to calling the `head()` method with no arguments - both return the first 5 'rows' of the dataset. 
    """
    def __init__(self, data):
        self.data = data
        self.texts = self.list_texts()
        self.time = self.list_time()

    def __call__(self, start:int = 0, end:int = 5):
        """
        This is a docstring
        """
        pprint(self.data[start:end])

    def __getitem__(self, index):
        """
        This is a docstring
        """
        return self.data[index]
        
    def preprocess(self, bigrams = False, custom_filter = False, model="en_core_web_sm"):
        """
        This is a docstring
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
        """
        This is a docstring
        """
        pprint(self.data[start:end])

    def list_texts(self, start:int = None, end:int = None):
        """
        This is a docstring
        """
        return [str(i.text) for i in self.data[start:end]]

    def list_time(self, start:int = None, end:int = None):
        """
        This is a docstring
        """
        return [i.time for i in self.data[start:end]]

    def list_ids(self, start:int = None, end:int = None): 
        """
        This is a docstring
        """ 
        return [i.unique_id for i in self.data[start:end]]

    def list_column(self, column_name:str, start:int = None, end:int = None): 
        """
        This is a docstring
        """ 
        return [getattr(i, column_name) for i in self.data[start:end]]

    def cooc_pipeline(self, minimum_offsets = 20, custom_filter = False): 
        """
        Returns an instance of the 'cooc' class, initialized with the relevant data contained 
        """
            
        offset_dict, lookup = cooc_offsets(self.post_nlp, self.time, minimum_offsets)
        
        return cooc(offset_dict, lookup, minimum_offsets)

    def socnet_pipeline(self, subset:int = None):
        """
        Returns an instance of the 'socnet_pipe' class, initialized with the relevant data contained.
        The 'Subset' parameter allows users to specify the maximum number of edges to calculate.
        """ 
        return socnet_pipe(self.data, self.edgelist[slice(subset)])

    def svo_pipeline(self, sub_tags=False, obj_tags=False, bigrams = False, model="en_core_web_sm"):
        """
        This is a docstring
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
        
        return svonet(sentences, svo_items, self.time)
