from . import pybursts
from ..utils.mp_helpers import mp
from .visualize_bursts import plot_bursts
from .export import df_export, max_bursts_export, all_bursts_export, offsets_export
 
def get_bursts(s, gamma, offset_list):
    """
	This is a docstring.
	"""    
    burst_list = pybursts.process(offset_list, s, gamma)   

    return burst_list
    

def detect_bursts(offsets, s = 2, gamma = 1):
    """
    This is a docstring
    """

    key_list = list(offsets.keys())
    offset_list = list(offsets.values())


    burst_list = mp(offset_list, get_bursts, s, gamma) #bursts(key_list, offset_list)

    edge_bursts = dict(zip(key_list, burst_list))

    return edge_bursts

class bursts():
    """
    This is a docstring.
    """
    def __init__(self, offset_dict, lookup, s, gamma):
        self.lookup = lookup
        self.offset_dict_int = offset_dict
        self.offset_dict = self.export_offsets()
        self.edge_burst_dict_int = detect_bursts(offset_dict, s, gamma)
        self.edge_burst_dict = self.export_all_bursts()
        self.s = s
        self.gamma = gamma
        
    def export_df(self):
        """
        This is a docstring.
        """
        return df_export(self.edge_burst_dict_int, self.offset_dict_int, self.lookup)
        
    def export_max_bursts(self):
        """
        This is a docstring.
        """
        return max_bursts_export(self.edge_burst_dict_int, self.lookup)
        
    def export_all_bursts(self):
        """
        This is a docstring.
        """
        return all_bursts_export(self.edge_burst_dict_int, self.offset_dict_int, self.lookup)
        
    def export_offsets(self):
        """
        This is a docstring.
        """
        return offsets_export(self.offset_dict_int, self.lookup)

    def create_burst_plot(self, token_pairs, zoom_level = 0, output_path = False, plot_size_x = 20, plot_size_y = 10, plot_vertically = False, num_ticks = 10):
        """
        `token_pair` accepts either a string or a list of strings corresponding to one of the token-token pairs in the edge_burst_dict dictionary. 
        If a list of valid token pairs is provided, one separate plot for each of the token pairs is produced. 

        `zoom_level` (default = 0) splits the burst structure for each provided token-token pair into a series of separate bursts hierarchies, omitting any levels
        below the indicated zoom_level. A zoom level of 0 does not omit any of the bursts (including the baseline burst, which spans the entirety of the supplied data)
        """ 
        if isinstance(token_pairs, str):
            token_pairs = [token_pairs]

        if zoom_level == 0: # When the zoom level is 0, we can just pass everything directly into the plotting function.
            for entry in token_pairs:
                plot_bursts(self.offset_dict[entry], self.edge_burst_dict[entry], entry, output_path, plot_size_x, plot_size_y, plot_vertically, num_ticks)

        else: # When the zoom level is above 0, we have to slice everything manually and pass the slices along to the plotting function:
            for entry in token_pairs:

                offsets = self.offset_dict[entry]
                bursts = self.edge_burst_dict[entry]

                burst_stack = []
                temp_burst_stack = []

                for burst in bursts:
                    if burst[0] < zoom_level:
                        pass
                    elif burst[0] == zoom_level:
                        if len(temp_burst_stack) > 0:
                            burst_stack.append(temp_burst_stack)
                        temp_burst_stack = []
                        temp_burst_stack.append(burst)
                    else:
                        temp_burst_stack.append(burst)
                        
                if len(temp_burst_stack) > 0:
                    burst_stack.append(temp_burst_stack)

                offset_stack = []

                for burst in burst_stack:
                    low = burst[0][1]
                    high = burst[0][2]
                    temp_offset_stack = []
                    for offset in offsets:
                        if low <= offset and offset <= high:
                            temp_offset_stack.append(offset)
                    offset_stack.append(temp_offset_stack)

                assert len(burst_stack) == len(offset_stack)

                for i in range(0, len(burst_stack)):
                    plot_title = ("{}, slice {} of {}".format(entry, i+1, len(burst_stack)))

                    plot_bursts(offset_stack[i], burst_stack[i], plot_title, output_path, plot_size_x, plot_size_y, plot_vertically, num_ticks)


