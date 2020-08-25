$BLOCK M_in 
	E_in_p_o[n]$((t_out_in[n]) and sigma.l[n] <> 1)..	PbT[n] =E= sum(nn$(map_test_in[nn,n]), mu[nn,n] * PwT[nn]**(1-sigma[n]))**(1/(1-sigma[n]));
	E_in_p_no[n]$((i_kno_no_in[n]) and sigma.l[n] <> 1)..	PwT[n] =E= sum(nn$(map_test_in[nn,n]), mu[nn,n] * PwT[nn]**(1-sigma[n]))**(1/(1-sigma[n]));
	E_in_pc_CD_o[n]$((t_out_in[n]) and sigma.l[n] = 1)..	PbT[n] =E= prod(nn$(map_test_in[nn,n]), PwT[nn]**(mu[nn,n]));
	E_in_p_CD_no[n]$((i_kno_no_in[n]) and sigma.l[n] = 1)..	PwT[n] =E= prod(nn$(map_test_in[nn,n]), PwT[nn]**(mu[nn,n]));
	E_in_d_o[n]$(i_bra_o_in[n])..	qD[n] =E= sum(nn$(map_test_in[n,nn]), mu[n,nn] * (PbT[nn]/PwT[n])**(sigma[nn]) * qS[nn]);
	E_in_d_no[n]$(i_bra_no_in[n])..	qD[n] =E= sum(nn$(map_test_in[n,nn]), mu[n,nn] * (PwT[nn]/PwT[n])**(sigma[nn]) * qD[nn]);
$ENDBLOCK
$BLOCK M_out 
	E_out_p[n]$(i_kno_out[n])..	PwT[n] =E= (sum(nn$(map_test_out[nn,n] and t_out_out[nn]), mu[nn,n] * PbT[nn]**(1-eta[n]))+sum(nn$(map_test_out[nn,n] and not t_out_out[nn]), mu[nn,n] * PwT[nn]**(1-eta[n])))**(1/(1-eta[n]));
	E_out_d_o[n]$(i_bra_o_out[n])..	qS[n] =E= sum(nn$(map_test_out[n,nn]), mu[n,nn] * (PbT[n]/PwT[nn])**(-eta[nn]) * qD[nn]);
	E_out_d_no[n]$(i_bra_no_out[n])..	qD[n] =E= sum(nn$(map_test_out[n,nn]), mu[n,nn] * (PwT[n]/PwT[nn])**(-eta[nn]) * qD[nn]);
$ENDBLOCK