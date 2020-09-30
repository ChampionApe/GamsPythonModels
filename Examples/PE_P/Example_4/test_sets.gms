sets
	alias_set
	alias_map2
	n
;

alias(n,nn,nnn);

sets
	i_kno_s1_in[n]
	t_out_s1_in[n]
	wT[n]
	fg[n]
	kno_inp[n]
	out[n]
	i_bra_o_s1_in[n]
	map_s1_in[n,nn]
	i_kno_no_s1_in[n]
	kno_out[n]
	inp[n]
	alias_[alias_set,alias_map2]
	i_bra_no_s1_in[n]
	int[n]
	map_all[n,nn]
;


$GDXIN %test%
$onMulti
$load alias_set
$load alias_map2
$load n
$load i_kno_s1_in
$load t_out_s1_in
$load wT
$load fg
$load kno_inp
$load out
$load i_bra_o_s1_in
$load i_kno_no_s1_in
$load kno_out
$load inp
$load i_bra_no_s1_in
$load int
$load map_all
$load alias_
$load map_s1_in
$GDXIN
$offMulti
