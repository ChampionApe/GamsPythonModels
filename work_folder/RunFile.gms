$FIX test_gtech, test_gexo;

$UNFIX test_gendo;

$Model test M_in, M_out;

solve test using CNS;
