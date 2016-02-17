__author__ = 'xiangyu'

import re
# import os
from gatedic import*


def v2cnf(camInV, startIndex):

    gateTypeDict = {'and':1, 'or':2, 'xor':3, 'inv':4, 'buf':5, 'nand':6, 'nor':7, 'one':8, 'zero':9}
    options = {1:transAND, 2:transOR, 3:transXOR, 4:transINV, 5:transBUF, 6:transNAND, 7:transNOR, 8:transONE, 9:transZERO}

    with open(camInV, 'r') as infile:
        inV = infile.read()
        Vlines = inV.split(';\n')

    has_CONST0 = False
    has_CONST1 = False
    inputs = []
    varIndexDict = {}
    varIndex = startIndex
    cnFile = []
    posIndex = []
    gateCnt = 0
    if '/' in Vlines[0]:  # delete the head comment lines
        Vlines[0] = Vlines[0].split('/')
        Vlines[0] = Vlines[0][-1]
        module_index = Vlines[0].index('module')
        Vlines[0] = Vlines[0][module_index:]
    for line in Vlines:
        line = line.replace('\n', '')
        if 'input' in line:
            if "RE__" in line:    # here, I need to assign forbidden bits!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                line = line[:line.find('/')]
            else:
                line = line.replace('\n','')
            if "CONST1" in line: has_CONST1 = True
            if "CONST0" in line: has_CONST0 = True
            PIs=re.search(r'(?<=input )(.*)(?=$)', line).group().replace(' ','').replace(';', '').split(',')
            tmpPis = []
            for pi in PIs:
                pi = pi.replace('\\','').replace('[','').replace(']','')
                varIndexDict[pi] = varIndex
                #intVarDict[varIndex] = pi
                #pisIndex.append(varIndex)
                tmpPis.append(varIndex)
                varIndex += 1
            inputs.append(tmpPis)

        elif 'output' in line:
            POs=re.search(r'(?<=output )(.*)(?=$)', line).group().replace(' ','').split(',')
            for po in POs:
                po = po.replace('\\','').replace('[','').replace(']','')
                varIndexDict[po] = varIndex
                #intVarDict[varIndex] = po
                posIndex.append(varIndex)
                #poVars.append(po)
                varIndex += 1
        elif 'wire' in line:
            wires=re.search(r'(?<=wire )(.*)(?=$)', line).group().replace(' ','').split(',')
            for w in wires:
                varIndexDict[w] = varIndex
                #intVarDict[varIndex] = w
                varIndex += 1
        elif line!='' and line[0]!='/' and not 'module'  in line:
            #print line
            line = line.replace(' ','')
            gate = re.search(r'^(.*)(?=g\S+\(\.)', line).group().strip('1234567890')
            #convert vars to standard form:
            buf_split = [term.replace('\\','').replace('[','').replace(']','') for term in line.split('.')]
            buf_processed = []
            for i in range(1,len(buf_split)):
                buf_processed.append(re.search(r'\((.*)\)', buf_split[i]).group().strip('( )'))
            #convert standard vars to integer indexes in cnf file:
            lineOut = varIndexDict[buf_processed[-1]]
            lineIn = []
            for i in range(len(buf_processed)-1):
                lineIn.append(varIndexDict[buf_processed[i]])
            #convert logic gate to CNF format:
            caseNo = gateTypeDict[gate]
            cnfLines = options[caseNo](lineIn, lineOut)
            for line in cnfLines:
                cnFile.append(line)
            gateCnt += 1
    if has_CONST1 == True:
        cnFile.append((str(varIndexDict["CONST1"]) + " 0\n"))
    if has_CONST0 == True:
        cnFile.append("-" + str(varIndexDict["CONST0"]) + " 0\n")
    camVarNum = varIndex-1 #total number of nodes in original ckt
    camCNFile = cnFile[:]
    # print 'This is PI: ', inputs[0]  # input[0] is a list with int elements
    return camCNFile, inputs, posIndex, camVarNum
