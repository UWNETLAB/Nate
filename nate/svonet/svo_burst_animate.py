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

def prepare_df(burst_dict, offset_dict):
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
    vertex_dict = {}
    for vertex in subs_obs_list:
        v = g.add_vertex()
        vertex_shapes[v] = 'circle'
        vertex_names[v] = vertex
        vertex_dict.update({vertex:int(v)})
    return g, vertex_dict
        
def add_verbs(g, verb_list, vertex_shapes, vertex_names):
    vertex_verb_dict = {}
    for vertex in verb_list:
        v = g.add_vertex()
        vertex_shapes[v] = 'square'
        vertex_names[v] = vertex
        vertex_verb_dict.update({vertex:int(v)})
    return g, vertex_verb_dict

def build_graph(df, pos = False, time_interval = False):
    """
    
    Args:
        df ([type]): [description]
        pos (bool, optional): [description]. Defaults to False.
        time_interval (bool, optional): [description]. Defaults to False.
    
    Returns:
        [type]: [description]
    """

    bursts_df = df[df['hierarchy'] > 0]
    bursts_df = bursts_df.sort_values(by=['svo', 'hierarchy'])
    bursts_df['max_hierarchy'] = bursts_df.groupby(['svo'])['hierarchy'].transform(max)


    edge_df = df[df['hierarchy'] == 0]

    edges = edge_df['svo'].tolist()

    edge_weights = edge_df['num_offsets'].tolist()

    vertex_dict = {}
    vertex_verb_dict = {}
    subs_obs = []
    verbs = []
    for svo in edges:
        subs_obs.append(svo[0])
        subs_obs.append(svo[2])
        verbs.append(svo[1])


    so_vertexes = list(set(subs_obs))
    v_vertexes = list(set(verbs))

    g = Graph()
    vertex_shapes = g.new_vertex_property("string")
    vertex_names = g.new_vertex_property("string")

    g, vertex_dict = add_subs_obs(g, so_vertexes, vertex_shapes, vertex_names)
    g, vertex_verb_dict = add_verbs(g, v_vertexes, vertex_shapes, vertex_names)
    
    g.vertex_properties['vertex_shape'] = vertex_shapes
    g.vertex_properties['vertex_name'] = vertex_names


    sv_weight_dict = defaultdict(int)
    vo_weight_dict = defaultdict(int)

    for i, term in enumerate(edges):
        sub, verb, obj = term[0], term[1], term[2]
        sv_weight_dict[(sub,verb)] += edge_weights[i]
        vo_weight_dict[(verb,obj)] += edge_weights[i]

    edge_weights = g.new_edge_property("int")

    for k, v in sv_weight_dict.items():
        v1 = k[0]
        v2 = k[1]

        e = g.add_edge(vertex_dict[v1], vertex_verb_dict[v2])
        edge_weights[e] = v

    for k, v in vo_weight_dict.items():
        v1 = k[0]
        v2 = k[1]

        e = g.add_edge(vertex_verb_dict[v1], vertex_dict[v2])
        edge_weights[e] = v

    g.edge_properties['edge_weights'] = edge_weights

    if pos:

        pos = pos
    else:
        pos = graphviz_draw(g, vsize = 10, overlap = False, elen = 2, output = None)

    g.vertex_properties['pos'] = pos

    bursting = g.new_vertex_property("object")
    max_hierarchy = g.new_vertex_property("object")
    hierarchies = g.new_vertex_property("object")
    new_burst = g.new_vertex_property("object")

    times = g.new_graph_property("object")
    
    e_bursting = g.new_edge_property("object")
    e_weights = g.new_edge_property("object")

    for v in g.vertices():
        bursting[v] = []
        max_hierarchy[v] = []
        hierarchies[v] = []
        new_burst[v] = []
    
    for e in g.edges():
        e_bursting[e] = []
        e_weights[e] = []


    times[g] = []

    bursts_df_pruned = bursts_df.drop_duplicates(subset=['svo', 'start', 'end'], keep='last')
    bursts_df_pruned = bursts_df_pruned.sort_values(by=['start'])

    interval_list = g.new_graph_property("object")
    interval_list[g] = []
    
    if time_interval == False:
        time_interval = int(86400)

    for index, row in bursts_df_pruned.iterrows():
        start, end = row['start'], row['end']
        for current_time in range(int(start), int(end), time_interval):
            interval_list[g].append(current_time)

    interval_list[g] = sorted(set(interval_list[g]))

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

    bursted_with = defaultdict(list)
    
    for index, row in bursts_df_pruned.iterrows():
        svo = row['svo']
        sub,verb,obj = svo[0], svo[1], svo[2]

        s_index = vertex_dict[sub]
        v_index = vertex_verb_dict[verb]
        o_index = vertex_dict[obj]
        
        vo = (verb,obj)

        for i, current_time in enumerate(interval_list[g]):

            if current_time == row['start']:
                first_burst = False
                
                if sub not in bursted_with:
                    first_burst = True
                elif vo not in bursted_with[sub]:
                    first_burst = True
                
                if first_burst == True:

                    new_burst[s_index][i] = True
                    new_burst[v_index][i] = True
                    new_burst[o_index][i] = True
                    bursted_with[sub].append(vo)                        

            if current_time >= row['start'] and current_time <= row['end']:
                bursting[s_index][i] = True
                bursting[v_index][i] = True
                bursting[o_index][i] = True
                
                e1 = g.edge(s_index, v_index)
                e2 = g.edge(v_index, o_index)
                
                e_bursting[e1][i] = True
                e_bursting[e2][i] = True
                
                e_weights[e1][i] = row['num_offsets']
                e_weights[e2][i] = row['num_offsets']

                if row['hierarchy'] == row['max_hierarchy']:
                    max_hierarchy[s_index][i] = True
                    max_hierarchy[v_index][i] = True
                    max_hierarchy[o_index][i] = True

                if row['hierarchy'] > hierarchies[s_index][i]:
                    hierarchies[s_index][i] = row['hierarchy']

                if row['hierarchy'] > hierarchies[v_index][i]:
                    hierarchies[v_index][i] = row['hierarchy']

                if row['hierarchy'] > hierarchies[o_index][i]:
                    hierarchies[o_index][i] = row['hierarchy']

    g.vertex_properties["bursting"] = bursting
    g.vertex_properties["max_hierarchy"] = max_hierarchy
    g.vertex_properties["hierarchies"] = hierarchies
    g.vertex_properties["new_burst"] = new_burst
    
    g.edge_properties["e_bursting"] = e_bursting
    g.edge_properties['e_weights'] = e_weights

    g.graph_properties["times"] = times
    g.graph_properties["interval_list"] = interval_list
    
    return g


def animate_graph(graph, pos, offscreen, dpi = 300, new_burst_halo = True):
    global g, frame
    frame = 0
    g = graph

    no_burst = [0.5, 0.5, 0.5, 0.25]    # Grey
    e_burst = [0,0,0,1]                 # Black
    e_no_burst = [0.5, 0.5, 0.5, 0.25]  # Grey
    
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
                    
    # Initialize all vertices to the not_bursting state
    state = g.new_vertex_property("vector<double>")
    for v in g.vertices():
        state[v] = no_burst
        
    e_state = g.new_edge_property("vector<double>")
    for e in g.edges():
        e_state[e] = e_no_burst

    # Initialize local graph properties

    currently_new = g.new_vertex_property("bool")
    currently_new.a = False
    current_hierarchy = g.new_vertex_property('vector<double>')
    
    current_v_name = g.new_vertex_property('string')
    
    current_edge_weight = g.new_edge_property("int")

    # Gather properties from imported graph

    bursting = g.vertex_properties["bursting"]
    max_hierarchy = g.vertex_properties["max_hierarchy"]
    hierarchies = g.vertex_properties["hierarchies"]
    new_burst = g.vertex_properties["new_burst"]
    if pos:
        pos = pos
    else:
        pos = g.vertex_properties["pos"]

    e_bursting = g.edge_properties["e_bursting"]
    e_weights = g.edge_properties['e_weights']
        
    times = g.graph_properties["times"]
    interval_list = g.graph_properties["interval_list"]


    global max_count
    max_count = len(interval_list)-1
    global current_interval
    current_interval = 0
    if offscreen and not os.path.exists(r"./data/frames"):
        os.makedirs(r"./data/frames")

    g.set_vertex_filter(None)
    g.set_edge_filter(None)

    # This creates a GTK+ window with the initial graph layout
    if not offscreen:
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

    # This function will be called repeatedly by the GTK+ main loop, and we use it
    # to update the state according to the bursting status.

    def update_state():
        global max_count, current_interval, g, frame 

        if current_interval == max_count:
            Gtk.main_quit()
            return False

        for v in g.vertices():
            if bursting[v][current_interval] == True:
                #currently_bursting[v] = True
                current_v_name[v] = g.vertex_properties.vertex_name[v]
                if new_burst[v][current_interval] == True:
                    currently_new[v] = True
                else:
                    currently_new[v] = False
                
                h_colour = blue_heatmap[hierarchies[v][current_interval]]
                state[v] = h_colour
            else:
                state[v] = no_burst
                current_v_name[v] = ''
                currently_new[v] = False
                        
        for e in g.edges():
            if e_bursting[e][current_interval] == True:
                #currently_e_bursting[e] = True
                current_edge_weight[e] = e_weights[e][current_interval]
                e_state[e] = e_burst
            else:
                e_state[e] = e_no_burst

        # Slow down the windowed animation

        if not offscreen:
            time.sleep(0.5)



        # The following will force the re-drawing of the graph, and issue a
        # re-drawing of the GTK window.

        win.graph.regenerate_surface()
        win.graph.queue_draw()

        # if doing an offscreen animation, dump frame to disk
        if offscreen:
            global frame
            this_filename = r'./data/frames/graph%06d.png' % frame

            pixbuf = win.get_pixbuf()
            pixbuf.savev(this_filename, 'png', ["x-dpi", "y-dpi"], ["300","300"])

            with Image.open(this_filename) as im:

                myfont = ImageFont.truetype("./Arial.ttf", 30)

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
            frame += 1
            if current_interval == max_count:
                Gtk.main_quit()
                return False

        # We need to return True so that the main loop will call this function more
        # than once.
        current_interval += 1
        return True


    # Bind the function above as an 'idle' callback.
    cid = GLib.idle_add(update_state)

    # We will give the user the ability to stop the program by closing the window.
    win.connect("delete_event", Gtk.main_quit)

    # Actually show the window, and start the main loop.
    win.show_all()
    Gtk.main()


