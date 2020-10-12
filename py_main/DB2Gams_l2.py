from DB2Gams_l1 import *
import os, shutil, pickle, pandas as pd, regex_gms


class gams_settings:
	"""
	settings for gams model. The specific use can be read from the application in the gams_model class above.
	"""
	def __init__(self,name="somename",pickle_path=None,placeholders=None,databases=None,run_file=None,blocks=None,g_endo=[],g_exo=[],solve=None,solvestat=True,files={},collect_file=None,collect_files=None,root_file=None,db_export=None):
		if pickle_path is None:
			self.name = name # Name of model instance
			self.placeholders = placeholders
			self.databases = databases
			self.run_file = run_file
			self.blocks = blocks
			self.g_endo = g_endo
			self.g_exo = g_exo
			self.solve = solve
			self.solvestat = solvestat
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

	def export_db(self,repo,db,**kwargs):
		self.databases[db] = database_type(self.databases[db])
		return self.databases[db].export(repo,**kwargs)

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

class gams_model_py:
	"""
	A Python object with all the information to write relevant files and settings for a gams_model instance.
	This class has the writing methods included.
	"""
	def __init__(self,database=None,pickle_path=None,gsettings=None,blocks_text=None,functions=None,groups={},exceptions=[],exceptions_load=[],components = {},export_files = None,**kwargs):
		if pickle_path is None:
			self.main_db = database.name
			if gsettings is None:
				self.settings = gams_settings(name=database.name,placeholders={database.name: database.name},databases={database.name: database},files={})
			self.groups = groups
			self.exceptions=exceptions
			self.exceptions_load = exceptions_load
			self.components = components
			self.export_files = export_files
			self.blocks = blocks_text
			self.functions = functions
			self.export_settings = {'settings': 'settings_'+self.settings.name if 'pickle_settings' not in kwargs else kwargs['settings']}
		else:
			self.import_from_pickle(os.path.split(pickle_path)[0],os.path.split(pickle_path)[1])

	def import_from_pickle(self,repo,pickle_name):
		with open(repo+'\\'+end_w_pkl(pickle_name),"rb") as file:
			self.__dict__.update(pickle.load(file).__dict__)
		self.settings = gams_settings(pickle_path=repo+'\\'+self.export_settings['settings'])
		return self

	def export(self,repo,pickle_name):
		self.settings.export(repo,self.export_settings['settings'])
		temp_empty_attrs = ['settings']
		temp = {attr: getattr(self,attr) for attr in temp_empty_attrs}
		[setattr(self,attr,None) for attr in temp_empty_attrs]
		with open(repo+'\\'+end_w_pkl(pickle_name),"wb") as file:
			pickle.dump(self,file)
		[setattr(self,attr,temp[attr]) for attr in temp_empty_attrs];

	@property
	def database(self):
		return self.settings.databases[self.main_db]

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

