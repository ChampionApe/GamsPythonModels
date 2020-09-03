$GROUP abate_gtech
	eta[n]$((kno_out[n])) ""
	mark_up[n]$((out[n])) ""
	sigma[n]$((kno_inp[n])) ""
	mu[n,nn]$((map_all[n,nn])) ""
;

$GROUP abate_gexo 
	PwT[n]$((inp[n])) ""
	qS[n]$((out[n])) ""
;

$GROUP abate_gendo
	PbT[n]$((out[n])) ""
	PwT[n]$((int[n])) ""
	qD[n]$((wT[n])) ""
;

$GROUP abate_g_techcalib
	theta_c[n]$((u_subset[n])) ""
	theta_p[n]$((c_subset[n])) ""
	cbar[n]$((KT_subset[n])) ""
;

$GROUP abate_g_calibendo
	mu[n,nn]$((mu_endo[n,nn])) ""
;

@load_level(abate_gendo,%qmark%%abate%");
@load_level(abate_g_calibendo,%qmark%%abate%");
@load_fixed(abate_gexo ,%qmark%%abate%");
@load_fixed(abate_g_techcalib,%qmark%%abate%");
@load_fixed(abate_gtech,%qmark%%abate%");
