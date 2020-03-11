from pprint import pprint
from ..cooc.cooc_class import cooc
from ..svo.process import process_svo, svo_to_df
from .edgelist_importers import edgelist_mixin
from ..socnet.socnet import socnet_pipe
from ..utils import nlp_helpers
from ..utils.mp_helpers import mp
import spacy
from spacy.pipeline import merge_entities
from ..cooc.generate_offsets import generate_offsets

class nate(edgelist_mixin):
    """
    This is the `nate` package's base class. Each of the importer functions the `nate` package loads into namespace returns a populated instance of the `nate` class.

    Calling this class directly is functionally identical to calling the `head()` method with no arguments - both return the first 5 'rows' of the dataset. 
    """
    def __init__(self, data):
        self.data = data
        #self.fields = data[0]._fields
        self.post_nlp = nlp_helpers.get_spacy_text(self.list_texts())

    def __call__(self, start:int = 0, end:int = 5):
        """
        This is a docstring
        """
        pprint(self.data[start:end])

    def __getitem__(self, index):
        return self.data[index]

    def head(self, start:int = 0, end:int = 5):
        """
        This is a docstring
        """
        pprint(self.data[start:end])

    def list_texts(self, start:int = None, end:int = None):
        return [i.text for i in self.data[start:end]]

    def list_nlp_text(self, start:int = None, end:int = None, bigrams = False, tokenized = False, nlp = False, custom_component = False, standard_component = False, merge_ents = False):
        """
        Returns a list of texts
        """ 
        texts = [str(i.text) for i in self.data[start:end]]
        if bigrams == True:
            texts = nlp_helpers.bigram_process(texts, tokenized=tokenized)        
        if nlp == True:
            nlp = spacy.load('en_core_web_sm')
            if merge_ents == True:
                nlp.add_pipe(merge_entities)
            if standard_component == True:
                nlp.add_pipe(nlp_helpers.spacy_component, name="standard_component", last=True)
            if custom_component:
                nlp.add_pipe(custom_component, name="custom_component", last=True)
            texts = mp(texts, nlp_helpers.spacy_process, nlp)
        return texts

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

    def cooc_pipeline(self, minimum_offsets = 20): 
        """
        Returns an instance of the 'cooc' class, initialized with the relevant data contained 
        """ 
        offset_dict, lookup = generate_offsets(self.post_nlp, self.list_time(), minimum_offsets)
        
        return cooc(offset_dict, lookup, minimum_offsets)

    def socnet_pipeline(self, subset:int = None):
        """
        Returns an instance of the 'socnet_pipe' class, initialized with the relevant data contained.
        The 'Subset' parameter allows users to specify the maximum number of edges to calculate.
        """ 
        return socnet_pipe(self.data, self.edgelist[slice(subset)])

    def svo(self, sub_tags=False, obj_tags=False, to_df = False, bigrams = False):
        """
        This is a docstring
        """ 
        text_list = self.list_nlp_text()
        if bigrams == True:
            text_list = nlp_helpers.bigram_process(text_list, tokenized=False)
        self.sentences, self.svo_items = process_svo(text_list, sub_tags, obj_tags)
        if to_df:
            return svo_to_df(self.sentences, self.svo_items)
        else:
            return self.svo_items
        