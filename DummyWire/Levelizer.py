__author__ = 'xiangyuzhang'
from networkx import nx

import re

def add_edge(circuit, input, output):   # add edge and also initialize type = else and level = -1
    if input not in circuit.nodes():
        circuit.add_node(input, type = "else", level = -1)
    if output not in circuit.nodes():
        circuit.add_node(output,type = "else", level = -1)
    circuit.add_edge(input,output)

def gate_scaner(gate_info_string, circuit):         # used to process gate info, connect input info and output info
    gate_info = parser(gate_info_string)
    input_list = gate_info[0:-1]  # input and output here is just string
    output = gate_info[-1]
    for input in input_list:
        add_edge(circuit, input, output)

def checker(circuit):
    print "The following is nodes info:", circuit.nodes(data = True), "\n"
    print "The following is edges info:", circuit.edges(data = True), "\n"


def parser(gate_info_string):   # parse line to find corresponding netname
    return_list = []
    temp_list = re.findall(r'(\(\w*\))', gate_info_string)
    for i in temp_list:
        if '(' in i or ')' in i:
            return_list.append(i.strip('(').strip(')'))
    return return_list

def input_initializer(input_info, circuit):     # process "input" info, and initlize type = input and make level = 1
    input_info = input_info.strip("input").strip(" ").strip(";")
    input_info = input_info.split(",")
    for input in input_info:
        if input not in circuit.nodes():
            circuit.add_node(input, type = "input", level = 1)
#   print circuit.nodes(data = True)

def all_its_precessor_is_not(node,circuit):
    level = nx.get_node_attributes(circuit,"level")
    # print node, "has predecessors: "
    for pre in circuit.predecessors(node):
        # print pre, " with level = ", level[pre]
        if level[pre] == -1:
#             print "node: ", node, " has predecessor: ", pre, " is not initialized"
            return False
    return True

def calculate_its_level(node,circuit,queue):
    # level = nx.get_node_attributes(circuit, "level")
    for pre in circuit.predecessors(node):
        if circuit.node[pre]["level"] >= circuit.node[node]["level"]:
#           queue[node][1]["level"] = level[pre]
#           circuit[node][1]["level"] = level[pre]
#            nx.set_node_attributes(circuit,"level",{node:level[pre]})
            circuit.node[node]["level"] = circuit.node[pre]["level"]
    circuit.node[node]["level"] += 1
#     print "node:", node, " has level = ", circuit.node[node]["level"]


def levelizer(circuit):
    # initialize queue
    queue = []

    # inqueue input's successor
    for node in circuit.nodes(data = True):
        if node[1]["type"] == "input":
            for i in circuit.successors(node[0]):
                if i not in queue:
                    queue.append(i)
    print queue
    # dequeue, if its precessor is empty or all its precessor is not -1, then calculate its level, inqueue otherwise

    while(len(queue) != 0):
        temp = queue.pop(0)
        print "pop", temp
        if all_its_precessor_is_not(temp, circuit) == True:
            calculate_its_level(temp, circuit,queue)
            print temp, " has successor: ", circuit.successors(temp)
            for next in circuit.successors(temp):
                if next not in queue:
                    queue.append(next)
                    print "enqueue1: ", next
        else:
            if temp not in queue:
                queue.append(temp)
                print "inqueue2: ", temp
        print "\t---------------------------------------------"

def generate_result(circuit):
    level_marker = 1
    max_level = 1
    result = []
    for node in circuit.nodes(data = True):
        if node[1]["level"] >= max_level:
            max_level = node[1]["level"]
    for i in range(1, max_level + 1):
        dict = {level_marker : []}
        for node in circuit.nodes(data = True):
            if node[1]["level"] == level_marker:
                dict[level_marker].append(node[0])
        level_marker += 1
        result.append(dict)
    return result

def find_key(value, dict):
    max_level = len(dict)
    for level in range(0, max_level - 1):
        if value in dict[level].get(level + 1):
            return level + 1

def levelization(path):
    circuit = nx.DiGraph()
    level_marker = 1  # used to mark the current level while output
    with open(path, "r") as infile:
        Vline = infile.read().split(";")

    for line in Vline:
        line = line.replace("\n", "").replace(" ", "")
        if "input" in line:
            if "RE" in line:
                line = line[:line.index("//")]
                input_initializer(line, circuit)
            else:
                input_initializer(line,circuit)
        if line != '' and '/' not in 'module' not in line and 'input' not in line and 'output' not in line and 'wire' not in line and 'endmodule' not in line:
            gate_scaner(line,circuit)

    # checker(circuit)
    levelizer(circuit)
    # checker(circuit)
    print generate_result(circuit)
    return generate_result(circuit)


