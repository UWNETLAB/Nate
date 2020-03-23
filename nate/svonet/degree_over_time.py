from nate.svonet.graph_svo import generate_ticks, find_max_burst
import networkx as nx
import copy
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import numpy as np


class DegreeOverTimeMixIn():

    def __init__(self):
        self.offset_dict:dict 
        self.edge_burst_dict:dict
        self.s: int
        self.gamma: int
        self.from_svo: bool
        self.lookup: dict


    def top_degree(
        self, 
        number_of_slices: int = 20, 
        list_top: int = 10,
        minimum_burst_level: int = 0, 
        degree_type = "both"):
        """[summary]
        
        Args:
            number_of_slices (int, optional): [description]. Defaults to 20.
            list_top (int, optional): [description]. Defaults to 10.
            degree_type (str, optional): Type of degree calculation to use.
            Must be one of "in", "out", or "both". Defaults to "both".
        
        Returns:
            [type]: [description]
        """

        if degree_type != "in" and degree_type != "out" and degree_type != "both":
            raise Exception("`degree_type` must be one of 'in', 'out', or 'both'")


        # Create list of time slices:

        offset_set = set()

        for key in self.offset_dict:
            for offset in self.offset_dict[key]:
                offset_set.add(offset)

        time_slices, time_labels = generate_ticks(offset_set, number_of_ticks=number_of_slices)

        # Create network consisting of all Subjects and Objects:

        G = nx.DiGraph()

        for entry in self.edge_burst_dict:
            G.add_node(entry[0])
            G.add_node(entry[-1])

        # Iterate over time slices

        top_degree_by_slice = {}

        for i in range(1, len(time_slices)):
            graphCopy = copy.deepcopy(G)

            for key in self.edge_burst_dict:
                burst_level = find_max_burst(self.edge_burst_dict[key], time_slices[i-1], time_slices[i])
 
                if burst_level > minimum_burst_level:
                    graphCopy.add_edge(key[0], key[-1])

            if degree_type == "in":
                degree_list = list(graphCopy.in_degree)
            elif degree_type == "out":
                degree_list = list(graphCopy.out_degree)
            elif degree_type == "both":
                degree_list = list(graphCopy.degree)

            degree_list.sort(key=lambda x: x[1], reverse=True)

            top_degree_by_slice[time_labels[i]] = degree_list[0:list_top]

        return top_degree_by_slice


    def specific_degree(
        self, 
        tokens: list, 
        number_of_slices: int = 20, 
        minimum_burst_level: int = 0,
        degree_type = "both"):

        if isinstance(tokens, list) == False:
            tokens = [tokens]

        full_lists = self.top_degree(
            number_of_slices = number_of_slices,
            list_top =  None,
            minimum_burst_level=minimum_burst_level,
            degree_type = degree_type)

        token_rank_dict = {}

        for day in full_lists:
            v = [item for item in full_lists[day] if item[0] in tokens]
            token_rank_dict[day] = v
        
        return token_rank_dict


    def plot_top_degree( 
        self, 
        number_of_slices: int = 20, 
        list_top: int = 10,
        minimum_burst_level: int = 0, 
        degree_type = "both"):

        data = self.top_degree(
            number_of_slices = number_of_slices, 
            list_top = list_top,
            minimum_burst_level = minimum_burst_level, 
            degree_type = degree_type)

        for date_name, time_slice in data.items():
            fig, ax = plt.subplots()
            fig.set_figwidth(10)
            fig.set_figheight(6)
            fig.suptitle('from last plot to {}'.format(date_name), fontsize=16)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))

            x = np.arange(list_top)
            values = []
            names = []

            for thing in time_slice:
                values.append(thing[1])
                names.append(thing[0])

            plt.bar(x, values)
            plt.xticks(x, names, rotation="vertical")
            plt.show()

    def plot_specific_degree(
        self,
        tokens: list, 
        number_of_slices: int = 20, 
        minimum_burst_level: int = 0,
        degree_type = "both"):

        pass

            

            


