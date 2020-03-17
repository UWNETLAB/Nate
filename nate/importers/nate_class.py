from pprint import pprint
from ..cooc.cooc_class import cooc
from ..svonet.svonet_class import svonet, process_svo
from .edgelist_importers import edgelist_mixin
from ..socnet.socnet import socnet_pipe
from ..utils import nlp_helpers
from ..utils.mp_helpers import mp, mp2
import spacy
from spacy.pipeline import merge_entities
from ..cooc.cooc_offsets import cooc_offsets

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
        return self.data[index]
        
    def preprocess(self, bigrams = False, custom_filter = False, model="en_core_web_sm"):
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
        return [str(i.text) for i in self.data[start:end]]

    # The following isn't currently in use:

    # def list_nlp_text(self, start:int = None, end:int = None, bigrams = False, tokenized = False, nlp = False, custom_filter = False, default_filter = False, merge_ents = False):
    #     """
    #     Returns a list of texts
    #     """ 
    #     if bigrams == True:
    #         self.texts = nlp_helpers.bigram_process(self.texts, tokenized=tokenized)        
    #     if nlp == True:
    #         nlp = spacy.load('en_core_web_sm')
    #         if merge_ents == True:
    #             nlp.add_pipe(merge_entities)
    #         if default_filter == True:
    #             nlp.add_pipe(nlp_helpers.default_filter_lemma, name="filter_lemmatize", last=True)
    #         elif custom_filter:
    #             nlp.add_pipe(custom_filter, name="custom_filter", last=True)
    #         self.texts = mp(self.texts, nlp_helpers.spacy_process, nlp)
    #     return self.texts

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
        # if self.for_svo == True and custom_filter == False:
        #     self.post_nlp = [nlp_helpers.default_filter_lemma(doc) for doc in self.post_nlp]
        # elif self.for_svo == True:
        #     self.post_nlp = [custom_filter(doc) for doc in self.post_nlp]
            
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
        
        sentences = [x[0] for x in post_svo]
        svo_items = [x[1] for x in post_svo]
        

        sentences, svo_items = mp2(self.post_nlp, process_svo, sub_tags, obj_tags)

        return svonet(sentences, svo_items, self.time)
        