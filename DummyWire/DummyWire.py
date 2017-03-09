__author__ = 'xiangyuzhang'
import argparse
import sys
import os
import re
import random
from wire_CircuitScanner import CircuitScanner
from Levelizer import levelization, find_key

def abcmap_MUX_OBF_netlist(pi1, pi2, pi3, pi4, output, seed, programbit):
    D_bit1 = 'D_' + str(programbit)
    D_bit2 = 'D_' + str(programbit + 1)
    D_bit1_not = 'D_' + str(programbit) + "_NOT"
    D_bit2_not = 'D_' + str(programbit + 1) + "_NOT"
    new_netlist = []
    new_netlist_str= ''
    wire = []
    CB = []
    result = []
    new_netlist.append("inv1 gate( .a(" + D_bit1 + "),.O(" +  D_bit1_not + ") );\n")
    new_netlist.append("inv1 gate( .a(" + D_bit2 + "),.O(" +  D_bit2_not + ") );\n")
    new_netlist.append("and2 gate( .a(" + pi1 + "), .b(" + D_bit1_not + "), .O(" + "ED_" + str(seed) + ") );\n")
    new_netlist.append("and2 gate( .a(" + pi2 + "), .b(" + D_bit1_not + "), .O(" + "ED_" + str(seed + 1) + ") );\n")
    new_netlist.append("and2 gate( .a(" + pi3 + "), .b(" + D_bit1 + "), .O(" + "ED_" + str(seed + 2) + ") );\n")
    new_netlist.append("and2 gate( .a(" + pi4 + "), .b(" + D_bit1 + "), .O(" + "ED_" + str(seed + 3) + ") );\n")
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
# return [new_netlist, wire, CB, output]
def find_backup_Mux_in_level(levelization_result, original_net):
    result = []

    max_level = len(levelization_result)
    level = find_key(original_net,levelization_result)   # level is the level for selected pair
    index = level - 1 # levelization_result is a list with all element to be dict, so the index means the index of the corresponding level
    for i in range(0, index):
        result.extend(levelization_result[i].get(i + 1))
    return result


def find_backup_Mux_in(circuitIn):
    result = []
    with open(circuitIn, 'r') as infile:
        inV = infile.read()
        Vlines = inV.replace('\r','').split(';\n')

    for line in Vlines:
        line = line.replace('\n', '')

        if 'input' in line:
            if '//RE_' in line:
                line = line[:line.find('//RE_')]
            PIs=re.search(r'(?<=input )(.*)(?=$)', line).group().replace(' ','').split(',')
            for pi in PIs:
                pi = pi.replace('\\','').replace('[','').replace(']','')
                result.append(pi)

#        if 'wire' in line:
#            PIs=re.search(r'(?<=wire )(.*)(?=$)', line).group().replace(' ','').split(',')
#            for pi in PIs:
#                pi = pi.replace('\\','').replace('[','').replace(']','')
#                result.append(pi)

    return result
#   return list result['N12','N23','N1234','N6723']


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


def camouflage_builder(target_pair, back_up_MUX_in, seed, programbit, output):
    this_gate_in_net = []
    this_gate_out_net = []
    wire = []   # contain extra wire
    random_sequence = []
    CB = []     # contain extra CB
    netlist = []

    this_gate_out_net = target_pair.out_netName
    random_sequence = random_sequence_generator(4, len(back_up_MUX_in))
    result = abcmap_MUX_OBF_netlist(back_up_MUX_in[random_sequence[0]], back_up_MUX_in[random_sequence[1]], back_up_MUX_in[random_sequence[2]], this_gate_out_net,output,seed,programbit)


    return result

# print abcmap_MUX_OBF_netlist("N1", "N2", "N3", "N4", "Output", 0, 1)

pair_list = []  # used to store the random selected gate pair
back_up_MUX_in = []
seed = 0
programbit = 0
MUX_O_index = 0
camouflage_gates = []    # used to contain MUX
new_CB = [] # used to contain the new CB for MUX
new_wires = []  # used to contain the new wire necessary in MUX
new_netlist = []
replaced_gate = []
reg_gateName = r'(gate[0-9]+)'
input_base = "\ninput "
out_circuit_name = ""
outxt = ''
# parser
parser = argparse.ArgumentParser(usage='python DummyWire.py [-h]  <circuit.v> [number]]', description='This program will camouflage <circuit.v> with dummy wire',)
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
# pair_list generator
pair_list= CircuitScanner(CircuitPath, Num_pair)
# get back up MUX_in
####### back_up_MUX_in = find_backup_Mux_in(circuitIn)
# MUX builder
level_result = levelization(circuitIn)
for target_pair in pair_list:
    back_up_MUX_in = find_backup_Mux_in_level(level_result,target_pair.out_netName)
    camouflage_gates = camouflage_builder(target_pair, back_up_MUX_in, seed, programbit, 'MUX_O_' + str(MUX_O_index))
    new_netlist.append(camouflage_gates[0])         # result 1: MUX new_netlist
    new_wires.append(camouflage_gates[1])       # result 2: MUX new_wire
    new_CB.append(camouflage_gates[2])      # result 3: MUX new_CB


    for line in Vlines:
        line = line.replace('\n', '')
        if re.findall(reg_gateName, line) in target_pair.next_gate:
            Out_name = "(" + target_pair.out_netName + ")"
            Replaced_name = '(MUX_O_' + str(MUX_O_index) + ")"
            Vlines[Vlines.index(line)] = Vlines[Vlines.index(line)].replace(Out_name,Replaced_name)
            line = line.replace(Out_name, Replaced_name)
            replaced_gate.append(line)      # result 4: MUX replaced_gate
    seed += 10
    programbit += 2
    MUX_O_index += 1

print ''

# content builder
    # build input
for input in new_CB:
    for i in input:
        input_base += i + ','
input_base = input_base[:-1]
input_base += " ;//RE__ALLOW(00,01,10,11)"

for find in Vlines:
    if 'input' in find:
        Vlines.insert(Vlines.index(find) + 1, input_base)
        break
for i in range(0,len(Vlines)):
    if 'wire' in Vlines[i]:
        for wire in new_wires:
            for j in wire:
                Vlines[i] = Vlines[i] + ',' + j
        break
print ''
for MUX in new_netlist:
    Vlines.insert(-1, MUX)
for line in Vlines:
    if 'input' in line:
        if 'RE__' not in line:
            Vlines[Vlines.index(line)] = Vlines[Vlines.index(line)] + ' ;//RE__PI'
            break
# circuit generator
out_circuit_name = circuitIn.strip('.v') + '-WIRE-' + str(Num_pair) + '.v'
outxt = (';\n').join(Vlines)
with open(out_circuit_name, 'w') as outfile:
    outfile.write(outxt)