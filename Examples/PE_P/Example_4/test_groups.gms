$GROUP test_gtech
	mark_up[n]$((out[n])) ""
	mu[n,nn]$((map_all[n,nn])) ""
	eta[n]$((kno_out[n])) ""
	sigma[n]$((kno_inp[n])) ""
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
@load_fixed(test_gexo ,%qmark%%test%");
@load_fixed(test_gtech,%qmark%%test%");
