sets
	n
	alias_set
	alias_map2
;

alias(n,nn,nnn);

sets
	kno_inp[n]
	i_bra_no_out[n]
	q2p_in[n,nn]
	fg[n]
	alias_[alias_set,alias_map2]
	i_kno_out[n]
	i_bra_o_out[n]
	out[n]
	map_all[n,nn]
	int[n]
	kno_out[n]
	i_bra_no_in[n]
	i_bra_o_in[n]
	map_test_in[n,nn]
	i_kno_in[n]
	t_out_in[n]
	wT[n]
	inp[n]
	i_kno_no_in[n]
	q2p_agg_in[n]
	t_out_out[n]
	PwT_dom[n]
	map_test_out[n,nn]
;


$GDXIN %test%
$onMulti
$load n
$load alias_set
$load alias_map2
$load kno_inp
$load i_bra_no_out
$load fg
$load i_kno_out
$load i_bra_o_out
$load out
$load int
$load i_bra_no_in
$load i_bra_o_in
$load i_kno_in
$load wT
$load t_out_in
$load inp
$load i_kno_no_in
$load q2p_agg_in
$load t_out_out
$load PwT_dom
$load kno_out
$load q2p_in
$load alias_
$load map_test_in
$load map_all
$load map_test_out
$GDXIN
$offMulti
