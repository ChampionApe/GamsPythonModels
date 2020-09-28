sets
	alias_map2
	alias_set
	n
;

alias(n,nnn,nn);

sets
	i_bra_o_s1_out[n]
	i_bra_o_s1_in[n]
	fg[n]
	i_kno_s1_out[n]
	alias_[alias_set,alias_map2]
	int[n]
	i_bra_no_s1_out[n]
	kno_out[n]
	i_bra_no_s1_in[n]
	map_s1_out[n,nn]
	wT[n]
	i_kno_no_s1_in[n]
	inp[n]
	i_kno_s1_in[n]
	kno_inp[n]
	t_out_s1_out[n]
	map_s1_in[n,nn]
	t_out_s1_in[n]
	out[n]
	map_all[n,nn]
;


$GDXIN %test%
$onMulti
$load alias_map2
$load alias_set
$load n
$load i_bra_o_s1_in
$load i_bra_o_s1_out
$load fg
$load i_kno_s1_out
$load int
$load i_bra_no_s1_out
$load kno_out
$load i_bra_no_s1_in
$load out
$load i_kno_no_s1_in
$load inp
$load i_kno_s1_in
$load kno_inp
$load t_out_s1_out
$load t_out_s1_in
$load wT
$load map_s1_in
$load map_all
$load alias_
$load map_s1_out
$GDXIN
$offMulti
