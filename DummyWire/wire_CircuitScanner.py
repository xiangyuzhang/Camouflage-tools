import argparse
import parser
import sys
import os
import re
import random

def reg_findall(reg, string):
    return_list = []
    temp_list = re.findall(reg,string)
    for i in temp_list:
        if  '(' in i or ')' in i:
            return_list.append(i.strip('(').strip(')'))
    return return_list


class pair:
    def __init__(self, next_gate, this_gate, this_gate_type, out_netName):

        self.next_gate = next_gate
        self.this_gate = this_gate
        self.this_gate_type = this_gate_type

        self.out_netName = out_netName

def CircuitScanner(circuitIn, Num_pair):

    reg_netName = r'(\(\w*\))'  # reg pattern used for searching netname in line
    line_netname = []  # temp, container used to store netname found through reg_netName in line
    pre_gate = []
    next_gate = []
    this_gate = ''
    line_input = ''  # input name in line
    line_output = ''  # output name in line
    connected_gate = [] # used to store the pre_gate and the next_gate
    reg_gateName = r'(gate[0-9]+)'
    reg_gateType = r'([a-z]+[0-9]+)'
    pair_list = []

    has_pre_gate = False
    has_next_gate = False
    random_sequence = []
    random_counter = 0
    random.seed(1)
    counter = 0
    i = 0

    CircuitPath = os.path.abspath(circuitIn)

    if not os.path.isfile(CircuitPath):
        print 'Invalid input circuit file!!!\n'


    # open circuit and scan line by line
    with open(circuitIn, 'r') as infile:
        inV = infile.read()
        Vlines = inV.replace('\r','').split(';\n')

    # random module
    for find_index in Vlines:
        if 'wire' in find_index:
            gate_start_index = Vlines.index(find_index) + 1
        if 'endmodule' in find_index:
            gate_end_index = Vlines.index(find_index) - 1

    while random_counter < (gate_end_index - gate_start_index + 1):
        temp = random.randint(gate_start_index, gate_end_index)
        if temp not in random_sequence:
            random_sequence.append(temp)
            random_counter += 1



    while counter <= Num_pair - 1:
        line = Vlines[random_sequence[i]]
        if line!='' and line[0]!='/' and not 'module' in line and not 'input' in line and not 'output' in line and not 'wire' in line:
    # select the input and output, the input should be the output from previous gate(pre_out), the output should be the input for next gate(next_in)
            line_netname = reg_findall(reg_netName, line)
            line_output = line_netname[-1]
#            print "Gate: ", re.findall(reg_gateName, line)
            for connected_line in Vlines:
                if connected_line!='' and connected_line[0]!='/' and not 'module' in connected_line and not 'input' in connected_line and not 'output' in connected_line and not 'wire' in connected_line:
                    if line_output in reg_findall(reg_netName, connected_line)[:-1]:     # meaning the buf is the fan in of this gate
                        if re.findall(reg_gateName, connected_line) is not 'gate' and len(re.findall(reg_gateName, connected_line)) != 0:       # means the next gate is not a buf
                            next_gate_temp = re.findall(reg_gateName, connected_line)        # make the gate next_gate
                            out_netName = reg_findall(reg_netName, line)[-1]
                            next_gate.append(next_gate_temp)
                            this_gate = re.findall(reg_gateName, line)
                            this_gate_type = re.findall(reg_gateType, line)[0]
                            if counter == Num_pair:
                                break
                            else:
                                pair_list.append(pair(next_gate,this_gate,this_gate_type, out_netName))
                                counter+=1


            i+=1
#                            print ' has next_gate', next_gate


            pre_gate = []
            next_gate =[]
            has_pre_gate = False
            has_next_gate = False
    #            print '\n'
    #  clean up all the pairs


    return pair_list



