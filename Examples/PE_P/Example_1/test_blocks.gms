$BLOCK M_in 
	E_pindex_o_in[n]$(t_out_in[n])..	PbT[n] =E= sum(nn$(map_test_in[nn,n]), qD[nn]*PwT[nn])/qD[n];
	E_pindex_no_in[n]$(i_kno_no_in[n])..	PwT[n] =E= sum(nn$(map_test_in[nn,n]), qD[nn]*PwT[nn])/qD[n];
	E_quant_o_in[n]$(i_bra_o_in[n])..	qD[n] =E= sum(nn$(map_test_in[n,nn]), (mu[n,nn] * (PbT[nn]/PwT[n])**(sigma[nn]) * qS[nn])/sum(nnn$(map_test_in[nnn,nn]), mu[nnn,nn] *(PbT[nn]/PwT[nnn])**(sigma[nn])));
	E_quant_no_in[n]$(i_bra_no_in[n])..	qD[n] =E= sum(nn$(map_test_in[n,nn]), (mu[n,nn] * (PwT[nn]/PwT[n])**(sigma[nn]) * qD[nn])/sum(nnn$(map_test_in[nnn,nn]), mu[nnn,nn] *(PwT[nn]/PwT[nnn])**(sigma[nn])));
$ENDBLOCK
$BLOCK M_out 
	E_pindex_out[n]$(i_kno_out[n])..	PwT[n] =E= (sum(nn$(map_test_out[nn,n] and out[nn]), mu[nn,n] * PbT[nn]**(1-eta[n]))+sum(nn$(map_test_out[nn,n] and not out[nn]), mu[nn,n] * PwT[nn]**(1-eta[n])))**(1/(1-eta[n]));
	E_quant_o_out[n]$(i_bra_o_out[n])..	qS[n] =E= sum(nn$(map_test_out[n,nn]), mu[n,nn] * (PbT[n]/PwT[nn])**(-eta[nn]) * qD[nn]);
	E_quant_no_out[n]$(i_bra_no_out[n])..	qD[n] =E= sum(nn$(map_test_out[n,nn]), mu[n,nn] * (PwT[n]/PwT[nn])**(-eta[nn]) * qD[nn]);
$ENDBLOCK
