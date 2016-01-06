import time
def CBconstrain (MuxStyle, camCBindex):
    result = []
    forbid = []
    CBconstrain = ''
    for j in range(0,len(MuxStyle)):  # how many bits of each set
        forbid.append(MuxStyle[j:j+1])  # now it is a list with every bits like ['1','0']
    # print "this is:" , i, forbid
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

    print "this is muxstyle", MuxStyle
    print "this is camCBindex", camCBindex
    print 'this is the result', result
    print "this is forbid",forbid
    print "this is len",len(MuxStyle)
    # time.sleep(100)
    return result
