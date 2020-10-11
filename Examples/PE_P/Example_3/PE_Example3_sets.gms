sets
	alias_map2
	n
	alias_set
;

alias(n,nn,nnn);

sets
	endo_PbT[n]
	alias_[alias_set,alias_map2]
	map_all[n,nn]
	exo_mu[n,nn]
	i_kno_s1_out[n]
	int[n]
	i_bra_o_s1_in[n]
	fg[n]
	i_bra_no_s1_in[n]
	t_out_s1_out[n]
	map_s1_in[n,nn]
	kno_out[n]
	t_out_s1_in[n]
	kno_inp[n]
	i_bra_no_s1_out[n]
	out[n]
	wT[n]
	i_kno_s1_in[n]
	i_kno_no_s1_in[n]
	inp[n]
	i_bra_o_s1_out[n]
	map_s1_out[n,nn]
;


$GDXIN %PE_Example3%
$onMulti
$load alias_map2
$load n
$load alias_set
$load endo_PbT
$load i_kno_s1_out
$load int
$load i_bra_o_s1_in
$load fg
$load i_bra_no_s1_in
$load t_out_s1_out
$load t_out_s1_in
$load kno_out
$load wT
$load out
$load kno_inp
$load i_bra_no_s1_out
$load i_kno_s1_in
$load i_kno_no_s1_in
$load inp
$load i_bra_o_s1_out
$load map_all
$load alias_
$load exo_mu
$load map_s1_out
$load map_s1_in
$GDXIN
$offMulti
