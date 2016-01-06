#!/usr/bin/python

import os
import readline
import glob
import sys
import time
from subprocess import call

from vbench2qbf import *


def cmmd_and_path_complete(text, state):
	'''automatically complete path'''
	return (glob.glob(text+'*')+[None])[state]+'/'


class buildCamCkt:
	'''This class build a camouflaged ckt with specified number of
	camouflaged gates.'''

	def __init__(self, OracInPath, gateLs, expCmdGateNum):
		self.OracInPath = OracInPath
		self.expCmdGateNum = int(expCmdGateNum)
		self.gateLs = gateLs
		self.orgV = {}
		self.orgCNF = {} ###\
		self.dupCNF = {}     ## These 4 comprise the 
		self.mtrCNF = []     ## complete cnf file.
		self.piConCnf = [] ###/
		self.orgPisIndex = [] # integer index for PIs in orgCkt
		self.dupPisIndex = [] # integer index for PIs in dupCkt
		self.orgPosIndex = [] # integer index for POs in orgCkt
		self.dupPosIndex = [] # integer index for POs in dupCkt 
		#self.gateNumIndex = []
		self.singleCktVarNum = 0 # # of vars in the original ckt
		self.singleCktClsNum = 0
		self.orgTmpRmd = [] # the cnf lines removed from orgCkt
		self.dupTmpRmd = [] # the cnf lines removed from dupCkt
		self.tmpGateNum = 0 # the number of the gate under investigation
		self.resolvCktVarNum = 0 # # of vars in miter ckt, need to be updated once gate camed
		self.resolvCktClsNum = 0 # # of cls in miter ckt, need to be updated once gate camed
		self.orgVgateCnt = 0 # # of gates in the original verilog file
		self.VgateCntCorrect = 1 # the number of gate increasement after camouflaging one gate
		self.caModCNF = ['-2 -1 -6 0', '2 1 -6 0', '2 -1 6 0', '-2 1 6 0', '-6 -3 -7 0',\
		 '6 7 0', '3 7 0', '-2 -1 8 0', '2 -8 0', '1 -8 0', '3 9 0', '-3 -9 0', '4 10 0',\
		 '-4 -10 0', '-10 -9 -11 0', '10 11 0', '9 11 0', '11 8 12 0', '-11 -12 0', '-8 -12 0',\
		 '1 13 0', '-1 -13 0', '2 14 0', '-2 -14 0', '-14 -13 -15 0', '14 15 0', '13 15 0', \
		 '-4 -9 -16 0', '4 16 0', '9 16 0', '16 15 17 0', '-16 -17 0', '-15 -17 0', \
		 '17 12 18 0', '-17 -18 0', '-12 -18 0', '-18 -7 -5 0', '18 5 0', '7 5 0']
		self.caModV = ['\n  xor2  g0(.a(pi12), .b(pi11), .O(n5));\n  nand2 g1(.a(n5), .b(s0), .O(n6));\n  and2  g2(.a(pi12), .b(pi11), .O(n7));\n  inv1  g3(.a(s0), .O(n8));\
\n  inv1  g4(.a(s1), .O(n9));\n  nand2 g5(.a(n9), .b(n8), .O(n10));\n  nor2  g6(.a(n10), .b(n7), .O(n11));\n  inv1  g7(.a(pi11), .O(n12));\n  inv1  g8(.a(pi12), .O(n13));\n  nand2 g9(.a(n13), .b(n12), .O(n14));\n  nand2 g10(.a(s1), .b(n8), .O(n15));\n  nor2  g11(.a(n15), .b(n14), .O(n16));\n  nor2  g12(.a(n16), .b(n11), .O(n17));\n  nand2 g13(.a(n17), .b(n6), .O(c1))']
		self.orgRmdGateInts = [] #store input and output integers of removed gate in org_ckt
		self.dupRmdGateInts = [] #store input and output integers of removed gate in dup_ckt
		self.orgCnfCBits = [] #store control bits for camouflaged circuots.

	#################################################
	#################################################
	#################################################
	#################################################

	def _vBen2cnf(self):
		'''Convert Verilog to CNF. Meanwhile, get orginal var #, clause #, PI/PO index, and Verilog lines.'''

		if os.path.isfile(self.OracInPath):
			reTup = vBen2cnf(self.OracInPath)
			self.orgPisIndex = reTup[0]
			self.orgPosIndex = reTup[1]
			self.orgCNF = reTup[2]
			self.singleCktVarNum = reTup[3]
			self.singleCktClsNum = reTup[4]
			self.orgV = reTup[5]
			self.orgVgateCnt = max(self.orgV.keys())
			return (1, self.OracInPath)
		else:
			print 'Invalid file path.'
			return (0, None)

	#################################################
	#################################################
	#################################################
	#################################################

	def _preprocessing(self):	
		'''In the _preprocessing, create all needed in the following iterations.
		Including dupCNF, dupPisIndex, piConCnf, mtrCNF'''

		##### 0.1 duplicate circuit, store cnf lines in self.dupCNF: #####
		#correction = self.singleCktVarNum #to avoid repetition of integers
		for i in self.orgCNF:
			tmpClauseLs = self.orgCNF[i][:]
			newTmpClauseLs = []
			for tmpClause in tmpClauseLs:
				intIndexLs = [tmpInt for tmpInt in tmpClause.split() if tmpInt!=''][:-1]
				newTmpCls = ''
				for j in range(len(intIndexLs)):
					tmpInt = intIndexLs[j]
					if '-' in tmpInt:
						newTmpCls += '-'+str(int(tmpInt.strip('-'))+self.singleCktVarNum)+' '
					else:
						newTmpCls += str(int(tmpInt)+self.singleCktVarNum)+' '
				newTmpClauseLs.append(newTmpCls+'0\n')
			self.dupCNF[i] = newTmpClauseLs[:]

		##### 0.2 connect PIs of orgCNF and dupCNF pairwisely, store cnf lines in self.piConCnf: #####
		for i in self.orgPisIndex:
			tmpDupPI = i+self.singleCktVarNum
			self.dupPisIndex.append(tmpDupPI)
			piConsLine1 = str(i)+' -'+str(tmpDupPI)+' 0\n'
			self.piConCnf.append(piConsLine1)
			piConsLine2 = '-'+str(i)+' '+str(tmpDupPI)+' 0\n'
			self.piConCnf.append(piConsLine2)	

		##### 0.3 build miter, store cnf lines in self.mtrCNF: ######
		xorInt = self.singleCktVarNum*2
		for po in self.orgPosIndex:
			xorInt += 1
			sig1 = po
			sig2 = sig1 + self.singleCktVarNum
			self.dupPosIndex.append(sig2)                        
			poConsLine1='-'+str(sig1)+' -'+str(sig2)+' -'+str(xorInt)+' 0\n'
			self.mtrCNF.append(poConsLine1)
			poConsLine2=str(sig1)+' '+str(sig2)+' -'+str(xorInt)+' 0\n'
			self.mtrCNF.append(poConsLine2)
			poConsLine3=str(sig1)+' -'+str(sig2)+' '+str(xorInt)+' 0\n'
			self.mtrCNF.append(poConsLine3)
			poConsLine4='-'+str(sig1)+' '+str(sig2)+' '+str(xorInt)+' 0\n'
			self.mtrCNF.append(poConsLine4)
		orIndex = xorInt+1
		self.resolvCktVarNum = orIndex
		orLine = ''
		for xorInt in range(self.singleCktVarNum*2+1, orIndex):
			orLine += str(xorInt)+' '
		orLine += '-'+str(orIndex)+' 0\n'
		self.mtrCNF.append(orLine)
		orLine1 = ''
		for xorInt in range(self.singleCktVarNum*2+1, orIndex):
			orLine1 = '-'+str(xorInt)+' '+str(orIndex)+' 0\n'
			self.mtrCNF.append(orLine1)
		self.mtrCNF.append(str(orIndex)+' 0\n')

	#################################################
	#################################################
	#################################################
	#################################################

	def _testResolvability(self, gateNum, first=True):	
		'''build the complete ckt and test the gate's resolvability'''

           ##### 1. remove clauses indexed by gateNum and build the miter:
		# 1.1 remove designated clauses from original orgCNF and dupCNF:
		#print '\nNow testing gate', gateNum
		self.tmpGateNum = gateNum
		self.orgTmpRmd = self.orgCNF[self.tmpGateNum][:]
		self.dupTmpRmd = self.dupCNF[self.tmpGateNum][:]
		del self.orgCNF[self.tmpGateNum]
		del self.dupCNF[self.tmpGateNum]

		# 1.2 figure out the integers in the removed clauses:
		self.orgRmdGateInts=[tmpInt.strip('-') for tmpInt in self.orgTmpRmd[0].split() if tmpInt!=''][:-1]
		#print 'Integers in orginal gate:', self.orgRmdGateInts
		self.dupRmdGateInts=[tmpInt.strip('-') for tmpInt in self.dupTmpRmd[0].split() if tmpInt!=''][:-1]
		#print 'Integers in duplicated gate:', self.dupRmdGateInts
		"""
		# 1.3 connect orgCkt, dupCkt, PIcons and miter together:
		# The original circuit:
		compCNF = []
		for gateCnt1 in self.orgCNF:
			tmpCNFlines = self.orgCNF[gateCnt1]
			if tmpCNFlines != []:
				for tmpLn in tmpCNFlines:
					compCNF.append(tmpLn)
		compCNF.append('\n\n')
		# The duplicated circuit:
		for gateCnt2 in self.dupCNF:
			tmpCNFlines = self.dupCNF[gateCnt2]
			if tmpCNFlines != []:
				for tmpLn in tmpCNFlines:
					compCNF.append(tmpLn)
		compCNF.append('\n\n')
		# The PI constraints and miter:
		compCNF += self.piConCnf
		compCNF.append('\n\n')
		compCNF += self.mtrCNF
		compCNF.append('\n\n')

           ###### 2. test the resolvability using newly built miter:
		#2.1 build the header for cnf file:
		self.resolvCktClsNum = len(compCNF)-4+6 # +'xx0 xx1', -'separate lines'
		strPIindex = ''
		for pi in self.orgPisIndex:
			strPIindex += str(pi)+' '
		if first==True: # the head for first iteration (no ctrl bits)
			compCNF.insert(0, 'e '+strPIindex+'0\n')
			compCNF.insert(0, 'p cnf '+str(self.resolvCktVarNum)+' '+str(self.resolvCktClsNum)+'\n')
			compCNF.insert(0, 'c Evaluate the resolvability of gate '+str(gateNum)+'\n')
		else: # the head for following iterations (with ctrl bits)
			strCBindex = ''
			for cb in self.orgCnfCBits:
				strCBindex += str(cb) + ' '
			strOtherVarIndex = ''
			for varInt in range(1, self.resolvCktVarNum+1):
				if varInt in self.orgPisIndex or varInt in self.orgCnfCBits: 
					pass
				else:
					strOtherVarIndex += str(varInt)+' '
			compCNF.insert(0,'e '+strOtherVarIndex+'0\n')
			compCNF.insert(0,'a '+strCBindex+'0\n')
			compCNF.insert(0,'e '+strPIindex+'0\n')
			compCNF.insert(0,'p cnf '+str(self.resolvCktVarNum)+' '+str(self.resolvCktClsNum)+'\n')
			compCNF.insert(0,'c Evaluate the resolvability of gate '+str(gateNum)+'\n')

		# 2.2 assign '00 0' and '00 1' in conCNF and test resolvability:
		tmpConsLns = []
		# orgckt '01 0'
		tmpConsLns.append('-'+self.orgRmdGateInts[0]+' 0\n')
		tmpConsLns.append('-'+self.orgRmdGateInts[1]+' 0\n')
		tmpConsLns.append('-'+self.orgRmdGateInts[2]+' 0\n')
		# dupckt '01 1'
		tmpConsLns.append('-'+self.dupRmdGateInts[0]+' 0\n')
		tmpConsLns.append('-'+self.dupRmdGateInts[1]+' 0\n')
		tmpConsLns.append(self.dupRmdGateInts[2]+' 0\n')
		compCNF1 = compCNF+tmpConsLns
		outxt1 = ('').join(compCNF1)
		outfileName1 = 'test-gate'+str(gateNum)+'-resolvability-00.cnf'
		with open(outfileName1, 'w') as outfile:
			outfile.write(outxt1)
		qbfCmmd = 'depqbf '+outfileName1+' > testResolvabilityRes.log'
		call(qbfCmmd, shell=True)
		with open('testResolvabilityRes.log', 'r') as readfile:
			_00result = ''
			for line in readfile:
				_00result = line.strip(' \n')
				print 'Test 00:', _00result
		#call('rm '+outfileName1, shell=True)

		# 2.3 assign '01 0' and '01 1' in conCNF and test resolvability:
		tmpConsLns = []
		# orgckt '01 0'
		tmpConsLns.append('-'+self.orgRmdGateInts[0]+' 0\n')
		tmpConsLns.append(self.orgRmdGateInts[1]+' 0\n')
		tmpConsLns.append('-'+self.orgRmdGateInts[2]+' 0\n')
		# dupckt '01 1'
		tmpConsLns.append('-'+self.dupRmdGateInts[0]+' 0\n')
		tmpConsLns.append(self.dupRmdGateInts[1]+' 0\n')
		tmpConsLns.append(self.dupRmdGateInts[2]+' 0\n')
		compCNF2 = compCNF+tmpConsLns
		outxt2 = ('').join(compCNF2)
		outfileName2 = 'test-gate'+str(gateNum)+'-resolvability-01.cnf'
		with open(outfileName2, 'w') as outfile:
			outfile.write(outxt2)
		qbfCmmd = 'depqbf '+outfileName2+' > testResolvabilityRes.log'
		call(qbfCmmd, shell=True)
		with open('testResolvabilityRes.log', 'r') as readfile:
			_01result = ''
			for line in readfile:
				_01result = line.strip(' \n')
				print 'Test 01:', _01result
		#call('rm '+outfileName2, shell=True)

		# 2.4 assign '10 0' and '10 1' in conCNF and test resolvability:
		tmpConsLns = []
		# orgckt '10 0'
		tmpConsLns.append(self.orgRmdGateInts[0]+' 0\n')
		tmpConsLns.append('-'+self.orgRmdGateInts[1]+' 0\n')
		tmpConsLns.append('-'+self.orgRmdGateInts[2]+' 0\n')
		# dupckt '10 1'
		tmpConsLns.append(self.dupRmdGateInts[0]+' 0\n')
		tmpConsLns.append('-'+self.dupRmdGateInts[1]+' 0\n')
		tmpConsLns.append(self.dupRmdGateInts[2]+' 0\n')
		compCNF3 = compCNF+tmpConsLns
		outxt3 = ('').join(compCNF3)
		outfileName3 = 'test-gate'+str(gateNum)+'-resolvability-10.cnf'
		with open(outfileName3, 'w') as outfile:
			outfile.write(outxt3)
		qbfCmmd = 'depqbf '+outfileName3+' > testResolvabilityRes.log'
		call(qbfCmmd, shell=True)
		with open('testResolvabilityRes.log', 'r') as readfile:
			_10result = ''
			for line in readfile:
				_10result = line.strip(' \n')
				print 'Test 10:', _10result
		#call('rm '+outfileName3, shell=True)

		# 3. conclude if the gate is resolvable:
		resolvRes = 1
		if _00result==_01result==_10result=='UNSAT':
			resolvRes = 0
			print 'Gate',self.tmpGateNum,'is non-resolvable. Begin to camouflage it ...'
		elif _00result==_01result=='SAT' or _00result==_01result=='SAT':
			resolvRes = 1
			print 'Gate',self.tmpGateNum,'is resolvable. Jump to next gate ...'
		elif _00result=='UNSAT': 
			resolvRes = 0
			print 'Gate',self.tmpGateNum,'is partially-resolvable. Begin to camouflage it ...'
		return resolvRes
	"""			

	#################################################
	#################################################
	#################################################
	#################################################

	def _updateCNFV(self):
		'''Use camouflage-module to replace non-resolvable gates, add ctrl bits. The module 
		is stored in self.caModCNF beforehand. Both orgCNF and dupCNF need to be updated
          because these 2 ckts will be used for evaluating resolvability of other gates.
          The 2 camd-mods (in org and dup) share the same pair of control bits.'''

		#print '\nUpdating CNF and Verilog ... ...'
        ######### UPDATE CNF ###################
		orgReplace = []
		dupReplace = []
		tmpCaModIntDict1 = {}
		tmpCaModIntDict2 = {}
        # 1. map ints in the cam module to node ints in org and dup ckts
		for i in range(1, 19):
			strI = str(i)
			if i==1 or i==2: # index for pi1 and pi2 to candidate gate are not changed
				tmpCaModIntDict1[strI]=self.orgRmdGateInts[i-1]
				tmpCaModIntDict2[strI]=self.dupRmdGateInts[i-1]
			elif i==3 or i==4: # ctrl bits to candidate gate are added
				cbCorrect = self.resolvCktVarNum+i-2
				tmpCaModIntDict1[strI]=str(cbCorrect)
				tmpCaModIntDict2[strI]=str(cbCorrect)
				self.orgCnfCBits.append(cbCorrect)
			elif i == 5: # po of candidate gate is not changed
				tmpCaModIntDict1[strI]=str(self.orgRmdGateInts[-1])
				tmpCaModIntDict2[strI]=str(self.dupRmdGateInts[-1])
			else: # intermediate signals
				tmpCaModIntDict1[strI]=str(self.resolvCktVarNum+i-3)
				tmpCaModIntDict2[strI]=str(self.resolvCktVarNum+i+10)
		for tmpCnfLn in self.caModCNF:
			# 2. rewrite cnf clauses in cam module
			tmpCnfLnInt = [tmpInt for tmpInt in tmpCnfLn.split() if tmpInt!=''][:-1]
			tmpCnfCls1 = ''
			tmpCnfCls2 = ''
			for tmpCnfInt in tmpCnfLnInt:
				if '-' in tmpCnfInt:
					tmpCnfCls1 += '-'+tmpCaModIntDict1[tmpCnfInt.strip('-')]+' '
					tmpCnfCls2 += '-'+tmpCaModIntDict2[tmpCnfInt.strip('-')]+' '
				else:
					tmpCnfCls1 += tmpCaModIntDict1[tmpCnfInt]+' '
					tmpCnfCls2 += tmpCaModIntDict2[tmpCnfInt]+' '
			orgReplace.append(tmpCnfCls1+'0\n')
			dupReplace.append(tmpCnfCls2+'0\n')
		# 3. update orgCnf, dupCnf, var number and clause number
		self.orgCNF[self.tmpGateNum] = orgReplace[:]
		self.dupCNF[self.tmpGateNum] = dupReplace[:]
		self.singleCktVarNum += 15
		self.singleCktClsNum += 39-len(self.orgTmpRmd)
		self.resolvCktVarNum += 30-2 #b/c programming bits for newly camed gate are the same in org & dup
		self.resolvCktClsNum += 2*(39-len(self.orgTmpRmd))
		#print self.resolvCktVarNum
			

        #################### UPDATE VERILOG ########################################
		modifyCamModV = self.caModV[0]
		ln2rm = self.orgV[self.tmpGateNum]
		#get the inputs and outputs to the gate to camouflage:
		ln2rm = ln2rm.replace('\n', '').replace(' ','')
		buf_split=[term.replace('\\','').replace('[','').replace(']','') for term in ln2rm.split('.')]
		buf_processed = []
		for i in range(1,len(buf_split)):
					buf_processed.append(re.search(r'\((.*)\)', buf_split[i]).group().strip('( )'))
        #only 2-input gates are tested, so currently we know there are only 3 vars in line:
		inp1 = buf_processed[0]
		inp2 = buf_processed[1]
		outp = buf_processed[2]
        # 1. replace inputs and output of candidate
		modifyCamModV = modifyCamModV.replace('pi11', inp1)
		modifyCamModV = modifyCamModV.replace('pi12', inp2)
		modifyCamModV = modifyCamModV.replace('c1', outp)
        # 2. replace intermediate signals and add them to wire:
		wireStr = self.orgV[0]
		#print wireStr
		for i in range(5, 18):
			replacementSig = 'gate'+str(self.tmpGateNum)+'inter'+str(i-5)
			wireStr += ', '+replacementSig
			modifyCamModV = modifyCamModV.replace('n'+str(i), replacementSig)
		self.orgV[0] = wireStr
		# 3. replace control signals and add them as inputs
		sel1='s_'+str(len(self.orgCnfCBits)-2) #orgCnfCBits is updated when updating orgCNF
		sel2='s_'+str(len(self.orgCnfCBits)-1)
		self.orgV[-2] = self.orgV[-2]+sel1+', '+sel2+', '
		modifyCamModV = modifyCamModV.replace('s0', sel1)
		modifyCamModV = modifyCamModV.replace('s1', sel2)
    	# 4. change gate name:
		for j in range(0, 14):
			modifyCamModV = modifyCamModV.replace('g'+str(j)+'(', 'gate'+str(self.orgVgateCnt+self.VgateCntCorrect)+'(')
			self.VgateCntCorrect += 1  
		self.orgV[self.tmpGateNum] = modifyCamModV  

	#################################################
	#################################################
	#################################################
	#################################################

	def _firstIteration(self, gateNum):
		'''The first iteration with no programming bits.'''

		#1. test if the gate is resolvable:
		resolvRes = self._testResolvability(gateNum) #means this is the first iteration
		#1.2. if resolvable:
		if resolvRes == 1:
			#1.2.1 recover the cnf files:
			self.orgCNF[self.tmpGateNum] = self.orgTmpRmd[:]
			self.dupCNF[self.tmpGateNum] = self.dupTmpRmd[:]
		#1.3. if non-resolvable, camouflage it:
		elif resolvRes == 0:
			self._updateCNFV()
   
 	#################################################
	#################################################
	#################################################
	#################################################
   
	def _normalIteration(self, gateNum):
		'''The normal iteration means there is camouflaged gates inside, we need to
		constrain control bits in order to test the resovlability of new gates. This
		is done by assigning 'False' to the second parameter in _testResolvability().'''
         
        ##### 1. test whether the gate is resolvable:
		resolvRes = self._testResolvability(gateNum, False) #means NOT the first iteration
        ##### 2. update ckt structure
		#print 'This program camouflages all gates. Begin to camouflage',self.tmpGateNum
		self._updateCNFV()           
             
 	#################################################
	#################################################
	#################################################
	#################################################    
           
	def _main(self):
		'''Connect all functions in a sequence to generate a verilog file that is camouflaged.'''
           
		##### 1. Convert Verilog to CNF. Meanwhile, get orginal var #, clause #, PI/PO index, and Verilog lines.
		while True:
			readIn = self._vBen2cnf()
			if readIn[0]==1:
				inFilePath = readIn[1]
				break

		##### 2. Test resolvability of gates in corruptability list; update CNF and Verilog.
		camdGates = 0
		if self.expCmdGateNum > len(self.gateLs):
			print 'At most',len(self.gateLs),'gates can be camouflaged.'		
		for i in range( len(self.gateLs) ):
			if camdGates == self.expCmdGateNum:
				break
			corruptLn = self.gateLs[i].replace(' ', '')
			corrLnInfo = re.search(r'Gate:(.*)No.ofgate:(.*)', corruptLn)
			corrGateType = corrLnInfo.group(1).lower()
			corrGateNum = int(corrLnInfo.group(2))
			gateLine = self.orgV[corrGateNum].replace('\n','')
			orgVgateType = re.search(r'^(.*)(?=g\S+\(\.)', gateLine.replace(' ','')).group()
			if corrGateType in orgVgateType:
				if i==0:
					self._preprocessing() #duplicate cnf, constrain PIs, make a miter.
					self._testResolvability(corrGateNum) 
					self._updateCNFV()
				else:
					self._normalIteration(corrGateNum) #test gate resolvability, update orgV if necessary
				camdGates += 1
				print 'gate', self.tmpGateNum, 'is camouflaged.'
			else:
				print self.gateLs[i],'gate type is not matched jump to next gate.'

		##### 3. reassemble modified Verilog lines to a file:
		camdCkt = []
		intIndex = sorted(self.orgV.keys())
		self.orgV[-2] = '  '+self.orgV[-2].strip(', ')
		for i in intIndex:
			tmpClsInFinal = self.orgV[i]
			#print tmpClsInFinal
			if tmpClsInFinal != '':
				camdCkt.append(tmpClsInFinal)

		return (camdCkt, inFilePath)

 	#################################################
	#################################################
	#################################################
	#################################################

# dubugging:
def corrGenCam():
	readline.set_completer_delims(' \t\n;')
	readline.parse_and_bind("tab: complete")	
	readline.set_completer(cmmd_and_path_complete)	

	print "\n\t##########  Welcome to corrCam  system.  ##########"
	print "\t#This system is used to select a gate from circuit#"
	print "\t#according to the Corruptability list and camoufl-#"
	print "\t#-age it by a camflaging module                   #"
	print "\t###################################################"


	parser = argparse.ArgumentParser(usage='python buildCamCkt-corCam-cmmdline.py [-h] <orac.v> <corr_list> [num]', description='',)
	parser.add_argument('<orac.v>', help='input oracle Verilog file that defines the function of the circuit')
	parser.add_argument('<corr_list>', help='the corruptability list')
	parser.add_argument('num', help='number of gates to camouflage.')
	#parser.add_argument('<camd_out.v>', type=argparse.FileType('w'), help='output camouflaged file')
	args = parser.parse_args()
	expCmdGateNum = args.num

	OracInPath = os.path.abspath(sys.argv[1])
	#print OracInPath
	inputLsPath = os.path.abspath(sys.argv[2])
	#print inputLsPath
	if os.path.isfile(inputLsPath) and os.path.isfile(OracInPath):
		with open(inputLsPath, 'r') as inputLs:
			inLsTxt = inputLs.read()
		inLsLs = [tmpLn for tmpLn in inLsTxt.split('\n') if tmpLn != '']
		camCkt = buildCamCkt(OracInPath, inLsLs, expCmdGateNum)
		camedTup = camCkt._main()
		camedCkt = camedTup[0]
		inFilePath = camedTup[1]
		#print camedCkt
		camedCkt.append('\nendmodule')
		outfilename=re.search(r'(.*)(?=\.)',inFilePath).group()+'-corrCam'+str(expCmdGateNum)+'.v'
		#print camedCkt
		outxt = (';\n').join(camedCkt)
		with open(outfilename, 'w') as outfile:
			outfile.write(outxt)
	else:
		print '\nInvalid input file!!!'


if __name__=='__main__':
	corrGenCam()