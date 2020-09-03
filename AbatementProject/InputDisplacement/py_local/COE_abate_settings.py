def afl(x):
	"""
	If no 'l' key is included, add a list of None's the same length as key 'a'.
	"""
	if 'l' in x:
		return x
	else:
		x.update({'l': ['']*len(x['a'])})
		return x

class V1:
	def __init__(self,version='std',**kwargs):
		self.version=version

	@property
	def doms(self):
		return {'uc': 'qD', 'currapp': 'qD', 'potapp': 'qD'}

	@property
	def conds(self):
		return {'uc': 'KT_subset', 'currapp': 'u_subset', 'potapp': 'c_subset'}

	@property
	def vartext(self):
		if self.version is 'std':
			return {'PwT': afl({'a': [None]}),
					'qD' : afl({'a': [None, 'a_aa', 'a_aaa']}),
					'theta_c': afl({'a': [None]}),
					'theta_p': afl({'a': [None]}),
					'cbar': afl({'a': [None]}),
					'n': afl({'a': ['a_aa','a_aaa']}),
					'k2t': afl({'a': [None]}),
					'u2c': afl({'a': [None]}),
					'c2e': afl({'a': [None, ['a_aa','aa_aaa']]})}
		elif self.version is 'Q2P':
			return {'PwT': afl({'a': ['a_aaa']}),
					'qD' : afl({'a': [None, 'a_aa', 'a_aaa']}),
					'theta_c': afl({'a': [None]}),
					'theta_p': afl({'a': [None]}),
					'cbar': afl({'a': [None]}),
					'n': afl({'a': ['a_aa','a_aaa']}),
					'k2t': afl({'a': [None]}),
					'u2c': afl({'a': [None]}),
					'c2e': afl({'a': [None, ['a_aa','aa_aaa']]}),
					'q2p': afl({'a': ['aa_aaa']})
					}
