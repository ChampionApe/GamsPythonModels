sets
	alias_set
	alias_map2
	n
;

alias(n,nn,nnn);

sets
	inp[n]
	map_s1_in[n,nn]
	map_s1_out[n,nn]
	i_kno_s1_out[n]
	map_all[n,nn]
	kno_out[n]
	i_bra_o_s1_out[n]
	exo_mu[n,nn]
	i_bra_no_s1_in[n]
	t_out_s1_out[n]
	i_bra_o_s1_in[n]
	wT[n]
	alias_[alias_set,alias_map2]
	t_out_s1_in[n]
	fg[n]
	i_bra_no_s1_out[n]
	kno_inp[n]
	i_kno_no_s1_in[n]
	int[n]
	endo_PbT[n]
	i_kno_s1_in[n]
	out[n]
;


$GDXIN %test%
$onMulti
$load alias_set
$load alias_map2
$load n
$load inp
$load i_kno_s1_out
$load kno_out
$load i_bra_o_s1_in
$load i_bra_o_s1_out
$load i_bra_no_s1_in
$load t_out_s1_out
$load wT
$load t_out_s1_in
$load i_bra_no_s1_out
$load fg
$load kno_inp
$load i_kno_no_s1_in
$load int
$load endo_PbT
$load i_kno_s1_in
$load out
$load map_s1_in
$load map_s1_out
$load map_all
$load exo_mu
$load alias_
$GDXIN
$offMulti
