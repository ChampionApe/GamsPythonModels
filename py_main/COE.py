##### Collection Of Equations (COE): Collection of popular functions used in gams codes #####

class CES:
	def equation(self,return_var,equi_name,domains,conditions,p,q,mu,sigma,inputs,in2aggs,**kwargs):
		if return_var=='price_index':
			return f"""{equi_name}_CD{domains}$({conditions} and {sigma['level']}=1)..	{CES.variable(return_var,p,q,mu,sigma,inputs,in2aggs,type_='CD')}
	{equi_name}{domains}$({conditions} and {sigma['level']} <> 1)..	{CES.variable(return_var,p,q,mu,sigma,inputs,in2aggs)}"""
		elif return_var=='demand':
			return f"""{equi_name}{domains}$({conditions})..	{CES.variable(return_var,p,q,mu,sigma,inputs,in2aggs)}"""

	@staticmethod
	def variable(return_var,p,q,mu,sigma,inputs,in2aggs,type_=None):
		if return_var=='price_index':
			if type_=='CD':
				return CES.price_CD(p['base'],p['alias'],mu['alias'],sigma['base'],in2aggs['alias'],inputs['alias'])
			else:
				return CES.price(p['base'],p['alias'],mu['alias'],sigma['base'],in2aggs['alias'],inputs['alias'])
		elif return_var=='demand':
			return CES.demand(q['base'],q['alias'],p['base'],p['alias'],mu['base'],sigma['alias'],in2aggs['base'],inputs['alias'])

	@staticmethod
	def price(p,p_a,mu_a,sigma,map_a,nn):
		return f"""{p} =E= sum({nn}$({map_a}), {mu_a} * {p_a}**(1-{sigma}))**(1/(1-{sigma}));"""

	@staticmethod
	def price_CD(p,p_a,mu_a,sigma,map_a,nn):
		return f"""{p} =E= prod({nn}$({map_a}), {p_a}**({mu_a}));"""

	@staticmethod
	def demand(q,q_a,p,p_a,mu,sigma_a,map_,nn):
		return f"""{q} =E= sum({nn}$({map_}), {mu}*({p}/{p_a})**(-{sigma_a})*{q_a});"""

class normalized_CES:
	"""
	Collection of normalized CES functions; Note that simply using a negative sigma value implies the CET format here.
	"""
	def equation(self,return_var,equi_name,domains,conditions,p,q,mu,sigma,inputs,in2aggs):
		return f"""{equi_name}{domains}$({conditions})..	{normalized_CES.variable(return_var,p,q,mu,sigma,inputs,in2aggs)}"""

	@staticmethod
	def variable(return_var,p,q,mu,sigma,inputs,in2aggs):
		if return_var=='price_index':
			return normalized_CES.price(q['base'],q['alias'],p['base'],p['alias'],in2aggs['alias'],inputs['alias'])
		elif return_var=='demand':
			return normalized_CES.demand(q['base'],q['alias'],p['base'],p['alias'],p['alias2'],mu['base'],mu['alias2'],sigma['alias'],in2aggs['base'],in2aggs['alias2'],inputs['alias'],inputs['alias2'])

	@staticmethod
	def demand(q,q_a,p,p_a,p_a2,mu,mu_a2,sigma_a,map_,map_a2,nn,nnn):
		return f"""{q} =E= sum({nn}$({map_}), {mu}*({p}/{p_a})**(-{sigma_a})*{q_a}/sum({nnn}$({map_a2}), {mu_a2}*({p_a2}/{p_a})**(-{sigma_a})));"""

	@staticmethod
	def price(q,q_a,p,p_a,map_a,nn):
		return f"""{p} =E= sum({nn}$({map_a}), {q_a}*{p_a})/{q};"""

class MNL:
	"""
	Collection of multinomial-logit-like demand structure. This MNL structure has (-p) as an element.
	Using negative values of sigma implies the appropriate output-split version.
	"""
	def equation(self,return_var,equi_name,domains,conditions,p,q,mu,sigma,inputs,in2aggs):
		return f"""{equi_name}{domains}$({conditions})..	{MNL.variable(return_var,p,q,mu,sigma,inputs,in2aggs)}"""

	@staticmethod
	def variable(return_var,p,q,mu,sigma,inputs,in2aggs):
		if return_var=='price_index':
			return MNL.price(q['base'],q['alias'],p['base'],p['alias'],in2aggs['alias'],inputs['alias'])
		elif return_var=='demand':
			return MNL.demand(q['base'],q['alias'],p['base'],p['alias2'],sigma['alias'],in2aggs['base'],in2aggs['alias2'],inputs['alias'],inputs['alias2'])

	@staticmethod
	def demand(q,q_a,p,p_a2,sigma_a,map_,map_a2,nn,nnn):
		return f"""{q} =E= sum({nn}$({map_}), exp(-{p}/{sigma_a})*{q_a}/sum({nnn}$({map_a2}), exp(-{p_a2}/{sigma_a})));"""

	@staticmethod
	def price(q,q_a,p,p_a,map_a,nn):
		return f"""{p} =E= sum({nn}$({map_a}), {q_a}*{p_a})/{q};"""

class CES_v2:
	"""
	Class of CES functions with prices and quantities defined over overlapping but different set elements.
	"""
	def equation(self,return_var,equi_name,domains,conditions,p,q,mu,sigma,inputs,in2aggs,q2p):
		if return_var=='price_index':
			return f"""{equi_name}_CD{domains}$({conditions} and {sigma['level']}=1)..	{CES_v2.variable(return_var,p,q,mu,sigma,inputs,in2aggs,q2p,type_='CD')}
	{equi_name}{domains}$({conditions} and {sigma['level']} <> 1)..	{CES_v2.variable(return_var,p,q,mu,sigma,inputs,in2aggs,q2p)}"""
		elif return_var=='demand':
			return f"""{equi_name}{domains}$({conditions})..	{CES_v2.variable(return_var,p,q,mu,sigma,inputs,in2aggs,q2p)}"""

	@staticmethod
	def variable(return_var,p,q,mu,sigma,inputs,in2aggs,q2p,type_=None):
		if return_var=='price_index':
			if type_=='CD':
				return CES_v2.price_CD(p['base'],p['alias2'],mu['alias'],sigma['base'],in2aggs['alias'],inputs['alias'],inputs['alias2'],q2p['alias'])
			else:
				return CES_v2.price(p['base'],p['alias2'],mu['alias'],sigma['base'],in2aggs['alias'],inputs['alias'],inputs['alias2'],q2p['alias'])
		elif return_var=='demand':
			return CES_v2.demand_alternative(q['base'],q['alias'],p['alias'],p['alias2'],mu['base'],sigma['alias'],in2aggs['base'],inputs['alias'],inputs['alias2'],q2p['base'])

	@staticmethod
	def price(p,p_a2,mu_a,sigma,map_a,nn,nnn,q2p_a):
		return f"""{p} =E= sum({nn}$({map_a}), {mu_a} * sum({nnn}$({q2p_a}), {p_a2})**(1-{sigma}))**(1/(1-{sigma}));"""

	@staticmethod
	def price_CD(p,p_a2,mu_a,sigma,map_a,nn,nnn,q2p_a):
		return f"""{p} =E= prod({nn}$({map_a}), sum({nnn}$({q2p_a}), {p_a2})**({mu_a}));"""

	@staticmethod
	def demand_alternative(q,q_a,p_a,p_a2,mu,sigma_a,map_,nn,nnn,q2p):
		return f"""{q} =E= sum({nn}$({map_}), {mu}*(sum({nnn}$({q2p}), {p_a2})/{p_a})**(-{sigma_a})*{q_a});"""

class sums:
	"""
	Define a variable as the sum over other variables (w. conditionals).
	"""
	def equation(self,eq_type,equi_name,domains,conditions,var_sum,var_i,i,in2agg):
		return f"""{equi_name}{domains}$({conditions})..	{self.apply_type(eq_type)(equi_name,domains,conditions,var_sum,var_i,i,in2agg)}"""

	def apply_type(self,type_):
		return eval(f"self.{type_}")

	@staticmethod
	def simple_sum(equi_name,domains,conditions,var_sum,var_i,i,in2agg):
		return f"""{var_sum} =E= sum({i}$({in2agg}), {var_i});"""