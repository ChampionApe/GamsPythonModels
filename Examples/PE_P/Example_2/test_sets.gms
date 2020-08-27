sets
	n
	alias_map2
	alias_set
;

alias(n,nn,nnn);

sets
	t_out_in[n]
	kno_inp[n]
	inp[n]
	i_bra_o_in[n]
	q2p_in[n,nn]
	int[n]
	map_test_in[n,nn]
	i_bra_no_in[n]
	i_bra_no_out[n]
	kno_out[n]
	i_kno_in[n]
	fg[n]
	wT[n]
	alias_[alias_set,alias_map2]
	q2p_agg_in[n]
	map_test_out[n,nn]
	t_out_out[n]
	i_kno_out[n]
	i_kno_no_in[n]
	map_all[n,nn]
	out[n]
	i_bra_o_out[n]
	PwT_dom[n]
;


$GDXIN %test%
$onMulti
$load n
$load alias_map2
$load alias_set
$load t_out_in
$load kno_inp
$load inp
$load i_bra_o_in
$load int
$load kno_out
$load i_bra_no_in
$load i_bra_no_out
$load i_kno_in
$load fg
$load wT
$load q2p_agg_in
$load t_out_out
$load i_kno_out
$load i_kno_no_in
$load out
$load i_bra_o_out
$load PwT_dom
$load map_test_out
$load q2p_in
$load map_test_in
$load map_all
$load alias_
$GDXIN
$offMulti
