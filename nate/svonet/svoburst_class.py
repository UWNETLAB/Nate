from nate.edgeburst.burst_class import Bursts
from nate.svonet.degree_over_time import DegreeOverTimeMixIn
from nate.svonet.svo_degree_over_time import SVODegreeOverTimeMixin


class SVOburst(Bursts, DegreeOverTimeMixIn, SVODegreeOverTimeMixin):
    """
    Creates an SVOburst class object containing data about SVO terms that burst over time.
    
    """

    def __init__(self, offset_dict, edge_burst_dict, s, gamma, from_svo,
                 lookup):
        """[summary]
        
        Args:
            offset_dict (Dict): Dictionary with terms as keys, list of offsets (occurrences) as values
            edge_burst_dict (Dict): Dictionary with terms as keys and nested burst data as values
            s (float): s parameter for tuning Kleinberg algorithm. Higher values make it more difficult 
                for bursts to move up the burst hierarchy
            gamma (float): gamma parameter for tuning Kleinberg algorithm. Higher values make it more 
                difficult for activity to be considered a burst
            from_svo (bool): flag to alert other functions to the SVO pipeline
            lookup (dict): Dictionary with integers as keys and the SVO terms they represent as values
        """

        self.offset_dict: dict = offset_dict
        self.edge_burst_dict: dict = edge_burst_dict
        self.s = s
        self.gamma = gamma
        self.from_svo = from_svo
        self.bdf = None
        self.odf = None
        self.lookup = lookup

    def animate(self, pos = False, offscreen = True, time_interval = False, new_burst_halo = True, dpi = 300):
        """
        Uses graph-tool to create either an onscreen animation window of a network of SVO burst over time, or
        dumps each frame to disk to use for creating an animation.
        """
        # check if graph-tool and other requirements are able to be imported
        try:
            from nate.svonet.svo_burst_animate import prepare_df, build_graph, animate_graph
            
            df = prepare_df(self.edge_burst_dict, self.offset_dict)
            graph = build_graph(df, pos, time_interval)
            animate_graph(graph, pos, offscreen, new_burst_halo, dpi)
            
        except ImportError:
            print("Graph-tool does not appear to be installed or importable")

