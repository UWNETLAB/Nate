"""Definition of the `SVOnet` class, for subject-verb-object analysis.

This module defines the `SVOnet` class, [description of SVO pipeline].
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
    """Detects SVOs in a document after spaCy has processed it.

    Custom pipeline component for spaCY.

    TODO: move this to utils, where it is used.
    """
    sentences = [x.string.strip() for x in doc.sents]  # list of raw sentences in the document
    svo_items = [findSVOs(x, sub_tags, obj_tags) for x in doc.sents] # detect SVOs sentence-by-sentence in the document

    return (sentences, svo_items)


class SVOnet(BurstMixin):
    """Provides data cleanup, export functions, and burst detection.

    Attributes:
        doc_ids (List): A list of document ids, determining which document
            the SVO at index i came from.
        sent_ids (List): A list of sentence ids, determining which sentence
            the SVO at index i came from.
        sentences (List): The sentence that the SVO was pulled from.
        svo_items (List): The entire SVO item.
        times (List): The time that the SVO's source document was written.
        subjects (List): The SVO at index i's subject.
        verbs (List): The SVO at index i's verb.
        objects (List): The SVO at index i's object
        sub_ent_types (List): The SVO at index i's subject entity type.
        obj_ent_types (List): The SVO at index i's object entity type.
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
        """Outputs a pandas dataframe with all SVOs and their timestamps.

        If tidy is set to True, each SVO will have its own line in the dataframe.
        If tidy is set to False, identical SVOs will be grouped and their
        document ids, timestamps, and datetimes will be aggregated into lists
        in the dataframe.

        Args:
            tidy (Bool, optional): Whether to output a tidy or non-tidy
                dataframe, the differences between which are documented above.
                Defaults to True.

        Returns:
            pandas.Dataframe: A dataframe containing data for all detected SVOs,
                including their associated timestamps (if present).

            The outputted dataframe will have the following columns:
              - 'doc_ids' (int) : A list of document ids, determining which
                document the SVO at index i came from.
              - 'sent_ids' (int): A list of sentence ids, determining which
                 sentence
                 the SVO at index i came from.
              - 'sentences' (string): The sentence that the SVO was pulled from.
              - 'svo' (Tuple): The entire SVO item.
              - 'times' (datetime): The time that the SVO's source document
                was written.
              - 'subjects' (string): The SVO at index i's subject.
              - 'verbs' (string): The SVO at index i's verb.
              - 'objects' (string): The SVO at index i's object
              - 'sub_ent_types' (string): The SVO at index i's subject entity
                type.
              - 'obj_ent_types' (string): The SVO at index i's object entity
                type.
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
        """Initiates burst detection on data contained in the SVOnet class.

        This function requires that the object was instantiates with a list
        of times.

        Args:
            minimum_offsets (int, optional): The minimum number of occurences
                of an SVO in the dataset for it to be included in the bursts
                calculation. Lower values include more of the dataset, at the
                cost of longer processing time. Defaults to 20.
            s (float, optional): s parameter for tuning Kleinberg algorithm.
                Higher values make it more difficult for bursts to move up the
                burst hierarchy. Defaults to 2.
            gamma (float, optional): gamma parameter for tuning Kleinberg
                algorithm. Higher values make it more difficult for activity to
                be considered a burst. Defaults to 1.

        Returns:
            SVOburst: An SVOburst object for exporting, visualizing, and otherwise
                manipulating burst data for the data contained in this class.
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
