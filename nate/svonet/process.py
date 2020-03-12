import spacy
from spacy.pipeline import merge_entities
from .svo import findSVOs
import pandas as pd
from ..utils.mp_helpers import mp
from ..utils.nlp_helpers import spacy_process

def process_svo(post_nlp, sub_tags = False, obj_tags = False):
    """
    This is a docstring.
    """
    sentences = [[x.string.strip() for x in y.sents] for y in post_nlp]
    svo_items = [[findSVOs(x, sub_tags, obj_tags) for x in y.sents] for y in post_nlp]

    return sentences, svo_items


class svonet():
    def __init__(self, sentences, svo_items):
        self.sentences = sentences
        self.svo_items = svo_items

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
            
    
