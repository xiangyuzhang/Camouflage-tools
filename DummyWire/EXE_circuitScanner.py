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
    def __init__(self, pre_gate, next_gate, this_gate, this_gate_type, in_netName, out_netName):
        self.pre_gate = pre_gate
        self.next_gate = next_gate
        self.this_gate = this_gate
        self.this_gate_type = this_gate_type
        self.in_netName = in_netName
        self.out_netName = out_netName

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
check = -1  #  used to check whether it is a legal gate
has_pre_gate = False
has_next_gate = False
random_sequence = []
random_counter = 0
i = 0
counter = 0
parser = argparse.ArgumentParser(usage='python wire_CircuitScanner [-h]  <circuit.v> [number]]', description='This program will camouflage <circuit.v> with dummy wire',)
parser.add_argument('<circuit.v>', help='input circuit to be camouflaged')
parser.add_argument('number', action='store', type=int, help='define the maximum number of gates to be selected, trade off between time and difficulty')
args = parser.parse_args()
Num_pair = args.number
circuitIn = sys.argv[1]
CircuitPath = os.path.abspath(circuitIn)

if not os.path.isfile(CircuitPath):
    print 'Invalid input circuit file!!!\n'


# open circuit and scan line by line
with open(circuitIn, 'r') as infile:
    inV = infile.read()
    Vlines = inV.replace('\r','').split(';\n')

    # random module
    while random_counter < (len(Vlines) - 10):
        temp = random.randint(0, len(Vlines) - 10)
        if temp not in random_sequence:
            random_sequence.append(temp)
            random_counter += 1


    # find inv
    while counter <= Num_pair - 1:
        line = Vlines[random_sequence[i]]
        if line!='' and line[0]!='/' and not 'module' in line and not 'input' in line and not 'output' in line and not 'wire' in line:
    # select the input and output, the input should be the output from previous gate(pre_out), the output should be the input for next gate(next_in)
            line_netname = reg_findall(reg_netName, line)
            line_input = line_netname[:-1]
            line_output = line_netname[-1]
#            print "Gate: ", re.findall(reg_gateName, line)
            for connected_line in Vlines:
                if connected_line!='' and connected_line[0]!='/' and not 'module' in connected_line and not 'input' in connected_line and not 'output' in connected_line and not 'wire' in connected_line:
                    if reg_findall(reg_netName, connected_line)[-1] in line_input:
                        if re.findall(reg_gateName, connected_line) is not 'gate' and len(re.findall(reg_gateName, connected_line)) != 0:  # meaning the gate is the fanout of this gate
                            pre_gate_temp = re.findall(reg_gateName, connected_line)     # make this gate pre_gate
                            in_netName = reg_findall(reg_netName, line)[:-1]
                            pre_gate.append(pre_gate_temp)
                            has_pre_gate = True
#                            print ' has pre_gate', pre_gate

                if connected_line!='' and connected_line[0]!='/' and not 'module' in connected_line and not 'input' in connected_line and not 'output' in connected_line and not 'wire' in connected_line:
                    if line_output in reg_findall(reg_netName, connected_line)[:-1]:     # meaning the buf is the fan in of this gate
                        if re.findall(reg_gateName, connected_line) is not 'gate' and len(re.findall(reg_gateName, connected_line)) != 0:       # means the next gate is not a buf
                            next_gate_temp = re.findall(reg_gateName, connected_line)        # make the gate next_gate
                            out_netName = reg_findall(reg_netName, line)[-1]
                            next_gate.append(next_gate_temp)
                            has_next_gate = True
#                            print ' has next_gate', next_gate

            this_gate = re.findall(reg_gateName, line)
            this_gate_type = re.findall(reg_gateType, line)[0]

            if has_pre_gate is True and has_next_gate is True:
                pair_list.append(pair(pre_gate,next_gate,this_gate,this_gate_type, in_netName, out_netName))
                counter+=1
                i+=1
            else:
                i+=1
            pre_gate = []
            next_gate =[]
            has_pre_gate = False
            has_next_gate = False
#            print '\n'
#  clean up all the pairs
for i in pair_list:
    if len(i.pre_gate) is 0 or len(i.next_gate) is 0:
        print i.this_gate, ' is illegal\n'
#        pair_list[pair_list.index(i)] = 'NULL'

for i in pair_list:
    with open('pair_check', 'a') as infile:
        infile.write(i.this_gate)
        infile.write(' ')
        infile.write



