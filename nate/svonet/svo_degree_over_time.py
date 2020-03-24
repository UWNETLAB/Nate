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


class SVODegreeOverTimeMixin():

    def __init__(self):
        self.offset_dict:dict 
        self.edge_burst_dict:dict
        self.s: int
        self.gamma: int
        self.from_svo: bool
        self.lookup: dict

    
    def top_svo_degree(
        self, 
        number_of_slices: int = 20, 
        list_top: int = 10,
        minimum_burst_level: int = 0,
        return_edge_overlaps: bool = True):

        stops = sw.get_stop_words("english")

        # Create list of time slices:

        offset_set = set()

        for key in self.offset_dict:
            for offset in self.offset_dict[key]:
                offset_set.add(offset)

        time_slices, time_labels = generate_ticks(offset_set, number_of_ticks=number_of_slices)


        # Create network consisting of all Subjects and Objects:

        G = nx.Graph()

        for entry in self.edge_burst_dict:
            G.add_node(entry)


        # Iterate over time slices

        top_degree_by_slice = {}
        edge_overlap = {}

        for i in range(1, len(time_slices)):
            graphCopy = copy.deepcopy(G)

            for key in self.edge_burst_dict:
                burst_level = find_max_burst(self.edge_burst_dict[key], time_slices[i-1], time_slices[i])
 
                if burst_level > minimum_burst_level:
                    for node in graphCopy.nodes():
                        for j in [0, -1]:
                            for k in [0, -1]:
                                if key[j] == node[k] and key[j] not in stops:
                                    overlap = len(set(key).intersection(set(node)))
                                    graphCopy.add_edge(key, node, overlap=overlap)

                        # if key[0] in node and key[0] not in stops:
                            
                        # if key[-1] in node and key[-1] not in stops:
                        #     graphCopy.add_edge(key, node)

            graphCopy.remove_edges_from(nx.selfloop_edges(graphCopy))

            degree_list = list(graphCopy.degree)

            degree_list.sort(key=lambda x: x[1], reverse=True)

            top_degree_by_slice[time_labels[i]] = degree_list[0:list_top]

            if return_edge_overlaps:
                overlap_list = []
                for entry in degree_list[0:list_top]:
                    overlap_sum = []
                    for edge in graphCopy.edges(entry[0]):
                        overlap_sum.append(graphCopy.edges[edge]['overlap'])

                    if len(overlap_sum) > 0:
                        avg = round(sum(overlap_sum) / len(overlap_sum), 2)
                    else:
                        avg = 0

                    overlap_list.append((entry[0], avg))

                edge_overlap[time_labels[i]] = overlap_list

        if return_edge_overlaps: 
            return top_degree_by_slice, edge_overlap
        else:
            return top_degree_by_slice

    
    def plot_top_svo_degree( 
        self, 
        number_of_slices: int = 20, 
        list_top: int = 10,
        minimum_burst_level: int = 0):

        data = self.top_svo_degree(
            number_of_slices = number_of_slices, 
            list_top = list_top,
            minimum_burst_level = minimum_burst_level,
            return_edge_overlaps = False)

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

            fig, ax = plt.subplots()
            fig.set_figwidth(10)
            fig.set_figheight(6)
            fig.suptitle('{} to {}'.format(date_names[i-1], date_names[i]), fontsize=16)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            plt.bar(x, values, color='#32363A')
            plt.xticks(x, names, rotation="vertical")
            plt.show()
