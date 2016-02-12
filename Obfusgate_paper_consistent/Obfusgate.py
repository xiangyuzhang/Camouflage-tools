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

def find_NAND_AND(Vlines, candidate_counter):
    candidate_index_list = []
    for index in range(0, len(Vlines)):
        if "and2 " in Vlines[index]  or "nand4 " in Vlines[index]:
            candidate_counter += 1
            candidate_index_list.append(index)
    return candidate_index_list
# return the index of the line if this line contain and2 or nand4, the index is corresponding to Vlines w/ only gates
# info

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

def camouflage_builder(gate, seed, programbit,):

# used to

#########################################################################################
seed = 0
programbit = 0
new_netlist = []
new_wires = []
new_CB = []
camouflage_counter = 0
candidate_index_list = []   # index of the line if this line contain and2 or nand4, the index is corresponding to Vlines w/ only gates
candidate_counter = 0   # used to count the number of and2 or nand4
camouflage_counter = 0 # used to count the number of gate that has already been camouflaged
random_sequence = []


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

# count the number of nand4 and and2, and also return the index
Vlines = gate_finder(Vlines)
candidate_index_list = find_NAND_AND(Vlines, candidate_counter)

# generate random sequence respect to the length of candidate_index_list
random_sequence = random_sequence_generator(Num_pair, len(candidate_index_list))

# build obfusgates
for i in random_sequence:
    candidate_index = candidate_index_list[i]
    gate = Vlines[candidate_index]