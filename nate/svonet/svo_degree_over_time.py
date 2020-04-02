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
from multiprocessing import Process, Queue
from os import cpu_count


def get_degree_for_slice(
        q: Queue,
        G, 
        edge_burst_dict, 
        time_slice_start,
        time_slice_end, 
        minimum_burst_level, 
        stops, 
        overlap_threshold,
        return_edge_overlaps,
        list_top,
        time_label):
    graphCopy = copy.deepcopy(G)

    for key in edge_burst_dict:
        burst_level = find_max_burst(edge_burst_dict[key], time_slice_start, time_slice_end)

        if burst_level > minimum_burst_level:
            for node in graphCopy.nodes():
                for j in [0, -1]:
                    for k in [0, -1]:
                        if key[j] == node[k] and key[j] not in stops:
                            overlap = len(set(key).intersection(set(node)))
                            if overlap >= overlap_threshold:
                                graphCopy.add_edge(key, node, overlap=overlap)

    graphCopy.remove_edges_from(nx.selfloop_edges(graphCopy))


    degree_list = list(graphCopy.degree)

    degree_list.sort(key=lambda x: x[1], reverse=True)

    degree_list = degree_list[0:list_top]

    overlap_list = []

    if return_edge_overlaps:
        
        for entry in degree_list[0:list_top]:
            overlap_sum = []
            for edge in graphCopy.edges(entry[0]):
                overlap_sum.append(graphCopy.edges[edge]['overlap'])

            if len(overlap_sum) > 0:
                avg = round(sum(overlap_sum) / len(overlap_sum), 2)
            else:
                avg = 0

            overlap_list.append((entry[0], avg))

    if return_edge_overlaps: 
        q.put((time_label, time_slice_end, degree_list, overlap_list))
    else:
        q.put((time_label, time_slice_end, degree_list))


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
        number_of_slices: int = 8, 
        list_top: int = 10,
        minimum_burst_level: int = 0,
        return_edge_overlaps: bool = True,
        overlap_threshold: int = 1):
        """[summary]
        
        Args:
            number_of_slices (int, optional): [description]. Defaults to 20.
            list_top (int, optional): [description]. Defaults to 10.
            minimum_burst_level (int, optional): [description]. Defaults to 0.
            return_edge_overlaps (bool, optional): [description]. Defaults to True.
            overlap_threshold (int, optional): [description]. Defaults to 1.
        
        Raises:
            Exception: [description]
        
        Returns:
            [type]: [description]
        """

        if overlap_threshold > 2 or overlap_threshold < 1:
            raise Exception("Overlap Filter must be 1 or 2.")

        stops = sw.get_stop_words("english")

        # Create list of time slices:

        offset_set = set()

        for key in self.offset_dict:
            for offset in self.offset_dict[key]:
                offset_set.add(offset)

        time_slices, time_labels = generate_ticks(offset_set, number_of_ticks=(number_of_slices))

        # Create network consisting of all Subjects and Objects:

        G = nx.Graph()

        for entry in self.edge_burst_dict:
            G.add_node(entry)

        if list_top == None:
            list_top = len(self.edge_burst_dict)

        # Iterate over time slices

        q = Queue()

        processes = []

        for i in range(1, len(time_slices)):

            time_slice_start = time_slices[i-1]
            time_slice_end = time_slices[i]
            time_label = time_labels[i]

            t = Process(
                target = get_degree_for_slice,
                args= (
                    q,
                    G,
                    self.edge_burst_dict,
                    time_slice_start,
                    time_slice_end,
                    minimum_burst_level,
                    stops,
                    overlap_threshold,
                    return_edge_overlaps,
                    list_top,
                    time_label
                )
            )

            processes.append(t)
            t.start()

        result_list = []

        for i in range(1, len(time_slices)):
            result_list.append(q.get())


        top_degree_by_slice = {}
        edge_overlap = {}

        result_list = sorted(result_list, key = lambda x: x[1])
                
        for result in result_list:
            time_label = result[0]
            degree_list = result[2]
            top_degree_by_slice[time_label] = degree_list
            if return_edge_overlaps:
                edge_overlap[time_label] = result[3]
        
        if return_edge_overlaps: 
            return top_degree_by_slice, edge_overlap
        else:
            return top_degree_by_slice

    def specific_svo_degree(self,
                        tokens: list,
                        number_of_slices: int = 15,
                        minimum_burst_level: int = 0,
                        overlap_threshold: int = 1):
        """[summary]
        
        Args:
            tokens (list): [description]
            number_of_slices (int, optional): [description]. Defaults to 20.
            minimum_burst_level (int, optional): [description]. Defaults to 0.
            overlap_threshold (int, optional): [description]. Defaults to 1.
        
        Returns:
            [type]: [description]
        """

        if isinstance(tokens, list) == False:
            tokens = [tokens]

        full_lists = self.top_svo_degree(number_of_slices=number_of_slices,
                                     list_top=None,
                                     minimum_burst_level=minimum_burst_level,
                                     return_edge_overlaps=False, 
                                     overlap_threshold=overlap_threshold,
                                     )


        token_rank_dict = {}

        for day in full_lists:
            v = [item for item in full_lists[day] if item[0] in tokens]
            token_rank_dict[day] = v

        return token_rank_dict

    def plot_top_svo_degree( 
        self, 
        number_of_slices: int = 8, 
        list_top: int = 10,
        minimum_burst_level: int = 0,
        overlap_threshold: int = 1,
        filename: str = False,):
        """[summary]
        
        Args:
            number_of_slices (int, optional): [description]. Defaults to 20.
            list_top (int, optional): [description]. Defaults to 10.
            minimum_burst_level (int, optional): [description]. Defaults to 0.
            overlap_threshold (int, optional): [description]. Defaults to 1.
        """

        data = self.top_svo_degree(
            number_of_slices = number_of_slices, 
            list_top = list_top,
            minimum_burst_level = minimum_burst_level,
            return_edge_overlaps = False,
            overlap_threshold=overlap_threshold,)

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

            values.reverse()
            names.reverse()

            fig, ax = plt.subplots()
            fig.set_figwidth(6)
            fig.set_figheight(10)
            fig.suptitle('{} to {}'.format(date_names[i-1], date_names[i]), fontsize=12, ha="center")
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            plt.barh(x, values, color='#32363A')
            plt.yticks(x, names)
            if filename:
                plt.savefig(str(filename) + str(i) + ".pdf")
            else:
                plt.show()

    def plot_specific_svo_degree(self,
                             tokens: list,
                             number_of_slices: int = 15,
                             minimum_burst_level: int = 0,
                             overlap_threshold: int = 1,
                             plot_type="line",
                             filename: str = False,):
        
        if isinstance(tokens, list) == False:
            tokens = [tokens]

        if plot_type != "line" and plot_type != "bar":
            raise Exception("`plot_type` must be one of 'line' or 'bar'")

        data = self.specific_svo_degree(tokens=tokens,
                                    number_of_slices=number_of_slices,
                                    minimum_burst_level=minimum_burst_level,
                                    overlap_threshold=overlap_threshold,
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
            dates = [item[0].replace(", ", "\n") for item in v]

            fig, ax = plt.subplots()
            fig.set_figwidth(10)
            fig.set_figheight(6)
            fig.suptitle("'{}'".format(k), fontsize=12, ha="center")
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            if plot_type == "bar":
                plt.bar(x, values, color='#32363A')
            elif plot_type == "line":
                plt.plot(x, values, color='#32363A')
            plt.xticks(x, dates)
            if filename:
                plt.savefig(str(filename) + str(k) + ".pdf")
            else:
                plt.show()