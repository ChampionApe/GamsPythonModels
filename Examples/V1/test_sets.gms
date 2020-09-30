sets
	alias_set
	n
	alias_map2
;

alias(n,nn,nnn);

sets
	t_out_s1_in[n]
	alias_[alias_set,alias_map2]
	kno_out[n]
	i_bra_no_s1_out[n]
	i_bra_o_s1_out[n]
	inp[n]
	map_s1_out[n,nn]
	t_out_s1_out[n]
	i_kno_s1_in[n]
	map_s1_in[n,nn]
	int[n]
	kno_inp[n]
	wT[n]
	i_kno_s1_out[n]
	out[n]
	i_bra_o_s1_in[n]
	fg[n]
	map_all[n,nn]
	i_kno_no_s1_in[n]
	i_bra_no_s1_in[n]
;


$GDXIN %test%
$onMulti
$load alias_set
$load n
$load alias_map2
$load t_out_s1_in
$load kno_out
$load i_bra_o_s1_out
$load fg
$load inp
$load t_out_s1_out
$load i_kno_s1_in
$load int
$load wT
$load kno_inp
$load i_kno_s1_out
$load out
$load i_bra_o_s1_in
$load i_bra_no_s1_out
$load i_kno_no_s1_in
$load i_bra_no_s1_in
$load map_s1_in
$load map_all
$load alias_
$load map_s1_out
$GDXIN
$offMulti
