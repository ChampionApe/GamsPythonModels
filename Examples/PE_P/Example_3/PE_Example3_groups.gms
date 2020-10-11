$GROUP PE_Example3_gtech
	mu[n,nn]$((map_all[n,nn])) ""
	sigma[n]$((kno_inp[n])) ""
	mark_up[n]$((out[n])) ""
	eta[n]$((kno_out[n])) ""
;

$GROUP PE_Example3_gexo 
	PwT[n]$((inp[n])) ""
	qS[n]$((out[n])) ""
;

$GROUP PE_Example3_gendo
	PbT[n]$((out[n])) ""
	PwT[n]$((int[n])) ""
	qD[n]$((wT[n])) ""
;

@load_level(PE_Example3_gendo,%qmark%%PE_Example3%");
@load_fixed(PE_Example3_gtech,%qmark%%PE_Example3%");
@load_fixed(PE_Example3_gexo ,%qmark%%PE_Example3%");
