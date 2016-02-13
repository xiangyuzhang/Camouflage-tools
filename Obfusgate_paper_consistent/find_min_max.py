__author__ = 'xiangyuzhang'
import re
str = "nand2 gate65( .a(N213), .b(N76), .O(N257) );"
print(re.search("^nand2",str).group())