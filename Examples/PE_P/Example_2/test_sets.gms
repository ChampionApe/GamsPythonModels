sets
	n
	alias_map2
	alias_set
;

alias(n,nn,nnn);

sets
	q2p_agg_in[n]
	t_out_in[n]
	int[n]
	i_kno_out[n]
	i_bra_o_in[n]
	alias_[alias_set,alias_map2]
	out[n]
	kno_inp[n]
	i_bra_o_out[n]
	i_bra_no_in[n]
	i_kno_in[n]
	t_out_out[n]
	inp[n]
	wT[n]
	PwT_dom[n]
	map_test_in[n,nn]
	map_test_out[n,nn]
	kno_out[n]
	q2p_in[n,nn]
	map_all[n,nn]
	i_bra_no_out[n]
	i_kno_no_in[n]
	fg[n]
;


$GDXIN %test%
$onMulti
$load n
$load alias_map2
$load alias_set
$load q2p_agg_in
$load t_out_in
$load int
$load i_kno_out
$load i_bra_o_in
$load out
$load kno_inp
$load i_kno_in
$load i_bra_no_in
$load t_out_out
$load i_bra_o_out
$load inp
$load wT
$load PwT_dom
$load kno_out
$load i_bra_no_out
$load i_kno_no_in
$load fg
$load alias_
$load map_test_out
$load q2p_in
$load map_all
$load map_test_in
$GDXIN
$offMulti
