__author__ = 'xiangyuzhang'
from subprocess import call
import os
from EC_lib import EC
# create
make_cmmd = ""
run_cmmd = ""
plot_cmmd = ""
with open("time-info", "a") as outfile:
    outfile.write("#Num_mux                 #Num_XOR                    #Runtime\n")
while(1):
    for Num_mux in range(1, 14):
        Mux_circuit = "c1908-mux4-"+ str(Num_mux) + ".v"
        XOR_circuit = "c1908-mux4-"+ str(Num_mux) + "-XOR-" + str(55-Num_mux*4) + ".v"
        make_cmmd = "python XOR_Cam_random.py " + Mux_circuit + " " + str(55-Num_mux*4)
        call(make_cmmd, shell = True)
    # run
        run_cmmd = "/usr/bin/time -v -o temp-time ./minisat-incre-simp decam-incre c1908-abcmap-fmt.v " + XOR_circuit
        call(run_cmmd, shell = True)
        #os.rename("increIterationInfo.log", XOR_circuit.strip(".v") + "-interationInfo.dat")
    # EC
        res = EC("c1908-abcmap-fmt.v", XOR_circuit, "finalSolu.log")
        if (res == 1):
            content = "Circuit: " + XOR_circuit + " is CORRECT!\n"
        elif (res == 0):
            content = "Circuit: " + XOR_circuit + " is WRONG!\n"
        else:
            content = "Circuit: " + XOR_circuit + " is BUG!\n"
        with open("EC_result.txt", "a") as output:
            output.write(content)
    # collect data
        with open("temp-time", "r") as infile:
            timeline = infile.read().split("\n")

        for line in timeline:
            if "User time (seconds):" in line:
                time_info = line.replace("User time (seconds):", "")
                break
        with open("time-info", "a") as outfile:
            outfile.write(str(Num_mux) + "                   " + str(55-Num_mux) + "                    " + time_info +"\n")
    # plot
        call("rm " + XOR_circuit, shell = True)
    plot_cmmd = "gnuplot script"
    call(plot_cmmd, shell =True)
 