module	c17 (N1,N2,N3,N4,N5,N6,N7,N8,N9,N12,N13,N14);

input  N1,N2,N3,N4,N5,CONST1,CONS0 //RE__PI;

input D_0,D_1,D_2,D_3 //RE__ALLOW(00,01,10,11);
 
output N10,N11;

wire N6,N7,N8,N9,D_0_NOT,D_1_NOT,N7_NOT,N7_OBF,ED_0,ED_1,ED_2,ED_3,ED_4,ED_5,ED_6,ED_7,ED_8,ED_9,D_2_NOT,D_3_NOT,N6_NOT,N6_OBF,ED_10,ED_11,ED_12,ED_13,ED_14,ED_15,ED_16,ED_17,ED_18,ED_19;
     
nand2 gate1( .a(N1), .b(N3), .O(N6) );
nand2 gate2( .a(N3), .b(N4), .O(N8) );
nand2 gate3( .a(N2), .b(N8), .O(N7) );
nand2 gate4( .a(N8), .b(N5), .O(N9) );
nand2 gate5( .a(N6_OBF), .b(N7), .O(N10) );
nand2 gate6( .a(N7_OBF), .b(N9), .O(N11) );
inv1 gate( .a(D_0), .O(D_0_NOT) );
inv1 gate( .a(D_1), .O(D_1_NOT) );
inv1 gate( .a(N7), .O(N7_NOT) );
and2 gate( .a(N7), .b(D_0_NOT), .O(ED_0) );
and2 gate( .a(N7_NOT), .b(D_0_NOT), .O(ED_1) );
and2 gate( .a(CONST1), .b(D_0), .O(ED_2) );
and2 gate( .a(CONST0), .b(D_0), .O(ED_3) );
and2 gate( .a(ED_0), .b(D_1_NOT), .O(ED_9) );
and2 gate( .a(ED_1), .b(D_1), .O(ED_7) );
and2 gate( .a(ED_2), .b(D_1_NOT), .O(ED_5) );
and2 gate( .a(ED_3), .b(D_1), .O(ED_4) );
or2  gate( .a(ED_4), .b(ED_5), .O(ED_6) );
or2  gate( .a(ED_6), .b(ED_7), .O(ED_8) );
or2  gate( .a(ED_9), .b(ED_8), .O(N7_OBF) );
inv1 gate( .a(D_2), .O(D_2_NOT) );
inv1 gate( .a(D_3), .O(D_3_NOT) );
inv1 gate( .a(N6), .O(N6_NOT) );
and2 gate( .a(N6), .b(D_2_NOT), .O(ED_10) );
and2 gate( .a(N6_NOT), .b(D_2_NOT), .O(ED_11) );
and2 gate( .a(CONST1), .b(D_2), .O(ED_12) );
and2 gate( .a(CONST0), .b(D_2), .O(ED_13) );
and2 gate( .a(ED_10), .b(D_3_NOT), .O(ED_19) );
and2 gate( .a(ED_11), .b(D_3), .O(ED_17) );
and2 gate( .a(ED_12), .b(D_3_NOT), .O(ED_15) );
and2 gate( .a(ED_13), .b(D_3), .O(ED_14) );
or2  gate( .a(ED_14), .b(ED_15), .O(ED_16) );
or2  gate( .a(ED_16), .b(ED_17), .O(ED_18) );
or2  gate( .a(ED_19), .b(ED_18), .O(N6_OBF) );

endmodule
