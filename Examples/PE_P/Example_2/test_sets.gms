sets
	alias_set
	n
	alias_map2
;

alias(n,nn,nnn);

sets
	i_bra_o_out[n]
	i_bra_o_in[n]
	map_all[n,nn]
	i_bra_no_in[n]
	out[n]
	q2p_in[n,nn]
	inp[n]
	i_kno_no_in[n]
	map_test_in[n,nn]
	i_bra_no_out[n]
	i_kno_in[n]
	map_test_out[n,nn]
	alias_[alias_set,alias_map2]
	fg[n]
	PwT_dom[n]
	t_out_in[n]
	q2p_agg_in[n]
	i_kno_out[n]
	int[n]
	wT[n]
	t_out_out[n]
	kno_out[n]
	kno_inp[n]
;


$GDXIN %test%
$onMulti
$load alias_set
$load n
$load alias_map2
$load i_bra_o_out
$load i_bra_o_in
$load i_bra_no_in
$load out
$load inp
$load i_kno_no_in
$load i_bra_no_out
$load i_kno_in
$load fg
$load PwT_dom
$load t_out_in
$load q2p_agg_in
$load i_kno_out
$load int
$load wT
$load t_out_out
$load kno_out
$load kno_inp
$load map_test_out
$load map_all
$load alias_
$load q2p_in
$load map_test_in
$GDXIN
$offMulti
