$GROUP test_gtech
	eta[n]$((kno_out[n])) ""
	mark_up[n]$((out[n])) ""
	sigma[n]$((kno_inp[n])) ""
	mu[n,nn]$((map_all[n,nn])) ""
;

$GROUP test_gexo 
	PwT[n]$((inp[n])) ""
	qS[n]$((out[n])) ""
;

$GROUP test_gendo
	PbT[n]$((out[n])) ""
	PwT[n]$((int[n])) ""
	qD[n]$((wT[n])) ""
;

@load_level(test_gendo,%qmark%%test%");
@load_fixed(test_gtech,%qmark%%test%");
@load_fixed(test_gexo ,%qmark%%test%");
