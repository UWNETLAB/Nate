from .svo import findSVOs
import pandas as pd
from ..utils.mp_helpers import mp
from typing import List, Dict
from .svo_offsets import generate_svo_offsets
from ..edgeburst.export import df_export, max_bursts_export, all_bursts_export, offsets_export
from ..edgeburst.burst_detection import bursts, detect_bursts

def process_svo(sub_tags, obj_tags, post_nlp):
    """
    This is a docstring.
    """
    sentences = [[x.string.strip() for x in y.sents] for y in post_nlp]
    svo_items = [[findSVOs(x, sub_tags, obj_tags) for x in y.sents] for y in post_nlp]

    return (sentences, svo_items)


class svonet():
    def __init__(self, sentences, svo_items, timestamps):
        self.sentences = sentences
        self.svo_items = svo_items
        self.times = timestamps

    def svo_to_df(self):
        """ 
        This is a docstring.
        """
        df = pd.DataFrame()
        doc_id = []
        sent_id = []
        sent_list_flat = []
        svo_list_flat = []
        sub_list_flat = []
        verb_list_flat = []
        obj_list_flat = []
        sub_ent_types = []
        obj_ent_types = []
        for i, doc in enumerate(self.sentences):
            for j, sent in enumerate(doc):
                for k, svo_item in enumerate(self.svo_items[i][j][0]):
                    doc_id.append(i)
                    sent_id.append(j)
                    sent_list_flat.append(sent)
                    svo_list_flat.append(svo_item)
                    sub_list_flat.append(svo_item[0])
                    verb_list_flat.append(svo_item[1])
                    obj_list_flat.append(svo_item[2])
                    sub_ent_types.append(self.svo_items[i][j][1][k])
                    obj_ent_types.append(self.svo_items[i][j][2][k])

                
        df['doc_id'], df['sent_id'], df ['sentence'], df['svo'] = doc_id, sent_id, sent_list_flat, svo_list_flat
        df['subject'], df['sub_type'], df['verb'], df['object'], df['obj_type'] = sub_list_flat, sub_ent_types, verb_list_flat, obj_list_flat, obj_ent_types

        
        return df
        
    def svo_to_burst(self, minimum_offsets = 20): 
            
        self.offset_dict, self.lookup = generate_svo_offsets(self.svo_items, self.times, minimum_offsets)
        


    
    def burst_detection(self, s:float = 2, gamma:float = 1):
        """
        Returns an object of the class `bursts`

        This method is used to detect bursts for _all_ of the term-term pairs in the offset dictionary generated when this class (`edge_burst`) was instantiated.
        This method is best employed as an exploratory tool for identifying unusually bursty term pairs, or groups of term pairs with correlated burst patterns.  

        Since calling this method on an entire dataset can consume significant amounts of time and memory, this method only allows for one value of s and one value of gamma.

        If you wish to detect bursts using a variety of different values for the s and gamma parameters, instead utilize the `multi_bursts` method contained in this class. 
        """

        offset_dict_strings = offsets_export(self.offset_dict, self.lookup, from_svo = True)
        edge_burst_dict_int = detect_bursts(self.offset_dict, s, gamma)
        edge_burst_dict_strings = all_bursts_export(edge_burst_dict_int, self.offset_dict, self.lookup, from_svo = True)

        return bursts(offset_dict_strings, edge_burst_dict_strings, s, gamma)


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
