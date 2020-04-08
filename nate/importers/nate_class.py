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

from nate.cooc.cooc_class import Cooc
from nate.cooc.cooc_offsets import cooc_offsets
#from ..socnet.socnet import SOCnet
from nate.svonet.svonet_class import process_svo, SVOnet
from nate.utils import nlp_helpers
from nate.utils.mp_helpers import mp, mp2
from nate.importers.edgelist_importers import EdgelistMixin
from collections import namedtuple
from typing import List, NamedTuple, Union, Dict


class Nate(EdgelistMixin):
    """The `nate` package's eponymous base class. 
    
    Each of the `nate` package's importer functions returns a populated instance
    of the `Nate` class. This class contains the data and methods necessary to 
    initialize any of the subsidary pipelines for network analysis with text.

    Calling an instance of this class directly is functionally identical to 
    calling the `head()` method with no arguments - both return the first
    5 'rows' of the dataset. 

    Attributes:
        data: A list of `NamedTuples` containing the project's formatted dataset.
        texts: A list of text documented, derived from the `data` attribute.
        time: A list of epoch times, derived from the `data` attribute.
        post_nlp: A collection of `spaCy` doc objects, produced by one of the
            `Nate`'s pipelines.

    """

    def __init__(self, data: List):
        """Inits `Nate`.
        
        See `Nate` class docstring.
        """
        self.data: List = data
        self.texts: List = self.list_texts()
        self.post_nlp: List

    def __call__(self, start: int = 0, end: int = 5):
        """Returns complete 'rows' from the contained dataset. 
        
        Args:
            start (int, optional): The index number of the first returned row. Defaults to 0.
            end (int, optional): The index number of the last returned row. Defaults to 5.
        """
        pprint(self.data[start:end])

    def __getitem__(self, index: slice) -> List:
        """Called when `Nate` is accessed using indexing or slicing.
        
        Args:
            index (slice): A range of integers used to retrieve corresponding entries
                in the dataset.
        
        Returns:
            A list of named tuples, each corresponding to one row in the dataset. 
        """

        return self.data[index]

    def head(self, start: int = 0, end: int = 5):
        """Returns complete 'rows' from the contained dataset. 
        
        Args:
            start (int, optional): The index number of the first returned row. 
                Defaults to 0.
            end (int, optional): The index number of the last returned row. 
                Defaults to 5.
        """
        pprint(self.data[start:end])

    def list_texts(self, start: int = None, end: int = None) -> List:
        """Returns the 'text' field from data in the range provided.

        Note that if both `start` and `end` are left at their default (None),
        the text 'column' of the entire dataset will be returned. If an 
        integer is supplied for `start`, but `end` is None, every row with an 
        index greater than `start` will be returned. The same applies in reverse:
        if `start` is None, but `end` is an integer, every row with an index 
        lesser than `end` will be returned.
        
        Args:
            start (int, optional): The index number of the first returned row. 
                Defaults to None.
            end (int, optional): The index number of the last returned row. 
                Defaults to None.
        
        Returns:
            List: A list of strings.
        """
        return [str(i.text) for i in self.data[start:end]]

    def list_times(self, start: int = None, end: int = None) -> List:
        """Returns the 'time' field from data in the range provided.

        Note that if both `start` and `end` are left at their default (None),
        the text 'column' of the entire dataset will be returned. If an 
        integer is supplied for `start`, but `end` is None, every row with an 
        index greater than `start` will be returned. The same applies in reverse:
        if `start` is None, but `end` is an integer, every row with an index 
        lesser than `end` will be returned.
        
        Args:
            start (int, optional): The index number of the first returned row. 
                Defaults to None.
            end (int, optional): The index number of the last returned row. 
                Defaults to None.
        
        Returns:
            List: A list of integers, representing time in epoch format (number 
                of seconds elapsed since midnight UTC on 1 January 1970)
        """
        return [i.time for i in self.data[start:end]]

    def list_ids(self, start: int = None, end: int = None) -> List:
        """Returns the 'unique_id' field from data in the range provided.

        Note that if both `start` and `end` are left at their default (None),
        the text 'column' of the entire dataset will be returned. If an 
        integer is supplied for `start`, but `end` is None, every row with an 
        index greater than `start` will be returned. The same applies in reverse:
        if `start` is None, but `end` is an integer, every row with an index 
        lesser than `end` will be returned.
        
        Args:
            start (int, optional): The index number of the first returned row. 
                Defaults to None.
            end (int, optional): The index number of the last returned row. 
                Defaults to None.
        
        Returns:
            List: A list of unique IDs.
        """
        return [i.unique_id for i in self.data[start:end]]

    def list_column(self,
                    column_name: str,
                    start: int = None,
                    end: int = None) -> List:
        """Returns the named field from data in the range provided.

        Note that if both `start` and `end` are left at their default (None),
        the text 'column' of the entire dataset will be returned. If an 
        integer is supplied for `start`, but `end` is None, every row with an 
        index greater than `start` will be returned. The same applies in reverse:
        if `start` is None, but `end` is an integer, every row with an index 
        lesser than `end` will be returned.
        
        Args:
            column_name (str): The name of the field (or 'column') to be 
                returned.
            start (int, optional): The index number of the first returned row. 
                Defaults to None.
            end (int, optional): The index number of the last returned row. 
                Defaults to None.
        
        Returns:
            List: A list of entries from the named 'column'.
        """
        return [getattr(i, column_name) for i in self.data[start:end]]

    def preprocess(self,
                   bigrams: bool = False,
                   trigrams: bool = False,
                   custom_filter: bool = False,
                   tokenized: bool = False,
                   joined: bool = False,
                   bigram_threshold: float = 0.75,
                   model: str = "en_core_web_sm"):
        """Defines a `spaCy` pipeline and uses it to process text data.

        This method *must* be called before any of the other non-`SVOnet` pipelines
        in the `nate` package can be instantiated. 
        
        Args:
            bigrams (bool, optional): If True, bigrams will be used
                in place of individual tokens. Defaults to False.
            custom_filter (bool, optional): If supplied, the user-defined custom filter
                will be used instead of the default filter. Defaults to False.
            model (str, optional): Determines the trained `spaCy` model which will be applied. 
                Defaults to "en_core_web_sm", which is suitable for english-language
                applications. Other models can be found on the `spaCy` project's homepage.  
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
                self.texts = nlp_helpers.bigram_process(self.texts,
                                                        trigrams,
                                                        bigram_threshold,
                                                        tokenized)
            elif trigrams == True:
                self.texts = nlp_helpers.bigram_process(self.texts,
                                                        trigrams,
                                                        bigram_threshold,
                                                        tokenized)
                                                        
            self.post_nlp = mp(self.texts, custom_filter,
                               nlp_helpers.spacy_process, self.nlp, joined, None, None)
        else:
            self.nlp = spacy.load(self.model, disable=['parser'])
            self.nlp.add_pipe(merge_entities)
            self.nlp.add_pipe(nlp_helpers.default_filter_lemma,
                              name="filter_lemmatize",
                              last=True)
            if bigrams == True:
                self.texts = nlp_helpers.bigram_process(self.texts,
                                                        trigrams,
                                                        bigram_threshold,
                                                        tokenized)
            elif trigrams == True:
                self.texts = nlp_helpers.bigram_process(self.texts,
                                                        trigrams,
                                                        bigram_threshold,
                                                        tokenized)
                                                        
            self.post_nlp = mp(self.texts, nlp_helpers.spacy_process, self.nlp,
                               joined, None, None)

    def cooc_pipeline(self, minimum_offsets: int = 20) -> Cooc:
        """Instantiates, initializes, and returns an instance of the `Cooc` pipeline.

        The `Cooc` pipeline is used for examining patterns of token/term co-occurrence
        in a text corpus. 

        *Note: this method will not resolve unless the containing instance of the `Nate`
        class has been supplied with valid `post_nlp` data, as produced by the
        `preprocessing` method.*
        
        Args:
            minimum_offsets (int, optional): The minimum number of 'offsets' - or occurrences
                in the dataset - a given token/term pair must have in order to be retained.
                Lower values retain more of the dataset, but at considerable cost in computing
                time. Defaults to 20.
 
        Returns:
            Cooc: An instance of the `Cooc` class.
        """

        offset_dict, lookup = cooc_offsets(self.post_nlp, self.list_times(),
                                           minimum_offsets)

        return Cooc(offset_dict, lookup, minimum_offsets)

    def socnet_pipeline(self, subset: int = None):
        """Instantiates, initializes, and returns an instance of the `SOCnet` pipeline.

        Returns an instance of the 'socnet_pipe' class, initialized with the relevant 
        data contained. The `SOCnet` pipeline is used for examining the impact of 
        intellectual or topical diversity on nodes in a network.

        *Note: this method will not resolve unless the containing instance of the `Nate`
        class has been supplied with valid `post_nlp` data, as produced by the
        `preprocessing` method.*

        *Note: this method will not resolve unless the containing instance of the `Nate`
        class has been supplied with a valid edgelist, either directly or via one of
        the edgelist importer methods.*
        
        Args:
            subset (int, optional): Allows users to specify the maximum number of edges 
                to calculate. Defaults to None, which processes the entire dataset.
        
        Returns:
            SOCnet: An instance of the `SOCnet` class.
        """

        print("NOT CURRENTLY IMPLEMENTED")

        return "NOT CURRENTLY IMPLEMENTED"  #SOCnet(self.data, self.edgelist[slice(subset)])

    def svonet_pipeline(self,
                     sub_tags: bool = False,
                     obj_tags: bool = False,
                     bigrams: bool = False,
                     trigrams: bool = False,
                     bigram_threshold: float = 0.75,
                     model: str = "en_core_web_sm") -> SVOnet:
        """Instantiates, initializes, and returns an instance of the `SVOnet` pipeline.

        The `SVOnet` pipeline is used to explore the narrative structures present in 
        a text corpus. It does so by locating semantic content in the supplied documents
        in the form of Subject -> Verb -> Object, where the subject performs the 
        verb to or with respect to the object. 
        
        The `SVOnet` pipeline places unusual requirements on `spaCy`, and thus cannot
        be supplied with NLP data from the `preprocessing` method. Instead, calling 
        `svo_pipeline` processes text data using an internal call to `spaCy`, and 
        uses the resulting output to initialize and instance of the `SVOnet` class. 
        
        Args:
            sub_tags (bool, optional): If not False, an optional list of user-defined 
                tags is passed `spaCy` to, and is used to isolate subjects in the text 
                data. Defaults to False.
            obj_tags (bool, optional): If not False, an optional list of user-defined 
                tags is passed `spaCy` to, and is used to isolate objects in the text 
                data. Defaults to False.
            bigrams (bool, optional): If True, bigrams will be used in place of 
                individual tokens. Defaults to False.
            model (str, optional): Determines the trained `spaCy` model which will be applied. 
                Defaults to "en_core_web_sm", which is suitable for english-language
                applications. Other models can be found on the `spaCy` project's homepage.  
                
        Returns:
            SVOnet: An instance of the `SVOnet` class.
        """

        # add error check for custom_filter, which cannot be applied in this step for svo
        self.model = model
        joined = False
        
        if bigrams == True:
            self.texts = nlp_helpers.bigram_process(self.texts, trigrams, bigram_threshold, tokenized=False)
        elif trigrams == True:
            self.texts = nlp_helpers.bigram_process(self.texts, trigrams, bigram_threshold, tokenized=False)
        

        self.nlp = spacy.load(self.model)
        self.nlp.add_pipe(merge_entities)
        self.nlp.add_pipe(nlp_helpers.svo_component,
                          name="svo_component",
                          last=True)

        self.post_svo = mp(self.texts, nlp_helpers.spacy_process, self.nlp, joined,
                           sub_tags, obj_tags)

        sentences = [x[0] for x in self.post_svo]
        svo_items = [x[1] for x in self.post_svo]

        return SVOnet(sentences, svo_items, self.list_times())
