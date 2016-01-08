__author__ = 'xiangyuzhang'
import re
string = "and3 gate11( .a(N29), .b(N75), .c(N42), .O(N290) );"

# print re.sub((N29), "(N29_OBF)", string)
print string.replace("(N29)", "(N29_OBF)")