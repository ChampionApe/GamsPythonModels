sets
	alias_set
	n
	alias_map2
;

alias(n,nn,nnn);

sets
	i_kno_s1_out[n]
	i_bra_no_s1_in[n]
	i_kno_s1_in[n]
	int[n]
	inp[n]
	i_bra_o_s1_out[n]
	map_s1_out[n,nn]
	map_s1_in[n,nn]
	map_all[n,nn]
	t_out_s1_in[n]
	i_bra_no_s1_out[n]
	i_bra_o_s1_in[n]
	kno_out[n]
	kno_inp[n]
	t_out_s1_out[n]
	i_kno_no_s1_in[n]
	wT[n]
	alias_[alias_set,alias_map2]
	fg[n]
	out[n]
;


$GDXIN %test%
$onMulti
$load alias_set
$load n
$load alias_map2
$load i_kno_s1_out
$load i_bra_no_s1_in
$load i_kno_s1_in
$load int
$load inp
$load i_bra_o_s1_out
$load t_out_s1_in
$load i_bra_no_s1_out
$load i_bra_o_s1_in
$load kno_out
$load kno_inp
$load t_out_s1_out
$load i_kno_no_s1_in
$load wT
$load fg
$load out
$load alias_
$load map_s1_in
$load map_s1_out
$load map_all
$GDXIN
$offMulti
