
module c432 (N1, NO);

input  N1,CONST1,CONST0 //RE__PI;

input D_0,D_1,D_2,D_3,D_4,D_5,D_6,D_7,D_8,D_9 //RE__ALLOW(00,01,10,11);

output NO;

wire ,D_0_NOT,D_1_NOT,N1_NOT,N1_OBF,ED_0,ED_1,ED_2,ED_3,ED_4,ED_5,ED_6,ED_7,ED_8,ED_9,
D_2_NOT,D_3_NOT,N1_NOT,N1_OBF,ED_10,ED_11,ED_12,ED_13,ED_14,ED_15,ED_16,ED_17,ED_18,ED_19,
D_4_NOT,D_5_NOT,N1_NOT,N1_OBF,ED_20,ED_21,ED_22,ED_23,ED_24,ED_25,ED_26,ED_27,ED_28,ED_29,
D_6_NOT,D_7_NOT,N1_NOT,N1_OBF,ED_30,ED_31,ED_32,ED_33,ED_34,ED_35,ED_36,ED_37,ED_38,ED_39,
D_8_NOT,D_9_NOT,NO_OBF_NOT,NO_OBF,ED_40,ED_41,ED_42,ED_43,ED_44,ED_45,ED_46,ED_47,ED_48,ED_49;
;
inv1 gate( .a(D_0), .O(D_0_NOT) );
inv1 gate( .a(D_1), .O(D_1_NOT) );
inv1 gate( .a(N1), .O(N1_NOT) );
and2 gate( .a(N1), .b(D_0_NOT), .O(ED_0) );
and2 gate( .a(N1_NOT), .b(D_0_NOT), .O(ED_1) );
and2 gate( .a(CONST1), .b(D_0), .O(ED_2) );
and2 gate( .a(CONST0), .b(D_0), .O(ED_3) );
and2 gate( .a(ED_0), .b(D_1_NOT), .O(ED_9) );
and2 gate( .a(ED_1), .b(D_1), .O(ED_7) );
and2 gate( .a(ED_2), .b(D_1_NOT), .O(ED_5) );
and2 gate( .a(ED_3), .b(D_1), .O(ED_4) );
or2  gate( .a(ED_4), .b(ED_5), .O(ED_6) );
or2  gate( .a(ED_6), .b(ED_7), .O(ED_8) );
or2  gate( .a(ED_9), .b(ED_8), .O(N1_OBF) );
inv1 gate( .a(D_2), .O(D_2_NOT) );
inv1 gate( .a(D_3), .O(D_3_NOT) );
inv1 gate( .a(N1), .O(N1_NOT) );
and2 gate( .a(N1), .b(D_2_NOT), .O(ED_10) );
and2 gate( .a(N1_NOT), .b(D_2_NOT), .O(ED_11) );
and2 gate( .a(CONST1), .b(D_2), .O(ED_12) );
and2 gate( .a(CONST0), .b(D_2), .O(ED_13) );
and2 gate( .a(ED_10), .b(D_3_NOT), .O(ED_19) );
and2 gate( .a(ED_11), .b(D_3), .O(ED_17) );
and2 gate( .a(ED_12), .b(D_3_NOT), .O(ED_15) );
and2 gate( .a(ED_13), .b(D_3), .O(ED_14) );
or2  gate( .a(ED_14), .b(ED_15), .O(ED_16) );
or2  gate( .a(ED_16), .b(ED_17), .O(ED_18) );
or2  gate( .a(ED_19), .b(ED_18), .O(N1_OBF) );
inv1 gate( .a(D_4), .O(D_4_NOT) );
inv1 gate( .a(D_5), .O(D_5_NOT) );
inv1 gate( .a(N1), .O(N1_NOT) );
and2 gate( .a(N1), .b(D_4_NOT), .O(ED_20) );
and2 gate( .a(N1_NOT), .b(D_4_NOT), .O(ED_21) );
and2 gate( .a(CONST1), .b(D_4), .O(ED_22) );
and2 gate( .a(CONST0), .b(D_4), .O(ED_23) );
and2 gate( .a(ED_20), .b(D_5_NOT), .O(ED_29) );
and2 gate( .a(ED_21), .b(D_5), .O(ED_27) );
and2 gate( .a(ED_22), .b(D_5_NOT), .O(ED_25) );
and2 gate( .a(ED_23), .b(D_5), .O(ED_24) );
or2  gate( .a(ED_24), .b(ED_25), .O(ED_26) );
or2  gate( .a(ED_26), .b(ED_27), .O(ED_28) );
or2  gate( .a(ED_29), .b(ED_28), .O(N1_OBF) );
inv1 gate( .a(D_6), .O(D_6_NOT) );
inv1 gate( .a(D_7), .O(D_7_NOT) );
inv1 gate( .a(N1), .O(N1_NOT) );
and2 gate( .a(N1), .b(D_6_NOT), .O(ED_30) );
and2 gate( .a(N1_NOT), .b(D_6_NOT), .O(ED_31) );
and2 gate( .a(CONST1), .b(D_6), .O(ED_32) );
and2 gate( .a(CONST0), .b(D_6), .O(ED_33) );
and2 gate( .a(ED_30), .b(D_7_NOT), .O(ED_39) );
and2 gate( .a(ED_31), .b(D_7), .O(ED_37) );
and2 gate( .a(ED_32), .b(D_7_NOT), .O(ED_35) );
and2 gate( .a(ED_33), .b(D_7), .O(ED_34) );
or2  gate( .a(ED_34), .b(ED_35), .O(ED_36) );
or2  gate( .a(ED_36), .b(ED_37), .O(ED_38) );
or2  gate( .a(ED_39), .b(ED_38), .O(N1_OBF) );
inv1 gate( .a(D_8), .O(D_8_NOT) );
inv1 gate( .a(D_9), .O(D_9_NOT) );
inv1 gate( .a(NO_OBF), .O(NO_OBF_NOT) );
and2 gate( .a(NO_OBF), .b(D_8_NOT), .O(ED_40) );
and2 gate( .a(NO_OBF_NOT), .b(D_8_NOT), .O(ED_41) );
and2 gate( .a(CONST1), .b(D_8), .O(ED_42) );
and2 gate( .a(CONST0), .b(D_8), .O(ED_43) );
and2 gate( .a(ED_40), .b(D_9_NOT), .O(ED_49) );
and2 gate( .a(ED_41), .b(D_9), .O(ED_47) );
and2 gate( .a(ED_42), .b(D_9_NOT), .O(ED_45) );
and2 gate( .a(ED_43), .b(D_9), .O(ED_44) );
or2  gate( .a(ED_44), .b(ED_45), .O(ED_46) );
or2  gate( .a(ED_46), .b(ED_47), .O(ED_48) );
or2  gate( .a(ED_49), .b(ED_48), .O(NO) );
nand4 gate( .a(N1_OBF), .b(N1_OBF), .c(N1_OBF), .d(N1_OBF), .O(NO_OBF) );

endmodule
