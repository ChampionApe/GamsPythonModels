
			qS.fx[n]$(out[n]) = qS.l[n];
			qD.fx[n]$(inp[n]) = qD.l[n];
			mu.lo[n,nn]$(map_all[n,nn] and (inp[n] or out[n])) = 0;
			mu.up[n,nn]$(map_all[n,nn] and (inp[n] or out[n])) = inf;
			PbT.fx[n]$(out[n]) = PbT.l[n];
			mu.fx[n,nn]$(exo_mu[n,nn]) = mu.l[n,nn];
			PbT.lo[n]$(endo_PbT[n]) = -inf;
			PbT.up[n]$(endo_PbT[n]) = inf;
			solve PE_Example3 using CNS;
			PE_Example3_modelstat = PE_Example3.modelstat; PE_Example3_solvestat = PE_Example3.solvestat;