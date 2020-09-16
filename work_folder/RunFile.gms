$FIX test_gtech, test_gexo;

$UNFIX test_gendo;

$Model test M_s1_in, M_s1_out;

solve test using CNS;
