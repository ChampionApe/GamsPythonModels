import os
import gams
import pandas as pd
import DataBase
import COE
import regex_gms
import nesting_tree
import DB2Gams

def apply_type(type_):
	return eval(f"COE.{type_}()")

def df(x,kwargs):
	"""
	Modify x using kwargs.
	"""
	return x if x not in kwargs else kwargs[x]

class GPM_STA_PE:
	"""
	Class of static, partial equilibrium GamsPythonModels.
	The class builds on nesting_tree.py and the collection of functions COE.py.
	"""
	def apply_fm(self,module,function,kwargs):
		return eval(f"self.{module}.{function}(**{kwargs})")

	def attr_fm(self,module,attr):
		return eval(f"self.{module}.{attr}")

	def __init__(self,modules=[],**kwargs):
		"""
		Add variables, modules (w. settings)
		"""
		self.modules = {x: None for x in modules} # dict for storing modules
	
	def add_globals(self,modules,**kwargs):
		self.globals = {'sets': {k: v for d in [self.attr_fm(module,'globals')['sets'] for module in modules] for k,v in d.items()},
						'vars': {k: v for d in [self.apply_fm(module,'global_vars',kwargs) for module in modules] for k,v in d.items()}}

	class production:
		"""
		Production module using nesting trees.
		"""
		def __init__(self,nt,**kwargs):
			self.mark_up = True if 'mark_up' not in kwargs else kwargs['mark_up']
			self.globals = {'sets': self.global_sets(nt), 'vars': self.global_vars(**kwargs)}
			self.globals['doms'] = self.vars_domains(**kwargs)
			self.locals = {tree: {attr: nt.trees[tree].__dict__[attr] for attr in nt.trees[tree].__dict__ if attr not in ('tree','database')} for tree in nt.trees} # trees without database and actual tree
			self.model = DB2Gams.gams_model_py(nt.database,**kwargs)
			self.model_instances = {}
			self.work_folder = os.getcwd() if 'work_folder' not in kwargs else kwargs['mark_up']
			for tree in nt.trees.values(): # merge data 
				DataBase.py_db.merge_dbs(self.model.database,tree.database)
			
		def create_model_instance(self,repo=None,name='temp'):
			"""
			Create model instance with working-folder at repo.
			"""
			self.model_instances[name] = DB2Gams.gams_model(self.repo) if repo is None else DB2Gams.gams_model(repo)

		def df_run(self,name='temp'):
			self.model_instances[name].run(self.model.settings)

		def global_sets(self,nt):
			"""
			retrieve sets from nesting tree.
			"""
			return {'n': nt.setname, 'nn': nt.alias, 'nnn': nt.alias2, 'inp': nt.inp, 'out': nt.out, 'int': nt.int, 'fg': nt.fg, 'wT': nt.wT, 'map_all': nt.map_all, 'kno_out': nt.kno_out, 'kno_inp': nt.kno_inp}

		def global_vars(self,**kwargs):
			"""
			Variables.
			"""
			if self.mark_up is True:
				return {x: df(x,kwargs) for x in ('PwT','PbT','qS','qD','mu','sigma','eta','mark_up')}
			else:
				return {x: df(x,kwargs) for x in ('PwT','PbT','qS','qD','mu','sigma','eta')}			

		@property
		def df_vals(self):
			"""
			Default values for variables.
			"""
			return {'PwT': 1, 'PbT': 1, 'qS': 1, 'qD': 1, 'mu': 1, 'sigma': 0.5, 'eta': -0.5, 'mark_up': 0.1}

		@property 
		def df_groups(self):
			"""
			Return the various groups, with (variable,domain) combinations for each one.
			"""
			return {'gtech': {vtech: self.globals['doms'][vtech] for vtech in set(['mu','sigma','eta','mark_up']).intersection(set(self.globals['vars'].keys()))},
					'gexo ': {'PwT': self.globals['sets']['inp'],'qS' : self.globals['doms']['qS']},
					'gendo': {'PbT': self.globals['doms']['PbT'],'PwT': self.globals['sets']['int'],'qD' : self.globals['doms']['qD']}}

		def vars_domains(self,**kwargs):
			"""
			Names of domains for each variable. The df(x,kwargs) allows the user to modify domains up-front for small ad-hoc adjustments.
			"""
			return {'PwT': df(self.globals['sets']['wT'],kwargs),
				    'PbT': df(self.globals['sets']['out'],kwargs),
				    'qS' : df(self.globals['sets']['out'],kwargs),
				    'qD' : df(self.globals['sets']['wT'],kwargs),
				    'mu' : df(self.globals['sets']['map_all'],kwargs),
				    'sigma': df(self.globals['sets']['kno_inp'],kwargs),
				    'eta' : df(self.globals['sets']['kno_out'],kwargs),
				    'mark_up': df(self.globals['sets']['out'],kwargs) if self.mark_up is True else None}

		def df_init(self):
			"""
			Add df_vals to variables that have not yet been defined.
			"""
			for var in self.globals['vars']:
				if var not in self.model.database:
					self.model.database[var] = pd.Series(self.df_vals[var], index = self.model.database[self.globals['doms'][var]], name=var)

		def df_write(self,repo=os.getcwd(),export_settings=False):
			self.df_init()
			self.add_groups()
			self.add_blocks()
			self.model.run_default(repo,export_settings=export_settings)

		def add_groups(self):
			"""
			Define 'groups': dictionaries with variable names and 'conditions' (sets to be defined over).
			Add the groups to the model settings. Add them to the meta-groups of exo/endo respectively.
			"""
			self.groups = {group: {var: {'conditions': self.model.database.get(self.df_groups[group][var]).to_str} for var in self.df_groups[group]} for group in self.df_groups}
			[self.model.add_group_to_groups(self.groups[group],self.model.settings.name+'_'+group) for group in self.groups];
			self.model.settings.g_endo += [self.model.settings.name+'_gendo']
			self.model.settings.g_exo += [self.model.settings.name+'_gtech',self.model.settings.name+'_gexo']

		def add_blocks(self):
			if self.model.blocks is None:
				self.model.blocks = ""
			if self.model.settings.blocks is None:
				self.model.settings.blocks = []
			for local in self.locals:
				self.model.settings.blocks += ['M_'+local]
				self.model.blocks += f"$BLOCK M_{local} \n\t{self.eqtext(local)}\n$ENDBLOCK\n"

		def eqtext(self,local):
			"""
			Write equations: Price indices and demand functions.
			"""
			fcoe = apply_type(self.locals[local]['type_f'])
			out,name,vartext = '', self.locals[local]['name'], self.vartext(local)
			if self.locals[local]['type_f']=='CES':
				out += fcoe.p_index(f"E_{name}_p_o", self.aux_write_d('PbT'), self.aux_write_s('tree_out',local), 
						vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['sets'],vartext['maps'],output=True)+'\n\t'
				out += fcoe.p_index(f"E_{name}_p_no", self.aux_write_d('PwT'), self.aux_write_s('i_tree_kno_no',local), 
						vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['sets'],vartext['maps'],output=False)+'\n\t'
				out += fcoe.p_index_CD(f"E_{name}_pc_CD_o", self.aux_write_d('PbT'), self.aux_write_s('tree_out',local), 
						vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['sets'],vartext['maps'],output=True)+'\n\t'
				out += fcoe.p_index_CD(f"E_{name}_p_CD_no", self.aux_write_d('PwT'), self.aux_write_s('i_tree_kno_no',local), 
						vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['sets'],vartext['maps'],output=False)+'\n\t'
				out += fcoe.demand(f"E_{name}_d_o", self.aux_write_d('qD'), self.aux_write_s('i_tree_bra_o',local),
						vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['sets'],vartext['maps'],output=True)+'\n\t'
				out += fcoe.demand(f"E_{name}_d_no", self.aux_write_d('qD'), self.aux_write_s('i_tree_bra_no',local),
						vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['sigma'],vartext['sets'],vartext['maps'],output=False)
			if self.locals[local]['type_f']=='CET':
				out += fcoe.p_index(f"E_{name}_p", self.aux_write_d('PwT'), self.aux_write_s('i_tree_kno',local),
						vartext['PbT'],vartext['PwT'],vartext['mu'],vartext['eta'],vartext['sets'],vartext['maps'],vartext['out'])+'\n\t'
				out += fcoe.demand(f"E_{name}_d_o", self.aux_write_d('qD'), self.aux_write_s('i_tree_bra_o',local),
						vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['eta'],vartext['sets'],vartext['maps'],output=True)+'\n\t'
				out += fcoe.demand(f"E_{name}_d_no", self.aux_write_d('qD'), self.aux_write_s('i_tree_bra_no',local),
						vartext['qS'],vartext['PbT'],vartext['qD'],vartext['PwT'],vartext['mu'],vartext['eta'],vartext['sets'],vartext['maps'],output=False)
			return out

		def vartext(self,local):
			"""
			Return dictionary with variable names as keys, and gams-strings in values. 'b' returns with domains as 'baseline', 
			'a' returns aliased domains, and 'aa' returns another type of aliased domains etc. 'l' adds '.l' to the variable.
			local is used to identify which of the nesting trees' maps are used to condition on.
			"""
			if self.locals[local]['type_f']=='CES':
				return {'PbT': {'b'	: self.aux_write('PbT'), 'a': self.aux_write('PbT', a=self.n2nn)},
						'PwT': {'b'	: self.aux_write('PwT'), 'a' : self.aux_write('PwT',a=self.n2nn), 'aa': self.aux_write('PwT',a=self.n2nnn)},
						'qS' : {'a' : self.aux_write('qS', a=self.n2nn)},
						'qD' : {'b' : self.aux_write('qD'),  'a' : self.aux_write('qD', a=self.n2nn)},
						'mu' : {'b' : self.aux_write('mu'),  'a' : self.aux_write('mu', a={**self.n2nn, **self.nn2n}), 'aa': self.aux_write('mu',a=self.n2nnn)},
						'sigma': {'b': self.aux_write('sigma'), 'a': self.aux_write('sigma',a=self.n2nn), 'l': self.aux_write('sigma',l='.l')},
						'maps': {'b': self.aux_write_s('map',local), 'a': self.aux_write_s('map',local,a={**self.n2nn,**self.nn2n})},
						'sets': {'a': self.aux_write_glb('nn'), 'aa': self.aux_write_glb('nnn')}
						}
			elif self.locals[local]['type_f']=='CET':
				return {'PbT': {'b'	: self.aux_write('PbT'), 'a': self.aux_write('PbT', a=self.n2nn), 'aa': self.aux_write('PbT',a=self.n2nnn)},
						'PwT': {'b'	: self.aux_write('PwT'), 'a' : self.aux_write('PwT',a=self.n2nn), 'aa': self.aux_write('PwT',a=self.n2nnn)},
						'qS' : {'b' : self.aux_write('qS')},
						'qD' : {'b' : self.aux_write('qD'),  'a' : self.aux_write('qD', a=self.n2nn)},
						'mu' : {'b' : self.aux_write('mu'),  'a' : self.aux_write('mu', a={**self.n2nn, **self.nn2n})},
						'eta': {'b': self.aux_write('eta'),  'a' : self.aux_write('eta',a=self.n2nn)},
						'maps': {'b': self.aux_write_s('map',local), 'a': self.aux_write_s('map',local,a={**self.n2nn,**self.nn2n})},
						'sets': {'a': self.aux_write_glb('nn'), 'aa': self.aux_write_glb('nnn')},
						'out' : {'a': self.aux_write_s('tree_out',local,a=self.n2nn)}
						}

		def aux_write(self,var,a=None,l=''):
			return self.model.database.get(self.globals['vars'][var],alias_domains=a,level=l).to_str

		def aux_write_s(self,set_,local,a=None):
			return self.model.database.get(self.locals[local][set_],alias_domains=a).to_str

		def aux_write_glb(self,set_,a=None):
			return self.model.database.get(self.globals['sets'][set_],alias_domains=a).to_str

		def aux_write_d(self,var,a=None):
			return self.model.database.get(self.globals['vars'][var],alias_domains=a).to_string('dom')

		@property
		def n2nn(self):
			return {self.globals['sets']['n']: self.globals['sets']['nn']}
		@property
		def nn2n(self):
			return {self.globals['sets']['nn']: self.globals['sets']['n']}
		@property
		def n2nnn(self):
			return {self.globals['sets']['n']: self.globals['sets']['nnn']}
