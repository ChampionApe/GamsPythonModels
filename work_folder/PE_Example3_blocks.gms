$BLOCK M_s1_in 
	E_pindex_o_s1_in[n]$((t_out_s1_in[n]) and sigma.l[n] <> 1)..	PbT[n] =E= sum(nn$(map_s1_in[nn,n]), mu[nn,n] * PwT[nn]**(1-sigma[n]))**(1/(1-sigma[n]));
	E_pindex_no_s1_in[n]$((i_kno_no_s1_in[n]) and sigma.l[n] <> 1)..	PwT[n] =E= sum(nn$(map_s1_in[nn,n]), mu[nn,n] * PwT[nn]**(1-sigma[n]))**(1/(1-sigma[n]));
	E_pindex_CD_o_s1_in[n]$((t_out_s1_in[n]) and sigma.l[n] = 1)..	PbT[n] =E= prod(nn$(map_s1_in[nn,n]), PwT[nn]**(mu[nn,n]));
	E_pindex_CD_no_s1_in[n]$((t_out_s1_in[n]) and sigma.l[n] = 1)..	PwT[n] =E= prod(nn$(map_s1_in[nn,n]), PwT[nn]**(mu[nn,n]));
	E_quant_o_s1_in[n]$(i_bra_o_s1_in[n])..	qD[n] =E= sum(nn$(map_s1_in[n,nn]), mu[n,nn] * (PbT[nn]/PwT[n])**(sigma[nn]) * qS[nn]);
	E_quant_no_s1_in[n]$(i_bra_no_s1_in[n])..	qD[n] =E= sum(nn$(map_s1_in[n,nn]), mu[n,nn] * (PwT[nn]/PwT[n])**(sigma[nn]) * qD[nn]);
$ENDBLOCK
$BLOCK M_s1_out 
	E_pindex_s1_out[n]$(i_kno_s1_out[n])..	PwT[n] =E= (sum(nn$(map_s1_out[nn,n] and out[nn]), mu[nn,n] * PbT[nn]**(1-eta[n]))+sum(nn$(map_s1_out[nn,n] and not out[nn]), mu[nn,n] * PwT[nn]**(1-eta[n])))**(1/(1-eta[n]));
	E_quant_o_s1_out[n]$(i_bra_o_s1_out[n])..	qS[n] =E= sum(nn$(map_s1_out[n,nn]), mu[n,nn] * (PbT[n]/PwT[nn])**(-eta[nn]) * qD[nn]);
	E_quant_no_s1_out[n]$(i_bra_no_s1_out[n])..	qD[n] =E= sum(nn$(map_s1_out[n,nn]), mu[n,nn] * (PwT[n]/PwT[nn])**(-eta[nn]) * qD[nn]);
$ENDBLOCK
