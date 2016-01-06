__author__ = 'xiangyuzhang'
import os
import sys
import argparse
import random
import re
def abcmap_MUX_OBF_netlist(pi1, output, seed, programbit):
    D_bit1 = 'D_' + str(programbit)
    D_bit2 = 'D_' + str(programbit + 1)
    D_bit1_not = 'D_' + str(programbit) + "_NOT"
    D_bit2_not = 'D_' + str(programbit + 1) + "_NOT"
    pi1_not = str(pi1) + "_NOT"
    new_netlist = []
    wire = []
    CB = []
    result = []
    new_netlist.append("inv1 gate( .a(" + D_bit1 + "), .O(" +  D_bit1_not + ") );\n")
    new_netlist.append("inv1 gate( .a(" + D_bit2 + "), .O(" +  D_bit2_not + ") );\n")
    new_netlist.append("inv1 gate( .a(" + pi1 + "), .O(" +  pi1_not + ") );\n")
    new_netlist.append("and2 gate( .a(" + pi1 + "), .b(" + D_bit1_not + "), .O(" + "ED_" + str(seed) + ") );\n")
    new_netlist.append("and2 gate( .a(" + pi1_not + "), .b(" + D_bit1_not + "), .O(" + "ED_" + str(seed + 1) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "CONST1" + "), .b(" + D_bit1 + "), .O(" + "ED_" + str(seed + 2) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "CONST0" + "), .b(" + D_bit1 + "), .O(" + "ED_" + str(seed + 3) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "ED_" + str(seed) + "), .b(" + D_bit2_not + "), .O(" + "ED_" + str(seed + 9) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "ED_" + str(seed + 1) + "), .b(" + D_bit2 + "), .O(" + "ED_" + str(seed + 7) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "ED_" + str(seed + 2) + "), .b(" + D_bit2_not + "), .O(" + "ED_" + str(seed + 5) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "ED_" + str(seed + 3) + "), .b(" + D_bit2 + "), .O(" + "ED_" + str(seed + 4) + ") );\n")
    new_netlist.append("or2  gate( .a(" +  "ED_" + str(seed + 4) + "), .b(" + "ED_" + str(seed + 5) +"), .O(" + "ED_" + str(seed + 6) +") );\n")
    new_netlist.append("or2  gate( .a(" +  "ED_" + str(seed + 6) + "), .b(" + "ED_" + str(seed + 7) +"), .O(" + "ED_" + str(seed + 8) +") );\n")
    new_netlist.append("or2  gate( .a(" +  "ED_" + str(seed + 9) + "), .b(" + "ED_" + str(seed + 8) +"), .O(" + str(output) +") )")
    new_netlist_str = ('').join(new_netlist)
    wire.append(D_bit1_not)
    wire.append(D_bit2_not)
    wire.append(pi1_not)
    wire.append(output)
    for i in range(0,10):
        wire.append("ED_" + str(seed + i))
    CB.append(D_bit1)
    CB.append(D_bit2)
    result.append(new_netlist_str)
    result.append(wire)
    result.append(CB)
    result.append(output)
    return result
# seed is the initial index for wires
# program bit is the initial index for CBs
# return [new_netlist, wire, CB, output]  output is also included in wire

def gate_finder(Vlines):
    for index in range(0,len(Vlines)):
        if "gate" in Vlines[index]:
            start = index
            break
    Vlines = Vlines[start:-1]
    return Vlines
# return PURE gate list, will be selected from random sequence

def netname_finder(gate):
    return_list = []
    reg = r'(\(\w*\))'
    temp_list = re.findall(reg,gate)
    for i in temp_list:
        if  '(' in i or ')' in i:
            return_list.append(i.strip('(').strip(')'))
    return return_list
# return ['input1', 'input2', 'input3', 'output']

def random_sequence_generator(limit_num, select_range):

    random_counter = 1
    random.random()
    random.seed(1)
    random_sequence = []
    while random_counter < limit_num:
        temp = random.randint(0, select_range-1)
        if temp not in random_sequence:
            random_sequence.append(temp)
            random_counter += 1

    return random_sequence
# limit_num is the length of random_sequence
# select_range is the range of int can be selected
# return list; random_sequence[1,23,55, ...]

def camouflage_builder(index, gate_list, seed, programbit):
    acceptable_list = [ 'nand','and', 'or', 'nor', 'inv']
    gate = gate_list[index]
    gate_info = re_find_gateType(gate)
    gate_type = gate_info[0]
    input_number = gate_info[1]
    if gate_type[0] not in acceptable_list:
        return False
    else:
        netname_list = netname_finder(gate)
        random.random()
        random.seed(1)
        index_of_input = random.randint(0, int(input_number[0]) -1) # index_of_input is 0, 1, 2 (left shifted)
        target_gate = netname_list[index_of_input]
        return abcmap_MUX_OBF_netlist(target_gate, target_gate + "_OBF", seed, programbit)
# return [new_netlist, wire, CB, output]

def re_find_gateType(gate):
    result = []
    temp = re.findall(r'([a-z]+[0-9])', gate)[0]
    gate_type = re.findall(r'([a-z]+)', temp)
    input_number = re.findall(r'([0-9])', temp)
    result.append(gate_type)
    result.append(input_number)
    return result
    # result = {"gate_type":gate_type, "input_number":input_number}

def input_modifier(input):
    input_info = input.replace("\n","").replace("input","")
    input_info = "\ninput CONST1,CONST0," + input_info
    return  input_info
# used to modify current PI to add CONST1 and CONST0

#########################################################################################
seed = 0
programbit = 0
new_netlist = []
new_wires = []
new_CB = []
camouflage_counter = 0 # used to count the number of gate that has already been camouflaged

parser = argparse.ArgumentParser(usage='python Obfusgate.py [-h]  <circuit.v> [number]]', description='This program will camouflage <circuit.v> with Obfusgate',)
parser.add_argument('<circuit.v>', help='input circuit to be camouflaged')
parser.add_argument('number', action='store', type=int, help='define the maximum number of gates to be selected, trade off between time and difficulty')
args = parser.parse_args()
Num_pair = args.number
circuitIn = sys.argv[1]
CircuitPath = os.path.abspath(circuitIn)

with open(circuitIn, 'r') as infile:
    inV = infile.read()
    Vlines = inV.replace('\r','').split(';\n')

if not os.path.isfile(CircuitPath):
    print 'Invalid input circuit file!!!\n'

# find gate_list
gate_list = gate_finder(Vlines)
candidate_index_list = random_sequence_generator(len(gate_list) + 1, len(gate_list)) # not left shifted

# prepare new wires, CBs, and netlists, and also modify Vlies
for candidate_index in candidate_index_list:
    if camouflage_counter < Num_pair:
        info = camouflage_builder(candidate_index - 1, gate_list, seed, programbit)
        if info is False:
            continue
        else:
            new_netlist.append(info[0])
            new_wires.extend(info[1])
            new_CB.extend(info[2])
            # repalce original netname with current

            for index in range(0, len(Vlines)):
                if gate_list[candidate_index -1 ] in Vlines[index]:
                    Vlines[index] = Vlines[index].replace(info[3].strip("_OBF"), info[3])
                    break
            seed+=10
            programbit+=2
            camouflage_counter += 1
    else:
        break
# modify wire
new_wires_string = (",").join(new_wires)
for index in range(0, len(Vlines)):
    if "wire" in Vlines[index]:
        Vlines[index] = Vlines[index] + "," + new_wires_string
        break
# add new input: CB
new_CB_string = (",").join(new_CB)
for index in range(0, len(Vlines)):
    if "input" in Vlines[index]:
        Vlines[index] = input_modifier(Vlines[index])
        Vlines[index] += " //RE__PI"
        Vlines.insert(index + 1, "\ninput " + new_CB_string + " //RE__ALLOW(00,01,10,11)")
        break
# add new netlist
Vlines = Vlines[0:-1]
for element in new_netlist:
    Vlines.append(element)

# append "\nendmodule\n"
Vlines.append("\nendmodule\n")


output = circuitIn.strip(".v") + "-OBF-" + str(Num_pair) + ".v"
Final_result = (";\n").join(Vlines)
with open(output,'w') as outfile:
    outfile.write(Final_result)
