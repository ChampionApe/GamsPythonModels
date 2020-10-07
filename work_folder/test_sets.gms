sets
	n
	alias_set
	alias_map2
;

alias(n,nnn,nn);

sets
	endo_PbT[n]
	wT[n]
	i_kno_s1_in[n]
	i_bra_no_s1_out[n]
	i_kno_s1_out[n]
	i_kno_no_s1_in[n]
	alias_[alias_set,alias_map2]
	i_bra_no_s1_in[n]
	t_out_s1_out[n]
	map_s1_out[n,nn]
	fg[n]
	exo_mu[n,nn]
	t_out_s1_in[n]
	map_s1_in[n,nn]
	inp[n]
	kno_inp[n]
	out[n]
	kno_out[n]
	i_bra_o_s1_in[n]
	map_all[n,nn]
	int[n]
	i_bra_o_s1_out[n]
;


$GDXIN %test%
$onMulti
$load n
$load alias_set
$load alias_map2
$load endo_PbT
$load wT
$load i_kno_s1_in
$load i_bra_no_s1_out
$load i_kno_s1_out
$load i_kno_no_s1_in
$load i_bra_no_s1_in
$load t_out_s1_out
$load fg
$load t_out_s1_in
$load inp
$load kno_inp
$load out
$load kno_out
$load i_bra_o_s1_in
$load int
$load i_bra_o_s1_out
$load exo_mu
$load map_s1_in
$load alias_
$load map_all
$load map_s1_out
$GDXIN
$offMulti
