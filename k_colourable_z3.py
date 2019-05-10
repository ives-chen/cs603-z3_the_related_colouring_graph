import sys
import pygraphviz as pgv
from z3 import *

#the list of colour
color_available = [
	'red', 'orange', 'green', 'blue', 'purple',
	'darkcyan', 'coral', 'chocolate', 'darkgoldenrod', 'darkgray',
	'darkkhaki', 'deeppink'
]

def graph_solver(type, solver=None, graph=None, chromatic_number=None):
	#Z3 init
	if type == 'init':
		return Solver()
	#use Z3 to solve chromatic number
	elif type == 'solve_chromatic_number':
		#use Dictionaries to collect all node and its value
		name_parameter = dict((name_node, Int('Node_%r' % name_node)) for name_node in graph.nodes())
		
		#increase the chromatic number gradually to a satisfied model
		chromatic_number = 0
		while True:
			chromatic_number += 1
			for node in graph.nodes():
				#Define the number of colour that node can use
				solver.add(name_parameter[node] >= 1, name_parameter[node] <= chromatic_number)
				
				#b.	Make a constraint for no two adjacent vertices in the graph have the same colour 
				for neighbor in graph.neighbors(node):
					solver.add(name_parameter[node] != name_parameter[neighbor])
			
			#find a satisfied model
			if solver.check() == sat:
				return chromatic_number
			#Can not find a satisfied model
			else:
				if chromatic_number > graph.number_of_nodes():
					raise Exception('Could not find a solution.')
				else:
					solver.reset()
	#find the possible ways of colouring the graph
	elif type == 'all_possible_way':
		solver.reset()
		
		#use Dictionaries to collect all node and its value
		#the basic constraints about
		#	1. Define the number of colour that node can use based on the found and fixed chromatic number
		#	2. Make a constraint for no two adjacent vertices in the graph have the same colour 
		name_parameter = dict((name_node, Int('Node_%r' % name_node)) for name_node in graph.nodes())
		for node in graph.nodes():
			solver.add(name_parameter[node] >= 0, name_parameter[node] <= (chromatic_number-1))
			for neighbor in graph.neighbors(node):
				solver.add(name_parameter[node] != name_parameter[neighbor])
		
		#add the new need blocked parameter that has found so far into Z3
		#in order to get the new parameter
		block_dict= []
		while solver.check()==sat:
			#get the parameter that has found from last time
			model_color=solver.model()
			dict_temp = dict((name_node, model_color[color_name_node].as_long()) for name_node, color_name_node in name_parameter.iteritems())
			block_dict.append(dict_temp)
			
			#add the parameter into Z3 as a blocked set
			block = []
			for element in model_color:
				name_param = element()
				block.append(name_param != model_color[element])
			solver.add(Or(block))

		return block_dict



def graph_operation(type, input_graph='', obj_graph=None, output_filename='', dict_list=None):
	#AGraph init
	if type == 'init':
		new_graph = pgv.AGraph(input_graph)
		new_graph.layout('circo')
		return new_graph
	#draw all the possible ways of colouring graph into images by AGraph
	elif type == 'draw':
		index = 0
		for dict_temp in dict_list:
			index += 1
			for node_name in obj_graph.nodes_iter():
				node = obj_graph.get_node(node_name)
				node.attr['color'] = color_available[dict_temp[node_name]]
			obj_graph.draw('./img/'+'%s_colored_%d.png' % (output_filename, index))

def write_summary(dict_list=None, filename=None, chromatic_number=None, k_colourable=None):
	file = open('./doc/Summary.txt','w')
	
	#write the error into a file
	if chromatic_number == None:
		file.write('The graph G (%s) is not k-colourable.\n' % repr(filename)) 
		file.write('The needed amount of colors is large than the number of node of grapth (%s).\n' % repr(filename)) 
	#write the summary into a file
	else:
		if k_colourable >= chromatic_number:
			file.write('The graph G (%s) is %d-colourable.\n' % (repr(filename), k_colourable)) 
		else:
			file.write('The graph G (%s) is not %d-colourable.\n' % (repr(filename), k_colourable)) 
		file.write('The chromatic number of the grap is %d.\n' % chromatic_number) 
		file.write('There are %d ways of colouring a graph.\n' % len(dict_list))
		file.write("    Where u\'1\' means node 1 and its value is after the \':\'.\n")
		file.write('          and the value of the node means the index of color.\n')
		file.write('          The list of color is:\n')
		file.write('              %s.\n' % color_available)
		file.write('	      0 => red.\n')
		file.write('\n')
		
		#write all the possible ways of colouring graph presented by a set
		file.write('The possible ways are below:\n')
		for dict_temp in dict_list:
			file.write(str(dict_temp)+'\n') 
	
	file.close() 


		
def main(argv):
	#load the graph by user assignment by console or the specific location which is described in the program
	if len(argv)== 1:
		filename_graph = './graph/graph_Petersen_5.dot'
		k_colourable = 3
	else:
		filename_graph = argv[1]
		k_colourable = int(argv[2])
	
	#init AGraph library to deal with graph lately
	graph = graph_operation('init', input_graph=filename_graph)

	#Z3 solver init
	solver = graph_solver('init')
	
	try:
		#use Z3 to solve the chromatic number problem
		chromatic_number = graph_solver(type='solve_chromatic_number', solver=solver, graph=graph)
		
		#use Z3 to find all the possible ways of colouring graph
		dict_result = graph_solver(type='all_possible_way', solver=solver, graph=graph, chromatic_number=chromatic_number)

		#draw all the possible ways of colouring graph into images by AGraph
		#In this program, I only provide a list of colour, if the chromatic number is larger than the size of list
		#The program does not draw the images
		if chromatic_number <= len(color_available):
			graph_operation('draw', obj_graph=graph, output_filename='project', dict_list=dict_result)
		else:
			print 'Due to the limitation of the amount of colors, the images can not be generated by the program.'
			
		#write the summary into a file
		write_summary(dict_list=dict_result, filename=filename_graph, chromatic_number=chromatic_number, k_colourable=k_colourable)
	except Exception as error:
		#write the error into a file
		write_summary(filename=filename_graph)
	
	return 0;

if __name__ == '__main__':
	sys.exit(main(sys.argv))