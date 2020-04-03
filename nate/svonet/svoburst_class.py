from nate.edgeburst.burst_class import Bursts
from nate.svonet.degree_over_time import DegreeOverTimeMixIn
from nate.svonet.svo_degree_over_time import SVODegreeOverTimeMixin
from nate.svonet.svo_burst_animate import prepare_df, build_graph, animate_graph
from gi.repository import Gtk
from xvfbwrapper import Xvfb

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

    def animate(self, pos = False, offscreen = True, time_interval = False, new_burst_halo = True, dpi = 300):
        if Gtk.init_check()[0] == False:
            print('Display not found. Starting virtual display.')
            self.xvfb = Xvfb(width=1920, height=1080)
            self.xvfb.start()
        df = prepare_df(self.edge_burst_dict, self.offset_dict)
        graph = build_graph(df, pos, time_interval)
        animate_graph(graph, pos, offscreen, new_burst_halo, dpi)

