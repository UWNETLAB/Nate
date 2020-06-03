"""Definition of the `Bursts` class, for analysis of bursty term relations.

While `BurstMixin` provides the actual burst detection functionality,
this module provides export and plotting functions to facilitate further
analysis.
"""
from nate.edgeburst import pybursts
from ..utils.mp_helpers import mp
from .visualize_bursts import plot_bursts
from .export import df_export, max_bursts_export
from nate.edgeburst import visualize_bursts
from typing import Tuple, Dict, Callable, Union


def get_bursts(s, gamma, offset_list):
    """Sends Kleinberg parameters and offset_list to pybursts."""
    burst_list = pybursts.process(offset_list, s, gamma)

    return burst_list


def detect_bursts(offsets, s=2, gamma=1):
    """Returns dictionary with bursting terms as keys and burst data as values.

    Args:
        offsets (Dict): A dictionary of offsets, with keys being edge
            objects and the values being lists of occurence times.
        s (float, optional): s parameter for tuning Kleinberg algorithm.
            Higher values make it more difficult for bursts to move up the
            burst hierarchy. Defaults to 2.
        gamma (float, optional): gamma parameter for tuning Kleinberg
            algorithm. Higher values make it more difficult for activity to
            be considered a burst. Defaults to 1.

    Returns:
        Dict: A dictionary of bursts, with keys being edge objects and values
            being lists of burst data. Each burst is in the format
            [intensity, start_time, end_time].
    """
    key_list = list(offsets.keys())
    offset_list = list(offsets.values())

    burst_list = mp(offset_list, get_bursts, s, gamma)

    edge_bursts = dict(zip(key_list, burst_list))

    return edge_bursts


class Bursts():
    """The core burst detection class.

    This class provides all burst analysis functionality, including export
    and plotting abilities.

    Attributes:
        offset_dict (Dict): A dictionary with edge objects in string format
            as keys and occurence times as values.
        edge_burst_dict (Dict): A dictionary with edge objects in string format
            as keys and a list of bursts as values. The burst lists are in the
            format [intensity, start_time, end_time].
        s (float, optional): s parameter for tuning Kleinberg algorithm.
            Higher values make it more difficult for bursts to move up the
            burst hierarchy. Changing this parameter after object instatiation
            does not change the object's data.
        gamma (float, optional): gamma parameter for tuning Kleinberg
            algorithm. Higher values make it more difficult for activity to
            be considered a burst. Changing this parameter after object
            instatiation does not change the object's data.
        from_svo (Bool): A flad that determines whether the pipeline should be
            configured for bursts of SVOs.
        lookup (Dict): A lookup dictionary for terms, with integer
            representations as keys and string representations as values.
    """

    def __init__(self, offset_dict, edge_burst_dict, s, gamma, from_svo,
                 lookup):
        self.offset_dict: dict = offset_dict
        self.edge_burst_dict: dict = edge_burst_dict
        self.s = s
        self.gamma = gamma
        self.from_svo = from_svo # flag that determines whether the pipeline should be configured for bursts of SVOs
        self.bdf = None
        self.odf = None
        self.lookup = lookup

    def __getitem__(self, index: Union[slice, int, tuple]):
        """Called when `Bursts` is accessed using indexing or slicing.

        Args:
            index (slice): A range of integers used to retrieve corresponding
                entries in the `offset_dict` attribute.

        Returns:
            List: A list of named tuples, each corresponding to one row in the
                dataset.
        """

        if isinstance(index, slice) or isinstance(index, int):
            return list(self.edge_burst_dict.items())[index]
        else:
            return self.edge_burst_dict[index]


    def export_df(self):
        """Exports burst data to a dataframe.

        Returns:
            pandas.Dataframe: A dataframe containing all bursts data.

            The returned dataframe has the following columns:
                - Column(s) representing the edge objects (terms), whose names
                  depend on the object the `Bursts` object was formed from.
                - 'bursts': A dict with
                - 'term_id' (int): The id of the edge object in the dataset.
                  This will match the index.
                - 'interval_start' (datetime): The start of the burst.
                - 'interval_end' (datetime): The end of the burst.
                - 'intensity' (int): The intensity of the burst.
        """
        return df_export(self.edge_burst_dict, self.offset_dict, self.from_svo)

    def export_max_bursts(self):
        """Returns a dict with edges as keys and all max bursts as values."""
        return max_bursts_export(self.edge_burst_dict, self.from_svo)

    def to_pandas(self, key: Tuple, unit='s') -> Tuple[Dict, Dict]:
        """Exports bursts and offsets to separate dataframes for a given key.

        TODO: refactor the wrapped function (visualize_bursts.to_pandas)
        so that it is not SVO specific. Should not be much of an issue.

        Args:
            key (Tuple): The edge for which burst and offset data will
                be extracted.
            unit (str, optional): The unit to be passed to pd.to_datetime.
                Defaults to 's'.

        Returns:
            Tuple[pandas.Dataframe, pandas.Dataframe]: The first dataframe
                contains burst data. The second dataframe contains offset data.

            The first dataframe has the following columns:
                - 'level' (int): The level of the burst.
                - 'start' (datetime): The start time of the burst.
                - 'end' (datetime): The end time of the burst.
                - 'svo' (string): The edge for which the dataframe contains
                  data.

            The second dataframe has the following columns:
                - 'Date' (int): The date of the occurence.
                - 'Year' (int): The year of occurence.
                - 'Month' (int): The month of the occurence.
                - 'Day' (int): The day of the occurence.
                - 'svo' (string): The edge for which the dataframe contains
                  data.
        """

        offsets = self.offset_dict[key]
        bursts = self.edge_burst_dict[key]

        return visualize_bursts.to_pandas(bursts, offsets, key, unit)

    def plot_bursts(self,
                    key: Tuple,
                    unit='s',
                    lowest_level=0,
                    title=True,
                    daterange=None,
                    xrangeoffsets=3):
        """Plots the occurences and bursts of the given key.

        TODO: Refactor wrapped function so that it is not SVO specific.

        Args:
            key (Tuple): The key whose burst data to plot.
            unit (str, optional): The unit to be passed to pd.to_datetime.
                Defaults to 's'.
            lowest_level (int, optional): If passed, includes bursts only if
                they are greater than the given lowest level. Defaults to 0.
            title (Bool, optional): If True, include the name of SVO as the
                title of the figure. Defaults to True.
            daterange (Tuple[str,str], optional): If passed, only bursts in the
                range daterange[0] to daterange[1] will be plotted. The dates
                must be passed as strings in the format 'year-month-day'.
                Defaults to None.
            xrangeoffsets (int, optional): The number of days to add before the
                minimum date and after the maximum date. Used to 'pad' the plot.
                Defaults to 3.
        """
        bdf, odf = self.to_pandas(key, unit)

        visualize_bursts.plot_bursts(odf=odf,
                                     bdf=bdf,
                                     lowest_level=lowest_level,
                                     title=True,
                                     daterange=daterange,
                                     xrangeoffsets=xrangeoffsets,
                                     s=self.s,
                                     gamma=self.gamma)

    # def create_burst_plot(self, token_pairs, zoom_level = 0, output_path = False, plot_size_x = 20, plot_size_y = 10, plot_vertically = False, num_ticks = 10, rug_alpha = 0.35, dark = True):
    #     """
    #     `token_pair` accepts either a tuple or a list of tuples corresponding to one of the token-token pairs in the edge_burst_dict dictionary.
    #     If a list of valid token pairs is provided, one separate plot for each of the token pairs is produced.

    #     `zoom_level` (default = 0) splits the burst structure for each provided token-token pair into a series of separate bursts hierarchies, omitting any levels
    #     below the indicated zoom_level. A zoom level of 0 does not omit any of the bursts (including the baseline burst, which spans the entirety of the supplied data)
    #     """
    #     if isinstance(token_pairs, tuple):
    #         token_pairs = [token_pairs]

    #     for entry in token_pairs:

    #         plot_title = "'{}' + '{}'  -  Full Plot (s = {}, gamma = {})".format(entry[0], entry[1], self.s, self.gamma)

    #         plot_bursts(self.offset_dict[entry], self.edge_burst_dict[entry], plot_title, output_path, plot_size_x, plot_size_y, plot_vertically, num_ticks, rug_alpha, dark)

    #         if zoom_level > 0: # When the zoom level is 0, we can just pass everything directly into the plotting function.
    #             offsets = self.offset_dict[entry]
    #             bursts = self.edge_burst_dict[entry]

    #             burst_stack = []
    #             temp_burst_stack = []

    #             for burst in bursts:
    #                 if burst[0] < zoom_level:
    #                     pass
    #                 elif burst[0] == zoom_level:
    #                     if len(temp_burst_stack) > 0:
    #                         burst_stack.append(temp_burst_stack)
    #                     temp_burst_stack = []
    #                     temp_burst_stack.append(burst)
    #                 else:
    #                     temp_burst_stack.append(burst)

    #             if len(temp_burst_stack) > 0:
    #                 burst_stack.append(temp_burst_stack)

    #             offset_stack = []

    #             for burst in burst_stack:
    #                 low = burst[0][1]
    #                 high = burst[0][2]
    #                 temp_offset_stack = []
    #                 for offset in offsets:
    #                     if low <= offset and offset <= high:
    #                         temp_offset_stack.append(offset)
    #                 offset_stack.append(temp_offset_stack)

    #             assert len(burst_stack) == len(offset_stack)

    #             for i in range(0, len(burst_stack)):
    #                 plot_title = ("'{}' + '{}'  -  Zoom Level {}, Slice {} of {} (s = {}, gamma = {})".format(entry[0], entry[1], zoom_level, i+1, len(burst_stack), self.s, self.gamma))

    #                 plot_bursts(offset_stack[i], burst_stack[i], plot_title, output_path, plot_size_x, plot_size_y, plot_vertically, num_ticks, rug_alpha, dark)
