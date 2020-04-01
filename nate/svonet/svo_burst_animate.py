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

	start = min(bursts_df['start'].tolist())
	stop = max(bursts_df['end'].tolist())

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
		pos = graphviz_draw(g, vsize = 10, overlap = False, output = None)

	g.vertex_properties['pos'] = pos

	bursting = g.new_vertex_property("object")
	max_hierarchy = g.new_vertex_property("object")
	hierarchies = g.new_vertex_property("object")
	new_burst = g.new_vertex_property("object")
	has_bursted = g.new_vertex_property('bool')
	has_bursted.a = False

	times = g.new_graph_property("object")

	for v in g.vertices():
		bursting[v] = []
		max_hierarchy[v] = []
		hierarchies[v] = []
		new_burst[v] = []


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


	for index, row in bursts_df_pruned.iterrows():
		svo = row['svo']
		sub,verb,obj = svo[0], svo[1], svo[2]

		s_index = vertex_dict[sub]
		v_index = vertex_verb_dict[verb]
		o_index = vertex_dict[obj]

		has_bursted[s_index] = False
		has_bursted[v_index] = False
		has_bursted[o_index] = False

		for i, current_time in enumerate(interval_list[g]):

			any_burst = False    
			s_bursting = False
			v_bursting = False
			o_bursting = False
			s_new_burst = False
			v_new_burst = False
			o_new_burst = False
			max_h = False

			if current_time >= row['start']:
				if has_bursted[s_index] == False:
					s_bursting = True
					s_new_burst = True
					has_bursted[s_index] = True
				else:
					s_new_burst = False

				if has_bursted[v_index] == False:
					v_bursting = True
					v_new_burst = True
					has_bursted[v_index] = True
				else:
					v_new_burst = False

				if has_bursted[o_index] == False:
					o_bursting = True
					o_new_burst = True
					has_bursted[o_index] = True
				else:
					o_new_burst = False

				if current_time < row['end']:
					s_bursting = True
					v_bursting = True
					o_bursting = True
					
					
				if s_new_burst == True or v_new_burst == True or o_new_burst == True:
					s_new_burst = True
					v_new_burst = True
					o_new_burst = True

				if s_bursting == True or v_bursting == True or o_bursting == True:
					s_bursting = True
					v_bursting = True
					o_bursting = True

					if row['hierarchy'] == row['max_hierarchy']:
						max_h = True



					bursting[s_index][i] = s_bursting
					bursting[v_index][i] = v_bursting
					bursting[o_index][i] = o_bursting

					max_hierarchy[s_index][i] = max_h
					max_hierarchy[v_index][i] = max_h
					max_hierarchy[o_index][i] = max_h

					new_burst[s_index][i] = s_new_burst
					new_burst[v_index][i] = v_new_burst
					new_burst[o_index][i] = o_new_burst


	g.vertex_properties["bursting"] = bursting
	g.vertex_properties["max_hierarchy"] = max_hierarchy
	g.vertex_properties["hierarchies"] = hierarchies
	g.vertex_properties["new_burst"] = new_burst

	g.graph_properties["times"] = times
	g.graph_properties["interval_list"] = interval_list

	return g


def animate_graph(graph, offscreen = True, offscreen_params = False, onscreen_params = False):
	global g, frame
	frame = 0
	g = graph
	burst = [1, 1, 1, 1]           # White color = bursting
	peak = [0, 0, 0, 1]           # Black color = peak burst
	no_burst = [0.5, 0.5, 0.5, 1.]    # Grey color (will not actually be drawn) = not bursting

	# Initialize all vertices to the not_bursting state
	state = g.new_vertex_property("vector<double>")
	for v in g.vertices():
		state[v] = no_burst

	# Initialize local graph properties

	has_bursted = g.new_vertex_property('bool')
	has_bursted.a = False
	currently_bursting = g.new_vertex_property("bool")
	currently_bursting.a = False
	currently_new = g.new_vertex_property("bool")
	currently_new.a = False

	# Gather properties from imported graph

	bursting = g.vertex_properties["bursting"]
	max_hierarchy = g.vertex_properties["max_hierarchy"]
	hierarchies = g.vertex_properties["hierarchies"]
	new_burst = g.vertex_properties["new_burst"]
	pos = g.vertex_properties["pos"]

	times = g.graph_properties["times"]
	interval_list = g.graph_properties["interval_list"]

	# If True, the frames will be dumped to disk as images.
	#the following was used when this script was run standalone
	#offscreen = sys.argv[1] == "offscreen" if len(sys.argv) > 1 else False
	#this is used in a notebook
	#offscreen = False
	global max_count
	max_count = len(interval_list)-1
	global current_interval
	current_interval = 0
	if offscreen and not os.path.exists("./frames"):
		os.mkdir("./frames")

	g.set_vertex_filter(None)

	# This creates a GTK+ window with the initial graph layout
	if not offscreen:
		if onscreen_params:
			custom_parameters = []
		else:
			win = GraphWindow(g, pos, geometry=(800, 800),
							  edge_color=[0.6, 0.6, 0.6, 1],
							  vertex_fill_color=state,
							  vertex_halo=currently_new,
							  vertex_halo_color=[0.8, 0, 0, 0.6],
							  vertex_text = g.vertex_properties['vertex_name'],
							  #edge_pen_width = g.edge_properties['edge_weights'],
							  vertex_text_position = 2,
							  vertex_text_color = 'black',
							  vertex_shape = g.vertex_properties['vertex_shape'])
	else:
		frame = 0
		win = Gtk.OffscreenWindow()

		if offscreen_params:
			custom_parameters = []
		else:
			win.set_default_size(800, 800)
			win.graph = GraphWidget(g, pos,
							  edge_color=[0.6, 0.6, 0.6, 1],
							  vertex_fill_color=state,
							  vertex_halo=currently_new,
							  vertex_halo_color=[0.8, 0, 0, 0.6],
							  vertex_text = g.vertex_properties['vertex_name'],
							  #edge_pen_width = g.edge_properties['edge_weights'],
							  vertex_text_position = 2,
							  vertex_text_color = 'black',
							  vertex_shape = g.vertex_properties['vertex_shape'])

		win.add(win.graph)

	# This function will be called repeatedly by the GTK+ main loop, and we use it
	# to update the state according to the bursting status.

	for v in g.vertices():
		if any(bursting[v]):
			has_bursted[v] = True

	def update_state():
		global max_count, current_interval, g, frame 

		if current_interval == max_count:
			Gtk.main_quit()
			return False
		
		currently_bursting.a = False
		g.set_vertex_filter(has_bursted)

		currently_new.a = False
		any_bursts = False
		for v in g.vertices():
				if bursting[v][current_interval] == True:
					currently_bursting[v] = True
					state[v] = burst
					if new_burst[v][current_interval] == True:
						currently_new[v] = True
					if max_hierarchy[v][current_interval] == True:
						state[v] = peak
					any_bursts = True



		# Filter out the non-bursting vertices
		g.set_vertex_filter(currently_bursting)

		#uncomment to slow-down the windowed animation

		#if not offscreen:
			#time.sleep(.3)

		

		# The following will force the re-drawing of the graph, and issue a
		# re-drawing of the GTK window.

		win.graph.regenerate_surface()
		win.graph.queue_draw()

		# if doing an offscreen animation, dump frame to disk
		if offscreen:
			global frame
			this_filename = r'./frames/sirs%06d.png' % frame

			pixbuf = win.get_pixbuf()
			pixbuf.savev(this_filename, 'png', [], [])

			with Image.open(this_filename) as im:

				myfont = ImageFont.truetype("Arial.ttf", 30)

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

		g.set_vertex_filter(None)

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


