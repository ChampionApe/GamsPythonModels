sets
	alias_map2
	alias_set
	n
;

alias(n,nn,nnn);

sets
	map_test_out[n,nn]
	out_test_out[n]
	kno_inp[n]
	int[n]
	t_fg_in[n]
	kno_test_in[n]
	t_inp_out[n]
	t_int_out[n]
	t_wT_out[n]
	i_bra_no_out[n]
	i_kno_out[n]
	i_kno_in[n]
	fg[n]
	i_bra_o_out[n]
	t_out_in[n]
	t_fg_out[n]
	bra_test_out[n]
	map_test_in[n,nn]
	out[n]
	t_out_out[n]
	out_test_in[n]
	bra_test_in[n]
	inp_test_out[n]
	inp_test_in[n]
	alias_[alias_set,alias_map2]
	t_inp_in[n]
	kno_test_out[n]
	map_all[n,nn]
	t_wT_in[n]
	i_bra_no_in[n]
	i_kno_no_in[n]
	wT[n]
	i_bra_o_in[n]
	t_int_in[n]
	inp[n]
	kno_out[n]
;


$GDXIN %test%
$onMulti
$load alias_map2
$load alias_set
$load n
$load out_test_out
$load kno_inp
$load int
$load t_fg_in
$load kno_test_in
$load t_inp_out
$load t_int_out
$load t_wT_out
$load i_bra_no_out
$load i_kno_out
$load i_kno_in
$load fg
$load i_bra_o_out
$load t_out_in
$load t_fg_out
$load bra_test_out
$load out
$load t_out_out
$load bra_test_in
$load inp_test_out
$load inp_test_in
$load t_inp_in
$load kno_test_out
$load t_wT_in
$load i_bra_no_in
$load i_kno_no_in
$load wT
$load inp
$load i_bra_o_in
$load t_int_in
$load out_test_in
$load kno_out
$load alias_
$load map_test_out
$load map_test_in
$load map_all
$GDXIN
$offMulti
