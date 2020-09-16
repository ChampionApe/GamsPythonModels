sets
	alias_map2
	alias_set
	n
;

alias(n,nnn,nn);

sets
	map_s1_in[n,nn]
	t_out_s1_out[n]
	t_out_s1_in[n]
	int[n]
	map_all[n,nn]
	i_kno_no_s1_in[n]
	kno_out[n]
	wT[n]
	fg[n]
	alias_[alias_set,alias_map2]
	inp[n]
	i_bra_o_s1_in[n]
	out[n]
	i_bra_no_s1_out[n]
	kno_inp[n]
	map_s1_out[n,nn]
	i_bra_no_s1_in[n]
	i_bra_o_s1_out[n]
	i_kno_s1_in[n]
	i_kno_s1_out[n]
;


$GDXIN %test%
$onMulti
$load alias_map2
$load alias_set
$load n
$load t_out_s1_out
$load t_out_s1_in
$load int
$load i_kno_no_s1_in
$load kno_out
$load wT
$load fg
$load i_bra_o_s1_in
$load inp
$load i_bra_no_s1_out
$load out
$load kno_inp
$load i_bra_no_s1_in
$load i_bra_o_s1_out
$load i_kno_s1_in
$load i_kno_s1_out
$load map_s1_out
$load map_s1_in
$load alias_
$load map_all
$GDXIN
$offMulti
