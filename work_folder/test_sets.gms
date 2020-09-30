sets
	alias_map2
	n
	alias_set
;

alias(n,nn,nnn);

sets
	kno_inp[n]
	t_out_s1_in[n]
	i_kno_no_s1_in[n]
	i_bra_no_s1_out[n]
	map_s1_out[n,nn]
	fg[n]
	map_s1_in[n,nn]
	map_all[n,nn]
	i_kno_s1_out[n]
	i_bra_o_s1_out[n]
	t_out_s1_out[n]
	inp[n]
	out[n]
	i_kno_s1_in[n]
	int[n]
	i_bra_o_s1_in[n]
	alias_[alias_set,alias_map2]
	kno_out[n]
	wT[n]
	i_bra_no_s1_in[n]
;


$GDXIN %test%
$onMulti
$load alias_map2
$load n
$load alias_set
$load kno_inp
$load t_out_s1_in
$load i_kno_no_s1_in
$load i_bra_no_s1_out
$load fg
$load i_kno_s1_out
$load i_bra_o_s1_out
$load t_out_s1_out
$load inp
$load out
$load i_kno_s1_in
$load int
$load i_bra_o_s1_in
$load kno_out
$load wT
$load i_bra_no_s1_in
$load map_s1_in
$load map_all
$load map_s1_out
$load alias_
$GDXIN
$offMulti
