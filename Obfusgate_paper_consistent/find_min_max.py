__author__ = 'xiangyuzhang'
import re
str = "and2 gate69( .a(N382), .b(N263), .O(N688) );"
if (re.search("^and2",str).group()) == "and2":
    print "yes"