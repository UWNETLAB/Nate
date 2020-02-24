import spacy
from spacy.pipeline import merge_entities
from .svo import findSVOs
import pandas as pd

def process_svo(text_list, sub_tags = False, obj_tags = False):
    nlp = spacy.load("en_core_web_lg")
    nlp.add_pipe(merge_entities)
    svo_list = []
    
    post_nlp = [doc for doc in nlp.pipe(text_list)]
    sentences = [[x for x in y.sents] for y in post_nlp]
    svo_list = [[findSVOs(x, sub_tags, obj_tags) for x in y.sents] for y in post_nlp]
    
    return sentences, svo_list
    
    
def svo_to_df(sentences, svo_list):
    df = pd.DataFrame()
    doc_id = []
    sent_id = []
    sent_list_flat = []
    svo_list_flat = []
    for i, doc in enumerate(sentences):
        for j, sent in enumerate(doc):
            doc_id.append(i)
            sent_id.append(j)
            sent_list_flat.append(sent)
            svo_list_flat.append(svo_list[i][j])
            
    df['doc_id'], df['sent_id'], df ['sentence'], df['svo'] = doc_id, sent_id, sent_list_flat, svo_list_flat
    
    
    return df



    

    