#!/usr/bin/python

from subprocess import call
from subprocess import Popen, PIPE, STDOUT 


"""Generate circuit with 200 gates randomly camouflaged."""

cktPath='/home/umass/Dropbox/Rearch-w-Prof-H/ReverseEngineeringProj/benchmarks/iscas/'
prgmPath='/home/umass/Dropbox/Rearch-w-Prof-H/ReverseEngineeringProj/experiment-files/camouflage/./camCkt-randCam-cmmdline.py '
files = ['c1355', 'c1908', 'c2670', 'c3540', 'c432', 'c499', 'c5315',  'c6288', 'c7552', 'c880']
#files = ['c5315']
rndLs=[0,1,2,3,4,5,6,7,8,9]
for rnd in rndLs:
	for filename in files:
		inCorr = cktPath+filename+'/'+filename+'-corr.log'
		lineCnt = 0
		with open (inCorr, 'r') as infile:
			for line in infile:
				lineCnt += 1
		if lineCnt < 200: # cam all gates:
			total = lineCnt+1
		else: 
			total = 202
		for i in range(1, total, 5):
			randCamCmmd = prgmPath+cktPath+filename+'/'+filename+'-abcmap-fmt.v'+' '+str(i)
			call(randCamCmmd, shell=True)
			outfilePath = cktPath+filename+'/'+filename+'-abcmap-fmt-randCam'+str(i)+'.v'
			renameFile = cktPath+filename+'/'+filename+'-abcmap-fmt-'+str(rnd)+'-randCam'+str(i)+'.v'
			call('mv '+outfilePath+' '+renameFile, shell=True)	
			dest = cktPath+filename+'/'+'rand'
			print dest
			call('mv '+renameFile+' '+dest, shell=True)			

