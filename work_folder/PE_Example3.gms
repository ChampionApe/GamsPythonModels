sets
	n
	l1
;


sets
	qS_subset[n]
	qD_subset[n]
	PbT_subset[n]
	PwT_subset[n]
;


$GDXIN %shock%
$onMulti
$load n
$load l1
$load qS_subset
$load qD_subset
$load PbT_subset
$load PwT_subset
$GDXIN
$offMulti
 parameters
	PwT_loopval[n,l1]
	qS_loopval[n,l1]
	qD_loopval[n,l1]
	PbT_loopval[n,l1]
;

$GDXIN %shock%
$onMulti
$load PwT_loopval
$load qS_loopval
$load qD_loopval
$load PbT_loopval
$offMulti
 loop( (l1), 	PwT.fx[n]$(PwT_subset[n]) = PwT_loopval[n,l1];
	qS.fx[n]$(qS_subset[n]) = qS_loopval[n,l1];
	PbT.fx[n]$(PbT_subset[n]) = PbT_loopval[n,l1];
	qD.fx[n]$(qD_subset[n]) = qD_loopval[n,l1];


solve PE_Example3 using CNS;

)
		