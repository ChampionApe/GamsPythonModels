import os
import gams
import pandas as pd
import DataBase
import COE
import COE_settings
import regex_gms
import nesting_tree
import DB2Gams

def apply_type(type_,version):
	return eval(f"COE.{type_}")(version=version)

def apply_type_settings(type_,version):
	return eval(f"COE_settings.{type_}")(version=version)

def df(x,kwargs):
	"""
	Modify x using kwargs.
	"""
	return x if x not in kwargs else kwargs[x]

class GPM_STA_PE:
	"""
	Class of static, partial equilibrium GamsPythonModels.
	The class builds on nesting_tree.py and the collection of gams functions in COE.py.
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
			self.version = nt.version
			self.mark_up = True if 'mark_up' not in kwargs else kwargs['mark_up']
			self.globals = {'sets': self.global_sets(nt), 'vars': self.global_vars(**kwargs)}
			self.globals['doms'] = self.vars_domains(**kwargs)
			self.locals = {tree: {attr: nt.trees[tree].__dict__[attr] for attr in nt.trees[tree].__dict__ if attr not in set(['tree','database']).union(nt.prune_trees)} for tree in nt.trees} # trees without database and actual tree
			self.model = DB2Gams.gams_model_py(nt.database,**kwargs)
			self.model_instances = {}
			self.work_folder = os.getcwd() if 'work_folder' not in kwargs else kwargs['mark_up']
			for tree in nt.trees.values(): # merge data 
				DataBase.py_db.merge_dbs(self.model.database,tree.database,exceptions=[eval(f"tree.{attr}") for attr in nt.prune_trees if hasattr(tree,attr)])
			
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
			return {'n': nt.setname, 'nn': nt.alias, 'nnn': nt.alias2, 'inp': nt.inp, 'out': nt.out, 'int': nt.int, 'fg': nt.fg, 'wT': nt.wT,'map_all': nt.map_all, 'kno_out': nt.kno_out, 'kno_inp': nt.kno_inp,
					'PwT_dom': nt.PwT_dom if self.version is 'Q2P' else nt.wT}

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
			return {'PwT': df(self.globals['sets']['PwT_dom'],kwargs),
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
			fcoe, name = apply_type(self.locals[local]['type_f'],self.locals[local]['version']), self.locals[local]['name']
			ftype_settings = self.ftype_settings(local)
			return fcoe.run(ftype_settings['vartext'], ftype_settings['domains'],ftype_settings['conditions'], name)
			
		def ftype_settings(self,local):
			"""
			To write a gams class, three dicts of information is needed: (1) domains of equations, (2) conditions on equations, (3) symbols needed.
			this information is collected here.
			"""
			out = {'domains': None, 'conditions': None, 'symboltext': None}
			settings = apply_type_settings(self.locals[local]['type_f'],version=self.locals[local]['version'])
			out['domains'] = {k: self.aux_write(v,dom=True) for k,v in settings.doms.items()}
			out['conditions'] = {k: self.aux_write(v,local=local) for k,v in settings.conds.items()}
			out['vartext'] = {k: {self.name_symbol(v['a'][i],v['l'][i]): 
								  self.aux_write(k, local=local, a=v['a'][i], l=v['l'][i]) for i in range(0,len(v['a']))} for k,v in settings.vartext.items()}
			return out

		def name_symbol(self,a,l):
			return self.nca(a)+l
 
		def nca(self,a):
			if a is None:
				return 'b'
			elif type(a) is str:
				return a
			elif type(a) is list:
				return '.'.join(a)

		def aux_write(self,symbol,local=None,a=None,dom=False,l=''):
			"""
			Write symbol with various alias' of 'n'. 
			"""
			if symbol is 'n':
				return self.globals['sets']['n'] if a is None else self.alias(a)[self.globals['sets']['n']]
			elif symbol in self.globals['vars']:
				return self.aux_write_d(symbol,a=self.alias(a)) if dom is True else self.aux_write_v(symbol,a=self.alias(a),l=l)
			elif symbol in self.globals['sets']:
				return self.aux_write_glb(symbol,a=self.alias(a))
			elif local is not None:
				return self.aux_write_s(symbol,local,a=self.alias(a))

		def alias(self,a):
			"""
			Return dict of alias' from string/list of strings. 
			'a_aa' returns a dictionary {'a': 'aa'}. ['a_aa','aa_aaa'] returns a dictionary {'a': 'aa', 'aa': 'aaa'}.
			"""
			if type(a) is str:
				return self.nx2nx(a.split('_'))
			elif type(a) is list:
				return {k:v for d in [self.nx2nx(a[i].split('_')) for i in range(0,len(a))] for k,v in d.items()}
			elif a is None:
				return None

		def aux_write_v(self,var,a=None,l=''):
			return self.model.database.get(self.globals['vars'][var],alias_domains=a,level=l).to_str

		def aux_write_d(self,var,a=None):
			return self.model.database.get(self.globals['vars'][var],alias_domains=a).to_string('dom')

		def aux_write_s(self,set_,local,a=None):
			return self.model.database.get(self.locals[local][set_],alias_domains=a).to_str

		def aux_write_glb(self,set_,a=None):
			return self.model.database.get(self.globals['sets'][set_],alias_domains=a).to_str

		def nx2nx(self,x):
			return {self.globals['sets']['n'*len(x[0])]: self.globals['sets']['n'*len(x[1])]}
