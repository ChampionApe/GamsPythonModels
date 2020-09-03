$FIX abate_gtech, abate_gexo, abate_g_techcalib;

$UNFIX abate_gendo, abate_g_calibendo;

$Model abate M_CES_types, M_ES, M_ESC, M_T_out, M_calib;

solve abate using CNS;
