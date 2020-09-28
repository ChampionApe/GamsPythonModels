sets
	n
	alias_map2
	alias_set
;

alias(n,nn,nnn);

sets
	t_out_s1_in[n]
	map_all[n,nn]
	inp[n]
	wT[n]
	i_kno_s1_out[n]
	i_bra_no_s1_in[n]
	i_kno_no_s1_in[n]
	i_kno_s1_in[n]
	int[n]
	i_bra_no_s1_out[n]
	i_bra_o_s1_out[n]
	fg[n]
	kno_out[n]
	kno_inp[n]
	map_s1_out[n,nn]
	t_out_s1_out[n]
	map_s1_in[n,nn]
	alias_[alias_set,alias_map2]
	i_bra_o_s1_in[n]
	out[n]
;


$GDXIN %test%
$onMulti
$load n
$load alias_map2
$load alias_set
$load t_out_s1_in
$load inp
$load wT
$load i_kno_s1_out
$load i_bra_no_s1_in
$load i_kno_no_s1_in
$load i_kno_s1_in
$load int
$load i_bra_no_s1_out
$load i_bra_o_s1_out
$load fg
$load kno_out
$load kno_inp
$load t_out_s1_out
$load i_bra_o_s1_in
$load out
$load alias_
$load map_s1_out
$load map_all
$load map_s1_in
$GDXIN
$offMulti
