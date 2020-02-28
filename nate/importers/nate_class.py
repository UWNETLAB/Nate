from pprint import pprint
from ..edgeburst.edge_burst_class import edge_burst
from ..svo.process import process_svo, svo_to_df
from .edgelist_importers import edgelist_mixin
from ..utils.text_helpers import spacy_process, spacy_component, bigram_process
from ..utils.mp_helpers import mp
import spacy
from spacy.pipeline import merge_entities

class nate(edgelist_mixin):
    """
    This is the `nate` package's base class. Each of the importer functions the `nate` package loads into namespace returns a populated instance of the `nate` class.

    Calling this class directly is functionally identical to calling the `head()` method with no arguments - both return the first 5 'rows' of the dataset. 
    """
    def __init__(self, data):
        self.data = data
        self.fields = data[0]._fields

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

    def list_texts(self, start:int = None, end:int = None, bigrams = False, tokenized = False, nlp = False, custom_component = False, standard_component = False, merge_ents = False):
        """
        Returns a list of texts
        """ 
        texts = [str(i.text) for i in self.data[start:end]]
        if bigrams == True:
            texts = bigram_process(texts, tokenized=tokenized)        
        if nlp == True:
            nlp = spacy.load('en_core_web_sm')
            if merge_ents == True:
                nlp.add_pipe(merge_entities)
            if standard_component == True:
                nlp.add_pipe(spacy_component, name="standard_component", last=True)
            if custom_component:
                nlp.add_pipe(custom_component, name="custom_component", last=True)
            texts = mp(texts, spacy_process, nlp)
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

    def edge_burst_pipeline(self): 
        """
        Returns an instance of the 'edge_burst' class, initialized with the relevant data contained 
        """ 
        return edge_burst(self)

    def svo(self, sub_tags=False, obj_tags=False, to_df = False, bigrams = False):
        """
        This is a docstring
        """ 
        text_list = self.list_texts()
        if bigrams == True:
            text_list = bigram_process(text_list, tokenized=False)
        self.sentences, self.svo_items = process_svo(text_list, sub_tags, obj_tags)
        if to_df:
            return svo_to_df(self.sentences, self.svo_items)
        else:
            return self.svo_items
        