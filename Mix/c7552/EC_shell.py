




import os
import readline
import glob
import sys
import time
from subprocess import call, Popen, PIPE, STDOUT
import argparse



#from abcProc import *

#from abcMapV2CNF import *
from EC_lib import EC

def cmmd_and_path_complete(text, state):
    '''automatically complete path'''
    return (glob.glob(text+'*')+[None])[state]+'/'


def rundecam():

    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(cmmd_and_path_complete)




    parser = argparse.ArgumentParser(usage='python EC [-h] <orac.v> <cam.v> <solu.v>', description='This program will check the correntness for corresponding solution',)
    parser.add_argument('<orac.v>', help='input oracle Verilog file that defines the function of the circuit')
    parser.add_argument('<cam.v>', help='the camouflaged circuit that we want to solve.')
    parser.add_argument('<solu.v>', help = 'the solutiion try to proof')




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
    soluIn = sys.argv[3]
    SoluInPath = os.path.abspath(soluIn)
    if not os.path.isfile(CamInPath):
        print 'Invalid solution  file!!!!\n'
        return






    res = EC(OracInPath, CamInPath, SoluInPath)

    if res == 1:
        print "Solution is correct!"
    elif res == 0:
        print "Solution is wrong!"
    else:
        print "BUG!"
    print 'Thank you!\n'




if __name__=='__main__':
    rundecam()
