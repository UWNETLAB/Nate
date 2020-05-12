"""
This is a MODULE docstring
"""

from nate.svonet.svo import findSVOs
import pandas as pd
from nate.utils.mp_helpers import mp
from nate.utils.text_helpers import is_ascii
from typing import List, Dict
from nate.svonet.svo_offsets import generate_svo_offsets
from nate.edgeburst.burst_mixin import BurstMixin
from nate.svonet.degree_over_time import DegreeOverTimeMixIn
from nate.svonet.svoburst_class import SVOburst


def process_svo(sub_tags, obj_tags, doc):
    """
    This is a docstring. Custom spaCy pipeline component to detect SVOs in each document
    after spaCy has processed it
    """
    sentences = [x.string.strip() for x in doc.sents]  # list of raw sentences in the document
    svo_items = [findSVOs(x, sub_tags, obj_tags) for x in doc.sents] # detect SVOs sentence-by-sentence in the document

    return (sentences, svo_items)


class SVOnet(BurstMixin):
    """
    This is a docstring. Primarily provides data clean-up upon initialization, as well as
    an export function and burst detection functions.
    """

    def __init__(self, sentences, svo_items, timestamps):

        self.doc_ids = []
        self.sent_ids = []
        self.sentences = []
        self.svo_items = []
        if timestamps:
            self.times = []
        self.subjects = []
        self.verbs = []
        self.objects = []
        self.sub_ent_types = []
        self.obj_ent_types = []

        # this somewhat obtuse code chunk flattens the heavily nested data format returned by the `svo` module
        for i, doc in enumerate(sentences):
            for j, sent in enumerate(doc):
                if len(svo_items[i][j][0]) > 0:
                    for k, svo_item in enumerate(svo_items[i][j][0]):
                        if is_ascii(svo_item[0]) and is_ascii(
                                svo_item[1]) and is_ascii(svo_item[2]):
                            svo_item = (svo_item[0].lower(),
                                        svo_item[1].lower(),
                                        svo_item[2].lower())
                            self.doc_ids.append(i)
                            self.sent_ids.append(j)
                            self.sentences.append(sent)
                            if timestamps:
                                self.times.append(timestamps[i])
                            self.svo_items.append(svo_item)
                            self.subjects.append(svo_item[0])
                            self.verbs.append(svo_item[1])
                            self.objects.append(svo_item[2])
                            self.sub_ent_types.append(svo_items[i][j][1][k])
                            self.obj_ent_types.append(svo_items[i][j][2][k])

        self.from_svo = True

    def svo_to_df(self, tidy=True):
        """ 
        This is a docstring. Outputs a Pandas dataframe of all detected SVOs and associated timestamps (if present). 
        If tidy is set to True, each SVO will have its own line in the dataframe.
        If tidy is set to False, identical SVOs will be grouped and their document ids, timestamps, and datetimes
        will be aggregated into lists in the dataframe.
        """
        df = pd.DataFrame()

        df['doc_id'], df['sent_id'], df['sentence'], df['svo'] =\
            self.doc_ids, self.sent_ids, self.sentences, self.svo_items
        if self.times:
            df['timestamp'] = self.times
        df['subject'], df['sub_type'], df['verb'], df['object'], df[
            'obj_type'] = self.subjects, self.sub_ent_types, self.verbs, self.objects, self.obj_ent_types
        if self.times:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

        if tidy == False and self.times:
            df = df.groupby('svo')['doc_id', 'timestamp', 'datetime'].agg(list)
        elif tidy == False:
            df = df.groupby('svo')['doc_id'].agg(list)

        return df

    def svo_to_burst(self, minimum_offsets=20, s=2, gamma=1) -> SVOburst:
        """
        Initiates burst detection on data contained in the SVOnet class. Returns an instance of the SVOburst class.
        """
        if not self.times:
            print("Burst detection requires timestamps")
            return None

        # send offset_dict and lookup dictionary to svo_offset generating function
        self.offset_dict, self.lookup = generate_svo_offsets(
            self.svo_items, self.times, minimum_offsets)

        offset_dict_strings, edge_burst_dict_strings, s, gamma, from_svo, lookup = self.burst_detection(
            s, gamma)

        return SVOburst(offset_dict=offset_dict_strings,
                        edge_burst_dict=edge_burst_dict_strings,
                        s=s,
                        gamma=gamma,
                        from_svo=from_svo,
                        lookup=lookup)
