$BLOCK M_CES_types 
	E_pindex_o_CES_types[n]$((t_out_CES_types[n]) and sigma.l[n] <> 1)..	PbT[n] =E= sum(nn$(map_CES_types[nn,n]), mu[nn,n] * sum(nnn$(q2p_CES_types[nn,nnn]), PwT[nnn])**(1-sigma[n]))**(1/(1-sigma[n]));
	E_pindex_no_CES_types[n]$((i_kno_no_CES_types[n]) and sigma.l[n] <> 1)..	PwT[n] =E= sum(nn$(map_CES_types[nn,n]), mu[nn,n] * sum(nnn$(q2p_CES_types[nn,nnn]), PwT[nnn])**(1-sigma[n]))**(1/(1-sigma[n]));
	E_pindex_CD_o_CES_types[n]$((t_out_CES_types[n]) and sigma.l[n] = 1)..	PbT[n] =E= prod(nn$(map_CES_types[nn,n]), sum(nnn$(q2p_CES_types[nn,nnn]),PwT[nnn])**(mu[nn,n]));
	E_pindex_CD_no_CES_types[n]$((i_kno_no_CES_types[n]) and sigma.l[n] = 1)..	PwT[n] =E= prod(nn$(map_CES_types[nn,n]), sum(nnn$(q2p_CES_types[nn,nnn]),PwT[nnn])**(mu[nn,n]));
	E_quant_o_CES_types[n]$(i_bra_o_CES_types[n])..	qD[n] =E= sum(nn$(map_CES_types[n,nn]), mu[n,nn] * (PbT[nn]/sum(nnn$(q2p_CES_types[n,nnn]),PwT[nnn]))**(sigma[nn]) * qS[nn]);
	E_quant_no_CES_types[n]$(i_bra_no_CES_types[n])..	qD[n] =E= sum(nn$(map_CES_types[n,nn]), mu[n,nn] * (PwT[nn]/sum(nnn$(q2p_CES_types[n,nnn]),PwT[nnn]))**(sigma[nn]) * qD[nn]);
	E_qagg_CES_types[n]$(q2p_agg_CES_types[n])..	qD[n] =E= sum(nn$(q2p_CES_types[nn,n]), qD[nn]);;
$ENDBLOCK
$BLOCK M_ES 
	E_pindex_o_ES[n]$(t_out_ES[n])..	PbT[n] =E= sum(nn$(map_ES[nn,n]), qD[nn]*PwT[nn])/qS[n];
	E_pindex_no_ES[n]$(i_kno_no_ES[n])..	PwT[n] =E= sum(nn$(map_ES[nn,n]), qD[nn]*PwT[nn])/qD[n];
	E_quant_o_ES[n]$(i_bra_o_ES[n])..	qD[n] =E= sum(nn$(map_ES[n,nn]), (mu[n,nn] * (PbT[nn]/PwT[n])**(sigma[nn]) * qS[nn])/sum(nnn$(map_ES[nnn,nn]), mu[nnn,nn] *(PbT[nn]/PwT[nnn])**(sigma[nn])));
	E_quant_no_ES[n]$(i_bra_no_ES[n])..	qD[n] =E= sum(nn$(map_ES[n,nn]), (mu[n,nn] * (PwT[nn]/PwT[n])**(sigma[nn]) * qD[nn])/sum(nnn$(map_ES[nnn,nn]), mu[nnn,nn] *(PwT[nn]/PwT[nnn])**(sigma[nn])));
$ENDBLOCK
$BLOCK M_ESC 
	E_pindex_o_ESC[n]$(t_out_ESC[n])..	PbT[n] =E= sum(nn$(map_ESC[nn,n]), qD[nn]*PwT[nn])/qS[n];
	E_pindex_no_ESC[n]$(i_kno_no_ESC[n])..	PwT[n] =E= sum(nn$(map_ESC[nn,n]), qD[nn]*PwT[nn])/qD[n];
	E_quant_o_ESC[n]$(i_bra_o_ESC[n])..	qD[n] =E= sum(nn$(map_ESC[n,nn]), mu[n,nn]* exp((PbT[nn]-PwT[n])/sigma[nn])*qS[nn] / sum(nnn$(map_ESC[nnn,nn]), mu[nnn,nn]* exp((PbT[nn]-PwT[nnn])/sigma[nn])));
	E_quant_no_ESC[n]$(i_bra_no_ESC[n])..	qD[n] =E= sum(nn$(map_ESC[n,nn]), mu[n,nn]* exp((PwT[nn]-PwT[n])/sigma[nn])*qD[nn] / sum(nnn$(map_ESC[nnn,nn]), mu[nnn,nn]* exp((PwT[nn]-PwT[nnn])/sigma[nn])));
$ENDBLOCK
$BLOCK M_T_out 
	E_pindex_T_out[n]$(i_kno_T_out[n])..	PwT[n] =E= (sum(nn$(map_T_out[nn,n] and out[nn]), mu[nn,n] * PbT[nn]**(1-eta[n]))+sum(nn$(map_T_out[nn,n] and not out[nn]), mu[nn,n] * PwT[nn]**(1-eta[n])))**(1/(1-eta[n]));
	E_quant_o_T_out[n]$(i_bra_o_T_out[n])..	qS[n] =E= sum(nn$(map_T_out[n,nn]), mu[n,nn] * (PbT[n]/PwT[nn])**(-eta[nn]) * qD[nn]);
	E_quant_no_T_out[n]$(i_bra_no_T_out[n])..	qD[n] =E= sum(nn$(map_T_out[n,nn]), mu[n,nn] * (PwT[n]/PwT[nn])**(-eta[nn]) * qD[nn]);
$ENDBLOCK

 $BLOCK M_calib 
	E_uc_calib[n]$(KT_subset[n])..	qD[n] =E= cbar[n] * sum(nn$(k2t[n,nn]), qD[nn]) / sum(nnn$(q2p[n,nnn]),PwT[nnn]);
	E_currapp_calib[n]$(u_subset[n])..	qD[n] =E= theta_c[n] * sum(nn$(u2c[n,nn]), sum(nnn$(c2e[nn,nnn]), qD[nnn]));
	E_potapp_calib[n]$(c_subset[n])..	qD[n] =E= theta_p[n] * sum(nn$(c2e[n,nn]), qD[nn]);
$ENDBLOCK
