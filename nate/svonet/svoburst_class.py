from nate.edgeburst.burst_class import Bursts
from nate.svonet.degree_over_time import DegreeOverTimeMixIn
from nate.svonet.svo_degree_over_time import SVODegreeOverTimeMixin
from nate.svonet.svo_burst_animate import prepare_df, build_graph, animate_graph



class SVOburst(Bursts, DegreeOverTimeMixIn, SVODegreeOverTimeMixin):
    """[summary]
    
    """

    def __init__(self, offset_dict, edge_burst_dict, s, gamma, from_svo,
                 lookup):
        """[summary]
        
        Args:
            offset_dict ([type]): [description]
            edge_burst_dict ([type]): [description]
            s ([type]): [description]
            gamma ([type]): [description]
            from_svo ([type]): [description]
            lookup ([type]): [description]
        """

        self.offset_dict: dict = offset_dict
        self.edge_burst_dict: dict = edge_burst_dict
        self.s = s
        self.gamma = gamma
        self.from_svo = from_svo
        self.bdf = None
        self.odf = None
        self.lookup = lookup

    def animate(self, pos = False, time_interval = False, offscreen = True, offscreen_params = False, onscreen_params = False, new_burst_halo = True):

        df = prepare_df(self.edge_burst_dict, self.offset_dict)
        graph = build_graph(df, pos, time_interval)
        animate_graph(graph, offscreen, offscreen_params, onscreen_params)

