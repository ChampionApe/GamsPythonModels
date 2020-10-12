import os, gams, pickle, numpy as np, pandas as pd, DataBase, COE, COE_settings, regex_gms, nesting_tree, DB2Gams,ShockFunction

def apply_type(type_,version):
	return eval(f"COE.{type_}")(version=version)

def apply_type_settings(type_,version):
	return eval(f"COE_settings.{type_}")(version=version)

def empty_index(symbol):
    if isinstance(symbol,pd.MultiIndex):
        return pd.MultiIndex.from_tuples([],names=symbol.names)
    elif isinstance(symbol,pd.Index):
        return pd.Index([], name=symbol.name)

def balanced_loop(PbT,qS,loop,TC,type_='both'):
	p0,pT = PbT.xs(loop[0],level=loop.name),PbT.xs(loop[-1],level=loop.name)
	q0,qT = qS.xs(loop[0],level=loop.name),qS.xs(loop[-1],level=loop.name)
	if type_=='both':
		a = sum(pT*qT+p0*q0-pT*q0-p0*qT)
		b = sum(pT*q0+qT*p0-2*p0*q0)
		c = -(TC-sum(p0*q0))
		sol_1 = (-b-np.sqrt(b**2-4*a*c))/(2*a)
		sol_2 = (-b+np.sqrt(b**2-4*a*c))/(2*a)
		sol_1[(sol_1>1)|(sol_1<0)] = sol_2[(sol_1>1)|(sol_1<0)]
		return sol_1
	elif type_=='price':
		return (TC-(PbT*q0).groupby(loop.name).sum())/(((qT-q0)*PbT).groupby(loop.name).sum())
	elif type_=='quant':
		return (TC-(qS*p0).groupby(loop.name).sum())/(((pT-p0)*qS).groupby(loop.name).sum())

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
		def __init__(self,nt=None,pickle_path=None,**kwargs):
			if pickle_path is None:
				self.version = nt.version
				self.mark_up = True if 'mark_up' not in kwargs else kwargs['mark_up']
				self.globals = {'sets': self.global_sets(nt), 'vars': self.global_vars(**kwargs)}
				self.globals['doms'] = self.vars_domains(**kwargs)
				self.locals = {tree: {attr: nt.trees[tree].__dict__[attr] for attr in nt.trees[tree].__dict__ if attr not in set(['tree','database']).union(nt.prune_trees)} for tree in nt.trees} # trees without database and actual tree
				self.model = DB2Gams.gams_model_py(database=nt.database,**kwargs)
				self.model_instances = {}
				self.checkpoints = {}
				self.initialized = False if 'initialized' not in kwargs else kwargs['initialized']
				self.work_folder = os.getcwd() if 'work_folder' not in kwargs else kwargs['work_folder']
				self.data_folder = os.getcwd() if 'data_folder' not in kwargs else kwargs['data_folder']
				for tree in nt.trees.values(): # merge data 
					DataBase.py_db.merge_dbs(self.model.database,tree.database,exceptions=[eval(f"tree.{attr}") for attr in nt.prune_trees if hasattr(tree,attr)])
				self.calib_db = None if 'calib_db' not in kwargs else kwargs['calib_db']
				self.export_settings = {'model': 'model' if 'model' not in kwargs else kwargs[model],'model_instances': {}}
			else:
				self.import_from_pickle(os.path.split(pickle_path)[0],os.path.split(pickle_path)[1])

		def import_from_pickle(self,repo,pickle_name):
			with open(repo+'\\'+DB2Gams.end_w_pkl(pickle_name),"rb") as file:
				self.__dict__.update(pickle.load(file).__dict__)
			self.model = DB2Gams.gams_model_py(pickle_path=repo+'\\'+DB2Gams.end_w_pkl(self.export_settings['model']))
			for mi in self.export_settings['model_instances']:
				self.model_instances[mi] = DB2Gams.gams_model(pickle_path=repo+'\\'+DB2Gams.end_w_pkl(self.export_settings['model_instances'][mi]))

		def export(self,pickle_name,repo=None):
			if repo is None:
				repo = self.data_folder
			self.model.export(repo,self.export_settings['model'])
			for mi in self.export_settings['model_instances']:
				self.model_instances[mi].export(repo,self.export_settings['model_instances'][mi])
			temp_empty_attrs = ('model','model_instances','checkpoints','calib_db')
			temp = {attr: getattr(self,attr) for attr in temp_empty_attrs}
			[setattr(self,attr,{}) for attr in temp_empty_attrs]
			with open(repo+'\\'+DB2Gams.end_w_pkl(pickle_name),"wb") as file:
				pickle.dump(self,file)
			[setattr(self,attr,temp[attr]) for attr in temp_empty_attrs];

		def calibrate(self,name_base='baseline',name_calib='calib',solve_sneakily=True,type_='both',kwargs_ns={},kwargs_shock={}):
			"""
			Add subsets for calibration
			"""
			self.globals['sets']['endo_PbT'] = 'endo_PbT' if 'endo_PbT' not in kwargs_ns else kwargs_ns['endo_PbT']
			self.globals['sets']['exo_mu'] = 'exo_mu' if 'exo_mu' not in kwargs_ns else kwargs_ns['exo_mu']
			(self.model.database[self.globals['sets']['endo_PbT']],self.model.database[self.globals['sets']['exo_mu']]) = self.calib_subsets
			self.run_baseline(name=name_base,add_checkpoint=name_base)
			self.create_model_instance(name=name_calib)
			self.checkpoints[name_calib] = self.model_instances[name_calib].ws.add_checkpoint()
			self.model_instances[name_calib].job = self.model_instances[name_calib].ws.add_job_from_string(self.calib_text(), **{'checkpoint': self.checkpoints[name_base]})
			self.model_instances[name_calib].run(run_from_job=True, options_run = {'checkpoint': self.checkpoints[name_calib]})
			if solve_sneakily is True:
				shock_db = self.calib_sneaky_db(self.model_instances[name_calib].out_db,type_=type_,kwargs_shock=kwargs_shock)
				self.model_instances[name_calib].solve_sneakily(from_cp=True,cp_init=self.checkpoints[name_calib],shock_db=shock_db,kwargs_shock=kwargs_shock)

		def run_baseline(self,name='baseline',add_checkpoint=False):
			self.df_write(repo=self.data_folder)
			self.create_model_instance(name=name)
			self.df_run(name=name,add_checkpoint=add_checkpoint)

		def calib_sneaky_db(self,baseline_db,type_='both',kwargs_shock={}):
			"""
			Create a database with linearly-spaced grids of exogenous variables in the baseline solution (baseline_db),
			and some target database (self.calib_db). This db is used to loop-over to sneak up on the solution.
			"""
			kwargs_shock['clean_up'],kwargs_shock['return_dict'] = False,True
			shock_db,kwargs_shock = ShockFunction.solve_sneaky_db(baseline_db,self.calib_db,**kwargs_shock)
			TC = (shock_db[self.globals['vars']['qD']+'_loopval']*shock_db[self.globals['vars']['PwT']+'_loopval']).groupby(kwargs_shock['loop_name']).sum() 
			PbT,qS = shock_db[self.globals['vars']['PbT']+'_loopval'],shock_db[self.globals['vars']['qS']+'_loopval']
			p0,pT = PbT.xs(shock_db[kwargs_shock['loop_name']][0],level=kwargs_shock['loop_name']),PbT.xs(shock_db[kwargs_shock['loop_name']][-1],level=kwargs_shock['loop_name'])
			q0,qT = qS.xs(shock_db[kwargs_shock['loop_name']][0],level=kwargs_shock['loop_name']),qS.xs(shock_db[kwargs_shock['loop_name']][-1],level=kwargs_shock['loop_name'])
			Delta = balanced_loop(PbT,qS,shock_db[kwargs_shock['loop_name']],TC,type_=type_)
			var = self.globals['vars']['PbT']+'_loopval'
			if type_!='price':
				shock_db[var] = ( (Delta * pd.Series(1, index=shock_db[var].index)) * shock_db[var].xs(shock_db[kwargs_shock['loop_name']][-1],level=kwargs_shock['loop_name'])+
								(1-Delta * pd.Series(1, index=shock_db[var].index)) * shock_db[var].xs(shock_db[kwargs_shock['loop_name']][0],level=kwargs_shock['loop_name']) )
				shock_db[var].attrs['type'] = 'parameter'
			var = self.globals['vars']['qS']+'_loopval'
			if type_!='quant':
				shock_db[var] = ( (Delta * pd.Series(1, index=shock_db[var].index)) * shock_db[var].xs(shock_db[kwargs_shock['loop_name']][-1],level=kwargs_shock['loop_name'])+
								(1-Delta * pd.Series(1, index=shock_db[var].index)) * shock_db[var].xs(shock_db[kwargs_shock['loop_name']][0],level=kwargs_shock['loop_name']) )
				shock_db[var].attrs['type'] = 'parameter'
			var,subset = self.globals['vars']['PbT']+'_loopval',self.globals['vars']['PbT']+'_subset'
			shock_db[var] = shock_db[var][~shock_db[var].index.get_level_values(self.globals['sets']['n']).isin(baseline_db[self.globals['sets']['endo_PbT']])]
			shock_db[subset] = shock_db[var].index.droplevel(kwargs_shock['loop_name']).unique()
			shock_db.merge_internal(priority='replace')
			return shock_db

		@property
		def calib_subsets(self):
			"""
			Return subsets used for calibration.
			"""
			endo_pbt,exo_mu = empty_index(self.model.database[self.globals['sets']['out']]),empty_index(self.model.database[self.globals['sets']['map_all']])
			for tree in self.locals:
				if self.locals[tree]['type_io']=='input':
					endo_pbt = endo_pbt.union(self.model.database[self.locals[tree]['tree_out']])
				elif self.locals[tree]['type_io']=='output':
					map_ = self.model.database[self.locals[tree]['map_']]
					tree_out = self.model.database[self.locals[tree]['tree_out']]
					for x in self.model.database[self.locals[tree]['i_tree_kno']]:
						z = map_[(map_.get_level_values(self.globals['sets']['nn'])==x) & (map_.get_level_values(self.globals['sets']['n']).isin(tree_out))]
						endo_pbt = endo_pbt.insert(0,z.get_level_values(self.globals['sets']['n'])[0])
						exo_mu = exo_mu.insert(0,z[0])
			return endo_pbt,exo_mu

		def calib_text(self):
			return f"""
			{self.aux_write('qS',l='.fx')}$({self.aux_write('out')}) = {self.aux_write('qS',l='.l')};
			{self.aux_write('qD',l='.fx')}$({self.aux_write('inp')}) = {self.aux_write('qD',l='.l')};
			{self.aux_write('mu',l='.lo')}$({self.aux_write('map_all')} and ({self.aux_write('inp')} or {self.aux_write('out')})) = 0;
			{self.aux_write('mu',l='.up')}$({self.aux_write('map_all')} and ({self.aux_write('inp')} or {self.aux_write('out')})) = inf;
			{self.aux_write('PbT',l='.fx')}$({self.aux_write('out')}) = {self.aux_write('PbT',l='.l')};
			{self.aux_write('mu',l='.fx')}$({self.aux_write('exo_mu')}) = {self.aux_write('mu',l='.l')};
			{self.aux_write('PbT',l='.lo')}$({self.aux_write('endo_PbT')}) = -inf;
			{self.aux_write('PbT',l='.up')}$({self.aux_write('endo_PbT')}) = inf;
			solve {self.model.settings.name} using CNS;
			{DB2Gams.update_solvestat(self.model.settings.name) if self.model.settings.solvestat is True else ''}"""

		def create_model_instance(self,name='temp'):
			"""
			Create model instance with working-folder at repo.
			"""
			self.model_instances[name] = DB2Gams.gams_model(self.work_folder,settings=self.model.settings)
			self.export_settings['model_instances'][name] = name

		def df_run(self,name='temp',options_add={},options_run={},add_checkpoint=False):
			if add_checkpoint is not False:
				self.checkpoints[add_checkpoint] = self.model_instances[name].ws.add_checkpoint()
				options_run = {**options_run,**{'checkpoint': self.checkpoints[add_checkpoint]}}
			self.model_instances[name].run(model=self.model.settings,options_add=options_add,options_run=options_run)

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
			self.initialized=True

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
			out = {'domains': None, 'conditions': None, 'vartext': None}
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
