"""
This is a MODULE docstring
"""

import networkx as nx
from PIL import Image
from os import remove
from typing import Tuple, List
from datetime import datetime

color_dict = {
    0: "#F62D2D",
    1: "#D3212D",
    2: "#A2264B",
    3: "#722B6A",
    4: "#412F88",
    5: "#1F0033",
    6: "#000000"
}


def generate_ticks(offsets, number_of_ticks=10) -> Tuple[List[int], List[str]]:
    """[summary]
    
    Args:
        offsets ([type]): [description]
        number_of_ticks (int, optional): [description]. Defaults to 10.
    
    Returns:
        Tuple[List[int], List[str]]: [description]
    """

    rawdif = max(offsets) - min(offsets)

    divdiff = rawdif / number_of_ticks

    chunk_size = round(divdiff)

    tick_positions: List[int] = []

    for i in range(0, number_of_ticks + 1):
        tick_positions.append(int(min(offsets) + (i * chunk_size)))

    tick_labels: List[str] = []

    for tick in tick_positions:

        time_label = datetime.utcfromtimestamp(tick).strftime("%b %d, %Y")

        tick_labels.append(time_label)

    return tick_positions, tick_labels


def find_max_burst(burst_list: list, offset_start, offset_end):
    """[summary]
    
    Args:
        burst_list (list): [description]
        offset_start ([type]): [description]
        offset_end ([type]): [description]
    
    Returns:
        [type]: [description]
    """

    burst_levels = set()
    burst_levels.add(0)

    for burst in burst_list:
        if offset_start < burst[1] < offset_end or offset_start < burst[
                2] < offset_end:
            burst_levels.add(burst[0])

    return max(burst_levels)


class SVOgraphMixin():

    def get_giant_component(self):
        """[summary]
        
        Returns:
            [type]: [description]
        """

        G = nx.DiGraph()

        svo_list = self.edge_burst_dict

        for entry in svo_list:
            G.add_edge(entry[0], entry[2], label=" " + entry[1])

        return G.subgraph(max(nx.weakly_connected_components(G),
                              key=len)).copy()

    def save_svo_graph(self,
                       term_list,
                       use_giant=False,
                       file_name=None,
                       return_networkx=False):
        """[summary]
        
        Args:
            term_list ([type]): [description]
            use_giant (bool, optional): [description]. Defaults to False.
            file_name ([type], optional): [description]. Defaults to None.
            return_networkx (bool, optional): [description]. Defaults to False.
        
        Returns:
            [type]: [description]
        """

        G = nx.DiGraph()

        if isinstance(term_list, str):
            term_list = [term_list]

        svo_list = self.edge_burst_dict

        for entry in svo_list:
            include = False
            for entry_part in entry:
                if entry_part in term_list:
                    include = True

                for term in term_list:
                    if term in entry_part or entry_part in term:
                        include = True

            if include:
                G.add_edge(entry[0], entry[2], label=" " + entry[1])

        for entry in G:
            G.nodes[entry]['style'] = 'filled'
            G.nodes[entry]['fillcolor'] = 'cadetblue2'

        toPdot = nx.drawing.nx_pydot.to_pydot
        N = toPdot(G)

        if return_networkx:
            return G
        else:
            if file_name == None:
                file_name = "_".join(term_list)

            N.write(file_name + "_svo_visualization.png",
                    prog='dot',
                    format='png')

    def create_svo_animation(self,
                             term_list,
                             use_giant=False,
                             num_ticks=20,
                             delay_per_tick=3,
                             file_name="test",
                             remove_images=True):
        """[summary]
        
        Args:
            term_list ([type]): [description]
            use_giant (bool, optional): [description]. Defaults to False.
            num_ticks (int, optional): [description]. Defaults to 20.
            delay_per_tick (int, optional): [description]. Defaults to 3.
            file_name (str, optional): [description]. Defaults to "test".
            remove_images (bool, optional): [description]. Defaults to True.
        """

        file_name = str(file_name)

        if use_giant:
            G = self.get_giant_component()
        else:
            G = self.save_svo_graph(self, term_list, return_networkx=True)

        offset_list = set()
        svo_keys = []

        for edge in G.edges:
            G[edge[0]][edge[1]]['burst_last'] = -100
            G[edge[0]][edge[1]]['burst_level'] = 0
            G[edge[0]][edge[1]]['color'] = "black"
            G[edge[0]][edge[1]]['penwidth'] = 1
            label = G.get_edge_data(edge[0], edge[1])['label']
            key = (edge[0], label[1:], edge[1])
            offsets = self.offset_dict[key]
            offset_list.add(min(offsets))
            offset_list.add(max(offsets))
            svo_keys.append(key)

        time_slices, time_labels = generate_ticks(offset_list, num_ticks)

        initial_graph = nx.drawing.nx_pydot.to_pydot(G)

        graphs = [initial_graph]

        for i in range(1, len(time_slices)):
            # The following lines are for functionality not yet implemented: we can cause the nodes - not just the edges - to show their burst patterns
            # bursting_nodes = set()
            # cooling_nodes = set()
            # inactive_nodes = set()
            for key in svo_keys:

                burst_level = find_max_burst(self.edge_burst_dict[key],
                                             time_slices[i - 1], time_slices[i])

                G[key[0]][key[2]]['burst_level'] = burst_level

                if burst_level > 0:
                    G[key[0]][key[2]]['burst_last'] = i
                    # print(key[0])
                    # print(key[1])
                    # print(key[2])
                    # print(i)

                distance = i - G[key[0]][key[2]]['burst_last']

                color = color_dict[min([distance, 6])]
                penwidth = max([6 - distance, 0.5])

                G[key[0]][key[2]]['penwidth'] = penwidth
                G[key[0]][key[2]]['color'] = color

            subgraph = nx.drawing.nx_pydot.to_pydot(G)

            graphs.append(subgraph)

        filenames = []

        for i in range(len(graphs)):
            this_file = file_name + "_" + str(i) + ".png"
            filenames.append(this_file)

            graphs[i].write_png(this_file)

        images = []

        for name in filenames:
            images.append(Image.open(name))

        images[0].save(file_name + ".gif",
                       save_all=True,
                       append_images=images[1:],
                       optimize=False,
                       duration=len(images * delay_per_tick),
                       loop=0)

        if remove_images:
            for file_ in filenames:
                remove(file_)
