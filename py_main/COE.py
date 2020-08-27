def equation(name,domains,conditions,LHS,RHS):
	return f"""{name}{domains}{'$('+conditions+')' if conditions != '' else conditions}..	{LHS} =E= {RHS};"""

class CES:
	"""
	The class includes various ways of writing price-indices and demand functions for nested CES.
	"""
	def run(self,vartext,domains,conditions,name):
		"""
		Map dictionaries with variables to equations and collect in one string.
		"""
		out  = self.p_index(f"E_pindex_o_{name}", domains['p_index_o'], conditions['p_index_o'],
			vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],output=True)+'\n\t'
		out += self.p_index(f"E_pindex_no_{name}", domains['p_index_no'], conditions['p_index_no'],
			vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],output=False)+'\n\t'
		out += self.p_index_CD(f"E_pindex_CD_o_{name}", domains['p_index_CD_o'], conditions['p_index_CD_o'],
			vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],output=True)+'\n\t'
		out += self.p_index_CD(f"E_pindex_CD_no_{name}", domains['p_index_CD_no'], conditions['p_index_CD_o'],
			vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],output=False)+'\n\t'
		out += self.demand(f"E_quant_o_{name}", domains['quant_o'], conditions['quant_o'],
			vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],output=True)+'\n\t'
		out += self.demand(f"E_quant_no_{name}", domains['quant_no'],conditions['quant_no'],
			vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],output=False)
		return out

	def run_Q2P(self,vartext,domains,conditions,name):
		"""
		Map dictionaries with variables to equations and collect in one string. Version of .run with quantities and prices defined over different, but overlapping sets.
		"""
		out  = self.p_index_Q2P(f"E_pindex_o_{name}", domains['p_index_o'], conditions['p_index_o'],
			vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],vartext['q2p'],output=True)+'\n\t'
		out += self.p_index_Q2P(f"E_pindex_no_{name}", domains['p_index_no'], conditions['p_index_no'],
			vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],vartext['q2p'],output=False)+'\n\t'
		out += self.p_index_Q2P_CD(f"E_pindex_CD_o_{name}", domains['p_index_CD_o'], conditions['p_index_CD_o'],
			vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],vartext['q2p'],output=True)+'\n\t'
		out += self.p_index_Q2P_CD(f"E_pindex_CD_no_{name}", domains['p_index_CD_no'], conditions['p_index_CD_no'],
			vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],vartext['q2p'],output=False)+'\n\t'
		out += self.demand_Q2P(f"E_quant_o_{name}", domains['quant_o'], conditions['quant_o'],
			vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],vartext['q2p'],output=True)+'\n\t'
		out += self.demand_Q2P(f"E_quant_no_{name}", domains['quant_no'],conditions['quant_no'],
			vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],vartext['q2p'],output=False)+'\n\t'
		out += self.Q2P_agg(f"E_qagg_{name}",domains['qagg'],conditions['qagg'],
			vartext['qD'],vartext['n'],vartext['q2p'])
		return out

	def p_index(self,e_name,domains,conditions,PbT,PwT,mu,sigma,n,map_,output=False):
		"""
		Returns CES price index summing only over prices with taxes: Thus suited for standard input-CES type function.
		Note that the condition that sigma!=1 is applied automatically, thus it is not needed in 'conditions'.
		If output=True, the price before taxes (pbt) is returned, and a mark-up is added (if this is not false).
		"""
		RHS = f"""sum({n['a_aa']}$({map_['a_aa.aa_a']}), {mu['a_aa.aa_a']} * {PwT['a_aa']}**(1-{sigma['b']}))**(1/(1-{sigma['b']}))"""
		conditions_w_sigma = f"""({conditions}) and {sigma['b.l']} <> 1"""
		if output is True:
			return equation(e_name,domains,conditions_w_sigma,PbT['b'],RHS)
		else:
			return equation(e_name,domains,conditions_w_sigma,PwT['b'],RHS)


	def p_index_CD(self,e_name,domains,conditions,PbT,PwT,mu,sigma,n,map_,output=False):
		"""
		p_index with cobb-douglas, i.e. when sigma=1. 
		"""
		RHS = f"""prod({n['a_aa']}$({map_['a_aa.aa_a']}), {PwT['a_aa']}**({mu['a_aa.aa_a']}))"""
		conditions_w_sigma = f"""({conditions}) and {sigma['b.l']} = 1"""
		if output is True:
			return equation(e_name,domains,conditions_w_sigma,PbT['b'],RHS)
		else:
			return equation(e_name,domains,conditions_w_sigma,PwT['b'],RHS)

	def p_index_Q2P(self,e_name,domains,conditions,PbT,PwT,mu,sigma,n,map_,q2p,output=False):
		"""
		Price index when prices and quantities are not defined over the same sets.
		Used in the case where a nesting tree includes the 'same' input more than once:
		In quantities these should enter (intermediate types), but prices can be mapped back to input-types.
		"""
		RHS = f"""sum({n['a_aa']}$({map_['a_aa.aa_a']}), {mu['a_aa.aa_a']} * sum({n['a_aaa']}$({q2p['a_aa.aa_aaa']}), {PwT['a_aaa']})**(1-{sigma['b']}))**(1/(1-{sigma['b']}))"""
		conditions_w_sigma = f"""({conditions}) and {sigma['b.l']} <> 1"""
		if output is True:
			return equation(e_name,domains,conditions_w_sigma,PbT['b'],RHS)
		else:
			return equation(e_name,domains,conditions_w_sigma,PwT['b'],RHS)

	def p_index_Q2P_CD(self,e_name,domains,conditions,PbT,PwT,mu,sigma,n,map_,q2p,output=False):
		"""
		p_index with cobb-douglas, i.e. when sigma=1. 
		"""
		RHS = f"""prod({n['a_aa']}$({map_['a_aa.aa_a']}), sum({n['a_aaa']}$({q2p['a_aa.aa_aaa']}),{PwT['a_aaa']})**({mu['a_aa.aa_a']}))"""
		conditions_w_sigma = f"""({conditions}) and {sigma['b.l']} = 1"""
		if output is True:
			return equation(e_name,domains,conditions_w_sigma,PbT['b'],RHS)
		else:
			return equation(e_name,domains,conditions_w_sigma,PwT['b'],RHS)

	def demand(self,e_name,domains,conditions,qS,PbT,qD,PwT,mu,sigma,n,map_,output=False):
		"""
		CES demand function: If output is False, this is demand in a nest with aggregate that is an intermediate/aggregate good and not output.
		In this case the price is PwT, and the quantity is in qD. If output is True, the this is demand in the most-upper nest, and the aggregate 
		is priced before taxes (PbT), and the quantity is the supply qS. 
		"""
		if output is False:
			RHS = f"""sum({n['a_aa']}$({map_['b']}), {mu['b']} * ({PwT['a_aa']}/{PwT['b']})**({sigma['a_aa']}) * {qD['a_aa']})"""
		else:
			RHS = f"""sum({n['a_aa']}$({map_['b']}), {mu['b']} * ({PbT['a_aa']}/{PwT['b']})**({sigma['a_aa']}) * {qS['a_aa']})"""
		return equation(e_name,domains,conditions,qD['b'],RHS)

	def demand_Q2P(self,e_name,domains,conditions,qS,PbT,qD,PwT,mu,sigma,n,map_,q2p,output=False):
		"""
		demand function, with summing over an alias$q2p mapping to indicate that price inputs are defined over different sets than output.
		"""
		if output is False:
			RHS = f"""sum({n['a_aa']}$({map_['b']}), {mu['b']} * ({PwT['a_aa']}/sum({n['a_aaa']}$({q2p['aa_aaa']}),{PwT['a_aaa']}))**({sigma['a_aa']}) * {qD['a_aa']})"""
		else:
			RHS = f"""sum({n['a_aa']}$({map_['b']}), {mu['b']} * ({PbT['a_aa']}/sum({n['a_aaa']}$({q2p['aa_aaa']}),{PwT['a_aaa']}))**({sigma['a_aa']}) * {qS['a_aa']})"""
		return equation(e_name,domains,conditions,qD['b'],RHS)

	def Q2P_agg(self,e_name,domains,conditions,qD,n,q2p):
		"""
		Define demand as sum over q2p terms.
		"""
		return equation(e_name,domains,conditions,qD['b'],sums.ss(n['a_aa'],q2p['b'],qD['a_aa']))

class norm_CES:
	"""
	Normalized version of CES class. NB: Q2P version is not implemented.
	"""

	def run(self,vartext,domains,conditions,name):
		"""
		Map dictionaries with variables to equations and collect in one string.
		"""
		out  = self.p_index(f"E_pindex_o_{name}", domains['p_index_o'], conditions['p_index_o'],
			vartext['PbT'],vartext['PwT'],vartext['qD'],vartext['n'],vartext['map_'],output=True)+'\n\t'
		out += self.p_index(f"E_pindex_no_{name}", domains['p_index_no'], conditions['p_index_no'],
			vartext['PbT'],vartext['PwT'],vartext['qD'],vartext['n'],vartext['map_'],output=False)+'\n\t'
		out += self.demand(f"E_quant_o_{name}", domains['quant_o'], conditions['quant_o'],
			vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],output=True)+'\n\t'
		out += self.demand(f"E_quant_no_{name}", domains['quant_no'],conditions['quant_no'],
			vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['n'],vartext['map_'],output=False)
		return out

	def p_index(self,e_name,domains,conditions,PbT,PwT,qD,n,map_,output=False):
		"""
		Weighted average price index
		"""
		RHS = f"""sum({n['a_aa']}$({map_['a_aa.aa_a']}), {qD['a_aa']}*{PwT['a_aa']})/{qD['b']}"""
		if output is True:
			return equation(e_name,domains,conditions,PbT['b'],RHS)
		else:
			return equation(e_name,domains,conditions,PwT['b'],RHS)

	def demand(self,e_name,domains,conditions,qS,PbT,qD,PwT,mu,sigma,n,map_,output=False):
		"""
		CES-type demand function, normalized such that sum(inputs) = output in optimum.
		"""
		if output is False:
			RHS = f"""sum({n['a_aa']}$({map_['b']}), ({mu['b']} * ({PwT['a_aa']}/{PwT['b']})**({sigma['a_aa']}) * {qD['a_aa']})/sum({n['a_aaa']}$({map_['a_aaa']}), {mu['a_aaa']} *({PwT['a_aa']}/{PwT['a_aaa']})**({sigma['a_aa']})))"""
		else:
			RHS = f"""sum({n['a_aa']}$({map_['b']}), ({mu['b']} * ({PbT['a_aa']}/{PwT['b']})**({sigma['a_aa']}) * {qS['a_aa']})/sum({n['a_aaa']}$({map_['a_aaa']}), {mu['a_aaa']} *({PbT['a_aa']}/{PwT['a_aaa']})**({sigma['a_aa']})))"""
		return equation(e_name,domains,conditions,qD['b'],RHS)


class CET:
	"""
	Similar class as CES functions, however, for output-splits.
	As output splits can take an aggregate, and split into either outputs, intermediate inputs, or a mix. the functions are a bit complicated.
	Essentially, however, this copies the CES functions with two differences: 
		(1) The elasticites are generally negative instead of positive, 
		(2) Sums has to be over both final outputs and others. 
	"""
	def run(self,vartext,domains,conditions,name):
		"""
		Map dictionaries with variables to equations and collect in one string.
		"""
		out = self.p_index(f"E_pindex_{name}", domains['p_index'], conditions['p_index'],
			vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['eta'],vartext['n'],vartext['map_'],vartext['out'])+'\n\t'
		out += self.demand(f"E_quant_o_{name}", domains['quant_o'], conditions['quant_o'],
			vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['eta'],vartext['n'],vartext['map_'],output=True)+'\n\t'
		out += self.demand(f"E_quant_no_{name}", domains['quant_no'], conditions['quant_no'],
			vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['eta'],vartext['n'],vartext['map_'],output=False)
		return out

	def p_index(self,e_name,domains,conditions,PbT,PwT,mu,eta,n,map_,out):
		RHS = f"""(sum({n['a_aa']}$({map_['a_aa.aa_a']} and {out['a_aa']}), {mu['a_aa.aa_a']} * {PbT['a_aa']}**(1-{eta['b']}))+sum({n['a_aa']}$({map_['a_aa.aa_a']} and not {out['a_aa']}), {mu['a_aa.aa_a']} * {PwT['a_aa']}**(1-{eta['b']})))**(1/(1-{eta['b']}))"""
		return equation(e_name,domains,conditions,PwT['b'],RHS)

	def demand(self,e_name,domains,conditions,qS,PbT,qD,PwT,mu,eta,n,map_,output=False):
		if output is False:
			RHS = f"""sum({n['a_aa']}$({map_['b']}), {mu['b']} * ({PwT['b']}/{PwT['a_aa']})**(-{eta['a_aa']}) * {qD['a_aa']})"""
			return equation(e_name,domains,conditions,qD['b'],RHS)
		else:
			RHS = f"""sum({n['a_aa']}$({map_['b']}), {mu['b']} * ({PbT['b']}/{PwT['a_aa']})**(-{eta['a_aa']}) * {qD['a_aa']})"""
			return equation(e_name,domains,conditions,qS['b'],RHS)

class sums:
	"""
	Simple sums.
	"""
	@staticmethod
	def ss(index,conditionals,var_i):
		"""
		Define variable as sum a simple sum over index with conditions.
		"""
		return f"""sum({index}$({conditionals}), {var_i});"""

	@staticmethod
	def ws(index,conditionals,weights,var):
		"""
		Weigthed sum over index with conditionals with weights * var
		"""
		return f"""sum({index}$({conditionals}), {weights}*{var_i})"""

	@staticmethod
	def wa(index,conditionals,wights,var,sumvar):
		"""
		weighted average
		"""
		return f"""({sums.ws(index,conditionals,weights,var)}/{sumvar})"""