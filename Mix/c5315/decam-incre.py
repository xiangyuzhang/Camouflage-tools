#!/usr/bin/python

'''This version is independent of ABC and still relys on external\
 SAT sovler Minidat, but sloves the problem incrementally.'''

import os
import readline
import glob
import sys
import time
from subprocess import call, Popen, PIPE, STDOUT
import argparse

from genMtrs import *
#from abcProc import *
from grabNodes import *
#from abcMapV2CNF import *


def cmmd_and_path_complete(text, state):
    '''automatically complete path'''
    return (glob.glob(text+'*')+[None])[state]+'/'

        
#################################################
#################################################
#################################################
#################################################


class DissectCkt:
    '''This class is used to dissect circuit and find the correct internal components.'''

    def __init__(self):

        # self.CamInPath = CamIn
        # self.OracInPath = OracIn
        # self.ObfGateNum = obfGateNum

        self.OracPIls = [] #PI vectors to Oracle circuit
        self.OracPOls = [] #PO vectors to Oracle circuit    

        self.PItemp = [] #temp found PI vector
        self.POtemp = [] #temp corresponding PO vector
        self.CBPtemp = [[], []] #temp Control Bit Pair

        self.OracPIndex = [] #int indexes for PI bits of Oracle ckt
        self.OracPOindex = [] #int indexes for PO bits of Oracle ckt

        self.pbitsNum = 0 #num of p-bits for an camouflaged ckt
        self.PInum2grab = 0 #num of PI bits of an camouflaged ckt
        self.camPIndex = [] #integer indexes for PI bits of cam ckt
        self.camCBindex = [] #integer indexes for p-bits of cam ckt
        self.camPOindex = [] #integer indexes for PO bits of cam ckt

        self.SATtime = 0
        self.ABCtime = 0

        self.OraCNFile = [] #stores basic Oracle cnf lines
        #there are commnet lines in self.OraCNFile
        self.camCNFile = [] #stores basic camouflaged circuit
        #there is no commnet line in self.camCNFile
        self.baseCnfMtrLs = [] #stores basic miter cnf w/o assignments
        #there are commnet lines in self.baseCnfMtrLs
        self.camVarNum = 0 #total # of vars in orignal cam ckt

        self.newDupCkt = []
        #readline.set_completer_delims(' \t\n;')
        #readline.parse_and_bind("tab: complete")   
        #readline.set_completer(cmmd_and_path_complete)
        self.oracPONodes2grab = []
        self.nodes2grab = []
        self.cktTotVarNum = 0
        self.OracVarNum = 0
        self.baseMtrVarNum = 0
        self.miterOutIndex = 0

    #################################################
    #################################################
    #################################################
    #################################################


    def _genOracCNF(self, oracIn):
        '''convert Oracle 2 cnf, used for evaluating POs.'''

        #OracPath = re.search(r'(.*)(?=\.)', self.OracInPath).group()
        #OracNFile = OracPath+'.cnf'
        genOraCnfRes = oracV2cnf( oracIn, False )
        #if os.path.isfile(OracNFile):
        self.OracPIndex = genOraCnfRes[0]
        self.OracPOindex = genOraCnfRes[1]
        self.OraCNFile = genOraCnfRes[2]    
        self.OracVarNum = genOraCnfRes[3]
        #return 1   


    #################################################
    #################################################
    #################################################
    #################################################

    def _genCamCNF(self, camIn, MuxStyle, forbitFlag):
        "build the basic miter"

        origCkt = re.search(r'(.*)(?=\.)', camIn).group()
        #1. generate the basic miter cnf
        cnfTup = v2cnfMtr(camIn, MuxStyle, forbitFlag, False)
        # time.sleep(100)
        self.baseCnfMtrLs = cnfTup[0]
        inputsInt = cnfTup[1]
        self.camPIndex = inputsInt[0]
        self.camCBindex = inputsInt[1]
        self.pbitsNum = len(self.camCBindex)
        self.ObfGateNum = self.pbitsNum/2
        self.camPOindex = cnfTup[2]
        self.camVarNum = cnfTup[3]
        self.camCNFile = cnfTup[4]
        self.baseMtrVarNum = cnfTup[5]
        self.PInum2grab = len(self.camPIndex)
        self.miterOutIndex = cnfTup[5]


    #################################################
    #################################################
    #################################################
    #################################################

    def initSolve(self, OracIn, CamIn, MuxStyle, forbitFlag):
        '''generates an initial pair of programming bit assignments, then generates an primary input vector that can distinguish them.'''

        ''' 1. generate the oracle cnf '''
        self._genOracCNF(OracIn)
        ''' 2. generate the miter cnf '''
        self._genCamCNF(CamIn, MuxStyle, forbitFlag)

        print '\n--------------------------------------------------------'
        #print "Generating the first pair of programming bits ... ..."
        print "Evaluating the first PI verctor using SAT solver... ..."

        ''' 3. connect orac ckt with camed-miter to form the base mtr 
        the camed-miter will start from integer index "1" '''       
        for po in self.OracPOindex:
            newPO = po+self.baseMtrVarNum
            self.oracPONodes2grab.append(newPO)
        self.baseCnfMtrLs.append("c oracle ckt\n")
        for line in self.OraCNFile:
            lits = line.split()[:-1][:]
            newOracLn = ''
            for lit in lits:
                if lit[0]=='-':
                    newOracLn += '-'+str(int(lit.strip('-'))+self.baseMtrVarNum)+' '
                else:
                    newOracLn += str(int(lit)+self.baseMtrVarNum)+' '
            newOracLn += '0\n'
            self.baseCnfMtrLs.append(newOracLn)
        #4. connect oracle PI with cam PI:
        self.baseCnfMtrLs.append("c connect oracle PI with cam PI\n")
        for i in range(len(self.OracPIndex)):
            oracPI = self.OracPIndex[i]
            newOracPI = oracPI+self.baseMtrVarNum
            camPI = self.camPIndex[i]
            newMtrLn1 = ''
            newMtrLn1 += str(newOracPI)+' -'+str(camPI)+' 0\n'
            newMtrLn2 = ''
            newMtrLn2 += '-'+str(newOracPI)+' '+str(camPI)+' 0\n'
            self.baseCnfMtrLs.append(newMtrLn1)
            self.baseCnfMtrLs.append(newMtrLn2)

        firstMtrCnfLs = self.baseCnfMtrLs[:]
        #firstMtrCnfLs += pbitsCons

        self.cktTotVarNum = self.OracVarNum+self.baseMtrVarNum      
        timeGend = time.asctime( time.localtime(time.time()) )      
        clauseNum = len(firstMtrCnfLs)-7 # 6 comments (besides first 3)
        cmmtLine1 = 'c This file is generated by v2cnfMtr\n'
        cmmtLine2 = 'c Generated on '+str(timeGend)+'\n'
        problemLn = 'p cnf '+str(self.cktTotVarNum)+' '+str(clauseNum)+'\n'
        firstMtrCnfLs.insert(0, problemLn)
        firstMtrCnfLs.insert(0, cmmtLine2)
        firstMtrCnfLs.insert(0, cmmtLine1)


        firstMtrTxt = ('').join(firstMtrCnfLs)
        with open("tmpIn.cnf", 'w') as outfile:
            outfile.write(firstMtrTxt)
        
        self.nodes2grab = (self.camPIndex + self.camCBindex)[:]
        # add CB bits of the second camd ckt:
        for pbitIndex in self.camCBindex:
            self.nodes2grab.append(pbitIndex + self.camVarNum)
        # add POs of oracle circuits as nodes to grab:
        for po in self.oracPONodes2grab:
            self.nodes2grab.append(po)

        return (
            self.camPIndex,
            self.camPOindex,
            self.camCBindex,
            self.camVarNum,
            self.PItemp,
            self.POtemp,
            self.oracPONodes2grab,
            self.OracPIls,
            self.OracPOls,
            self.cktTotVarNum,
            self.camCNFile,
            self.miterOutIndex,
            self.nodes2grab
        )
        #5. send the first base mtr to mimisat solver:
        #pySendPort.send(firstMtrTxt)
        #pySendPort.close()

        
    #################################################
    #################################################
    #################################################
    #################################################

    def grabNodes(self, camPIndex, camCBindex, camVarNum, oracPONodes2grab, OracPIls, OracPOls):
        "Grab new PI, PO nodes from solution given by Minisat and stored in satRes.log."

        # allNodes = pyRecvPort.recv()
        # add PIs and programming bits as nodes to grab:
        # nodes2grab = [PI, CB1, CB2, PO]
        #print camCBindex
        PInum2grab = len(camPIndex)
        pbitsNum = len(camCBindex)
        PItemp = []
        POtemp = []
        CBPtemp = [[], []]
        nodes2grab = (camPIndex+camCBindex)[:]
        secondCB = []
        # add CB bits of the second camd ckt:
        for pbitIndex in camCBindex:
            secondCB.append(pbitIndex+camVarNum)
        nodes2grab = (nodes2grab + secondCB)[:]
        # add POs of oracle circuits as nodes to grab:
        for po in oracPONodes2grab:
            nodes2grab.append(po)

        grabedNodes = grabMSnodes2("increIterationSolution.log", nodes2grab, True)
        #call('rm '+firstMtrCnf, shell=True)
        #call('rm '+initVfile, shell=True)
        if grabedNodes[0] == True: #means problem is satisfiable:
            del grabedNodes[0]
            PItemp = grabedNodes[ :PInum2grab ][:]
            CBPtemp[0] = grabedNodes[PInum2grab : (PInum2grab+pbitsNum)][:]
            CBPtemp[1] = grabedNodes[ (PInum2grab+pbitsNum) : (PInum2grab+2*pbitsNum)][:]
            POtemp = grabedNodes[ (PInum2grab+2*pbitsNum):][:]
            print "------The found PI vector that differentiates programing vector"
            for i in camCBindex:
                print i,'\t',
            print '\n'
            for i in CBPtemp[0]:
                print i,'\t',
            print "\n------with\n"
            for i in secondCB:
                print i,'\t',
            print '\n'
            for i in CBPtemp[1]:
                print i,'\t',
            print "\n------is:\n" 
            CBtext = ""
            for subCB in CBPtemp:
                for CBbit in subCB:
                    CBtext += CBbit+","
                CBtext = CBtext.strip(",")  
                CBtext += "\n"
            CBtext += "----------------(Separation Line)--------------------\n"
            with open("controlPairs.log", "a") as outfile:
                outfile.write(CBtext)
            for i in camPIndex:
                print i, '\t',
            print '\n'
            for i in PItemp:
                print i,'\t',
            print '\n'
            OracPIls.append(PItemp)
            PItext = ""
            for PIbit in PItemp:
                PItext += PIbit+","
            PItext = PItext.strip(",")  
            PItext += "\n"
            PItext += "----------------(Separation Line)--------------------\n"
            with open("PIs.log", "a") as outfile:
                outfile.write(PItext)           
            print "The corresponding primary outputs are:"
            print POtemp
            OracPOls.append(POtemp)
            return (1, OracPIls, OracPOls, PItemp, POtemp)
            #print "New input vector added to I."   
        else:
            print "Problem is not SATisfiable." 
            return (0, OracPIls, OracPOls)
        

    #################################################
    #################################################
    #################################################
    #################################################


    def addCons(self, cktTotVarNum, camVarNum, camCNFile, camCBindex, camPIndex, camPOindex, PItemp, POtemp):
        ''' add new constrain cnf clauses to "tmpIn.cnf" '''

        print '\n---------------------------------------------------------'
        # print '1. Look for new programming bit pairs that current PI set can\'t distinguish'
        # print '2. If such pair found, look for another PI verctor that can distinguish them' 

        # !!! input order of generated CompCkt: objPI, S0, S1, PI1, PI2, ...
        # !!! output order: finalMtrOut, PO1, PO2, ...
        #1.1 get the first int index for duplicated circuits:
        #prevNodeNum = int(oldDupCkt[2].split()[2]) 

        #self._grabNodes()
        dupCkt1 = []
        dupCkt2 = []
        correction1 = cktTotVarNum
        correction2 = correction1+camVarNum
        ####1.2 create 2 duplicated circuits
        for i in range(len(camCNFile)):
            tmpClause = camCNFile[i]
            intIndexLs = [tmpInt for tmpInt in tmpClause.split() if tmpInt!=''][:-1]
            newTmpCls1 = ''
            newTmpCls2 = ''
            for j in range(len(intIndexLs)):
                tmpInt = intIndexLs[j]
                if '-' in tmpInt:
                    newTmpCls1+='-'+str(int(tmpInt.strip('-'))+correction1)+' '
                    newTmpCls2+='-'+str(int(tmpInt.strip('-'))+correction2)+' '
                else:
                    newTmpCls1+=str(int(tmpInt)+correction1)+' '
                    newTmpCls2+=str(int(tmpInt)+correction2)+' '
            dupCkt1.append(newTmpCls1+'0\n')        
            dupCkt2.append(newTmpCls2+'0\n')
        # print "dupCkt1", len(dupCkt1)
        # print "dupCkt2", len(dupCkt2)

        ####1.3 connect the p-bits of new duplicated ckts with those of the miter:
        firstCBints = camCBindex[:]
        secondCBints = []
        dupCkt1CBints = []
        dupCkt2CBints = []
        for i in range(len(firstCBints)):
            baseCBInt = firstCBints[i]
            secondCBints.append(baseCBInt+camVarNum)
            dupCkt1CBints.append(baseCBInt+correction1)
            dupCkt2CBints.append(baseCBInt+correction2)
        dupCkt1CBset = []
        dupCkt2CBset = []
        for j in range(len(firstCBints)):
            #connect the first set of programming bits:
            line1=str(firstCBints[j])+' -'+str(dupCkt1CBints[j])+' 0\n'
            dupCkt1CBset.append(line1)
            line2='-'+str(firstCBints[j])+' '+str(dupCkt1CBints[j])+' 0\n'
            dupCkt1CBset.append(line2)      
            #connect the second set of programming bits:
            line3=str(secondCBints[j])+' -'+str(dupCkt2CBints[j])+' 0\n'
            dupCkt2CBset.append(line3)
            line4='-'+str(secondCBints[j])+' '+str(dupCkt2CBints[j])+' 0\n'
            dupCkt2CBset.append(line4)  
        # print "dupCkt1", len(dupCkt1CBset)
        # print "dupCkt2", len(dupCkt2CBset)

        ####1.4 assign new temp PI vectors to new duplicated circuits:  
        dupCkt1PI = []
        dupCkt2PI = []
        for m in range(len(camPIndex)): 
            basePInt = camPIndex[m]
            if PItemp[m] == '1':
                dupCkt1PI.append(str(basePInt+correction1)+' 0\n')
                dupCkt2PI.append(str(basePInt+correction2)+' 0\n')
            elif PItemp[m] == '0':
                dupCkt1PI.append('-'+str(basePInt+correction1)+' 0\n')
                dupCkt2PI.append('-'+str(basePInt+correction2)+' 0\n')  
        #print "dupCkt1", len(dupCkt1PI)
        #print "dupCkt2", len(dupCkt2PI)             
        ####1.5 assign new temp PO vectors to new duplicated circuits:
        dupCkt1PO = []
        dupCkt2PO = []          
        for n in range(len(camPOindex)):
            basePOint = camPOindex[n]
            if POtemp[n] == '1':
                dupCkt1PO.append(str(basePOint+correction1)+' 0\n')
                dupCkt2PO.append(str(basePOint+correction2)+' 0\n')
            elif POtemp[n] == '0':
                dupCkt1PO.append('-'+str(basePOint+correction1)+' 0\n')
                dupCkt2PO.append('-'+str(basePOint+correction2)+' 0\n')
        #print "dupCkt1", len(dupCkt1PO)
        #print "dupCkt2", len(dupCkt2PO)             
        ####1.6 merge all new cnf lines together:
        totDupCkt1 = dupCkt1 + dupCkt1CBset + dupCkt1PI + dupCkt1PO
        totDupCkt2 = dupCkt2 + dupCkt2CBset + dupCkt2PI + dupCkt2PO
        #print "dupCkt1", len(totDupCkt1)
        #print "dupCkt2", len(totDupCkt2)            
        newCons = totDupCkt1+totDupCkt2
        newClausesNum = len(newCons)
        cktTotVarNum += 2*camVarNum

        #timeGend = time.asctime( time.localtime(time.time()) )     
        #cmmtLine1 = 'c This file is generated by v2cnfMtr\n'
        #cmmtLine2 = 'c Generated on '+str(timeGend)+'\n'
        #problemLn = 'p cnf '+str(2*camVarNum)+' '+str(newClausesNum)+'\n'
        #newCons.insert(0, problemLn)
        #newCons.insert(0, cmmtLine2)
        #newCons.insert(0, cmmtLine1)
        newConsCnf = ('').join(newCons)

        with open("tmpIn.cnf", 'w') as outfile:
            outfile.write(newConsCnf)
        return (cktTotVarNum, newClausesNum)

    #################################################
    #################################################
    #################################################
    #################################################


    def findSolu(self, OracPIls, OracPOls, camVarNum, camCNFile,\
        camCBindex, camPIndex, camPOindex, MuxStyle, forbitFlag):
        ''' Create a file 'finalSolu.cnf' that contains all necessary clauses to fine the final programming bit assignment solution for the cam ckt.'''

        print '\n---------------------------------------------------------'
        print 'All necessary vectors are collected, now generating solution...'

        ### 1. duplicate camouflaged circuits:      
        num2dup = len(OracPIls)
        totVarNum = num2dup * camVarNum

        # print "this is forbid flag", forbitFlag
        # time.sleep(100)


        if num2dup-1 > 0:

            #initialte the # of empty lists as (#-1) of found PI vecs:
            tmpCnfLs = [[] for ls in range((num2dup-1))]

            #1. duplicate
            for i in range(len(camCNFile)):
                tmpClause = camCNFile[i]
                intIndexLs = [tmpInt for tmpInt in tmpClause.split() if tmpInt!=''][:-1]
                for j in range(num2dup-1):              
                    newTmpCls = ''
                    for k in range(len(intIndexLs)):
                        tmpInt = intIndexLs[k]
                        if '-' in tmpInt:
                            newTmpCls+='-'+str(int(tmpInt.strip('-'))+(j+1)*camVarNum)+' '
                        else:
                            newTmpCls+=str(int(tmpInt)+(j+1)*camVarNum)+' '
                    tmpCnfLs[j].append(newTmpCls+'0\n')

            #2. p-bit constraints (all connected together):
            firstCBints = camCBindex[:]
            for i in range(len(firstCBints)):
                baseCBInt=firstCBints[i]
                for j in range(num2dup-1):
                    line1=str(baseCBInt)+' -'+str(baseCBInt+(j+1)*camVarNum)+' 0\n'
                    tmpCnfLs[j].append(line1)
                    line2='-'+str(baseCBInt)+' '+str(baseCBInt+(j+1)*camVarNum)+' 0\n'                  
                    tmpCnfLs[j].append(line2)
            
            #insert original cam cnf as the head of total cnf file:
            tmpCnfLs.insert(0, camCNFile)
            # print "this is forbid flag", forbitFlag

            #5. rule rule out illegal p-bit assignments (11s), add them to the first ckt module:
            if (forbitFlag == 1):
                # print "enter target zone"
                # time.sleep(10)
                soluCBline = CBconstrain(MuxStyle, self.camCBindex)
                print "This forbidden bits added in last step is: ", soluCBline
                for i in soluCBline:
                    tmpCnfLs[0].append(i)

            for i in range(num2dup): #i-th ckt in tmpCnfLs
                PI2assign = OracPIls[i][:] #i-th PI vec
                PO2assign = OracPOls[i][:] #i-th PO vec
                #3. assign PIs:
                for j in range(len(camPIndex)): #j-th PI bit.
                    if PI2assign[j]=='1':
                        tmpCnfLs[i].append(str(camPIndex[j]+i*camVarNum)+' 0\n')
                    elif PI2assign[j]=='0':
                        tmpCnfLs[i].append('-'+str(camPIndex[j]+i*camVarNum)+' 0\n')
                #4. assign POs:
                for k in range(len(camPOindex)): #k-th PO bit.
                    if PO2assign[k]=='1':
                        tmpCnfLs[i].append(str(camPOindex[k]+i*camVarNum)+' 0\n')
                    elif PO2assign[k]=='0':
                        tmpCnfLs[i].append('-'+str(camPOindex[k]+i*camVarNum)+' 0\n')


            clauseNum = 0
            finalCNF = []
            for tmpCnf in tmpCnfLs:
                clauseNum += len(tmpCnf)
                finalCNF += tmpCnf      
                finalCNF.append('c New duplicated circuit:\n')
            finalCNF.pop()

        else:
            finalCNF = camCNFile[:]
            if(forbitFlag == 1):
                soluCBline = CBconstrain(MuxStyle, self.camCBindex)
                print "This forbidden bits added in last step is: ", soluCBline
                for i in soluCBline:
                    tmpCnfLs[0].append(i)

            # assign PIs:
            PI2assign = OracPIls[0]
            for i in range(len(PI2assign)):
                if PI2assign[i]=='1':
                    finalCNF.append(str(camPIndex[i])+' 0\n')
                elif PI2assign[i]=='0':
                    finalCNF.append('-'+str(camPIndex[i])+' 0\n')
            PO2assign = OracPOls[0]
            for i in range(len(PO2assign)):
                if PO2assign[i]=='1':
                    finalCNF.append(str(camPOindex[i])+' 0\n')
                elif PO2assign[i]=='0':
                    finalCNF.append('-'+str(camPOindex[i])+' 0\n')
            clauseNum = len(finalCNF)

        timeGend = time.asctime( time.localtime(time.time()) )
        cmmtLine1 = 'c This file is generated by _findSolu\n'
        cmmtLine2 = 'c Generated on '+str(timeGend)+'\n'
        firstLine = 'p cnf '+str(totVarNum)+' '+str(clauseNum)+'\n'
        finalCNF.insert(0, firstLine)
        finalCNF.insert(0, cmmtLine2)
        finalCNF.insert(0, cmmtLine1)       
        outxt = ('').join(finalCNF)


        findSoluCnf = 'finalSolu.cnf'
        with open(findSoluCnf, 'w') as outfile:
            outfile.write(outxt)

        ###### 2.3.    use SAT to solve    #####        
        if os.path.isfile(findSoluCnf):
            conSatLog = 'finalSolu.log' 
            #satCmmd = 'minisat ' + cnFile + ' ' + satLog
            #uncomment above line and comment next line to get more info on SAT
            satCmmd = '\nminisat '+findSoluCnf+' '+conSatLog
            print satCmmd, '\n'
            #satTime7 = time.time()
            satProc = call(satCmmd, shell=True)
            # satTime8 = time.time()
            #self.SATtime += round((satTime8 - satTime7), 4)
            #grab pbits generated:  
            solu= grabMSnodes2(conSatLog, camCBindex, True)
        if solu[0]==True:
            print "\nThe final solution for the programming bits is:"
            print solu[1:]  
            print 'Number of PI vectors need:', len(OracPIls)
            print 'Number of bits in one PI vector:', len(OracPIls[0])
            print 'Number of bits in solution CB:', len(camCBindex)
            print 'Number of bits in one PO vector:', len(OracPOls[0])

            print '\n---------------------------------------------------------'
            line1 =  str(len(OracPIls)) + ' Vectors are needed.'
            line2 = 'Total time used in MINISAT (including calling time):'
            #line3 = str(self.SATtime) + ' seconds.'        
            return line1+'\n'+line2+'\n'    
        else:
            print 'No solution found!!!!'
            return 'None\n'
    

    #################################################
    #################################################
    #################################################
    #################################################

    """
    def _main(self):
        '''Integrates functions.'''

        iterCnt = 1
        #iterTimeRec = {}
        #1. _initDissect: gen initial PI and PO:
        #time1=time.time()
        self._initDissect()
        #time2=time.time()
        if initRes==1:
            print '\n---------------------------------------------------------'
            print 'Evaluating the PO of Oracle circuit given newly found PI ... ...'
            self._genOracCNF()
            #2. generate PO w.r.t new PI for Oracle ckt:
            time3=time.time()
            self._addIOpair()
            time4=time.time()
            #iterTimeRec[iterCnt] = round(time4-time3+time2-time1, 4)
            iterCnt += 1
            #3. iteratively look for new p-bit pairs and PI:
            iterate = 1
            #the first newDupCkt is the baseMtrCnf:
            self.newDupCkt = self.baseCnfMtrLs[:]
            while iterate==1:
                #self.newDupCkt is updated internally:
                time1=time.time()
                iterate=self._findNewPInewCB()
                time2=time.time()
                #if iterate == 1:
                #   time3=time.time()
                #   self._addIOpair()
                #   time4=time.time()
                    #iterTimeRec[iterCnt]=round(time4-time3+time2-time1, 4)
                #else:
                    #iterTimeRec[iterCnt]=round(time2-time1, 4)
                iterCnt += 1
                print '\n---------------------------------------------------------'
                #print 'Current collected PI-PO pairs of the oracle circuit:'
                #print 'Primary input vectors:'
                #print self.OracPIls    
                #print 'Primary output vectors:'
                #print self.OracPOls
            #4. find final solution:
            res = self._findSolu()
            res = '\n\n'+self.CamInPath+'\n'+res
            res += "iteration\ttime (s)\n"
            for i in iterTimeRec:
                res += str(i)+'\t:\t'+str(iterTimeRec[i])+'\n'
            return res
        else:
            return 'No solution found.\n'
    """


#################################################
#################################################
#################################################
#################################################

"""
def rundecam():

    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")    
    readline.set_completer(cmmd_and_path_complete)

    print "\n\t########## Welcome to SAT SLOVER system. ##########"
    print "\t#This system is used to solve the camouflaged ckt #"
    print "\t#reverse engineering problem.                     #"
    print "\t###################################################"
    print "\n\tThis program dissects circuit and finds the correct" 
    print "\tinternal components. User needs to inform the number"
    print "\tof obfuscated gates in the circuit. The program now c-"
    print "\t-onsiders 3 choices for each obfuscated gate by default.\n"    
    

    parser = argparse.ArgumentParser(usage='python decam-v4-cmmdline.py [-h] <orac.v> <cam.v> [-o <res_file>]', description='This program will use orac.v and cam.v to generate a programming bit vector (if exists)\
     that can make the cam.v has the same function as orac.v. The results and solution are presented in the\
     output file.',)
    parser.add_argument('<orac.v>', help='input oracle Verilog file that defines the function of the circuit')
    parser.add_argument('<cam.v>', help='the camouflaged circuit that we want to solve.')
    parser.add_argument('-o', "--res_file", nargs='?', type=argparse.FileType('a'), help='output file')
    args = parser.parse_args()
    outfile = args.res_file


    orcIn = sys.argv[1]
    OracInPath = os.path.abspath(orcIn)
    if not os.path.isfile(OracInPath):
        print 'Invalid oracle circuit file!!!!\n'
        return  
    camIn = sys.argv[2]
    CamInPath = os.path.abspath(camIn)
    if not os.path.isfile(CamInPath):
        print 'Invalid camouflaged circuit file!!!!\n'
        return
    #obfGateNum = raw_input('>>> ')
    #obfGateNum = int(obfGateNum)
    totTime1 = time.time()
    mainClass = DissectCkt(OracInPath, CamInPath)
    res = mainClass._main()
    totTime2 = time.time()
    totTime = round(totTime2-totTime1, 4)
    line4 = 'The total time used (including file parse time) is\n'
    line5 = str(totTime)+' s\n'
    res += line4
    res += line5
    if outfile != None:
        outfile.write(res)
        outfile.close()
        print 'Result is written in', os.path.abspath(outfile.name) #b/c 'outfile' is a file object
    else:
        print res
    print 'Thank you!\n'
    #outfilepath = os.path.abspath(outfile)
""" 

"""
if __name__=='__main__':
    rundecam()
"""









