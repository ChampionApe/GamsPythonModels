def equation(name,domains,conditions,LHS,RHS):
	return f"""{name}{domains}{'$('+conditions+')' if conditions != '' else conditions}..	{LHS} =E= {RHS};"""

class CES:
	"""
	The class includes various ways of writing price-indices and demand functions.
	"""
	def p_index(self,e_name,domains,conditions,PbT,PwT,mu,sigma,sets,maps,output=False):
		"""
		Returns CES price index summing only over prices with taxes: Thus suited for standard input-CES type function.
		Note that the condition that sigma!=1 is applied automatically, thus it is not needed in 'conditions'.
		If output=True, the price before taxes (pbt) is returned, and a mark-up is added (if this is not false).
		"""
		RHS = f"""sum({sets['a']}$({maps['a']}), {mu['a']} * {PwT['a']}**(1-{sigma['b']}))**(1/(1-{sigma['b']}))"""
		conditions_w_sigma = f"""({conditions}) and {sigma['l']} <> 1"""
		if output is True:
			return equation(e_name,domains,conditions_w_sigma,PbT['b'],RHS)
		else:
			return equation(e_name,domains,conditions_w_sigma,PwT['b'],RHS)

	def p_index_CD(self,e_name,domains,conditions,PbT,PwT,mu,sigma,sets,maps,output=False):
		"""
		p_index with cobb-douglas, i.e. when sigma=1. 
		"""
		RHS = f"""prod({sets['a']}$({maps['a']}), {PwT['a']}**({mu['a']}))"""
		conditions_w_sigma = f"""({conditions}) and {sigma['l']} = 1"""
		if output is True:
			return equation(e_name,domains,conditions_w_sigma,PbT['b'],RHS)
		else:
			return equation(e_name,domains,conditions_w_sigma,PwT['b'],RHS)

	def p_index_Q2P(self,e_name,domains,conditions,PbT,PwT,mu,sigma,sets,maps,q2p,output=False):
		"""
		Price index when prices and quantities are not defined over the same sets.
		Used in the case where a nesting tree includes the 'same' input more than once:
		In quantities these should enter (intermediate types), but prices can be mapped back to input-types.
		"""
		RHS = f"""sum({sets['a']}$({maps['a']}), {mu['a']} * sum({sets['aa']}$({q2p['a']}), {PwT['aa']})**(1-{sigma['b']}))**(1/(1-{sigma['b']}))"""
		conditions_w_sigma = f"""({conditions}) and {sigma['l']} <> 1"""
		if output is True:
			return equation(e_name,domains,conditions_w_sigma,PbT['b'],RHS)
		else:
			return equation(e_name,domains,conditions_w_sigma,PwT['b'],RHS)

	def p_index_Q2P_CD(self,e_name,domains,conditions,PbT,PwT,mu,sigma,sets,maps,q2p,output=False):
		"""
		p_index with cobb-douglas, i.e. when sigma=1. 
		"""
		RHS = f"""prod({sets['a']}$({maps['a']}), sum({sets['aa']}$({q2p['a']}),{PwT['a']})**({mu['a']}))"""
		conditions_w_sigma = f"""({conditions}) and {sigma['l']} = 1"""
		if output is True:
			return equation(e_name,domains,conditions_w_sigma,PbT['b'],RHS)
		else:
			return equation(e_name,domains,conditions_w_sigma,PwT['b'],RHS)

	def demand(self,e_name,domains,conditions,qS,PbT,qD,PwT,mu,sigma,sets,maps,output=False):
		"""
		CES demand function: If output is False, this is demand in a nest with aggregate that is an intermediate/aggregate good and not output.
		In this case the price is PwT, and the quantity is in qD. If output is True, the this is demand in the most-upper nest, and the aggregate 
		is priced before taxes (PbT), and the quantity is the supply qS. 
		"""
		if output is False:
			RHS = f"""sum({sets['a']}$({maps['b']}), {mu['b']} * ({PwT['a']}/{PwT['b']})**({sigma['a']}) * {qD['a']})"""
		else:
			RHS = f"""sum({sets['a']}$({maps['b']}), {mu['b']} * ({PbT['a']}/{PwT['b']})**({sigma['a']}) * {qS['a']})"""
		return equation(e_name,domains,conditions,qD['b'],RHS)


	def demand_Q2P(self,e_name,domains,conditions,qS,PbT,qD,PwT,mu,sigma,sets,maps,q2p,output=False):
		"""
		demand function, with summing over an alias$q2p mapping to indicate that price inputs are defined over different sets than output.
		"""
		if output is False:
			RHS = f"""sum({sets['a']}$({maps['b']}), {mu['b']} * ({PwT['a']}/sum({sets['aa']}$({q2p['b']}),{PwT['aa']}))**({sigma['a']}) * {qD['a']})"""
		else:
			RHS = f"""sum({sets['a']}$({maps['b']}), {mu['b']} * ({PbT['a']}/sum({sets['aa']}$({q2p['b']}),{PwT['aa']}))**({sigma['a']}) * {qS['a']})"""
		return equation(e_name,domains,conditions,qD['b'],RHS)


class CET:
	"""
	Similar class as CES functions, however, for output-splits.
	As output splits can take an aggregate, and split into either outputs, intermediate inputs, or a mix. the functions are a bit complicated.
	Essentially, however, this copies the CES functions with two differences: 
		(1) The elasticites are generally negative instead of positive, 
		(2) Sums has to be over both final outputs and others. 
	"""
	def p_index(self,e_name,domains,conditions,PbT,PwT,mu,eta,sets,maps,out):
		RHS = f"""(sum({sets['a']}$({maps['a']} and {out['a']}), {mu['a']} * {PbT['a']}**(1-{eta['b']}))+sum({sets['a']}$({maps['a']} and not {out['a']}), {mu['a']} * {PwT['a']}**(1-{eta['b']})))**(1/(1-{eta['b']}))"""
		return equation(e_name,domains,conditions,PwT['b'],RHS)

	def p_index_Q2P(self,e_name,domains,conditions,PbT,PwT,mu,eta,sets,maps,out,q2p):
		RHS = f"""(sum({sets['a']}$({maps['a']} and {out['a']}), {mu['a']} * sum({sets['aa']}$({q2p['a']}), {PbT['aa']})**(1-{eta['b']}))+sum({sets['a']}$({maps['a']} and not {out['a']}), {mu['a']} * sum({sets['aa']}$({q2p['a']}), {PwT['aa']})**(1-{eta['b']})))"""
		return equation(e_name,domains,conditions,PwT['b'],RHS)

	def demand(self,e_name,domains,conditions,qS,PbT,qD,PwT,mu,eta,sets,maps,output=False):
		if output is False:
			RHS = f"""sum({sets['a']}$({maps['b']}), {mu['b']} * ({PwT['b']}/{PwT['a']})**(-{eta['a']}) * {qD['a']})"""
			return equation(e_name,domains,conditions,qD['b'],RHS)
		else:
			RHS = f"""sum({sets['a']}$({maps['b']}), {mu['b']} * ({PbT['b']}/{PwT['a']})**(-{eta['a']}) * {qD['a']})"""
			return equation(e_name,domains,conditions,qS['b'],RHS)

	def demand_Q2P(self,e_name,domains,conditions,qS,PbT,qD,PwT,mu,eta,sets,maps,q2p,output=False):
		if output is False:
			RHS = f"""sum({sets['a']}$({maps['b']}), {mu['b']} * (sum({sets['aa']}$({q2p['b']}), {PwT['aa']})/{PwT['a']})**(-{eta['a']}) * {qD['a']})"""
			return equation(e_name,domains,conditions,qD['b'],RHS)
		else:
			RHS = f"""sum({sets['a']}$({maps['b']}), {mu['b']} * (sum({sets['aa']}$({q2p['b']}), {PbT['aa']})/{PwT['a']})**(-{eta['a']}) * {qD['a']})"""
			return equation(e_name,domains,conditions,qS['b'],RHS)


# class normalized_CES:
# 	"""
# 	Collection of normalized CES functions; Note that simply using a negative sigma value implies the CET format here.
# 	"""
# 	def equation(self,return_var,equi_name,domains,conditions,p,q,mu,sigma,inputs,in2aggs):
# 		return f"""{equi_name}{domains}$({conditions})..	{normalized_CES.variable(return_var,p,q,mu,sigma,inputs,in2aggs)}"""

# 	@staticmethod
# 	def variable(return_var,p,q,mu,sigma,inputs,in2aggs):
# 		if return_var=='price_index':
# 			return normalized_CES.price(q['base'],q['alias'],p['base'],p['alias'],in2aggs['alias'],inputs['alias'])
# 		elif return_var=='demand':
# 			return normalized_CES.demand(q['base'],q['alias'],p['base'],p['alias'],p['alias2'],mu['base'],mu['alias2'],sigma['alias'],in2aggs['base'],in2aggs['alias2'],inputs['alias'],inputs['alias2'])

# 	@staticmethod
# 	def demand(q,q_a,p,p_a,p_a2,mu,mu_a2,sigma_a,map_,map_a2,nn,nnn):
# 		return f"""{q} =E= sum({nn}$({map_}), {mu}*({p}/{p_a})**(-{sigma_a})*{q_a}/sum({nnn}$({map_a2}), {mu_a2}*({p_a2}/{p_a})**(-{sigma_a})));"""

# 	@staticmethod
# 	def price(q,q_a,p,p_a,map_a,nn):
# 		return f"""{p} =E= sum({nn}$({map_a}), {q_a}*{p_a})/{q};"""

# class MNL:
# 	"""
# 	Collection of multinomial-logit-like demand structure. This MNL structure has (-p) as an element.
# 	Using negative values of sigma implies the appropriate output-split version.
# 	"""
# 	def equation(self,return_var,equi_name,domains,conditions,p,q,mu,sigma,inputs,in2aggs):
# 		return f"""{equi_name}{domains}$({conditions})..	{MNL.variable(return_var,p,q,mu,sigma,inputs,in2aggs)}"""

# 	@staticmethod
# 	def variable(return_var,p,q,mu,sigma,inputs,in2aggs):
# 		if return_var=='price_index':
# 			return MNL.price(q['base'],q['alias'],p['base'],p['alias'],in2aggs['alias'],inputs['alias'])
# 		elif return_var=='demand':
# 			return MNL.demand(q['base'],q['alias'],p['base'],p['alias2'],sigma['alias'],in2aggs['base'],in2aggs['alias2'],inputs['alias'],inputs['alias2'])

# 	@staticmethod
# 	def demand(q,q_a,p,p_a2,sigma_a,map_,map_a2,nn,nnn):
# 		return f"""{q} =E= sum({nn}$({map_}), exp(-{p}/{sigma_a})*{q_a}/sum({nnn}$({map_a2}), exp(-{p_a2}/{sigma_a})));"""

# 	@staticmethod
# 	def price(q,q_a,p,p_a,map_a,nn):
# 		return f"""{p} =E= sum({nn}$({map_a}), {q_a}*{p_a})/{q};"""

# class CES_v2:
# 	"""
# 	Class of CES functions with prices and quantities defined over overlapping but different set elements.
# 	"""
# 	def equation(self,return_var,equi_name,domains,conditions,p,q,mu,sigma,inputs,in2aggs,q2p):
# 		if return_var=='price_index':
# 			return f"""{equi_name}_CD{domains}$({conditions} and {sigma['level']}=1)..	{CES_v2.variable(return_var,p,q,mu,sigma,inputs,in2aggs,q2p,type_='CD')}
# 	{equi_name}{domains}$({conditions} and {sigma['level']} <> 1)..	{CES_v2.variable(return_var,p,q,mu,sigma,inputs,in2aggs,q2p)}"""
# 		elif return_var=='demand':
# 			return f"""{equi_name}{domains}$({conditions})..	{CES_v2.variable(return_var,p,q,mu,sigma,inputs,in2aggs,q2p)}"""

# 	@staticmethod
# 	def variable(return_var,p,q,mu,sigma,inputs,in2aggs,q2p,type_=None):
# 		if return_var=='price_index':
# 			if type_=='CD':
# 				return CES_v2.price_CD(p['base'],p['alias2'],mu['alias'],sigma['base'],in2aggs['alias'],inputs['alias'],inputs['alias2'],q2p['alias'])
# 			else:
# 				return CES_v2.price(p['base'],p['alias2'],mu['alias'],sigma['base'],in2aggs['alias'],inputs['alias'],inputs['alias2'],q2p['alias'])
# 		elif return_var=='demand':
# 			return CES_v2.demand_alternative(q['base'],q['alias'],p['alias'],p['alias2'],mu['base'],sigma['alias'],in2aggs['base'],inputs['alias'],inputs['alias2'],q2p['base'])

# 	@staticmethod
# 	def price(p,p_a2,mu_a,sigma,map_a,nn,nnn,q2p_a):
# 		return f"""{p} =E= sum({nn}$({map_a}), {mu_a} * sum({nnn}$({q2p_a}), {p_a2})**(1-{sigma}))**(1/(1-{sigma}));"""

# 	@staticmethod
# 	def price_CD(p,p_a2,mu_a,sigma,map_a,nn,nnn,q2p_a):
# 		return f"""{p} =E= prod({nn}$({map_a}), sum({nnn}$({q2p_a}), {p_a2})**({mu_a}));"""

# 	@staticmethod
# 	def demand_alternative(q,q_a,p_a,p_a2,mu,sigma_a,map_,nn,nnn,q2p):
# 		return f"""{q} =E= sum({nn}$({map_}), {mu}*(sum({nnn}$({q2p}), {p_a2})/{p_a})**(-{sigma_a})*{q_a});"""

# class sums:
# 	"""
# 	Define a variable as the sum over other variables (w. conditionals).
# 	"""
# 	def equation(self,eq_type,equi_name,domains,conditions,var_sum,var_i,i,in2agg):
# 		return f"""{equi_name}{domains}$({conditions})..	{self.apply_type(eq_type)(equi_name,domains,conditions,var_sum,var_i,i,in2agg)}"""

# 	def apply_type(self,type_):
# 		return eval(f"self.{type_}")

# 	@staticmethod
# 	def simple_sum(equi_name,domains,conditions,var_sum,var_i,i,in2agg):
# 		return f"""{var_sum} =E= sum({i}$({in2agg}), {var_i});"""