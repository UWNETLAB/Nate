from .svo import findSVOs
import pandas as pd
from ..utils.mp_helpers import mp
from typing import List, Dict
from .svo_offsets import generate_svo_offsets
from ..edgeburst.burst_mixin import burst_mixin
from ..edgeburst.burst_class import bursts
import networkx as nx
from types import MethodType

def process_svo(sub_tags, obj_tags, post_nlp):
    """
    This is a docstring.
    """
    sentences = [[x.string.strip() for x in y.sents] for y in post_nlp]
    svo_items = [[findSVOs(x, sub_tags, obj_tags) for x in y.sents] for y in post_nlp]

    return (sentences, svo_items)


def save_svo_graph(self, term_list, file_name = "test"):

    G = nx.DiGraph()

    if isinstance(term_list, str):
        term_list = [term_list]
    
    svo_list = self.edge_burst_dict

    for entry in svo_list:
        include = False
        for entry_part in entry:
            if entry_part in term_list:
                include = True

            for term in term_list:
                if term in entry_part or entry_part in term:
                    include = True

        
        if include:
            G.add_edge(entry[0], entry[2], label = " "+ entry[1])

    for entry in G:
        G.nodes[entry]['style'] = 'filled'
        G.nodes[entry]['fillcolor'] = 'cadetblue2'


    toPdot = nx.drawing.nx_pydot.to_pydot
    N = toPdot(G)

    N.write(file_name + ".png", prog='dot', format='png')


class svonet(burst_mixin):
    """
    This is a docstring.
    """
    def __init__(self, sentences, svo_items, timestamps):
        self.sentences = sentences
        self.svo_items = svo_items
        self.times = timestamps
        self.from_svo = True


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
        

    def svo_to_burst(self, minimum_offsets = 20, s = 2, gamma = 1): 
            
        self.offset_dict, self.lookup = generate_svo_offsets(self.svo_items, self.times, minimum_offsets)

        burst_instance = self.burst_detection(s, gamma)

        burst_instance.save_svo_graph = MethodType(save_svo_graph, burst_instance)

        return burst_instance
