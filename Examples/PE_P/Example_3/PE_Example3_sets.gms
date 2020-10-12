sets
	alias_set
	alias_map2
	n
;

alias(n,nnn,nn);

sets
	i_bra_no_s1_in[n]
	exo_mu[n,nn]
	int[n]
	kno_inp[n]
	inp[n]
	alias_[alias_set,alias_map2]
	t_out_s1_out[n]
	map_all[n,nn]
	t_out_s1_in[n]
	out[n]
	i_bra_no_s1_out[n]
	wT[n]
	map_s1_in[n,nn]
	i_bra_o_s1_in[n]
	i_kno_no_s1_in[n]
	i_bra_o_s1_out[n]
	i_kno_s1_in[n]
	i_kno_s1_out[n]
	fg[n]
	map_s1_out[n,nn]
	endo_PbT[n]
	kno_out[n]
;


$GDXIN %PE_Example3%
$onMulti
$load alias_set
$load alias_map2
$load n
$load i_bra_no_s1_in
$load int
$load kno_inp
$load inp
$load t_out_s1_in
$load fg
$load out
$load i_bra_no_s1_out
$load i_bra_o_s1_in
$load i_kno_no_s1_in
$load i_bra_o_s1_out
$load kno_out
$load i_kno_s1_in
$load i_kno_s1_out
$load wT
$load endo_PbT
$load t_out_s1_out
$load exo_mu
$load alias_
$load map_s1_in
$load map_s1_out
$load map_all
$GDXIN
$offMulti
