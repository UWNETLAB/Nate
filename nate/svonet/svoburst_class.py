from nate.edgeburst.burst_class import Bursts
from nate.svonet.degree_over_time import DegreeOverTimeMixIn
from nate.svonet.svo_degree_over_time import SVODegreeOverTimeMixin


class SVOburst(Bursts, DegreeOverTimeMixIn, SVODegreeOverTimeMixin):
    """
    Creates an SVOburst class object containing data about SVO terms that burst over time.

    Attributes:
        offset_dict (Dict): A dictionary with terms as keys, and a list
            of offsets (occurrences) as values.
        edge_burst_dict (Dict): A dictionary with terms as keys and nested
            burst data as values.
        s (float): s parameter for tuning Kleinberg algorithm. Higher values
            make it more difficult for bursts to move up the burst hierarchy.
        gamma (float): gamma parameter for tuning Kleinberg algorithm. Higher
            values make it more difficult for activity to be considered a
            burst.
        from_svo (bool): A flag to alert other functions to the SVO pipeline.
        lookup (dict): A dictionary with integers as keys and the SVO terms
            they represent as values.
    """

    def __init__(self, offset_dict, edge_burst_dict, s, gamma, from_svo,
                 lookup):

        self.offset_dict: dict = offset_dict
        self.edge_burst_dict: dict = edge_burst_dict
        self.s = s
        self.gamma = gamma
        self.from_svo = from_svo
        self.bdf = None
        self.odf = None
        self.lookup = lookup

    def animate(self, pos = False, offscreen = True, time_interval = False, new_burst_halo = True, dpi = 300):
        """Creates an animation of the network of SVO bursts over time.

        The function will either create an onscreen animation window, or
        dump each frame to disk. The function requires graph-tool to be
        installed and able to be imported.

        Args:
            pos (object, optional): A graph-tool `pos` vertex
                property map to specify layout. If passed, the map will be
                used to create the graph layout. Otherwise, one will be
                generated. Defaults to False.
            offscreen (Bool, optional): Whether to generate the animation
                offscreen. If True, the frames will be dumped to disk in
                the directory `./data/frames`. if False, the animation will
                be shown onscreen. Defaults to True.
            time_interval (int, optional): Specifes a custom time step
                interval in seconds. Defaults to 86400 (one day).
            new_burst_halo (): not used in animate_graph
            dpi (int): not used in animate_graph
        """
        # check if graph-tool and other requirements are able to be imported
        try:
            from nate.svonet.svo_burst_animate import prepare_df, build_graph, animate_graph

            df = prepare_df(self.edge_burst_dict, self.offset_dict)
            graph = build_graph(df, pos, time_interval)
            animate_graph(graph, pos, offscreen, new_burst_halo, dpi)

        except ImportError:
            print("Graph-tool does not appear to be installed or importable")
