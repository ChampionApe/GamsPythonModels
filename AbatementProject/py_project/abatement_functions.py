from gams import *
import os
curr = os.getcwd()
py = {}
py['main'] = os.path.dirname(os.path.dirname(os.getcwd()))+'\\py_main'
os.chdir(py['main'])
import pandas as pd
import DataBase
import COE
import regex_gms
from DB2Gams import *
os.chdir(curr)

class am_base(gams_model_py):
	def __init__(self,tree,gams_settings=None):
		self.tree = tree
		super().__init__(self.tree.database,gsettings=gams_settings, blocks_text = None, functions = None, groups = {}, exceptions = [], exceptions_load = [], components = {}, export_files = None)

	def apply_type(self,type_):
		return eval(f"COE.{type_}()")

	def run_abatement_model(self,repo=os.getcwd(),type_='CES',export_settings=False):
		self.define_groups()
		self.define_blocks(type_=type_)
		self.run_default(repo,export_settings=export_settings)

	def define_groups(self,p='p',q='q',mu='mu',sigma='sigma'):
		self.p = p
		self.q = q
		self.mu = mu
		self.sigma = sigma
		if p not in self.database:
			self.database[p] = pd.Series(1,index=self.database[self.tree.setname],name=p)
		if q not in self.database:
			self.database[q] = pd.Series(1,index=self.database[self.tree.setname],name=q)
		if mu not in self.database:
			self.database[mu] = pd.Series(0.5,index=self.database[self.tree.mapname],name=mu)
		if sigma not in self.database:
			self.database[sigma] = pd.Series(0.5, index = self.database[self.tree.aggname],name=sigma)
		self.group_tech = {sigma: {'conditions': self.database.get(self.tree.aggname).to_str},
					       mu	: {'conditions': self.database.get(self.tree.mapname).to_str}}
		self.group_exo = {p: {'conditions': self.database.get(self.tree.inpname).to_str},
						  q: {'conditions': self.database.get(self.tree.outname).to_str}}
		self.group_endo= {p: {'conditions': self.database.get(self.tree.aggname).to_str},
						  q: {'conditions': self.database.get(self.tree.sector).to_str+' and not '+self.database.get(self.tree.outname).to_str}}
		self.add_group_to_groups(self.group_tech,self.model.name+'_tech')
		self.add_group_to_groups(self.group_exo ,self.model.name+'_exo')
		self.add_group_to_groups(self.group_endo,self.model.name+'_endo')
		self.model.g_endo = [self.model.name+'_endo']
		self.model.g_exo = [self.model.name+'_tech', self.model.name+'_exo']
		# Arrange variables in types, with alias' etc. that are used to write equations:
		n2nn  = {self.tree.setname: self.tree.alias}
		n2nnn = {self.tree.setname: self.tree.alias2}
		nn2n  = {self.tree.alias  : self.tree.setname}
		self.write_vars = { 'q': {'base'  : self.database.get(self.q).to_str,
								  'alias' : self.database.get(self.q,alias_domains=n2nn).to_str,
								  'alias2': self.database.get(self.q,alias_domains=n2nnn).to_str},
							'p': {'base'  : self.database.get(self.p).to_str,
								  'alias' : self.database.get(self.p,alias_domains=n2nn).to_str,
								  'alias2': self.database.get(self.p,alias_domains=n2nnn).to_str},
							'mu':{'base'  : self.database.get(self.mu).to_str,
								  'alias' : self.database.get(self.mu,alias_domains={**n2nn,**nn2n}).to_str,
								  'alias2': self.database.get(self.mu,alias_domains=n2nnn).to_str},
							'sigma':{'base'  : self.database.get(self.sigma).to_str,
									 'alias' : self.database.get(self.sigma,alias_domains=n2nn).to_str,
									 'alias2': self.database.get(self.sigma,alias_domains=n2nnn).to_str,
									 'level': self.database.get(self.sigma,level='.l').to_str},
							'inputs': { 'base'  : self.tree.setname,
										'alias' : self.tree.alias,
										'alias2': self.tree.alias2},
							'in2aggs': {'base'  : self.database.get(self.tree.mapname).to_str,
										'alias' : self.database.get(self.tree.mapname,alias_domains={**n2nn,**nn2n}).to_str,
										'alias2': self.database.get(self.tree.mapname,alias_domains=n2nnn).to_str}
							}

	def define_blocks(self,type_):
		functype = self.apply_type(type_)
		self.blocks = """
$BLOCK M_{mname}
	{demand_equation}
	{price_equation}
$ENDBLOCK

""".format(	mname = self.model.name,
			demand_equation = functype.equation('demand',f"E_{self.model.name}_q",
														  self.groups[self.model.name+'_endo'][self.q]['domains'],
														  self.groups[self.model.name+'_endo'][self.q]['conditions'],
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['sigma'],self.write_vars['inputs'],self.write_vars['in2aggs']),
			price_equation  = functype.equation('price_index',f"E_{self.model.name}_p",
														  self.groups[self.model.name+'_endo'][self.p]['domains'],
														  self.groups[self.model.name+'_endo'][self.p]['conditions'],
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['sigma'],self.write_vars['inputs'],self.write_vars['in2aggs']))
		self.model.blocks = ['M_'+self.model.name]

class am_base_v2(gams_model_py):
	"""
	abatement model with quantities/prices defined over different sets.
	"""
	def __init__(self,tree,gams_settings=None):
		self.tree = tree
		super().__init__(self.tree.database,gsettings=gams_settings, blocks_text = None, functions = None, groups = {}, exceptions = [], exceptions_load = [], components = {}, export_files = None)

	def apply_type(self,type_):
		return eval(f"COE.{type_}()")

	def run_abatement_model(self,repo=os.getcwd(),type_='CES',export_settings=False,add_aggregates=False):
		self.define_groups()
		self.define_blocks(type_=type_)
		if add_aggregates is True:
			self.add_aggregates()
		self.run_default(repo,export_settings=export_settings)

	def define_groups(self,p='p',q='q',mu='mu',sigma='sigma',eta='eta'):
		self.p = p
		self.q = q
		self.mu = mu
		self.sigma = sigma
		self.eta = eta
		if p not in self.database:
			self.database[p] = pd.Series(1,index=self.database[self.tree.p_all],name=p)
		if q not in self.database:
			self.database[q] = pd.Series(1,index=self.database[self.tree.q_all],name=q)
		if mu not in self.database:
			self.database[mu] = pd.Series(0.5,index=self.database[self.tree.mapname],name=mu)
		if sigma not in self.database:
			self.database[sigma] = pd.Series(0.5, index = self.database[self.tree.aggname],name=sigma)
		self.group_tech = {sigma: {'conditions': self.database.get(self.tree.aggname).to_str},
					       mu	: {'conditions': self.database.get(self.tree.mapname).to_str}}
		self.group_exo = {p: {'conditions': self.database.get(self.tree.inpname).to_str},
						  q: {'conditions': self.database.get(self.tree.outname).to_str}}
		self.group_endo= {p: {'conditions': self.database.get(self.tree.aggname).to_str},
						  q: {'conditions': self.database.get(self.tree.sector).to_str+' and not '+self.database.get(self.tree.outname).to_str}}
		self.add_group_to_groups(self.group_tech,self.model.name+'_tech')
		self.add_group_to_groups(self.group_exo ,self.model.name+'_exo')
		self.add_group_to_groups(self.group_endo,self.model.name+'_endo')
		self.model.g_endo = [self.model.name+'_endo']
		self.model.g_exo = [self.model.name+'_tech', self.model.name+'_exo']
		n2nn  = {self.tree.setname: self.tree.alias}
		n2nnn = {self.tree.setname: self.tree.alias2}
		nn2n  = {self.tree.alias  : self.tree.setname}
		nn2nnn = {self.tree.alias : self.tree.alias2}
		self.write_vars = { 'q': {'base'  : self.database.get(self.q).to_str,
								  'alias' : self.database.get(self.q,alias_domains=n2nn).to_str,
								  'alias2': self.database.get(self.q,alias_domains=n2nnn).to_str},
							'p': {'base'  : self.database.get(self.p).to_str,
								  'alias' : self.database.get(self.p,alias_domains=n2nn).to_str,
								  'alias2': self.database.get(self.p,alias_domains=n2nnn).to_str},
							'mu':{'base'  : self.database.get(self.mu).to_str,
								  'alias' : self.database.get(self.mu,alias_domains={**n2nn,**nn2n}).to_str,
								  'alias2': self.database.get(self.mu,alias_domains=n2nnn).to_str},
							'sigma':{'base'  : self.database.get(self.sigma).to_str,
									 'alias' : self.database.get(self.sigma,alias_domains=n2nn).to_str,
									 'alias2': self.database.get(self.sigma,alias_domains=n2nnn).to_str,
									 'level': self.database.get(self.sigma,level='.l').to_str},
							'inputs': { 'base'  : self.tree.setname,
										'alias' : self.tree.alias,
										'alias2': self.tree.alias2},
							'in2aggs': {'base'  : self.database.get(self.tree.mapname).to_str,
										'alias' : self.database.get(self.tree.mapname,alias_domains={**n2nn,**nn2n}).to_str,
										'alias2': self.database.get(self.tree.mapname,alias_domains=n2nnn).to_str},
							'q2p': {'base': self.database.get(self.tree.q2p,alias_domains=nn2nnn).to_str,
									'alias': self.database.get(self.tree.q2p,alias_domains={**n2nn,**nn2nnn}).to_str}}


	def define_blocks(self,type_):
		"""
		Equation blocks for CES-input-like part of model:
		"""
		functype = self.apply_type(type_)
		self.blocks = """
$BLOCK M_{mname}
	{demand_equation}
	{price_equation}
$ENDBLOCK

""".format(	mname = self.model.name,
			demand_equation = functype.equation('demand',f"E_{self.model.name}_q",
														  self.database.get(self.q).to_string('dom'),
														  self.groups[self.model.name+'_endo'][self.q]['conditions'],
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['sigma'],self.write_vars['inputs'],self.write_vars['in2aggs'],
														  self.write_vars['q2p']),
			price_equation  = functype.equation('price_index',f"E_{self.model.name}_p",
														  self.database.get(self.p).to_string('dom'),
														  self.database.get(self.tree.aggname).to_str,
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['sigma'],self.write_vars['inputs'],self.write_vars['in2aggs'],
														  self.write_vars['q2p']))
		self.model.blocks = ['M_'+self.model.name]

	def add_aggregates(self):
		self.group_endo_aggs = {self.q: {'conditions': self.database.get(self.tree.n2nn_agg).to_str}}
		self.add_group_to_groups(self.group_endo_aggs,self.model.name+'_aggs')
		self.model.g_endo += [self.model.name+'_aggs']
		self.write_vars['n2nn'] = {'alias': self.database.get(self.tree.n2nn,alias_domains={**{self.tree.setname: self.tree.alias},**{self.tree.alias: self.tree.setname}}).to_str}
		self.blocks += """
$BLOCK M_{mname}_agg
	{sum_eq}
$ENDBLOCK

""".format( mname =self.model.name,
			sum_eq=COE.sums().equation('simple_sum',f"E_{self.model.name}_agg",
													self.database.get(self.q).to_string('dom'),
													self.groups[self.model.name+'_aggs'][self.q]['conditions'],
													self.write_vars['q']['base'],self.write_vars['q']['alias'],
													self.write_vars['inputs']['alias'],
													self.write_vars['n2nn']['alias']
													))
		self.model.blocks += ['M_'+self.model.name+'_agg']

class am_cet(gams_model_py):
	"""
	Includes an arbitrary combination of input/output nests (e.g. CES-input/CET-outputsplit)
	"""
	def __init__(self,tree,gams_settings=None):
		self.tree=tree
		self.block_components = {}
		super().__init__(self.tree.database,gsettings=gams_settings,blocks_text=None,functions=None,groups={},exceptions=[],exceptions_load=[],components = {},export_files = None)

	def apply_type(self,type_):
		return eval(f"COE.{type_}()")

	def run_abatement_model(self,repo=os.getcwd(),type_in='CES',type_out='CES',export_settings=False):
		self.define_groups()
		self.define_blocks_in(type_=type_in)
		self.define_blocks_out(type_=type_out)
		self.agg_block_components()
		self.run_default(repo,export_settings=export_settings)

	def agg_block_components(self):
		self.model.blocks = list(self.block_components.keys())
		self.blocks = ""
		for component in self.block_components:
			self.blocks += self.block_components[component]

	# Define groups: 
	def define_groups(self,p='p',q='q',mu='mu',sigma='sigma',eta='eta'):
		self.p = p
		self.q = q
		self.mu = mu
		self.sigma = sigma
		self.eta = eta
		if p not in self.database:
			self.database[p] = pd.Series(1,index=self.database[self.tree.setname],name=p)
		if q not in self.database:
			self.database[q] = pd.Series(1,index=self.database[self.tree.setname],name=q)
		if mu not in self.database:
			self.database[mu] = pd.Series(0.5,index=self.database[self.tree.all_map],name=mu)
		if sigma not in self.database:
			self.database[sigma] = pd.Series(0.5, index = self.database[self.tree.in_agg],name=sigma)
		if eta not in self.database:
			self.database[eta] = pd.Series(-0.5, index = self.database[self.tree.out_agg], name=eta)
		self.group_tech = {sigma: {'conditions': self.database.get(self.tree.in_agg).to_str},
						   eta : {'conditions': self.database.get(self.tree.out_agg).to_str},
					       mu	: {'conditions': self.database.get(self.tree.all_map).to_str}}
		self.group_exo = {p: {'conditions': self.database.get(self.tree.inpname).to_str},
						  q: {'conditions': self.database.get(self.tree.outname).to_str}}
		self.group_endo= {p: {'conditions': self.database.get(self.tree.out_endo).to_str+' or '+self.database.get(self.tree.in_agg).to_str},
						  q: {'conditions': self.database.get(self.tree.in_endo).to_str +' or '+self.database.get(self.tree.out_agg).to_str}}
		self.add_group_to_groups(self.group_tech,self.model.name+'_tech')
		self.add_group_to_groups(self.group_exo ,self.model.name+'_exo')
		self.add_group_to_groups(self.group_endo,self.model.name+'_endo')
		self.model.g_endo = [self.model.name+'_endo']
		self.model.g_exo = [self.model.name+'_tech', self.model.name+'_exo']
		n2nn  = {self.tree.setname: self.tree.alias}
		n2nnn = {self.tree.setname: self.tree.alias2}
		nn2n  = {self.tree.alias  : self.tree.setname}
		self.write_vars = { 'q': {'base'  : self.database.get(self.q).to_str,
								  'alias' : self.database.get(self.q,alias_domains=n2nn).to_str,
								  'alias2': self.database.get(self.q,alias_domains=n2nnn).to_str},
							'p': {'base'  : self.database.get(self.p).to_str,
								  'alias' : self.database.get(self.p,alias_domains=n2nn).to_str,
								  'alias2': self.database.get(self.p,alias_domains=n2nnn).to_str},
							'mu':{'base'  : self.database.get(self.mu).to_str,
								  'alias' : self.database.get(self.mu,alias_domains={**n2nn,**nn2n}).to_str,
								  'alias2': self.database.get(self.mu,alias_domains=n2nnn).to_str},
							'sigma':{'base'  : self.database.get(self.sigma).to_str,
									 'alias' : self.database.get(self.sigma,alias_domains=n2nn).to_str,
									 'alias2': self.database.get(self.sigma,alias_domains=n2nnn).to_str,
									 'level': self.database.get(self.sigma,level='.l').to_str},
							'eta' : {'base'  : self.database.get(self.eta).to_str,
									 'alias' : self.database.get(self.eta,alias_domains=n2nn).to_str,
									 'alias2': self.database.get(self.eta,alias_domains=n2nnn).to_str},
							'inputs': { 'base'  : self.tree.setname,
										'alias' : self.tree.alias,
										'alias2': self.tree.alias2},
							'in2aggs_in': {'base'  : self.database.get(self.tree.in_map).to_str,
										   'alias' : self.database.get(self.tree.in_map,alias_domains={**n2nn,**nn2n}).to_str,
										   'alias2': self.database.get(self.tree.in_map,alias_domains=n2nnn).to_str},
							'in2aggs_out':{'base'  : self.database.get(self.tree.out_map).to_str,
										   'alias' : self.database.get(self.tree.out_map,alias_domains={**n2nn,**nn2n}).to_str,
										   'alias2': self.database.get(self.tree.out_map,alias_domains=n2nnn).to_str}}

	def define_blocks_in(self,type_):
		"""
		Equation blocks for CES-input-like part of model:
		"""
		functype = self.apply_type(type_)
		self.block_components['M_'+self.model.name+'_in'] = """
$BLOCK M_{mname}_in
	{demand_equation}
	{price_equation}
$ENDBLOCK

""".format(	mname = self.model.name,
			demand_equation = functype.equation('demand',f"E_{self.model.name}_in_q",
														  self.database.get(self.q).to_string('dom'),
														  self.database.get(self.tree.in_endo).to_str,
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['sigma'],self.write_vars['inputs'],self.write_vars['in2aggs_in']),
			price_equation  = functype.equation('price_index',f"E_{self.model.name}_in_p",
														  self.database.get(self.p).to_string('dom'),
														  self.database.get(self.tree.in_agg).to_str,
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['sigma'],self.write_vars['inputs'],self.write_vars['in2aggs_in']))

	def define_blocks_out(self,type_):
		"""
		Equation blocks for CET-output-split-like part of model:
		"""
		functype = self.apply_type(type_)
		self.block_components['M_'+self.model.name+'_out'] = """
$BLOCK M_{mname}_out
	{demand_equation}
	{price_equation}
$ENDBLOCK

""".format(	mname = self.model.name,
			demand_equation = functype.equation('demand',f"E_{self.model.name}_out_q",
														  self.database.get(self.q).to_string('dom'),
														  self.database.get(self.tree.out_endo).to_str,
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['eta'],self.write_vars['inputs'],self.write_vars['in2aggs_out']),
			price_equation  = functype.equation('price_index',f"E_{self.model.name}_out_p",
														  self.database.get(self.p).to_string('dom'),
														  self.database.get(self.tree.out_agg).to_str,
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['eta'],self.write_vars['inputs'],self.write_vars['in2aggs_out']))


class am_CET_v2(gams_model_py):
	"""
	abatement model with CTE outputs and quantities/prices defined over different sets.
	"""
	def __init__(self,tree,gams_settings=None):
		self.tree = tree
		self.block_components = {}
		super().__init__(self.tree.database,gsettings=gams_settings,blocks_text=None,functions=None,groups={},exceptions=[],exceptions_load=[],components = {},export_files = None)

	def apply_type(self,type_):
		return eval(f"COE.{type_}()")

	def run_abatement_model(self,repo=os.getcwd(),type_in='CES_v2',type_out='CES',export_settings=False,add_aggregates=False):
		self.define_groups()
		self.define_blocks_in(type_=type_in)
		self.define_blocks_out(type_=type_out)
		self.agg_block_components()
		if add_aggregates is True:
			self.add_aggregates()
		self.run_default(repo,export_settings=export_settings)

	def agg_block_components(self):
		self.model.blocks = list(self.block_components.keys())
		self.blocks = ""
		for component in self.block_components:
			self.blocks += self.block_components[component]
 
	def define_groups(self,p='p',q='q',mu='mu',sigma='sigma',eta='eta'):
		self.p = p
		self.q = q
		self.mu = mu
		self.sigma = sigma
		self.eta = eta
		if p not in self.database:
			self.database[p] = pd.Series(1,index=self.database[self.tree.p_all],name=p)
		if q not in self.database:
			self.database[q] = pd.Series(1,index=self.database[self.tree.q_all],name=q)
		if mu not in self.database:
			self.database[mu] = pd.Series(0.5,index=self.database[self.tree.all_map],name=mu)
		if sigma not in self.database:
			self.database[sigma] = pd.Series(0.5, index = self.database[self.tree.in_agg],name=sigma)
		if eta not in self.database:
			self.database[eta] = pd.Series(-0.5, index = self.database[self.tree.out_agg], name=eta)
		self.group_tech = {sigma: {'conditions': self.database.get(self.tree.in_agg).to_str},
						   eta : {'conditions': self.database.get(self.tree.out_agg).to_str},
					       mu	: {'conditions': self.database.get(self.tree.all_map).to_str}}
		self.group_exo = {p: {'conditions': self.database.get(self.tree.inpname).to_str},
						  q: {'conditions': self.database.get(self.tree.outname).to_str}}
		self.group_endo= {p: {'conditions': self.database.get(self.tree.out_endo).to_str+' or '+self.database.get(self.tree.in_agg).to_str},
						  q: {'conditions': self.database.get(self.tree.in_endo).to_str +' or '+self.database.get(self.tree.out_agg).to_str}}
		self.add_group_to_groups(self.group_tech,self.model.name+'_tech')
		self.add_group_to_groups(self.group_exo ,self.model.name+'_exo')
		self.add_group_to_groups(self.group_endo,self.model.name+'_endo')
		self.model.g_endo = [self.model.name+'_endo']
		self.model.g_exo = [self.model.name+'_tech', self.model.name+'_exo']
		n2nn  = {self.tree.setname: self.tree.alias}
		n2nnn = {self.tree.setname: self.tree.alias2}
		nn2n  = {self.tree.alias  : self.tree.setname}
		nn2nnn = {self.tree.alias : self.tree.alias2}
		self.write_vars = { 'q': {'base'  : self.database.get(self.q).to_str,
								  'alias' : self.database.get(self.q,alias_domains=n2nn).to_str,
								  'alias2': self.database.get(self.q,alias_domains=n2nnn).to_str},
							'p': {'base'  : self.database.get(self.p).to_str,
								  'alias' : self.database.get(self.p,alias_domains=n2nn).to_str,
								  'alias2': self.database.get(self.p,alias_domains=n2nnn).to_str},
							'mu':{'base'  : self.database.get(self.mu).to_str,
								  'alias' : self.database.get(self.mu,alias_domains={**n2nn,**nn2n}).to_str,
								  'alias2': self.database.get(self.mu,alias_domains=n2nnn).to_str},
							'sigma':{'base'  : self.database.get(self.sigma).to_str,
									 'alias' : self.database.get(self.sigma,alias_domains=n2nn).to_str,
									 'alias2': self.database.get(self.sigma,alias_domains=n2nnn).to_str,
									 'level': self.database.get(self.sigma,level='.l').to_str},
							'eta' : {'base'  : self.database.get(self.eta).to_str,
									 'alias' : self.database.get(self.eta,alias_domains=n2nn).to_str,
									 'alias2': self.database.get(self.eta,alias_domains=n2nnn).to_str},
							'inputs': { 'base'  : self.tree.setname,
										'alias' : self.tree.alias,
										'alias2': self.tree.alias2},
							'in2aggs_in': {'base'  : self.database.get(self.tree.in_map).to_str,
										   'alias' : self.database.get(self.tree.in_map,alias_domains={**n2nn,**nn2n}).to_str,
										   'alias2': self.database.get(self.tree.in_map,alias_domains=n2nnn).to_str},
							'in2aggs_out':{'base'  : self.database.get(self.tree.out_map).to_str,
										   'alias' : self.database.get(self.tree.out_map,alias_domains={**n2nn,**nn2n}).to_str,
										   'alias2': self.database.get(self.tree.out_map,alias_domains=n2nnn).to_str},
							'q2p': {'base': self.database.get(self.tree.q2p,alias_domains=nn2nnn).to_str,
									'alias': self.database.get(self.tree.q2p,alias_domains={**n2nn,**nn2nnn}).to_str}}

	def define_blocks_in(self,type_):
		"""
		Equation blocks for CES-input-like part of model:
		"""
		functype = self.apply_type(type_)
		self.block_components['M_'+self.model.name+'_in'] = """
$BLOCK M_{mname}_in
	{demand_equation}
	{price_equation}
$ENDBLOCK

""".format(	mname = self.model.name,
			demand_equation = functype.equation('demand',f"E_{self.model.name}_in_q",
														  self.database.get(self.q).to_string('dom'),
														  self.database.get(self.tree.in_endo).to_str,
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['sigma'],self.write_vars['inputs'],self.write_vars['in2aggs_in'],
														  self.write_vars['q2p']),
			price_equation  = functype.equation('price_index',f"E_{self.model.name}_in_p",
														  self.database.get(self.p).to_string('dom'),
														  self.database.get(self.tree.in_agg).to_str,
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['sigma'],self.write_vars['inputs'],self.write_vars['in2aggs_in'],
														  self.write_vars['q2p']))

	def define_blocks_out(self,type_):
		"""
		Equation blocks for CET-output-split-like part of model:
		"""
		functype = self.apply_type(type_)
		self.block_components['M_'+self.model.name+'_out'] = """
$BLOCK M_{mname}_out
	{demand_equation}
	{price_equation}
$ENDBLOCK

""".format(	mname = self.model.name,
			demand_equation = functype.equation('demand',f"E_{self.model.name}_out_q",
														  self.database.get(self.q).to_string('dom'),
														  self.database.get(self.tree.out_endo).to_str,
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['eta'],self.write_vars['inputs'],self.write_vars['in2aggs_out']),
			price_equation  = functype.equation('price_index',f"E_{self.model.name}_out_p",
														  self.database.get(self.p).to_string('dom'),
														  self.database.get(self.tree.out_agg).to_str,
														  self.write_vars['p'],self.write_vars['q'],self.write_vars['mu'],
														  self.write_vars['eta'],self.write_vars['inputs'],self.write_vars['in2aggs_out']))
	def add_aggregates(self):
		self.group_endo_aggs = {self.q: {'conditions': self.database.get(self.tree.n2nn_agg).to_str}}
		self.add_group_to_groups(self.group_endo_aggs,self.model.name+'_aggs')
		self.model.g_endo += [self.model.name+'_aggs']
		self.write_vars['n2nn'] = {'alias': self.database.get(self.tree.n2nn,alias_domains={**{self.tree.setname: self.tree.alias},**{self.tree.alias: self.tree.setname}}).to_str}
		self.blocks += """
$BLOCK M_{mname}_agg
	{sum_eq}
$ENDBLOCK

""".format( mname =self.model.name,
			sum_eq=COE.sums().equation('simple_sum',f"E_{self.model.name}_agg",
													self.database.get(self.q).to_string('dom'),
													self.groups[self.model.name+'_aggs'][self.q]['conditions'],
													self.write_vars['q']['base'],self.write_vars['q']['alias'],
													self.write_vars['inputs']['alias'],
													self.write_vars['n2nn']['alias']
													))
		self.model.blocks += ['M_'+self.model.name+'_agg']


