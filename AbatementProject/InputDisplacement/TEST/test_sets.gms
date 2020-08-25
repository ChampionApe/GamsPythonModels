sets
	alias_map2
	n
	alias_set
;

alias(n,nnn,nn);

sets
	kno_inp[n]
	kno_out[n]
	t_fg_out[n]
	inp_test_in[n]
	int[n]
	t_inp_in[n]
	t_int_out[n]
	out_test_out[n]
	i_kno_out[n]
	i_bra_no_in[n]
	t_out_out[n]
	alias_[alias_set,alias_map2]
	i_bra_no_out[n]
	t_out_in[n]
	t_inp_out[n]
	map_test_out[n,nn]
	t_fg_in[n]
	i_bra_o_out[n]
	out[n]
	out_test_in[n]
	inp[n]
	map_all[n,nn]
	t_wT_in[n]
	i_bra_o_in[n]
	i_kno_in[n]
	bra_test_out[n]
	wT[n]
	i_kno_no_in[n]
	inp_test_out[n]
	fg[n]
	t_int_in[n]
	t_wT_out[n]
	bra_test_in[n]
	kno_test_out[n]
	kno_test_in[n]
	map_test_in[n,nn]
;


$GDXIN %test%
$onMulti
$load n
$load alias_map2
$load alias_set
$load kno_inp
$load kno_out
$load t_fg_out
$load inp_test_in
$load int
$load t_inp_in
$load t_int_out
$load out_test_out
$load i_kno_out
$load i_bra_no_in
$load t_out_out
$load i_bra_no_out
$load t_out_in
$load t_inp_out
$load t_fg_in
$load i_bra_o_out
$load out
$load out_test_in
$load inp
$load t_wT_in
$load i_bra_o_in
$load i_kno_in
$load bra_test_out
$load wT
$load i_kno_no_in
$load inp_test_out
$load fg
$load t_int_in
$load t_wT_out
$load bra_test_in
$load kno_test_out
$load kno_test_in
$load alias_
$load map_test_in
$load map_test_out
$load map_all
$GDXIN
$offMulti
