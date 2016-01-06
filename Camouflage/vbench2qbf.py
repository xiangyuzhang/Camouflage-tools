#!/usr/bin/python

import re
import time
import argparse
import sys




def gateType( line ):
	'''This function returns gateType together with inputs and output'''

	'''
	logicAND = False
	logicOR = False
	logicINV = False
	logicXOR =False
	eqn = re.search(r'(?<=assign )(.*)(?=;)', line).group().replace(' ','')
	if '|' in eqn: logicOR =True
	if '&' in eqn: logicAND =True
	if '~' in eqn: logicINV = True
	if '^' in eqn: logicXOR = True
	if logicAND==True and logicOR==False and logicINV==False and logicXOR==False:
		gateType = 'AND'
	elif logicAND==False and logicOR==True and logicINV==False and logicXOR==False:
		gateType = 'OR'
	elif logicAND==False and logicOR==False and logicINV==True and logicXOR==False:
		gateType = 'INV'
	elif logicAND==False and logicOR==False and logicINV==False and logicXOR==True:
		gateType = 'XOR'


	return gateType
	'''
	
def transINV( lineIn, lineOut ):
	inV = str(lineIn[0])
	outV = str(lineOut)
	cnfLines = []
	cnfLines.append(inV+' '+outV+' 0\n')
	cnfLines.append('-'+inV+' -'+outV+' 0\n')
	return cnfLines
	
def transAND( lineIn, lineOut ):
	cnfLines = []
	outV = str(lineOut)
	firstLine = ''
	for inV in lineIn:
		inVstr = str(inV)
		firstLine += '-'+inVstr+' '
		cnfLines.append(inVstr+' -'+outV+' 0\n')
	firstLine += outV+' 0\n'
	cnfLines.insert(0, firstLine)
	return cnfLines

def transOR( lineIn, lineOut ):
	cnfLines = []
	outV = str(lineOut)
	firstLine = ''
	for inV in lineIn:
		inVstr = str(inV)
		firstLine += inVstr+' '
		cnfLines.append('-'+inVstr+' '+outV+' 0\n')
	firstLine += '-'+outV+' 0\n'
	cnfLines.insert(0, firstLine)
	return cnfLines

def transXOR( lineIn, lineOut ):
	inV1 = str(lineIn[0])
	inV2 = str(lineIn[1])
	outV = str(lineOut)
	cnfLines = []
	cnfLines.append('-'+inV1+' -'+inV2+' -'+outV+' 0\n')
	cnfLines.append(inV1+' '+inV2+' -'+outV+' 0\n')
	cnfLines.append(inV1+' -'+inV2+' '+outV+' 0\n')
	cnfLines.append('-'+inV1+' '+inV2+' '+outV+' 0\n')
	return cnfLines

def transNOR( lineIn, lineOut ):
	cnfLines = []
	outV = str(lineOut)
	firstLine = ''
	for inV in lineIn:
		inVstr = str(inV)
		firstLine += inVstr+' '
		cnfLines.append('-'+inVstr+' -'+outV+' 0\n')
	firstLine += outV+' 0\n'
	cnfLines.insert(0, firstLine)
	return cnfLines

def transNAND( lineIn, lineOut ):
	cnfLines = []
	outV = str(lineOut)
	firstLine = ''
	for inV in lineIn:
		inVstr = str(inV)
		firstLine += '-'+inVstr+' '
		cnfLines.append(inVstr+' '+outV+' 0\n')
	firstLine += '-'+outV+' 0\n'
	cnfLines.insert(0, firstLine)
	return cnfLines

def transBUF( lineIn, lineOut ):
	inV = str(lineIn[0])
	outV = str(lineOut)
	cnfLines = []
	cnfLines.append(inV+' -'+outV+' 0\n')
	cnfLines.append('-'+inV+' '+outV+' 0\n')
	return cnfLines

def transZERO( lineIn, lineOut ):
	cnfLines = []
	cnfLines.append('-'+str(lineOut)+' 0\n')
	return cnfLines

def transONE( lineIn, lineOut ):
	cnfLines = []
	cnfLines.append(str(lineOut)+' 0\n')
	return cnfLines


#################################################
#################################################
#################################################
#################################################


def abcMapV2cnf(inputV, nonMiter=False):
	'''
	This is a function that converts verilog file strashed by ABC to CNF format that\
	can be accepted by SAT solver.
	'''

	cnfLines = []
	gateTypeDict = {'and':1, 'or':2, 'xor':3, 'inv':4, 'buf':5, 'nand':6, 'nor':7, 'one':8, 'zero':9}
	options = {1:transAND, 2:transOR, 3:transXOR, 4:transINV, 5:transBUF, 6:transNAND, 7:transNOR, 8:transONE, 9:transZERO}

	orgV = {}
	with open(inputV) as infile:
		inV = infile.read()
		Vlines = inV.split(';\n')
	#print Vlines
	orgV[-4] = 'module'+Vlines[0].split('module')[1]
	clauseNum = 0
	gateNumIndex = {}
	varIndexDict = {}
	intVarDict = {}
	varIndex = 1
	#cnFile = []
	pisIndex = [] #store integer indexes of pis to return
	#piVars = []
	posIndex = [] #store integer indexes of pos to return
	#poVars = []
	gateCnt = 1

	for line in Vlines:
		# store all variables (inputs, outputs and wires):
		if ('input' in line) and (not '//' in line):
			orgV[-3] = line.strip(';\n')
			line = line.replace('\n', '')
			PIs=re.search(r'(?<=input)(.*)(?=$)', line).group().replace(' ','').split(',')
			for pi in PIs:
				pi=pi.replace('\\','').replace('[','').replace(']','')
				varIndexDict[pi] = varIndex
				intVarDict[varIndex] = pi
				pisIndex.append(varIndex)
				varIndex += 1
		elif ('output' in line) and (not '//' in line):
			orgV[-1] = line.strip(';\n')
			line = line.replace('\n', '')
			POs=re.search(r'(?<=output)(.*)(?=$)', line).group().replace(' ','').split(',')
			for po in POs:
				po=po.replace('\\','').replace('[','').replace(']','')
				varIndexDict[po] = varIndex
				intVarDict[varIndex] = po
				posIndex.append(varIndex)
				varIndex += 1
		elif 'wire' in line:
			orgV[0] = line.strip(';\n')
			line = line.replace('\n', '')
			wires=re.search(r'(?<=wire)(.*)(?=$)', line).group().replace(' ','').split(',')
			for w in wires:
				varIndexDict[w] = varIndex
				intVarDict[varIndex] = w
				varIndex += 1		
		# translate Verilog lines to CNF clauses:	
		elif line != '' and not 'module' in line:		
			if line[0]!='/':
				orgV[gateCnt] = line
				line = line.replace('\n', '')
				line = line.replace(' ','')
				#print line
				#gateInfo = [] #[start line #, line # for this gate]
				gate = re.search(r'^(.*)(?=g\S+\(\.)', line).group().strip('1234567890')
				buf_split=[term.replace('\\','').replace('[','').replace(']','') for term in line.split('.')]
				buf_processed = []
				for i in range(1,len(buf_split)):
					buf_processed.append(re.search(r'\((.*)\)', buf_split[i]).group().strip('( )'))
				lineOut = varIndexDict[buf_processed[-1]]
				lineIn = []
				for i in range(len(buf_processed)-1):
					lineIn.append(varIndexDict[buf_processed[i]])
				caseNo = gateTypeDict[gate]
				cnfLines = options[caseNo](lineIn, lineOut)
				clauseNum += len(cnfLines)
				gateNumIndex[gateCnt] = cnfLines[:]
				gateCnt += 1
	orgV[-2] = 'input '  
	if nonMiter==False: #means this is a 1-output miter problem		
		cnFile.append(str(varIndexDict[POs[0]])+' 0\n')
	
	varNum = varIndex-1
	'''
	print '\n', gateCnt-1, 'gates converted.'
	print "pisIndex:", pisIndex
	print "posIndex:", posIndex
	print cnFile
	print gateNumIndex
	'''
	#print intVarDict
	#print orgV
	return (pisIndex, posIndex, gateNumIndex, varNum, clauseNum, orgV)
	

#################################################
#################################################
#################################################
#################################################


def bench2cnf(inputB, nonMiter=False):
	'''
	This is a function that converts verilog file strashed by ABC to CNF format that\
	can be accepted by SAT solver.
	'''

	cnfLines = []
	gateTypeDict = {'AND':1, 'OR':2, 'XOR':3, 'NOT':4, 'BUFF':5, 'NAND':6, 'NOR':7, 'ONE':8, 'ZERO':9}
	options = {1:transAND, 2:transOR, 3:transXOR, 4:transINV, 5:transBUF, 6:transNAND, 7:transNOR, 8:transONE, 9:transZERO}

	with open(inputB) as infile:
		inB = infile.read()
		Vlines = inB.split('\n')

	clauseNum = 0
	varIndex = 1
	gateNumIndex = {}
	varIndexDict = {}
	intVarDict = {}
	#var2int = []
	#cnFile = []
	pisIndex = [] #store integer indexes of pis to return
	posIndex = [] #store integer indexes of pos to return
	gateCnt = 1
	for line in Vlines:
		line = line.replace('\n', '')
		if 'INPUT' in line:
			PIs=re.search(r'(?<=INPUT\()(.*)(?=\)$)', line).group().replace(' ','').split(',')
			for pi in PIs:
				pi=pi.replace('\\','').replace('[','').replace(']','')
				varIndexDict[pi] = varIndex # pi in bench may be a number in char format
				intVarDict[varIndex] = pi
				pisIndex.append(varIndex)
				varIndex += 1
		elif 'OUTPUT' in line:
			POs=re.search(r'(?<=OUTPUT\()(.*)(?=\)$)', line).group().replace(' ','').split(',')
			for po in POs:
				po=po.replace('\\','').replace('[','').replace(']','')
				varIndexDict[po] = varIndex
				intVarDict[varIndex] = po
				posIndex.append(varIndex)
				varIndex += 1				
		elif line != '':
			line = line.replace(' ','')
			if line[0]!='#':
				gate = re.search(r'(?<=\=)(.*)(?=\()', line).group()
				caseNo = gateTypeDict[gate]
				interOut=re.search(r'^(.*)(?=\=)', line).group()
				if not interOut in varIndexDict:
					varIndexDict[interOut] = varIndex
					intVarDict[varIndex] = interOut
					varIndex += 1
				tmpLineIn=re.search(r'(?<=\()(.*)(?=\))', line).group().split(',')
				lineIn = []
				for i in range(len(tmpLineIn)):
					lineIn.append(varIndexDict[tmpLineIn[i]])
				cnfLines = options[caseNo](lineIn, varIndexDict[interOut])
				gateNumIndex[gateCnt] = cnfLines[:]
				clauseNum += len(cnfLines)
				gateCnt += 1
	if nonMiter==False: #means this is a 1-output miter problem		
		cnFile.append(str(varIndexDict[POs[0]])+' 0\n')
	#print posIndex
	varNum = varIndex-1

	'''
	print gateCnt-1, 'gates converted.'
	print 'pisIndex:',pisIndex
	print 'posIndex:',posIndex
	print 'gateNumIndex:',gateNumIndex
	print 'varNum:',varNum
	print 'clauseNum:',clauseNum
	print varIndexDict
	'''
	return (pisIndex, posIndex, gateNumIndex, varNum, clauseNum)



def vBen2cnf(inFile):
	parseFilePath = inFile.split('/')
	fileType = re.search(r'(?<=\.)(.*)$', parseFilePath[-1]).group()
	if fileType=='v':
		reTup = abcMapV2cnf(inFile, True)
	elif fileType=='bench':
		reTup = bench2cnf(inFile, True)
	else:
		print "Unrecognized file type:", fileType
		print "Not one of verilog and bench."	
		return 0
	return reTup



'''
if __name__ == "__main__":
	parser = argparse.ArgumentParser(usage='python vbench2qbf.py [-h] <input_file> <output_file>', description='',)
	parser.add_argument('<input_file>', help='plain verilog file or bench file')
	parser.add_argument('<output_file>', help='cnf file')
	inFile = sys.argv[1]
	outCNF = sys.argv[2]
	reTup = vBen2cnf(inFile)
	gateNumIndex = reTup[2]
	completeCnf = []
	for gateCnt in gateNumIndex:
		tmpCNFlines = gateNumIndex[gateCnt]
		if tmpCNFlines != [] and tmpCNFlines != None:
			for tmpLn in tmpCNFlines:
				completeCnf.append(tmpLn)	
	outxt = ('').join(completeCnf)
	with open(outCNF, 'w') as outfile:
		outfile.write(outxt)
'''




			

