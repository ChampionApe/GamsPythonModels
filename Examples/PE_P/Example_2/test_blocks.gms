$BLOCK M_in 
	E_pindex_o_in[n]$((t_out_in[n]) and sigma.l[n] <> 1)..	PbT[n] =E= sum(nn$(map_test_in[nn,n]), mu[nn,n] * sum(nnn$(q2p_in[nn,nnn]), PwT[nnn])**(1-sigma[n]))**(1/(1-sigma[n]));
	E_pindex_no_in[n]$((i_kno_no_in[n]) and sigma.l[n] <> 1)..	PwT[n] =E= sum(nn$(map_test_in[nn,n]), mu[nn,n] * sum(nnn$(q2p_in[nn,nnn]), PwT[nnn])**(1-sigma[n]))**(1/(1-sigma[n]));
	E_pindex_CD_o_in[n]$((t_out_in[n]) and sigma.l[n] = 1)..	PbT[n] =E= prod(nn$(map_test_in[nn,n]), sum(nnn$(q2p_in[nn,nnn]),PwT[nnn])**(mu[nn,n]));
	E_pindex_CD_no_in[n]$((i_kno_no_in[n]) and sigma.l[n] = 1)..	PwT[n] =E= prod(nn$(map_test_in[nn,n]), sum(nnn$(q2p_in[nn,nnn]),PwT[nnn])**(mu[nn,n]));
	E_quant_o_in[n]$(i_bra_o_in[n])..	qD[n] =E= sum(nn$(map_test_in[n,nn]), mu[n,nn] * (PbT[nn]/sum(nnn$(q2p_in[n,nnn]),PwT[nnn]))**(sigma[nn]) * qS[nn]);
	E_quant_no_in[n]$(i_bra_no_in[n])..	qD[n] =E= sum(nn$(map_test_in[n,nn]), mu[n,nn] * (PwT[nn]/sum(nnn$(q2p_in[n,nnn]),PwT[nnn]))**(sigma[nn]) * qD[nn]);
	E_qagg_in[n]$(q2p_agg_in[n])..	qD[n] =E= sum(nn$(q2p_in[n,nn]), qD[nn]);;
$ENDBLOCK
$BLOCK M_out 
	E_pindex_out[n]$(i_kno_out[n])..	PwT[n] =E= (sum(nn$(map_test_out[nn,n] and out[nn]), mu[nn,n] * PbT[nn]**(1-eta[n]))+sum(nn$(map_test_out[nn,n] and not out[nn]), mu[nn,n] * PwT[nn]**(1-eta[n])))**(1/(1-eta[n]));
	E_quant_o_out[n]$(i_bra_o_out[n])..	qS[n] =E= sum(nn$(map_test_out[n,nn]), mu[n,nn] * (PbT[n]/PwT[nn])**(-eta[nn]) * qD[nn]);
	E_quant_no_out[n]$(i_bra_no_out[n])..	qD[n] =E= sum(nn$(map_test_out[n,nn]), mu[n,nn] * (PwT[n]/PwT[nn])**(-eta[nn]) * qD[nn]);
$ENDBLOCK
