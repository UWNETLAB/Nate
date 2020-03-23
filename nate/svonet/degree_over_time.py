from nate.svonet.graph_svo import generate_ticks, find_max_burst
import networkx as nx
import stop_words as sw
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
        degree_type = "both",
        remove_stop_words = True):
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

            if remove_stop_words:
                stops = sw.get_stop_words("english")
                degree_list = [item for item in degree_list if item[0] not in stops]

            top_degree_by_slice[time_labels[i]] = degree_list[0:list_top]

        return top_degree_by_slice


    def specific_degree(
        self, 
        tokens: list, 
        number_of_slices: int = 20, 
        minimum_burst_level: int = 0,
        degree_type = "both",
        remove_stop_words = False):

        if isinstance(tokens, list) == False:
            tokens = [tokens]

        full_lists = self.top_degree(
            number_of_slices = number_of_slices,
            list_top =  None,
            minimum_burst_level=minimum_burst_level,
            degree_type = degree_type,
            remove_stop_words=remove_stop_words)

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
        degree_type = "both",
        remove_stop_words = True):

        data = self.top_degree(
            number_of_slices = number_of_slices, 
            list_top = list_top,
            minimum_burst_level = minimum_burst_level, 
            degree_type = degree_type,
            remove_stop_words = remove_stop_words)

        date_names = []
        time_slices = []

        for k, v in data.items():
            date_names.append(k)
            time_slices.append(v)
   
        for i in range(1, len(date_names)):

            x = np.arange(list_top)
            values = []
            names = []

            for top_degrees in time_slices[i]:
                values.append(top_degrees[1])
                names.append(top_degrees[0])

            if np.sum(values) > 0:
                fig, ax = plt.subplots()
                fig.set_figwidth(10)
                fig.set_figheight(6)
                fig.suptitle('{} to {}'.format(date_names[i-1], date_names[i]), fontsize=16)
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))
                plt.bar(x, values, color='#32363A')
                plt.xticks(x, names, rotation="vertical")
                plt.show()
            else:
                print("No nodes with degree > 0 in this time slice.")


    def plot_specific_degree(
        self,
        tokens: list, 
        number_of_slices: int = 20, 
        minimum_burst_level: int = 0,
        degree_type = "both",
        plot_type = "line",
        remove_stop_words = False):

        if plot_type != "line" and plot_type != "bar":
            raise Exception("`plot_type` must be one of 'line' or 'bar'")


        data = self.specific_degree(
            tokens = tokens, 
            number_of_slices = number_of_slices, 
            minimum_burst_level = minimum_burst_level,
            degree_type = degree_type,
            remove_stop_words=remove_stop_words
        )

        inverted_dict = {}

        for token in tokens:
            full_list = []

            for date, degree_list in data.items():
                degree = [item[1] for item in degree_list if item[0] == token]
                full_list.append((date, degree[0]))

            inverted_dict[token] = full_list

        x = np.arange(number_of_slices)

        for k, v in inverted_dict.items():

            values = [item[1] for item in v]
            dates = [item[0].replace(", ", "\n")  for item in v]


            fig, ax = plt.subplots()
            fig.set_figwidth(10)
            fig.set_figheight(6)
            fig.suptitle("'{}'".format(k), fontsize=16)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            if plot_type == "bar":
                plt.bar(x, values, color='#32363A')
            elif plot_type == "line":
                plt.plot(x, values, color='#32363A')
            plt.xticks(x, dates)
            plt.show()

