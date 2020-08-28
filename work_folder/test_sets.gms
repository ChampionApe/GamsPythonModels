sets
	alias_map2
	alias_set
	n
;

alias(n,nn,nnn);

sets
	wT[n]
	kno_out[n]
	t_out_out[n]
	i_kno_no_in[n]
	i_bra_no_out[n]
	fg[n]
	i_bra_o_out[n]
	i_kno_out[n]
	i_kno_in[n]
	map_all[n,nn]
	i_bra_no_in[n]
	map_test_out[n,nn]
	kno_inp[n]
	i_bra_o_in[n]
	t_out_in[n]
	map_test_in[n,nn]
	inp[n]
	int[n]
	out[n]
	alias_[alias_set,alias_map2]
;


$GDXIN %test%
$onMulti
$load alias_map2
$load alias_set
$load n
$load wT
$load kno_out
$load t_out_out
$load i_kno_no_in
$load i_bra_no_out
$load fg
$load i_bra_o_out
$load i_kno_out
$load i_kno_in
$load i_bra_no_in
$load kno_inp
$load i_bra_o_in
$load t_out_in
$load inp
$load int
$load out
$load map_all
$load map_test_in
$load map_test_out
$load alias_
$GDXIN
$offMulti
