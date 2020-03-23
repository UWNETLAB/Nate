from nate.edgeburst.burst_class import Bursts
from nate.svonet.graph_svo import SVOgraphMixin
from nate.svonet.degree_over_time import DegreeOverTimeMixIn


class SVOburst(Bursts, SVOgraphMixin, DegreeOverTimeMixIn):
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
