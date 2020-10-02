sets
	n
	alias_map2
	alias_set
;

alias(n,nn,nnn);

sets
	kno_out[n]
	i_bra_o_s1_in[n]
	fg[n]
	wT[n]
	out[n]
	inp[n]
	map_all[n,nn]
	kno_inp[n]
	alias_[alias_set,alias_map2]
	i_kno_s1_in[n]
	map_s1_in[n,nn]
	i_kno_no_s1_in[n]
	int[n]
	t_out_s1_in[n]
	i_bra_no_s1_in[n]
;


$GDXIN %test%
$onMulti
$load n
$load alias_map2
$load alias_set
$load kno_out
$load i_bra_o_s1_in
$load wT
$load fg
$load out
$load inp
$load kno_inp
$load i_kno_s1_in
$load i_kno_no_s1_in
$load int
$load t_out_s1_in
$load i_bra_no_s1_in
$load map_all
$load map_s1_in
$load alias_
$GDXIN
$offMulti
