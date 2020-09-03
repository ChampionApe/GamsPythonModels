sets
	n
	alias_set
	alias_map2
;

alias(n,nn,nnn);

sets
	inp[n]
	out[n]
	t_out_in[n]
	fg[n]
	i_bra_no_out[n]
	map_all[n,nn]
	kno_out[n]
	alias_[alias_set,alias_map2]
	i_kno_no_in[n]
	kno_inp[n]
	map_test_in[n,nn]
	i_bra_o_out[n]
	i_bra_no_in[n]
	i_kno_in[n]
	i_bra_o_in[n]
	t_out_out[n]
	map_test_out[n,nn]
	wT[n]
	int[n]
	i_kno_out[n]
;


$GDXIN %test%
$onMulti
$load n
$load alias_set
$load alias_map2
$load inp
$load out
$load t_out_in
$load i_bra_no_out
$load wT
$load kno_out
$load i_kno_no_in
$load kno_inp
$load i_bra_o_out
$load i_bra_no_in
$load i_kno_in
$load i_bra_o_in
$load t_out_out
$load fg
$load int
$load i_kno_out
$load map_all
$load alias_
$load map_test_out
$load map_test_in
$GDXIN
$offMulti
