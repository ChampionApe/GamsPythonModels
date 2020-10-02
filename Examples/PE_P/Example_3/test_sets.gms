sets
	alias_set
	alias_map2
	n
;

alias(n,nnn,nn);

sets
	fg[n]
	i_bra_no_s1_out[n]
	t_out_s1_in[n]
	t_out_s1_out[n]
	i_kno_no_s1_in[n]
	out[n]
	wT[n]
	alias_[alias_set,alias_map2]
	kno_inp[n]
	i_kno_s1_in[n]
	i_kno_s1_out[n]
	int[n]
	map_all[n,nn]
	map_s1_in[n,nn]
	i_bra_no_s1_in[n]
	kno_out[n]
	map_s1_out[n,nn]
	i_bra_o_s1_out[n]
	inp[n]
	i_bra_o_s1_in[n]
;


$GDXIN %test%
$onMulti
$load alias_set
$load alias_map2
$load n
$load fg
$load i_bra_no_s1_out
$load t_out_s1_in
$load t_out_s1_out
$load i_kno_no_s1_in
$load out
$load wT
$load kno_inp
$load i_kno_s1_in
$load i_kno_s1_out
$load int
$load i_bra_no_s1_in
$load kno_out
$load i_bra_o_s1_out
$load inp
$load i_bra_o_s1_in
$load map_all
$load alias_
$load map_s1_out
$load map_s1_in
$GDXIN
$offMulti
