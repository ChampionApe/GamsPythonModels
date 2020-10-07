sets
	n
	alias_map2
	alias_set
;

alias(n,nnn,nn);

sets
	t_out_s1_out[n]
	i_bra_o_s1_in[n]
	kno_inp[n]
	wT[n]
	i_bra_o_s1_out[n]
	i_bra_no_s1_out[n]
	i_bra_no_s1_in[n]
	map_all[n,nn]
	kno_out[n]
	i_kno_s1_out[n]
	map_s1_out[n,nn]
	map_s1_in[n,nn]
	i_kno_s1_in[n]
	i_kno_no_s1_in[n]
	alias_[alias_set,alias_map2]
	int[n]
	t_out_s1_in[n]
	out[n]
	fg[n]
	inp[n]
;


$GDXIN %test%
$onMulti
$load n
$load alias_map2
$load alias_set
$load t_out_s1_out
$load i_bra_o_s1_in
$load kno_inp
$load wT
$load i_bra_o_s1_out
$load i_bra_no_s1_out
$load i_bra_no_s1_in
$load kno_out
$load i_kno_s1_out
$load i_kno_s1_in
$load i_kno_no_s1_in
$load int
$load t_out_s1_in
$load out
$load fg
$load inp
$load map_s1_in
$load map_s1_out
$load map_all
$load alias_
$GDXIN
$offMulti
