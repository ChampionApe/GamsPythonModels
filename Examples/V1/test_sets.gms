sets
	n
	alias_set
	alias_map2
;

alias(n,nn,nnn);

sets
	int[n]
	t_out_s1_in[n]
	i_bra_no_s1_in[n]
	alias_[alias_set,alias_map2]
	t_out_s1_out[n]
	i_bra_o_s1_in[n]
	kno_inp[n]
	i_bra_no_s1_out[n]
	wT[n]
	kno_out[n]
	i_kno_s1_in[n]
	map_all[n,nn]
	i_kno_no_s1_in[n]
	out[n]
	i_kno_s1_out[n]
	fg[n]
	map_s1_in[n,nn]
	i_bra_o_s1_out[n]
	inp[n]
	map_s1_out[n,nn]
;


$GDXIN %test%
$onMulti
$load n
$load alias_set
$load alias_map2
$load int
$load t_out_s1_in
$load i_bra_no_s1_in
$load t_out_s1_out
$load i_bra_o_s1_in
$load kno_inp
$load i_bra_no_s1_out
$load wT
$load kno_out
$load i_kno_s1_in
$load i_kno_s1_out
$load i_kno_no_s1_in
$load out
$load fg
$load i_bra_o_s1_out
$load inp
$load map_all
$load map_s1_in
$load alias_
$load map_s1_out
$GDXIN
$offMulti
