__author__ = 'xiangyuzhang'

import re
import argparse
import os
import sys
from random import*
parser = argparse.ArgumentParser(usage='python XOR_Cam.py [-h] <cam.v> ]', description='This program will use cam.v to generate a evener harder circuit.',)
parser.add_argument('cam.v>', help='input cam circuit that will be made harder')
args = parser.parse_args()
camIn = sys.argv[1]
camInPath = os.path.abspath(camIn)

if not os.path.isfile(camInPath):
    print 'Invalid cam circuit file!!!!\n'

Camfile = camInPath
varIndexDict = {}
varIndex = 1
posIndex = []  # store integer indexes of pos to return
X_index = 1  # used to designate the index for XOR input
reg = r'\((N[0-9]+)\)'
port_in_1 = ""
port_in_2 = ""
port_out = ""
XOR_model = "xor2 gate( .a(in_1), .b(in_2), .O(out) );"
content = []  # contain the refreshed codes
inputs = []
new_inputs = []  # used to contain the replaced inputs
outputs = []
new_outputs = []  # used to contain the replaced outputs
new_gates = []  # used to contain the new xor gated
X_inputs = []  # used to store the new input
with open(Camfile, 'r') as infile:
    inV = infile.read()
    Vlines = inV.split(';\n')

for line in Vlines:
    line = line.replace('\n', '')
    if 'input' in line and '//' not in line:
        PIs = re.search(r'(?<=input )(.*)(?=$)', line).group().replace(' ', '').split(',')
        tmpPis = []
        for pi in PIs:
            pi = pi.replace('\\', '').replace('[', '').replace(']', '')
            tmpPis.append(pi)
        inputs.append(tmpPis)

    elif 'output' in line and '//' not in line:
        POs = re.search(r'(?<=output )(.*)(?=$)', line).group().replace(' ', '').split(',')
        tmpPos = []
        for po in POs:
            po = po.replace('\\', '').replace('[', '').replace(']', '')
            outputs.append(po)

# change the gate verilog file only
with open(Camfile, 'r') as infile:
    inV = infile.read()
    Vlines = inV.split(';\n')

for line in Vlines:
    line = line.replace('\n', '')
    if line != '' and line[0] != '/' and not 'module' in line and not 'output' in line and not 'input' in line and not 'wire' in line:
        for out in outputs:
            if out in re.findall(reg, line):
                port_in_1 = "X_" + str(X_index)
                port_in_2 = out
                port_out = out + "_new"
                X_index += 1
                X_inputs.append(port_in_1)
                if port_out not in new_outputs:
                    new_outputs.append(port_out)
                new_gates.append( XOR_model.replace("in_1", port_in_1).replace("in_2", port_in_2).replace("out", port_out))
                outputs.remove(out)
        for ins in inputs[0]:
            if ins in re.findall(reg, line):
                port_in_1 = "X_" + str(X_index)
                port_in_2 = ins + "_new"
                port_out = ins
                X_index += 1
                X_inputs.append(port_in_1)
                if port_in_2 not in new_inputs:
                    new_inputs.append(port_in_2)
                new_gates.append( XOR_model.replace("in_1", port_in_1).replace("in_2", port_in_2).replace("out", port_out))
                inputs[0].remove(ins)


# -> replace the output/input name in  zone, add X_index
with open(Camfile, 'r') as infile:
    inV = infile.read().replace('endmodule', '')
    Vlines = inV.split(';\n')
# Vlines[4] += Vlines[4] + '\n'
for x in inputs[0]:
    Vlines[1] = Vlines[1].replace(str(x)+',', str(x) + '_new,')
    Vlines[4] += ',' + x
Vlines[1] = Vlines[1].strip(';') + '_new'
for y in outputs:
    Vlines[3] = Vlines[3].replace(str(y) + ',', str(y) + "_new,")
    Vlines[4] += ',' + y
Vlines[3] = Vlines[3].strip(';') + '_new'
for z in X_inputs:
    Vlines[2] = Vlines[2] + "," + z

for i in range(0, len(Vlines)):
    Vlines[i] += ';\n'

Vlines[-1] = ''
for gates in new_gates:
    Vlines.append('\n' + gates)
Vlines.append('\n' + 'endmodule')

outfile_name = camIn.strip('.v') + '-XOR.v'

for new_lines in Vlines:
    with open(outfile_name, 'a') as outfile:
        outfile.write(new_lines)


