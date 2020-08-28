$BLOCK M_in 
	E_pindex_o_in[n]$(t_out_in[n])..	PbT[n] =E= sum(nn$(map_test_in[nn,n]), qD[nn]*PwT[nn])/qD[n];
	E_pindex_no_in[n]$(i_kno_no_in[n])..	PwT[n] =E= sum(nn$(map_test_in[nn,n]), qD[nn]*PwT[nn])/qD[n];
	E_quant_o_in[n]$(i_bra_o_in[n])..	qD[n] =E= sum(nn$(map_test_in[n,nn]), mu[n,nn]* exp((PbT[nn]-PwT[n])/sigma[nn])*qS[nn] / sum(nnn$(map_test_in[nnn,nn]), mu[nnn,nn]* exp((PbT[nn]-PwT[nnn])/sigma[nn])));
	E_quant_no_in[n]$(i_bra_no_in[n])..	qD[n] =E= sum(nn$(map_test_in[n,nn]), mu[n,nn]* exp((PwT[nn]-PwT[n])/sigma[nn])*qD[nn] / sum(nnn$(map_test_in[nnn,nn]), mu[nnn,nn]* exp((PwT[nn]-PwT[nnn])/sigma[nn])));
$ENDBLOCK
$BLOCK M_out 
	E_pindex_out[n]$(i_kno_out[n])..	PwT[n] =E= (sum(nn$(map_test_out[nn,n] and out[nn]), qS[nn]*PbT[nn])+sum(nn$(map_test_out[nn,n] and not out[nn]), qD[nn]*PwT[nn]))/qD[n];
	E_quant_o_out[n]$(i_bra_o_out[n])..	qS[n] =E= sum(nn$(map_test_out[n,nn]),  exp((PwT[nn]-PbT[n])/eta[nn])*qD[nn] / (sum(nnn$(map_test_out[nnn,nn] and out[nnn]),  exp((PwT[nn]-PbT[nnn])/eta[nn]))+sum(nnn$(map_test_out[nnn,nn] and not out[nnn]),  exp((PwT[nn]-PwT[nnn])/eta[nn]))));
	E_quant_no_out[n]$(i_bra_no_out[n])..	qD[n] =E= sum(nn$(map_test_out[n,nn]),  exp((PwT[nn]-PwT[n])/eta[nn])*qD[nn] / (sum(nnn$(map_test_out[nnn,nn] and out[nnn]),  exp((PwT[nn]-PbT[nnn])/eta[nn]))+sum(nnn$(map_test_out[nnn,nn] and not out[nnn]),  exp((PwT[nn]-PwT[nnn])/eta[nn]))));
$ENDBLOCK
