sets
	n
	alias_set
	alias_map2
;

alias(n,nnn,nn);

sets
	out[n]
	kno_inp[n]
	i_kno_in[n]
	inp[n]
	i_bra_no_out[n]
	wT[n]
	i_kno_no_in[n]
	i_kno_out[n]
	map_test_in[n,nn]
	i_bra_o_out[n]
	map_all[n,nn]
	t_out_in[n]
	int[n]
	alias_[alias_set,alias_map2]
	i_bra_o_in[n]
	map_test_out[n,nn]
	i_bra_no_in[n]
	kno_out[n]
	fg[n]
	t_out_out[n]
;


$GDXIN %test%
$onMulti
$load n
$load alias_set
$load alias_map2
$load out
$load kno_inp
$load i_kno_in
$load inp
$load i_bra_no_out
$load wT
$load i_kno_no_in
$load i_kno_out
$load t_out_in
$load i_bra_o_out
$load int
$load i_bra_o_in
$load i_bra_no_in
$load t_out_out
$load fg
$load kno_out
$load alias_
$load map_all
$load map_test_in
$load map_test_out
$GDXIN
$offMulti
