def equation(name,domains,conditions,LHS,RHS):
	return f"""{name}{domains}{'$('+conditions+')' if conditions != '' else conditions}..	{LHS} =E= {RHS};"""

class V1:
	def __init__(self,version='std',**kwargs):
		self.version = version

	def run(self,vartext,domains,conditions,name):
		if self.version is 'std':
			out = self.unit_cost(f"E_uc_{name}", domains['uc'],conditions['uc'],
				vartext['PwT'],vartext['qD'],vartext['cbar'],vartext['n'],vartext['k2t'])+'\n\t'
		elif self.version is 'Q2P':
			out = self.unit_cost_Q2P(f"E_uc_{name}", domains['uc'],conditions['uc'],
				vartext['PwT'],vartext['qD'],vartext['cbar'],vartext['n'],vartext['k2t'],vartext['q2p'])+'\n\t'
		out += self.current_application(f"E_currapp_{name}", domains['currapp'], conditions['currapp'],
			vartext['qD'],vartext['theta_c'],vartext['n'],vartext['u2c'],vartext['c2e'])+'\n\t'
		out += self.potential_application(f"E_potapp_{name}", domains['potapp'], conditions['potapp'],
			vartext['qD'],vartext['theta_p'],vartext['n'],vartext['c2e'])
		return out

	def unit_cost(self,e_name,domains,conditions,PwT,qD,cbar,n,k2t):
		"""
		Equation for calibration of unit cost of the technology.
		"""
		RHS = f"""{cbar['b']} * sum({n['a_aa']}$({k2t['b']}), {qD['a_aa']}) / {PwT['b']}"""
		return equation(e_name,domains,conditions,qD['b'],RHS)

	def unit_cost_Q2P(self,e_name,domains,conditions,PwT,qD,cbar,n,k2t,q2p):
		RHS = f"""{cbar['b']} * sum({n['a_aa']}$({k2t['b']}), {qD['a_aa']}) / sum({n['a_aaa']}$({q2p['aa_aaa']}),{PwT['a_aaa']})"""
		return equation(e_name,domains,conditions,qD['b'],RHS)


	def current_application(self,e_name,domains,conditions,qD,theta_c,n,u2c,c2e):
		"""
		The share u/E = theta_c. 
		"""
		RHS = f"""{theta_c['b']} * sum({n['a_aa']}$({u2c['b']}), sum({n['a_aaa']}$({c2e['a_aa.aa_aaa']}), {qD['a_aaa']}))"""
		return equation(e_name,domains,conditions,qD['b'],RHS)

	def potential_application(self,e_name,domains,conditions,qD,theta_p,n,c2e):
		RHS = f"""{theta_p['b']} * sum({n['a_aa']}$({c2e['b']}), {qD['a_aa']})"""
		return equation(e_name,domains,conditions,qD['b'],RHS)

