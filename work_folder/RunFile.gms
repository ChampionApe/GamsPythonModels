$FIX PE_Example3_gtech, PE_Example3_gexo;

$UNFIX PE_Example3_gendo;

$Model PE_Example3 M_s1_in, M_s1_out;

scalars PE_Example3_modelstat, PE_Example3_solvestat;solve PE_Example3 using CNS;PE_Example3_modelstat = PE_Example3.modelstat; PE_Example3_solvestat = PE_Example3.solvestat;