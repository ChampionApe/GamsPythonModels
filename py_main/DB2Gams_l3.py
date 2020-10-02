from DB2Gams_l2 import *
import ShockFunction

class gams_model:
	"""
	Databases: Dictionary with databases. Keys = name of database, value∈{path to gdx file, GamsDatabase, or a DataBase.py_db}.
	work_folder: Point to folder where the model should be run from. 
	opt_file: Add options file. If None, a default options file is written (see default_opt).
	"""
	def __init__(self,work_folder,opt_file=None,execute_name='CollectAndRun.gms'):
		self.work_folder = work_folder
		self.execute_name = execute_name
		self.dbs = {}
		self.ws = GamsWorkspace(working_directory = self.work_folder)
		if opt_file is None:
			self.opt = default_opt(self.ws,name='temp.opt')
		else:
			self.opt = self.ws.add_options(opt_file=opt_file)

	def upd_databases(self,merge_internal=True,from_gdx=False):
		"""
		Read in databases, export to work_folder, and add to GamsWorkspace.
		"""
		for database in self.settings.databases:
			if merge_internal is True:
				self.settings.databases[database].merge_internal()
			if from_gdx is True:
				self.settings.databases[database].db_Gdx.export(self.work_folder+'\\'+end_w_gdx(database))
				self.dbs[database] = self.ws.add_database_from_gdx(self.work_folder+'\\'+end_w_gdx(database))
			else:
				self.dbs[database] = self.ws.add_database(source_database=self.settings.databases[database].db_Gdx.database)

	def run(self,model=None,run_from_job=False,options_add={},options_run={}):
		"""
		Create Model instance and run.
		"""
		if run_from_job is False:
			self.model_instance(model)
			self.compile_collect_file()
			self.add_job(options_add)
		self.run_job(options_run)
		self.out_db = DataBase.py_db(database_gdx=self.job.out_db,default_db='db_Gdx')

	def solve_sneaky(self,db_star,n_steps,update_vars='All',shock_name='shock',loop_name='l1',model=None,run_from_job=False,options_add={},options_run={},cp=None):
		"""
		solve_sneaky adjusts a number of exogenous values gradually towards a new level. More specifically:
			(1) Add a checkpoint if one is not passed. (2) run baseline model with checkpoint. (3) Create database with parameters to loop through (shock_db). 
			(4) Export shock-database to working_folder. (5) Create shock-instance and settings for it. 
		"""
		if cp is None:
			cp = self.ws.add_checkpoint()
		self.run(model=model,run_from_job=run_from_job,options_add=options_add,options_run={**options_run,**{'checkpoint': cp}})
		if update_vars == 'All':
			update_vars = db_star.variables['variables']
		shock_db = ShockFunction.solve_sneaky_db(self.out_db,db_star,update_vars,shock_name,n_steps,loop_name)
		shock_db.db_other.export(self.work_folder+'\\'+shock_db.name+'.gdx')
		shock = ShockFunction.AddShocks(self.settings.name,shock_db,loop_name)
		shock.UpdateExoVarsAndSolve(self)
		for var in update_vars:
			shock.UEVAS_adjVar(var,var+'_loopval',conditions=shock_db.get(var+'_subset').to_str)
		self.opt.defines[shock_name] = shock_db.name+'.gdx'
		shock.UEVAS_2gmy(self.work_folder+'\\'+shock.shock_gm.database.name)
		self.job = self.ws.add_job_from_file(shock.gms,cp)
		self.run(run_from_job=True)

	def model_instance(self,gams_settings):
		"""
		Create instance of model using gams_settings (See the class gams_settings below).
		(1) Adds settings to the .model attribute.
		(2) Writes 'placeholders' used in the gams code to the opt.file; places where %PLACEHOLDER% is used. 
		(3) If a run_file is included (part where statement of fixing and solve statement is included), the
			attribute self.model.run_file = NAMEOFFILE. If a run_file is not included, a default run_file
			is created from a number of settings in *gams_settings* as well. See write_run_file() for more.
		(4) If a collect_file is included (part where $IMPORT of components are called), the attribute 
			self.model.collect_file = NAMEOFFILE. If a collect_file is not included, a default file is created.
			See write_collect_file() for more.
		(5) The relevant files for running the model are copied to the work_folder, ready to execute.
		"""
		self.settings = gams_settings
		self.upd_databases()
		self.update_placeholders()
		if self.settings.run_file is None:
			self.write_run_file()
		if self.settings.collect_file is None:
			self.write_collect_file()
		for file in self.settings.files:
			if not os.path.isfile(self.work_folder+'\\'+end_w_gms(file)):
				shutil.copy(self.settings.files[file]+'\\'+end_w_gms(file),self.work_folder+'\\'+end_w_gms(file))

	def compile_collect_file(self):
		with open(self.work_folder+'\\'+end_w_gms(self.settings.collect_file).replace('.gms','.gmy'), "w") as file:
			file.write(Precompiler(self.work_folder+'\\'+end_w_gms(self.settings.collect_file))())
		return self.work_folder+'\\'+end_w_gms(self.settings.collect_file).replace('.gms','.gmy')

	def add_job(self,options={}):
		"""
		Given a model_instance is created, this creates a GamsJob by compiling the self.model.collect_file
		using Precompiler from the dreamtools package. The GamsJob is added as an attribute self.job.
		"""
		self.compile_collect_file()
		self.job = self.ws.add_job_from_file(self.work_folder+'\\'+end_w_gms(self.settings.collect_file).replace('.gms','.gmy'),**options)
		return self.job

	def run_job(self,options={}):
		"""
		Add options using dict with key = option_name, value = option.
		"""
		self.job.run(self.opt,databases=list(self.dbs.values()),**options)

	def update_placeholders(self):
		"""
		Add placeholders to the options-file.
		"""
		[self.add_placeholder(placeholder,self.settings.placeholders[placeholder]) for placeholder in self.settings.placeholders];

	def add_placeholder(self,placeholder,db):
		"""
		Placeholder is a dict with keys 'name' and 'db'. The value for 'name' is the placeholder used in the Gams code.
		The value for 'db' is the name of the database used when initializing the 'databases' attribute in the gams_model.
		NB: Currently the placeholders only include names of databases. Straightforward to extend this to more general case.
		"""
		self.opt.defines[placeholder] = self.dbs[db].name

	def write_run_file(self):
		"""
		Writes a run_file for the code. This includes:
		(1) If a list of exogenous groups are included in the list self.model.g_exo, these are included in a $FIX statement.
		(2) If a list of endogenous groups are included in the list self.model.g_endo, these are included in an $UNFIX statement.
		(3) If a list of block names are included in the list self.model.blocks, these are used to define a model with name self.model.name.
		(4) If a specific solve statement is included in self.model.solve, this is used; otherwise a default solve statement is included.
		(5) Once the run_file has been written, the attribute is set to the new file name, and added to the dictionary of model instance files.
		"""
		with open(self.work_folder+'\\'+'RunFile.gms', "w") as file:
			if self.settings.g_exo is not None:
				file.write("$FIX {gnames};\n\n".format(gnames=', '.join(self.settings.g_exo)))
			if self.settings.g_endo is not None:
				file.write("$UNFIX {gnames};\n\n".format(gnames=', '.join(self.settings.g_endo)))
			if self.settings.blocks is not None:
				file.write("$Model {mname} {blocks};\n\n".format(mname=self.settings.name, blocks=', '.join(self.settings.blocks)))
			if self.settings.solve is None:
				file.write(default_solve(self.settings.name))
			else:
				file.write(self.settings.solve)
		self.settings.run_file = 'RunFile.gms'
		self.settings.files['RunFile.gms'] = self.work_folder

	def write_collect_file(self):
		"""
		Writes a collect_file for the code. This includes:
		(1) The start of the code (root_file) can either be default (see read_root()), or the user can
			supply its own string in self.model.root_file (NB: A file option should be included here as well).
		(2) Then $IMPORT statements are included for all files in self.model.files (in the sequence they appear).
		(3) If the run_file is not included in the self.model.files, it is added in the end.
		(4) The attribute self.model.collect_file is updated to point to the collect_file.
		"""
		with open(self.work_folder+'\\'+self.execute_name, "w") as file:
			file.write(self.settings.write_collect_and_run_file(self.execute_name))


class condition_tree:
	"""
	Small class of nesting tree for writing conditions.
	"""
	def __init__(self,tree=None,max_=10):
		self.tree = tree
		self.mapping_from_tree()
		self.aggregates()
		self.inputs()
		self.all_elements()
		self.outputs()
		self.max_depth = max_
		self.check_map = pd.Series(False,index=self.map_)
		self.check_map[self.check_map.index.get_level_values('in').isin(self.inp)] = True
		self.check_agg = pd.Series(False,index=self.agg)
		self.write_element = {x:'' for x in self.all}
		for x in self.inp:
			self.write_element[x] = x
		self.incomplete = True

	def mapping_from_tree(self):
		temp = []
		for key in self.tree:
			temp += [(value,key) for value in self.tree[key]['vals']]
		self.map_ = pd.MultiIndex.from_tuples(temp,names=['in','agg'])

	def aggregates(self):
		self.agg = self.map_.get_level_values('agg').unique()

	def inputs(self):
		self.inp = pd.Index(set(self.map_.get_level_values('in'))-set(self.agg),name='in')

	def all_elements(self):
		self.all = pd.Index(self.agg.union(self.inp), name='all')

	def outputs(self):
		self.out = list((set(self.map_.get_level_values('agg'))-set(self.map_.get_level_values('in'))))[0]

	def write_condition(self):
		count = 0
		while self.incomplete:
			count += 1
			pre_update = self.check_agg.copy()
			self.update_aggs()
			for x in self.check_agg.index:
				if pre_update[x]!=self.check_agg[x]:
					self.write_nest(x)
					self.update_map(x)
			if count==self.max_depth:
				raise RuntimeError("Iterations exceeded max_depth.")
			if self.check_agg[self.out]:
				self.incomplete = False
		return self.write_element[self.out]

	def write_nest(self,agg):
		self.write_element[agg] = '({x})'.format(x=self.tree[agg]['cond'].join([self.write_element[x] for x in self.tree[agg]['vals']]))

	def update_aggs(self):
		[self.update_agg(agg) for agg in self.agg];

	def update_agg(self,agg):
		self.check_agg[agg] = (self.check_map[self.check_map.index.get_level_values('agg')==agg]==True).all()

	def update_map(self,inp):
		self.check_map[self.check_map.index.get_level_values('in')==inp] = True

	def agg_from_inp(self,inp):
		return self.map_[self.map_.get_level_values('in')==inp].get_level_values('agg')[0]