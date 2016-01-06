
def CBconstrain (MuxStyle, camCBindex):
    result = []
    for i in range(0,len(MuxStyle)):  # how many sets of CB
        forbid = []
        CBconstrain = ''
        for j in range(0,len(MuxStyle[i])):  # how many bits of each set
            forbid.append(MuxStyle[i][j:j+1])  # now it is a list with every bits like ['1','0']
        forbidlen = len(forbid)
        for it in range(0,len(camCBindex)/forbidlen):
            for k in range(0, len(forbid)):
                if forbid[k] == '0':
                    CBconstrain += (str(camCBindex[it*forbidlen + k])+' ')
                elif forbid[k] == '1':
                    CBconstrain +=('-'+ str(camCBindex[it*forbidlen + k])+' ')
            CBconstrain += '0\n'
            result.append(CBconstrain)
            CBconstrain = ''

    return result
