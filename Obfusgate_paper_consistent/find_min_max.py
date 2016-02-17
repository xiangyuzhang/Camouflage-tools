import re

def NAND4_builder(net1, net2, net3, net4, output, seed, programbit):
    PIPO_list = [net1, net2, net3, net4]
    OBF_list = [net1 + "_OBF", net2 + "_OBF", net3 + "OBF", net4 + "_OBF"]
    NAND4 = "nand4 gate( .a(" + net1 + "_OBF" + "), .b(" + net2 + "_OBF" + "), .c(" + net3 + "_OBF" + "), .d(" + net4 + "_OBF" + "), .O(" + output + "_OBF" + ") )"
    res = {"new_netlist":[], "CB":[], "wire":[],"output":[]}
    result = {"new_netlist":'', "CB":'', "wire":'',"output":[]}
    for net in PIPO_list:
        info = abcmap_MUX_OBF_netlist(net, net + "_OBF", seed, programbit)
        res["new_netlist"].append(info[0])
        res["CB"].append(info[2])
        res["wire"].append(info[1])
        res["output"].append(info[3])
        seed+=9
        programbit+=2
    info = abcmap_MUX_OBF_netlist(output + "_OBF", output, seed, programbit)
    res["new_netlist"].append(info[0])
    res["CB"].append(info[2])
    info[1] = info[1].replace("," + output + ",", "," + output + "_OBF" + ",")
    res["wire"].append(info[1])
    res["output"].append(info[3])
    res["new_netlist"].append(NAND4)
    result["new_netlist"] = ";\n".join(res["new_netlist"])
    result["CB"] = ",".join(res["CB"])
    result["wire"] = ",\n".join(res["wire"])
    result["output"] = res["output"]
    return result

def abcmap_MUX_OBF_netlist(pi1, output, seed, programbit):
    D_bit1 = 'D_' + str(programbit)
    D_bit2 = 'D_' + str(programbit + 1)
    D_bit1_not = 'D_' + str(programbit) + "_NOT"
    D_bit2_not = 'D_' + str(programbit + 1) + "_NOT"
    pi1_not = str(pi1) + "_NOT"
    new_netlist = []
    wire = []
    CB = []
    result = []
    new_netlist.append("inv1 gate( .a(" + D_bit1 + "), .O(" +  D_bit1_not + ") );\n")
    new_netlist.append("inv1 gate( .a(" + D_bit2 + "), .O(" +  D_bit2_not + ") );\n")
    new_netlist.append("inv1 gate( .a(" + pi1 + "), .O(" +  pi1_not + ") );\n")
    new_netlist.append("and2 gate( .a(" + pi1 + "), .b(" + D_bit1_not + "), .O(" + "ED_" + str(seed) + ") );\n")
    new_netlist.append("and2 gate( .a(" + pi1_not + "), .b(" + D_bit1_not + "), .O(" + "ED_" + str(seed + 1) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "CONST1" + "), .b(" + D_bit1 + "), .O(" + "ED_" + str(seed + 2) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "CONST0" + "), .b(" + D_bit1 + "), .O(" + "ED_" + str(seed + 3) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "ED_" + str(seed) + "), .b(" + D_bit2_not + "), .O(" + "ED_" + str(seed + 9) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "ED_" + str(seed + 1) + "), .b(" + D_bit2 + "), .O(" + "ED_" + str(seed + 7) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "ED_" + str(seed + 2) + "), .b(" + D_bit2_not + "), .O(" + "ED_" + str(seed + 5) + ") );\n")
    new_netlist.append("and2 gate( .a(" + "ED_" + str(seed + 3) + "), .b(" + D_bit2 + "), .O(" + "ED_" + str(seed + 4) + ") );\n")
    new_netlist.append("or2  gate( .a(" +  "ED_" + str(seed + 4) + "), .b(" + "ED_" + str(seed + 5) +"), .O(" + "ED_" + str(seed + 6) +") );\n")
    new_netlist.append("or2  gate( .a(" +  "ED_" + str(seed + 6) + "), .b(" + "ED_" + str(seed + 7) +"), .O(" + "ED_" + str(seed + 8) +") );\n")
    new_netlist.append("or2  gate( .a(" +  "ED_" + str(seed + 9) + "), .b(" + "ED_" + str(seed + 8) +"), .O(" + str(output) +")")
    new_netlist_str = ('').join(new_netlist)
    wire.append(D_bit1_not)
    wire.append(D_bit2_not)
    wire.append(pi1_not)
    wire.append(output)
    for i in range(0,10):
        wire.append("ED_" + str(seed + i))
    wire = ','.join(wire)
    CB.append(D_bit1)
    CB.append(D_bit2)
    CB = ','.join(CB)
    result.append(new_netlist_str)
    result.append(wire)
    result.append(CB)
    result.append(output)
    return result
# seed is the initial index for wires
# program bit is the initial index for CBs
# return [new_netlist, wire, CB, output]  output is also included in wire
def re_find_gateType(gate):
    result = []
    temp = re.findall(r'([a-z]+[0-9])', gate)[0]
    gate_type = re.findall(r'([a-z]+)', temp)
    input_number = re.findall(r'([0-9])', temp)
    result = {"gate_type":gate_type, "input_number":input_number}
    return result
    # result = {"gate_type":gate_type, "input_number":input_number}
gate = "or2 gate19( .a(N257), .b(N264), .O(N768) );"
res = re_find_gateType(gate)

res = NAND4_builder("N1", "N2", "N3", "N4", "Output", 0, 0)

CB = "input " + res["CB"] + "\n\n"
netlist = res["new_netlist"] + "\n\n"
wire = "wire" + res["wire"] + "\n\n"

with open("test", "a") as f:
    f.write(CB)
    f.write(wire)
    f.write(netlist)
print ''