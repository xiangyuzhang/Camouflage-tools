#!/usr/bin/python

from subprocess import call
from subprocess import Popen, PIPE, STDOUT 

"""camouflage all gates in the corruptability list."""


cktPath='/home/umass/Dropbox/Rearch-w-Prof-H/ReverseEngineeringProj/benchmarks/iscas/'
prgmPath='/home/umass/Dropbox/Rearch-w-Prof-H/ReverseEngineeringProj/experiment-files/camouflage/./camCkt-corrCam-cmmdline.py '
files = ['c1355', 'c1908', 'c2670', 'c3540', 'c432', 'c499', 'c5315',  'c6288', 'c7552', 'c880']
#files = ['c499']
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
		corrCamCommd = prgmPath+cktPath+filename+'/'+filename+'-abcmap-fmt.v'+' '+inCorr+' '+str(i)
		call(corrCamCommd, shell=True)
		outfilePath = cktPath+filename+'/'+filename+'-abcmap-fmt-corrCam'+str(i)+'.v'
		dest = cktPath+filename+'/'+'corr'
		call('mv '+outfilePath+' '+dest, shell=True)