__author__ = 'xiangyuzhang'
from subprocess import call
<<<<<<< HEAD
'''
camlist = [
    "c7552-mux4-1.v",
    "c7552-mux4-11.v",
    "c7552-mux4-21.v",
    "c7552-mux4-31.v",
    "c7552-mux4-41.v",
    "c7552-mux4-51.v",
    "c7552-mux4-61.v",
    "c7552-mux4-71.v",
    "c7552-mux4-81.v",
    "c7552-mux4-91.v",
    "c7552-mux4-101.v",
    "c7552-mux4-111.v",
    "c7552-mux4-121.v",
    "c7552-mux4-131.v",
    "c7552-mux4-141.v",
    "c7552-mux4-151.v",
    "c7552-mux4-161.v",
    "c7552-mux4-171.v",
    "c7552-mux4-181.v",
    "c7552-mux4-191.v",
    "c7552-mux4-201.v"
    ]
||||||| merged common ancestors
import os

camlist = ["c3540-mux4-1.v",
"c3540-mux4-11.v",
"c3540-mux4-21.v",
"c3540-mux4-31.v",
"c3540-mux4-41.v",
"c3540-mux4-51.v",
"c3540-mux4-61.v",
"c3540-mux4-71.v",
"c3540-mux4-81.v",
"c3540-mux4-91.v",
"c3540-mux4-101.v",
"c3540-mux4-111.v",
"c3540-mux4-121.v",
"c3540-mux4-131.v",
"c3540-mux4-141.v",
"c3540-mux4-151.v",
"c3540-mux4-161.v",
"c3540-mux4-171.v",
"c3540-mux4-181.v",
"c3540-mux4-191.v",
"c3540-mux4-201.v"]
=======

camlist = [
    "c7552-mux4-1.v",
    "c7552-mux4-11.v",
    "c7552-mux4-21.v",
    "c7552-mux4-31.v",
    "c7552-mux4-41.v",
    "c7552-mux4-51.v",
    "c7552-mux4-61.v",
    "c7552-mux4-71.v",
    "c7552-mux4-81.v",
    "c7552-mux4-91.v",
    "c7552-mux4-101.v",
    "c7552-mux4-111.v",
    "c7552-mux4-121.v",
    "c7552-mux4-131.v",
    "c7552-mux4-141.v",
    "c7552-mux4-151.v",
    "c7552-mux4-161.v",
    "c7552-mux4-171.v",
    "c7552-mux4-181.v",
    "c7552-mux4-191.v",
    "c7552-mux4-201.v"
    ]
>>>>>>> origin/master
for i in camlist:
    camd = "python XOR_Cam.py " + i
<<<<<<< HEAD
    call(camd, shell = True)

for j in range(1,202,10):
        camd = "python XOR_Cam.py c5315-mux4-" + str(j) + ".v"
        call(camd, shell = True)

for k in range(1,202,10):
        camd = "python XOR_Cam.py c1908-mux4-" + str(k) + ".v"
        call(camd, shell = True)
'''
for e in range(1,202,10):
        camd = "python XOR_Cam.py c3540-mux4-" + str(e) + ".v"
        call(camd, shell = True)


||||||| merged common ancestors
    call(camd, shell = True)
=======
    call(camd, shell = True)

for j in range(1,202,10):
        camd = "python XOR_Cam.py c5315-mux4-" + str(j) + ".v"
        call(camd, shell = True)

for k in range(1,202,10):
        camd = "python XOR_Cam.py c1908-mux4-" + str(k) + ".v"
        call(camd, shell = True)

for e in range(1,202,10):
        camd = "python XOR_Cam.py c1355-mux4-" + str(e) + ".v"
        call(camd, shell = True)


>>>>>>> origin/master
