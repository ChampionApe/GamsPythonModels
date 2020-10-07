sets
	l1
	n
;


sets
	PwT_subset[n]
	qD_subset[n]
	qS_subset[n]
	PbT_subset[n]
;


$GDXIN %shock%
$onMulti
$load l1
$load n
$load PwT_subset
$load qD_subset
$load qS_subset
$load PbT_subset
$GDXIN
$offMulti
 parameters
	qS_loopval[n,l1]
	PbT_loopval[n,l1]
	qD_loopval[n,l1]
	PwT_loopval[n,l1]
;

$GDXIN %shock%
$onMulti
$load qS_loopval
$load PbT_loopval
$load qD_loopval
$load PwT_loopval
$offMulti
 loop( (l1), 	PwT.fx[n]$(PwT_subset[n]) = PwT_loopval[n,l1];
	qS.fx[n]$(qS_subset[n]) = qS_loopval[n,l1];
	PbT.fx[n]$(PbT_subset[n]) = PbT_loopval[n,l1];
	qD.fx[n]$(qD_subset[n]) = qD_loopval[n,l1];


solve test using CNS;

)
		