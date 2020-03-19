"""
This is a MODULE docstring
"""

import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.axes
import datetime
from typing import Tuple, List
from datetime import datetime, timezone
 

def generate_ticks(offsets, number_of_ticks = 10) -> Tuple[List[int], List[str]]:
    """
    This is a docstring
    """ 
    chunk_size = round((max(offsets) - min(offsets))/number_of_ticks)
    
    tick_positions:List[int] = []
    
    for i in range(0, number_of_ticks + 1):
        tick_positions.append(int(min(offsets) + (i * chunk_size)))
        
    tick_labels:List[str] = []
        
    for tick in tick_positions:
        
        time_label = datetime.utcfromtimestamp(tick).strftime("%b %d, %Y")
        
        tick_labels.append(time_label)
    
    return tick_positions, tick_labels


def plot_bursts(offsets, bursts, plot_title, output_path = False, 
                plot_size_x = 20, plot_size_y = 10, plot_vertically = False, num_ticks = 10, rug_alpha = 0.45, dark = True):
    """
    This is a docstring
    """ 
    tick_positions, tick_labels = generate_ticks(offsets, number_of_ticks=num_ticks)

    plt.figure(figsize=(plot_size_x, plot_size_y))
    
    if plot_vertically == True:
        burst_axis = "y"
        burst_lines = plt.vlines
        burst_ticks = plt.yticks
        time_ticks = plt.xticks
        time_label = plt.xlabel
        
    else:
        burst_axis = "x"
        burst_lines = plt.hlines
        burst_ticks = plt.xticks
        time_ticks = plt.yticks
        time_label = plt.ylabel  


    if dark:
        sns.set_style("ticks")
        plt.style.use("dark_background")
        rug_colour = "turquoise"
        line_colour = '#caa0ff'
    else:
        sns.set_style("dark")
        rug_colour = "#107ab0"
        line_colour = 'k'

        

    seaborn_plot = sns.rugplot(offsets, axis = burst_axis, height = 0.1, linewidths = 200, alpha = rug_alpha, colors = rug_colour).set_title(plot_title, fontsize = 20)

    burst_ticks(tick_positions, tick_labels, rotation=35, fontsize = 15)
    time_ticks(fontsize = 15)
    time_label("Burst Intensity (0 = Lowest)", fontsize = 20)

    for entry in bursts:
        burst_lines(entry[0], entry[1], entry[2], label=str(entry[0]), colors = line_colour, linewidths = 7.5)

    if output_path != False:
        final_path = output_path + "_" + plot_title.replace(" + ", "_").replace(" ", "_") + ".png"
        seaborn_plot.get_figure().savefig(final_path, dpi=100)