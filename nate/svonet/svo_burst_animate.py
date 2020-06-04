import nate
from graph_tool.all import *
import matplotlib
import pandas as pd
import numpy as np
from collections import defaultdict
from numpy.random import *
import sys, os, os.path
import time
import datetime
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib
from PIL import Image, ImageDraw, ImageFont
from xvfbwrapper import Xvfb

"""
This module provides functions for animating the presence of bursting SVO terms over time
"""

def prepare_df(burst_dict, offset_dict):
    """
    Takes a dictionary of SVO bursts and SVO time offsets to return a temporary dataframe used
    in subsequent functions
    """
    df = pd.DataFrame()
    svo_list = []
    hierarchy_list = []
    start_list = []
    end_list = []
    num_offsets_list = []
    
    for k, v in burst_dict.items():
        for interval in v:
            svo_list.append(k)
            hierarchy_list.append(interval[0])
            start_list.append(interval[1])
            end_list.append(interval[2])
            i = 0
            for offset in offset_dict[k]:
                if offset >= interval[1] and offset <= interval[2]:
                    i+=1
            num_offsets_list.append(i)
            
    df['svo'], df['hierarchy'], df['start'], df['end'], df['num_offsets']  = svo_list, hierarchy_list, start_list, end_list, num_offsets_list
    
    return df

def add_subs_obs(g, subs_obs_list, vertex_shapes, vertex_names):
    """
    Accepts a graph-tool graph object and a list of subjects and objects to add as vertices in the graph.
    Updates the vertex_shapes vertex property map to make each subject and object a circle
    Updates the vertex_name vertex property map to assign each subject or object string as a name for each vertex
    Creates a vertex_dict that can be used to lookup the vertex ID of a given subject or object string
    """
    vertex_dict = {}
    for vertex in subs_obs_list:
        v = g.add_vertex()
        vertex_shapes[v] = 'circle'
        vertex_names[v] = vertex
        vertex_dict.update({vertex:int(v)})
    return g, vertex_dict
        
def add_verbs(g, verb_list, vertex_shapes, vertex_names):
    """
    Accepts a graph-tool graph object and a list of verbs to add as vertices in the graph.
    Updates the vertex_shapes vertex property map to make each verb a square
    Updates the vertex_name vertex property map to assign each verb string as a name for each vertex
    Creates a vertex_dict that can be used to lookup the vertex ID of a given verb string    
    """
    vertex_verb_dict = {}
    for vertex in verb_list:
        v = g.add_vertex()
        vertex_shapes[v] = 'square'
        vertex_names[v] = vertex
        vertex_verb_dict.update({vertex:int(v)})
    return g, vertex_verb_dict

def build_graph(df, pos = False, time_interval: int = 86400):
    """
    
    Args:
        df (object, optional): Pandas dataframe created by `prepare_df`
        pos (object, optional): Accepts a graph-tool `pos` vertex property map to specify graph layout. Defaults to False.
        time_interval (int, optional): Specify a custom time step interval in seconds. Defaults to 86400 (one day).
    
    Returns:
        g (object): graph-tool `graph` object with all vertex properties made internal to the object
    """

    bursts_df = df[df['hierarchy'] > 0]  # remove non-bursting terms
    bursts_df = bursts_df.sort_values(by=['svo', 'hierarchy']) # sort by SVO and then by hierarchy, ascending
    bursts_df['max_hierarchy'] = bursts_df.groupby(['svo'])['hierarchy'].transform(max) # add df column specifying the maximum burst level of each SVO entry


    edge_df = df[df['hierarchy'] == 0]  # create a dataframe of each unique SVO entry

    edges = edge_df['svo'].tolist() # create a list of SVO entries to be used for edge and vertex creation

    edge_weights = edge_df['num_offsets'].tolist() # list of edge weights based on the number of occurrences of the SVO term

    subs_obs = []  # list of subjects and objects
    verbs = [] # list of verbs
    for svo in edges:
        subs_obs.append(svo[0]) # update subject and object list with first item (subject) of each SVO
        subs_obs.append(svo[2]) # update subject and object list with third item (object) of each SVO
        verbs.append(svo[1]) # update verb list with second item (verb) of each SVO


    so_vertices = list(set(subs_obs)) # create a list of unique subjects and objects
    v_vertices = list(set(verbs)) # create a list of unique verbs

    # instantiate the graph-tool `Graph` object, as well as the shape and name property maps
    g = Graph()
    vertex_shapes = g.new_vertex_property("string")
    vertex_names = g.new_vertex_property("string")

    # pass the graph to the vertex adding functions to have vertices added and lookup dictionaries returned
    g, vertex_dict = add_subs_obs(g, so_vertices, vertex_shapes, vertex_names)
    g, vertex_verb_dict = add_verbs(g, v_vertices, vertex_shapes, vertex_names)
    
    # make the vertex property maps internal to the graph-tool `Graph` object
    g.vertex_properties['vertex_shape'] = vertex_shapes
    g.vertex_properties['vertex_name'] = vertex_names

    # check if a graph layout has been passed, otherwise use default
    if pos:

        pos = pos
    else:
        pos = graphviz_draw(g, vsize = 10, overlap = False, elen = 2, output = None)

    # make graph layout internal to graph object
    g.vertex_properties['pos'] = pos

    # the following vertex property maps are list objects that indicate the state of the vertex at each time interval
    bursting = g.new_vertex_property("object") # whether the vertex is bursting
    max_hierarchy = g.new_vertex_property("object") # whether a vertex is at maximum burst
    hierarchies = g.new_vertex_property("object") # the current burst hierarchy of the vertex
    new_burst = g.new_vertex_property("object") # whether the vertex is bursting for the first time

    times = g.new_graph_property("object") # time intervals
    
    e_bursting = g.new_edge_property("object") # whether an edge is bursting
    e_weights = g.new_edge_property("object") # edge weights

    # initialize all property maps
    for v in g.vertices():
        bursting[v] = []
        max_hierarchy[v] = []
        hierarchies[v] = []
        new_burst[v] = []
    
    for e in g.edges():
        e_bursting[e] = []
        e_weights[e] = []


    times[g] = []

    # only the maximum burst hierarchy of each SVO is needed in a given time period
    bursts_df_pruned = bursts_df.drop_duplicates(subset=['svo', 'start', 'end'], keep='last')
    bursts_df_pruned = bursts_df_pruned.sort_values(by=['start']) # sort by time for df iterating


    # create a list of time intervals to step through
    interval_list = g.new_graph_property("object")
    interval_list[g] = []

    start = bursts_df_pruned.start.min()
    end = bursts_df_pruned.end.max()

    # add times in selected intervals between start of first burst and end of last burst
    for current_time in range(int(start), int(end), time_interval):
        interval_list[g].append(current_time)

    # ensure the end of the last burst is included if time interval doesn't line up
    interval_list[g].append(end)

    # ensure that all bursts appear even if they start and end between intervals
    interval_list[g].extend(bursts_df_pruned.start.tolist())
    interval_list[g] = sorted(set(interval_list[g]))


    # initialize all vertex and edge property map masks into non-bursting state
    for i, current_time in enumerate(interval_list[g]):
        for v in g.vertices():
            bursting[v].append(False)
            max_hierarchy[v].append(False)
            hierarchies[v].append(0)
            new_burst[v].append(False)
        times[g].append(current_time)
        
        for e in g.edges():
            e_bursting[e].append(False)
            e_weights[e].append(0)

    # a set to determine if an SVO has bursted before
    bursted = set()
    
    for index, row in bursts_df_pruned.iterrows():
        svo = row['svo']
        sub,verb,obj = svo[0], svo[1], svo[2]

        # find vertex indexes using their string names
        s_index = vertex_dict[sub]
        v_index = vertex_verb_dict[verb]
        o_index = vertex_dict[obj]

        # step through each timepoint in the interval list, creating a burst-state mask for each vertex and edge
        for i, current_time in enumerate(interval_list[g]):

            # because the beginning of each burst will always be in the interval list, only check new burst status at these times
            if current_time == row['start']:
                
                if (sub,verb,obj) in bursted:
                    first_burst = False
                else:
                    first_burst = True
                
                if first_burst == True:

                    new_burst[s_index][i] = True
                    new_burst[v_index][i] = True
                    new_burst[o_index][i] = True
                    bursted.add((sub,verb,obj))                        

            # check if the current timepoint falls between the start and end times of the current burst in the DF
            if current_time >= row['start'] and current_time <= row['end']:
                # set SVO vertices to bursting at current time
                bursting[s_index][i] = True
                bursting[v_index][i] = True
                bursting[o_index][i] = True
                
                # temporary pointer to access graph-tool edges by the vertices they connect
                e1 = g.edge(s_index, v_index)
                e2 = g.edge(v_index, o_index)
                
                # set SVO edges to bursting at current time
                e_bursting[e1][i] = True
                e_bursting[e2][i] = True
                
                # set edge weights based on number of occurrences in current burst
                e_weights[e1][i] = row['num_offsets']
                e_weights[e2][i] = row['num_offsets']

                # determines whether this is the SVO's highest burst
                if row['hierarchy'] == row['max_hierarchy']:
                    max_hierarchy[s_index][i] = True
                    max_hierarchy[v_index][i] = True
                    max_hierarchy[o_index][i] = True

                # ensure that subjects, verbs, or objects that appear in multiple bursting SVO terms at once
                # do not have their hierarchy overwritten by the lower bursting SVO
                if row['hierarchy'] > hierarchies[s_index][i]:
                    hierarchies[s_index][i] = row['hierarchy']

                if row['hierarchy'] > hierarchies[v_index][i]:
                    hierarchies[v_index][i] = row['hierarchy']

                if row['hierarchy'] > hierarchies[o_index][i]:
                    hierarchies[o_index][i] = row['hierarchy']

    # make all vertex and edge properties internal to the graph-tool graph object
    g.vertex_properties["bursting"] = bursting
    g.vertex_properties["max_hierarchy"] = max_hierarchy
    g.vertex_properties["hierarchies"] = hierarchies
    g.vertex_properties["new_burst"] = new_burst
    
    g.edge_properties["e_bursting"] = e_bursting
    g.edge_properties['e_weights'] = e_weights

    g.graph_properties["times"] = times
    g.graph_properties["interval_list"] = interval_list
    
    return g


def animate_graph(graph, pos, offscreen, new_burst_halo, dpi):
    """Animates the bursts of an SVO network over time.

    The `new_burst_halo` and `dpi` arguments are not used.
    """
    frame = 0
    g = graph

    # counter to make sure Gtk exits
    max_count = len(interval_list)-1
    current_interval = 0

    # make sure there is a directory to dump frames to
    if offscreen and not os.path.exists(r"./data/frames"):
        os.makedirs(r"./data/frames")

    # for machines without video cards, emulate a display to allow saving frames to disk
    if Gtk.init_check()[0] == False:
        print('Display not found. Starting virtual display.')
        _xvfb = Xvfb(width=1920, height=1080)
        _xvfb.start()


    # light grey for default states, edges black when bursting
    no_burst = [0.5, 0.5, 0.5, 0.25]    # Grey
    e_burst = [0,0,0,1]                 # Black
    e_no_burst = [0.5, 0.5, 0.5, 0.25]  # Grey

    # heatmap for burst hierarchies, from seaborn color palettes: https://seaborn.pydata.org/tutorial/color_palettes.html    
    blue_heatmap = {
        **dict.fromkeys([0], [0.5, 0.5, 0.5, 0.25]),
        **dict.fromkeys([1,2,3], [0.8978854286812764, 0.939038831218762, 0.977362552864283, 1]), 
        **dict.fromkeys([4,5,6], [0.828881199538639, 0.8937639369473279, 0.954725105728566, 1]),
        **dict.fromkeys([7,8,9], [0.7506343713956171, 0.8478431372549019, 0.9282122260668974, 1]),
        **dict.fromkeys([10,11,12], [0.6325259515570935, 0.7976470588235294, 0.8868742791234141, 1]),
        **dict.fromkeys([13,14,15], [0.491764705882353, 0.7219684736639754, 0.8547789311803152, 1]),
        **dict.fromkeys([16,17,18], [0.36159938485198, 0.6427374086889658, 0.8165782391387928, 1]),
        **dict.fromkeys([19,20,21], [0.24816608996539793, 0.5618915801614763, 0.7709803921568628, 1]),
        **dict.fromkeys([22,23,24], [0.15072664359861593, 0.4644521337946943, 0.7207843137254902, 1]),
        **dict.fromkeys([25,26,27], [0.07481737793156479, 0.3732564398308343, 0.6552095347943099, 1]),
        **dict.fromkeys([28,29,30,31,32], [0.03137254901960784, 0.28161476355247983, 0.5582622068435218, 1])
    }
                    
    # initialize all vertices and edges to the not_bursting state
    state = g.new_vertex_property("vector<double>")
    for v in g.vertices():
        state[v] = no_burst
        
    e_state = g.new_edge_property("vector<double>")
    for e in g.edges():
        e_state[e] = e_no_burst

    # initialize graph properties for current state

    currently_new = g.new_vertex_property("bool")
    currently_new.a = False  # assigns False to all vertices    
    current_v_name = g.new_vertex_property('string')    
    current_edge_weight = g.new_edge_property("int")

    # gather properties from imported graph

    bursting = g.vertex_properties["bursting"]
    max_hierarchy = g.vertex_properties["max_hierarchy"]
    hierarchies = g.vertex_properties["hierarchies"]
    new_burst = g.vertex_properties["new_burst"]

    # check if a different graph layout has been supplied, otherwise collect default layout from graph object
    if pos:
        pos = pos
    else:
        pos = g.vertex_properties["pos"]

    e_bursting = g.edge_properties["e_bursting"]
    e_weights = g.edge_properties['e_weights']
        
    times = g.graph_properties["times"]
    interval_list = g.graph_properties["interval_list"]

    # make sure graph is not filtered
    g.set_vertex_filter(None)
    g.set_edge_filter(None)

    # this creates a GTK+ window with the initial graph layout
    if not offscreen:
        # creates pop-up interactive Gtk window
        win = GraphWindow(g, pos, geometry=(800, 800),
                          edge_color= e_state,
                          vertex_fill_color=state,
                          vertex_halo=currently_new,
                          vertex_halo_color=[0.8, 0, 0, 0.6],
                          vertex_text = current_v_name,
                          #edge_pen_width = g.edge_properties['current_edge_weight'],
                          vertex_text_position = 2,
                          vertex_font_size = 13,
                          vertex_text_color = 'black',
                          vertex_shape = g.vertex_properties['vertex_shape'])
    else:
        # for dumping frames to disk
        frame = 0
        win = Gtk.OffscreenWindow()
        win.set_default_size(800, 800)
        win.graph = GraphWidget(g, pos,
                          edge_color=e_state,  
                          vertex_fill_color=state,
                          vertex_halo=currently_new,
                          vertex_halo_color=[0.8, 0, 0, 0.6],
                          vertex_text = current_v_name,
                          #edge_pen_width = g.edge_properties['current_edge_weight'],
                          vertex_text_position = 2,
                          vertex_font_size = 13,  
                          vertex_text_color = 'black',
                          vertex_shape = g.vertex_properties['vertex_shape'])

        win.add(win.graph)

    # This function will be called repeatedly by the GTK+ main loop, updating vertex and edge states
    # according to their bursting status.

    def update_state():
        # Gtk needs these variables to be global
        global max_count, current_interval, g, frame, _xvfb 

        # check for failed virtual display
        if Gtk.init_check()[0] == False:
            print('Virtual display failed, quitting.')
            Gtk.main_quit()
            return False
        
        # check if we've exhausted all timepoints
        if current_interval > max_count:
            Gtk.main_quit()
            return False

        # update state of vertices and edges using the index of the current interval to access property map masks
        for v in g.vertices():
            if bursting[v][current_interval] == True:
                current_v_name[v] = g.vertex_properties.vertex_name[v]
                if new_burst[v][current_interval] == True:
                    currently_new[v] = True
                else:
                    currently_new[v] = False

                # use current burst hierarchy to update state based on heatmap color palette 
                h_colour = blue_heatmap[hierarchies[v][current_interval]]
                state[v] = h_colour
            else:
                state[v] = no_burst
                current_v_name[v] = '' # avoid drawing vertex labels if they aren't bursting
                currently_new[v] = False
                        
        for e in g.edges():
            if e_bursting[e][current_interval] == True:
                current_edge_weight[e] = e_weights[e][current_interval]
                e_state[e] = e_burst
            else:
                e_state[e] = e_no_burst

        # slow down the windowed animation

        if not offscreen:
            time.sleep(0.5)



        # the following will force the re-drawing of the graph and issue a
        # re-drawing of the GTK window.

        win.graph.regenerate_surface()
        win.graph.queue_draw()

        # if doing an offscreen animation, dump frame to disk
        if offscreen:

            # names file based on current frame number
            this_filename = r'./data/frames/graph%06d.png' % frame

            pixbuf = win.get_pixbuf()
            pixbuf.savev(this_filename, 'png', ["x-dpi", "y-dpi"], ["300","300"])

            # add datetime to the frame just saved to disk
            with Image.open(this_filename) as im:
                try:
                    myfont = ImageFont.truetype("./Arial.ttf", 30)
                except:
                    myfont = ImageFont.load_default()

                width, height = im.size
                
                try:
                    date = datetime.datetime.fromtimestamp(times[frame - 1]).strftime('%Y-%m-%d')
                    msg = str(date)
                except KeyError:
                    msg = "No time data for this slice"

                draw = ImageDraw.Draw(im)
                w, h = draw.textsize(msg, myfont)
                draw.text(((width - w)/2, height/50), msg, font=myfont, fill="black")

                im.save(this_filename)
            frame += 1  # increment frame for file naming and date stamping

            # exit after dumping the final time interval frame
            if current_interval == max_count:
                Gtk.main_quit()
                return False

        # need to return True so that the main loop will call this function more
        # than once.
        current_interval += 1
        return True


    # bind the function above as an 'idle' callback
    cid = GLib.idle_add(update_state)

    # give the user the ability to stop the program by closing the window
    win.connect("delete_event", Gtk.main_quit)

    # actually show the window, and start the main loop
    win.show_all()
    Gtk.main()


