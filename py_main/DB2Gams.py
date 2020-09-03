import os, shutil, pickle, pandas as pd, DataBase, regex_gms
from gams import *
from dreamtools.gams_pandas import *
from dreamtools.gamY import Precompiler

def database_type(database):
	if isinstance(database,str):
		return DataBase.py_db(file_path=database)
	elif isinstance(database,GamsDatabase):
		return DataBase.py_db(database_gdx=database)
	elif isinstance(database,DataBase.py_db):
		return database

def end_w_y(x,y):
	if x.endswith(y):
		return x
	else:
		return x+y
def end_w_gdx(x):
	return end_w_y(x,'.gdx')
def end_w_gms(x):
	return end_w_y(x,'.gms')
def end_w_pkl(x):
	return end_w_y(x,'.pkl')

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

	def upd_databases(self):
		"""
		Read in databases, export to work_folder, and add to GamsWorkspace.
		"""
		for database in self.settings.databases:
			self.settings.databases[database].db_Gdx.export(self.work_folder+'\\'+end_w_gdx(database))
			self.dbs[database] = self.ws.add_database_from_gdx(self.work_folder+'\\'+end_w_gdx(database))

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

class mgs:
	"""
	Collection of methods for merging gams_settings (classes) into one, to run combined models.
	"""
	@staticmethod
	def merge(ls,merge_dbs_adhoc=True,name=None,run_file=None,solve=None):
		return gams_settings(name = mgs.merge_names(ls,name=name),
						 	databases = mgs.merge_databases(ls,merge_dbs_adhoc=merge_dbs_adhoc),
						 	placeholders = mgs.merge_placeholders(ls),
						 	run_file = mgs.merge_run_files(ls,run_file),
						 	blocks = mgs.merge_blocks(ls),
						 	g_endo = mgs.merge_g_endo(ls),
						 	g_exo  = mgs.merge_g_exo(ls),
						 	solve  = mgs.merge_run_files(ls,solve),
						 	files  = mgs.merge_files(ls),
						 	collect_files = mgs.merge_collect_files(ls))

	@staticmethod
	def merge_names(ls,name):
		return '_'.join([s.name for s in ls] if name is None else name)

	@staticmethod
	def merge_databases(ls,merge_dbs_adhoc):
		"""
		Note that if merge_dbs_adhoc is True the databases that share the same name are merged. 
		However, if symbols overlap in the various databases, these are merged as well. Thus 
		the underlying data may be altered as well. 
		"""
		if merge_dbs_adhoc is True:
			databases = {}
			for database_name in set([x for s in ls for x in s.databases]):
				db_temp = DataBase.py_db(default_db='db_Gdx')
				for database in [s.databases[x] for s in ls for x in s.databases if x==database_name]:
					DataBase.py_db.merge_dbs(db_temp.db_Gdx,database)
				databases[database_name] = db_temp
		else:
			if len(set([x for s in ls for x in s.databases]))==len([x for s in ls for x in s.databases]):
				databases = {key: value for s in ls for key,value in s.databases.items()}
			else:
				raise ValueError(f"Databases overlap in names. Consider setting merge_dbs_adhoc=True, or in another way merge databases")
		return databases

	@staticmethod
	def merge_placeholders(ls):
		return {key: value for s in ls for key,value in s.placeholders.items()}
	@staticmethod
	def merge_run_files(ls,run_file):
		return None if run_file is None else run_file
	@staticmethod
	def merge_blocks(ls):
		return [x for y in ls for x in y.blocks]
	@staticmethod
	def merge_g_endo(ls):
		return [x for y in ls for x in y.g_endo]
	@staticmethod
	def merge_g_exo(ls):
		return [x for y in ls for x in y.g_exo]
	@staticmethod
	def merge_files(ls):
		return {key: value for s in ls for key,value in s.files.items()}
	@staticmethod
	def merge_collect_files(ls):
		return [x for y in ls for x in y.collect_files]

class gams_settings:
	"""
	settings for gams model. The specific use can be read from the application in the gams_model class above.
	"""
	def __init__(self,name="somename",pickle_path=None,placeholders=None,databases=None,run_file=None,blocks=None,g_endo=[],g_exo=[],solve=None,files={},collect_file=None,collect_files=None,root_file=None,db_export=None):
		if pickle_path is None:
			self.name = name # Name of model instance
			self.placeholders = placeholders
			self.databases = databases
			self.run_file = run_file
			self.blocks = blocks
			self.g_endo = g_endo
			self.g_exo = g_exo
			self.solve = solve
			self.files = files
			self.collect_file = collect_file
			self.collect_files = collect_files
			self.root_file = root_file
			self.db_export = db_export
		else:
			self.import_from_pickle(os.path.split(pickle_path)[0],os.path.split(pickle_path)[1])

	def import_from_pickle(self,repo,pickle_name):
		with open(repo+'\\'+end_w_pkl(pickle_name), "rb") as file:
			self.__dict__.update(pickle.load(file).__dict__)
		for db in self.db_export:
			self.databases = {db: DataBase.py_db(file_path=self.db_export[db],default_db='db_Gdx') for db in self.db_export}
		return self

	def export(self,repo,pickle_name,inplace_db = False):
		self.db_export = {db: self.export_db(repo,db) for db in self.databases}
		if inplace_db:
			temp = None
		else:
			temp = self.databases
		self.databases = None
		with open(repo+'\\'+end_w_pkl(pickle_name), "wb") as file:
			pickle.dump(self,file)
		self.databases = temp

	def export_db(self,repo,db):
		self.databases[db] = database_type(self.databases[db])
		self.databases[db].default_db = 'db_pd'
		self.databases[db].merge_internal()
		self.databases[db].default_db = 'db_Gdx'
		self.databases[db].db.export(repo+'\\'+end_w_gdx(db))
		return repo+'\\'+end_w_gdx(db)

	def write_collect_files(self,name):
		"""
		Write a file that collects other files, but not the only one that is used in execution. 
		This collect $import statements, but does not add the self.run_file nor the self.root_file.
		"""
		out_str = ''
		if self.collect_files is None:
			for x in self.files:
				out_str += f"$IMPORT {x};\n"
			self.collect_files = [name]
		else:
			for x in self.collect_files:
				out_str += f"$IMPORT {x};\n"
			self.collect_files += [name]
		return out_str

	def write_collect_and_run_file(self,name):
		out_str = ''
		if self.root_file is None:
			out_str += read_root()
		else:
			out_str += read_root(default=False,text=self.root_file)
		if self.collect_files is None:
			for x in self.files:
				out_str += f"$IMPORT {x};\n"
			if self.run_file not in self.files:
				if self.run_file is not None:
					out_str += f"$IMPORT {self.run_file};\n"
		else:
			for x in self.collect_files:
				out_str += f"$IMPORT {x};\n"
			if self.run_file not in self.collect_files:
				if self.run_file is not None:
					out_str += f"$IMPORT {self.run_file};\n"
		self.collect_file = name
		return out_str


class gams_model_py:
	"""
	A Python object with all the information to write relevant files and settings for a gams_model instance.
	This class has the writing methods included.
	"""
	def __init__(self,database,gsettings=None,blocks_text=None,functions=None,groups={},exceptions=[],exceptions_load=[],components = {},export_files = None):
		self.database = database
		if gsettings is None:
			self.settings = gams_settings(name=self.database.name,placeholders=self.default_placeholders(),databases={self.database.name: self.database},files={})
		self.groups = groups
		self.exceptions=exceptions
		self.exceptions_load = exceptions_load
		self.components = components
		self.export_files = export_files
		self.blocks = blocks_text
		self.functions = functions

	def default_placeholders(self):
		return {self.database.name: self.database.name}

	def run_default(self,repo,export_settings=False):
		if not os.path.exists(repo):
			os.makedirs(repo)
		self.write_default_components()
		self.default_export(repo,export_settings=export_settings)

	def write_default_components(self):
		self.functions = gams_model_py.merge_functions(regex_gms.functions_from_str(default_user_functions()),self.functions)
		self.components['functions'] = self.write_functions()
		self.components['sets'] = self.write_sets()
		self.components['alias'] = self.write_aliased_sets()
		self.components['sets_other'] = self.write_sets_other()
		self.components['alias_other'] = self.write_aliased_sets_other()
		self.components['sets_load'] = self.write_sets_load(self.database.name)
		self.components['parameters'] = self.write_parameters()
		self.components['parameters_load'] = self.write_parameters_load(self.database.name)
		self.components['groups'] = self.write_groups()
		self.components['groups_load'] = self.write_groups_load(self.database.name)
		self.components['blocks'] = self.blocks

	@staticmethod
	def merge_functions(functions1,functions2):
		"""
		Merge two dictionaries with potentially overlapping keys; if keys are overlapping, keep values from dict = function1.
		"""
		if functions1 is None:
			return functions2
		elif functions2 is None:
			return functions1 
		else:
			return {**functions1,**{key: functions2[key] for key in set(functions2.keys())-set(functions1.keys())}}

	def default_export(self,repo,export_settings=False):
		self.export_components(self.default_files_components(repo))
		self.add_default_collect(self.settings.name+'_CollectFile.gms',repo)
		if export_settings:
			self.settings.export(repo,self.settings.name)

	def add_default_collect(self,name,repo):
		with open(repo+'\\'+end_w_gms(name),"w") as file:
			file.write(self.settings.write_collect_files(name))
		self.settings.files[end_w_gms(name)] = repo

	def default_files_components(self,repo):
		self.export_files = {self.settings.name+'_functions.gms': {'repo': repo, 'components': ['functions']},
							 self.settings.name+'_sets.gms': {'repo': repo, 'components': ['sets','alias','sets_other','alias_other','sets_load']},
							 self.settings.name+'_parameters.gms': {'repo': repo, 'components': ['parameters','parameters_load']},
							 self.settings.name+'_groups.gms': {'repo': repo, 'components': ['groups','groups_load']},
							 self.settings.name+'_blocks.gms': {'repo': repo, 'components': ['blocks']}}
		return self.export_files

	def export_components(self,files,add_to_settings=True):
		"""
		Files is a dictionary where:
			keys = file names.
			dict[file]: Dictionary with keys = {'repo','components'}. 
		"""
		for x in files:
			with open(files[x]['repo']+'\\'+end_w_gms(x),"w") as file:
				[file.writelines(self.components[c]) for c in files[x]['components']];
			if add_to_settings:
				self.settings.files[end_w_gms(x)] = files[x]['repo']

	def add_group_to_groups(self,group,gname):
		self.groups[gname] = {var: self.var_in_group(var,group[var]['conditions']) for var in group}

	def var_in_group(self,x,conditions):
		var = self.database.get(x,conditions=conditions)
		return {'domains': var.to_string('dom'), 'conditions': var.to_string('cond')}

	def write_sets(self):
		"""
		If there are no additional fundamental sets to be added → return ''
		If there are, declare them.
		"""
		if bool(set(self.database.sets['sets'])-set(self.database.aliased_sets_all)-set(self.exceptions)) is False:
			return ''
		else:
			out_str = 'sets\n'
			for x in (set(self.database.sets['sets'])-set(self.database.aliased_sets_all)-set(self.exceptions)):
				out_str += '\t'+self.database.get(x).to_str+'\n'
			out_str = out_str+';\n\n'
			return out_str

	def write_aliased_sets(self):
		out_str = ''
		sets_w_alias = [x for x in self.database.alias_all if x in self.database.sets['sets']]
		for x in set(sets_w_alias)-set(self.exceptions): # is the set itself in 'exceptions'?
			if bool(set(self.database.alias_all[x])-set(self.exceptions)) is not False: # is the aliased sets in 'exceptions'?
				out_str += 'alias({x},{y});\n'.format(x=x,y=','.join(list(set(self.database.alias_all[x])-set(self.exceptions)))) # write alias statement
		return out_str+'\n'

	def write_sets_other(self):
		if bool(set(self.database.sets_flat)-set(self.database.sets['sets'])-set(self.exceptions)-set(self.database.aliased_sets_all)) is False:
			return ''
		else:
			out_str = 'sets\n'
			for x in (set(self.database.sets_flat)-set(self.database.sets['sets'])-set(self.exceptions)-set(self.database.aliased_sets_all)):
				out_str += '\t'+self.database.get(x).to_str+'\n'
			out_str = out_str+';\n\n'
			return out_str

	def write_aliased_sets_other(self):
		out_str = ''
		sets_other_w_alias = [x for x in self.database.alias_all if x not in self.database.sets['sets']]
		for x in set(sets_other_w_alias)-set(self.exceptions):
			if bool(set(self.database.alias_all[x])-set(self.exceptions)) is not False:
				out_str += 'alias({x},{y});\n'.format(x=x,y=','.join(list(set(self.database.alias_all[x])-set(self.exceptions))))
		return out_str+'\n'

	def write_sets_load(self,gdx,onmulti=True):
		if bool(set(self.database.sets_flat)-set(self.exceptions_load)-set(self.database.aliased_all_all)) is False:
			return ''
		else:
			out_str = '$GDXIN %'+gdx+'%\n'
			if onmulti:
				out_str += '$onMulti\n'
			for x in set(self.database.sets['sets'])-set(self.exceptions_load)-set(self.database.aliased_all_all):
				out_str += '$load '+x+'\n'
			for x in set(self.database.sets['subsets'])-set(self.exceptions_load)-set(self.database.aliased_all_all):
				out_str += '$load '+x+'\n'
			for x in set(self.database.sets['mappings'])-set(self.exceptions_load)-set(self.database.aliased_all_all):
				out_str += '$load '+x+'\n'
			out_str += '$GDXIN\n'
			if onmulti:
				out_str += '$offMulti\n'
			return out_str

	def write_parameters(self):
		if bool(set(self.database.parameters_flat)-set(self.exceptions)) is False:
			return ''
		else:
			out_str = 'parameters\n'
			for x in (set(self.database.parameters_flat)-set(self.exceptions)):
				out_str += '\t'+self.database.get(x).to_str+'\n'
			out_str += ';\n\n'
		return out_str

	def write_parameters_load(self,gdx,onmulti=True):
		if bool(set(self.database.parameters_flat)-set(self.exceptions_load)) is False:
			return ''
		else:
			out_str = '$GDXIN %'+gdx+'%\n'
			if onmulti:
				out_str += '$onMulti\n'
			for x in set(self.database.parameters_flat)-set(self.exceptions_load):
				out_str += '$load '+x+'\n'
			if onmulti:
				out_str += '$offMulti\n'
			return out_str

	def write_groups(self):
		out_str = ''
		for group in self.groups:
			out_str += self.write_group(group)
		return out_str

	def write_group(self,group):
		out_str = '$GROUP '+group+'\n'
		for var in self.groups[group]:
			out_str += '\t'+self.database.get(var,conditions=self.groups[group][var]['conditions']).to_str+' ""\n'
		out_str += ';\n\n'
		return out_str

	def write_groups_load(self,gdx):
		out_str = ''
		for group in self.settings.g_endo:
			out_str += self.write_group_load(group,gdx,level='level')
		for group in set(self.groups.keys())-set(self.settings.g_endo):
			out_str += self.write_group_load(group,gdx)
		return out_str

	def write_group_load(self,group,gdx,level='fixed'):
		if level=='fixed':
			out_str = '@load_fixed({group},%qmark%%{gdx}%");\n'.format(group=group,gdx=gdx)
		elif level=='level':
			out_str = '@load_level({group},%qmark%%{gdx}%");\n'.format(group=group,gdx=gdx)
		return out_str

	def write_functions(self):
		out_str = ''
		if self.functions is not None:
			for func in self.functions:
				out_str += self.functions[func]+'\n\n'
		return out_str

def read_root(default=True,file=False,text=False):
	if default:
		return default_Root()
	elif file is not False:
		with open(file,"r") as file:
			return file.read()
	elif text is not False:
		return text

def read_user_functions(default=True,file=False,text=False):
	if default:
		return default_user_functions()
	elif file is not False:
		with open(file,"r") as file:
			return file.read()
	elif text is not False:
		return text

def default_solve(model):
	return """solve {a} using CNS;
""".format(a=model)

def default_Root():
	return """# Root File for model
OPTION SYSOUT=OFF, SOLPRINT=OFF, LIMROW=0, LIMCOL=0, DECIMALS=6;
$SETLOCAL qmark ";
"""

def default_user_functions():
	return """
# User defined functions:
$FUNCTION load_level({group}, {gdx}):
  $offlisting
  $GROUP __load_group {group};
  $LOOP __load_group:
    parameter load_{name}{sets} "";
    load_{name}{sets}$({conditions}) = 0;
  $ENDLOOP
  execute_load {gdx} $LOOP __load_group: load_{name}={name}.l $ENDLOOP;
  $LOOP __load_group:
    {name}.l{sets}$({conditions}) = load_{name}{sets};
  $ENDLOOP
  $onlisting
$ENDFUNCTION
$FUNCTION load_fixed({group}, {gdx}):
  $offlisting
  $GROUP __load_group {group};
  $LOOP __load_group:
    parameter load_{name}{sets} "";
    load_{name}{sets}$({conditions}) = 0;
  $ENDLOOP
  execute_load {gdx} $LOOP __load_group: load_{name}={name}.l $ENDLOOP;
  $LOOP __load_group:
    {name}.fx{sets}$({conditions}) = load_{name}{sets};
  $ENDLOOP
  $onlisting
$ENDFUNCTION
"""

def default_opt(ws,name="options.opt"):
	opt = ws.add_options()
	opt.all_model_types = "CONOPT4" # use solver
	file = open(os.path.join(ws.working_directory, name), "w") # open options file and write:
	file.write("\
		# Tell the solver that the system is square \n\
		# lssqrs = t \n\
		\n\
		# Keep searching for a solution even if a bound is hit (due to non linearities) \n\
		lmmxsf = 1 \n\
		\n\
		# Time limit in seconds \n\
		rvtime = 1000000 \n\
		reslim = 1000000 \n\
		\n\
		# Limit for slow progress, Range: [12,MAXINT], Default: 12 \n\
		# lfnicr = 100 \n\
		\n\
		# Optimality tolerance for reduced gradient \n\
		#  RTREDG = 1.e-9 \n\
		\n\
		# Absolute pivot tolerance, Range: [2.2e-16, 1.e-7], Default: 1.e-10 \n\
		# rtpiva = 2.22044605e-16 \n\
		Threads = 4 \n\
		THREADF=4 \n\
		")
	file.close()
	opt.file = 1
	return opt

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