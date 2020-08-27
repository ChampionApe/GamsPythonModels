def afl(x):
	"""
	If no 'l' key is included, add a list of None's the same length as key 'a'.
	"""
	if 'l' in x:
		return x
	else:
		x.update({'l': ['']*len(x['a'])})
		return x

class CES:
	"""
	Simple collection of information on CES class.
	Keys = equations in corresponding COE class.
	Values = relevant attribute in ModelFrame_PE.production module. 
		In 'doms' the attribute is a variable name that shares domains with the equation.
		In 'conds' the attribute is a name of a subset that the equation is conditioned on ($-condition).
	In 'vartext' the key-value pairs are:
		Key = Name of variable.
		Value = list of strings with 'alias' settings. See the 'alias' function under the production module for more.
	"""
	def __init__(self,version='std',**kwargs):
		self.version=version

	@property
	def doms(self):
		if self.version is 'std':
			return {'p_index_o': 'PbT', 'p_index_no': 'PwT','p_index_CD_o':'PbT','p_index_CD_no': 'PwT','quant_o': 'qD','quant_no':'qD'}
		elif self.version is 'Q2P':
			return {'p_index_o': 'PbT', 'p_index_no': 'PwT','p_index_CD_o':'PbT','p_index_CD_no': 'PwT','quant_o': 'qD','quant_no':'qD','qagg': 'qD'}

	@property 
	def conds(self):
		if self.version is 'std':
			return {'p_index_o': 'tree_out', 'p_index_no': 'i_tree_kno_no', 'p_index_CD_o': 'tree_out', 'p_index_CD_no': 'i_tree_kno_no','quant_o': 'i_tree_bra_o','quant_no': 'i_tree_bra_no'}
		elif self.version is 'Q2P':
			return {'p_index_o': 'tree_out', 'p_index_no': 'i_tree_kno_no', 'p_index_CD_o': 'tree_out', 'p_index_CD_no': 'i_tree_kno_no','quant_o': 'i_tree_bra_o','quant_no': 'i_tree_bra_no','qagg': 'q2p_agg'}

	@property
	def vartext(self):
		"""
		Define the variables needed in the module. For each variable:
			'a': adds an alias-specification. The following convention is used:
				- None: No alias is applied.
				- 'a_aa': Whenever a enters in the domains of the variable, it is swapped with aa.
				- ['a_aa','aa_n']: 'a' is swapped for 'aa', and vice versa. 
			'l': is added in the end to the string.
				- l = '.l' adds the level attribute to the string for the given variable.
				- If no 'l' key is specified, the afl function adds empty strings as a default.
		"""
		if self.version is 'std':
			return {'PbT': afl({'a': [None, 'a_aa']}),
					'PwT': afl({'a': [None, 'a_aa']}),
					'qS' : afl({'a': ['a_aa']}),
					'qD' : afl({'a': [None, 'a_aa']}),
					'mu' : afl({'a': [None, ['a_aa','aa_a']]}),
					'sigma': afl({'a': [None,'a_aa',None], 'l': ['','','.l']}),
					'map_': afl({'a': [None,['a_aa','aa_a']]}),
					'n'  : afl({'a': ['a_aa']})}
		elif self.version is 'Q2P':
			return {'PbT': afl({'a': [None, 'a_aa']}),
					'PwT': afl({'a': [None, 'a_aa','a_aaa']}),
					'qS' : afl({'a': ['a_aa']}),
					'qD' : afl({'a': [None, 'a_aa']}),
					'mu' : afl({'a': [None, ['a_aa','aa_a']]}),
					'sigma': afl({'a': [None,'a_aa',None], 'l': ['','','.l']}),
					'map_': afl({'a': [None,['a_aa','aa_a']]}),
					'n'  : afl({'a': ['a_aa','a_aaa']}),
					'q2p': afl({'a': [None,['a_aa','aa_aaa'], 'aa_aaa']})}

class CET:
	"""
	Similar to CES class.
	"""
	def __init__(self,version='std',**kwargs):
		self.version=version

	@property
	def doms(self):
		return {'p_index': 'PwT', 'quant_o': 'qD', 'quant_no': 'qD'}

	@property 
	def conds(self):
		return {'p_index': 'i_tree_kno', 'quant_o': 'i_tree_bra_o', 'quant_no': 'i_tree_bra_no'}

	@property
	def vartext(self):
		return {'PbT': afl({'a': [None, 'a_aa']}),
				'PwT': afl({'a': [None, 'a_aa']}),
				'qS' : afl({'a': [None]}),
				'qD' : afl({'a': [None, 'a_aa']}),
				'mu' : afl({'a': [None, ['a_aa','aa_a']]}),
				'eta': afl({'a': [None, 'a_aa']}),
				'map_': afl({'a':[None, ['a_aa','aa_a']]}),
				'n'  : afl({'a': ['a_aa']}),
				'out': afl({'a': ['a_aa']})
				}

class norm_CES:
	"""
	Similar to CES class (normalized such that sum of inputs = output). Note: Q2P version is not implemented.
	"""
	def __init__(self,version='std',**kwargs):
		self.version = version
		if version is 'Q2P':
			raise TypeError('Q2P version not yet implemented with norm_CES')

	@property 
	def doms(self):
		if self.version is 'std':
			return {'p_index_o': 'PbT', 'p_index_no': 'PwT', 'quant_o': 'qD', 'quant_no': 'qD'}

	@property
	def conds(self):
		if self.version is 'std':
			return {'p_index_o': 'tree_out', 'p_index_no': 'i_tree_kno_no','quant_o': 'i_tree_bra_o', 'quant_no': 'i_tree_bra_no'}
	
	@property
	def vartext(self):
		if self.version is 'std':
			return {'PbT': afl({'a': [None, 'a_aa']}),
					'PwT': afl({'a': [None, 'a_aa','a_aaa']}),
					'qS' : afl({'a': ['a_aa']}),
					'qD' : afl({'a': [None, 'a_aa']}),
					'mu' : afl({'a': [None, 'a_aaa']}),
					'sigma': afl({'a': ['a_aa']}),
					'map_': afl({'a': [None,['a_aa','aa_a'],'a_aaa']}),
					'n'  : afl({'a': ['a_aa','a_aaa']})}