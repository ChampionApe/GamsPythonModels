import openpyxl
import pandas as pd
from gams import *
from dreamtools.gams_pandas import *

def type_gams(symbol):
	if isinstance(symbol,gams.GamsVariable):
		if len(symbol)==1:
			return 'scalar_variable'
		else:
			return 'variable'
	elif isinstance(symbol,gams.GamsParameter):
		if len(symbol)==1:
			return 'scalar_parameter'
		else:
			return 'parameter'
	elif isinstance(symbol,gams.GamsSet):
		if len(symbol.domains_as_strings)==1:
			if symbol.domains_as_strings in [['*'], [symbol.name]]:
				return 'set'
			else:
				return 'subset'
		elif symbol.name!='SameAs':
			return 'mapping'

def type_agg(symbol,name=None,param=False):
	if type_py(symbol,name=name,param=param) in ('set','subset','mapping'):
		return 'set'
	elif type_py(symbol,name=name,param=param) in ('parameter','scalar_parameter'):
		return 'parameter'
	elif type_py(symbol,name=name,param=param) in ('variable','scalar_variable'):
		return 'variable'

def type_py(symbol,name=None,param=False):
	if isinstance(symbol,pd.Series):
		try: 
			if symbol.attrs['type']=='parameter':
				return par_or_var(True)
			else:
				return par_or_var(False)
		except KeyError:
			return par_or_var(False)
	elif isinstance(symbol,pd.MultiIndex):
		return 'mapping'
	elif isinstance(symbol,pd.Index):
		return set_or_subset(symbol.name,name)
	elif isinstance(symbol,(int,float,str)):
		return 'scalar_'+par_or_var(param)

def par_or_var(param):
	if param:
		return 'parameter'
	else:
		return 'variable'

def set_or_subset(s_name,name):
	if s_name in ('index_0',name):
		return 'set'
	else:
		return 'subset'

def merge_symbols(s1,s2):
	if isinstance(s1,pd.Series):
		return s1.combine_first(s2)
	elif isinstance(s1,pd.Index):
		return s1.union(s2)
	elif type_py(s1) in ('scalar_variable','scalar_parameter'):
		return s1

def idx(x):
	if isinstance(x,pd.Index):
		return x
	elif isinstance(x,pd.Series):
		return x.index

def domains(x):
	return idx(x).names

def traverse(o, tree_types=(list,tuple,pd.Index)):
    if isinstance(o, tree_types):
        for value in o:
            for subvalue in traverse(value, tree_types):
                yield subvalue
    else:
        yield o

def empty_as_list(x):
	return [] if x is None else x

# Class of items when retrieving from a database:
class gpy_symbol:
	"""
	alias = 
	"""
	def __init__(self,symbol,name=None,param=False,conditions=None,alias=None,alias_domains=None,level=''):
		self.symbol = symbol
		if name is None:
			self.name = self.symbol.name
		else:
			self.name = name
		self.type = type_py(symbol,name=name,param=param)
		self.type_agg = type_agg(symbol,name=name,param=param)
		self.conditions = conditions
		self.alias = alias
		self.alias_domains=alias_domains
		self.level=level

	@property
	def idx(self):
		"""
		Index from symbol
		"""
		return idx(self.symbol)

	@property
	def dom(self):
		"""
		domains from symbol
		"""
		if self.alias_domains is None:
			return domains(self.symbol)
		else:
			return self.alias_domains

	@property
	def to_str(self):
		if self.alias is None:
			if self.conditions is None:
				return self.name+self.level+self.to_string('dom')
			else:
				return self.name+self.level+self.to_string('dom')+'$'+self.to_string('cond')
		else:
			if self.conditions is None:
				return self.alias+self.level+self.to_string('dom')
			else:
				return self.alias+self.level+self.to_string('dom')+'$'+self.to_string('cond')

	def to_string(self,component):
		if self.type in ('set','scalar_variable','scalar_parameter'):
			return ''
		elif component=='dom':
			return '[{x}]'.format(x=','.join(self.dom))
		elif component=='cond':
			if self.conditions is None:
				return ''
			else:
				return '({x})'.format(x=self.conditions)

class db_pd:
	"""
	A very simple pandas database similar to GamsPandasDatabase. 
	"""

	def __init__(self,name=""):
		self.name=name
		self.database = {}

	def __getattr__(self,item):
		return self[item]

	def __getitem__(self,item):
		try:
			return self.database[item]
		except KeyError:
			return None

	def __setitem__(self,name,value):
		self.database[name]=value

	def items(self):
		return self.database.items()

	def keys(self):
		return self.database.keys()

	def values(self):
		return self.database.values()

	def __iter__(self):
		return iter(self.database)

	def __len__(self):
		return len(self.database)

class py_db:
	"""
	Database that encompasses two types of databases: 
		The GamsPandasDatabase defined from the packages dreamtools, and the pandas database defined above.
		The GamsPandasDatabase is defined under 'self.db_Gdx', and the pandas database defined as 'self.db_py'.
		The property 'self.db' is shorthand for the one of the two databases given under 'self.default_db'.
		As alias' are not extracted by Gams, we store a set (multiindex) with the name 'alias_' with mappings
		of names from sets to alias'. Note: The names 'alias_set', and 'alias_maps2' are reserved as the basic
		indices used in the multiindex 'alias_'. 
	"""

	def __init__(self,name=None,file_path=None,database_gdx=None,database_py=None,workspace=None,alias=None,default_db='db_pd'):
		if name is not None:
			self.name=name
		if file_path is None:
			self.db_Gdx = GamsPandasDatabase(database_gdx,workspace)
		else:
			self.db_Gdx = Gdx(file_path,workspace)
		if database_py is None:
			self.db_pd = db_pd()
		else:
			self.db_pd = database_py
		self.default_db = default_db
		if alias is not None:
			alias.names = ['alias_set','alias_map2']
			alias.name = 'alias_'
			py_db.add_or_merge(self.db,alias.get_level_values('alias_set').unique(),'alias_set','first')
			py_db.add_or_merge(self.db,alias.get_level_values('alias_map2').unique(),'alias_map2','first')
			py_db.add_or_merge(self.db,alias,'alias_','first')

	def get(self,x,param=False,conditions=None,alias=None,alias_domains=None,level=''):
		"""
		An important feature is the 'get' function. This initializes the self[item] (which is returned as a pandas index) 
		as an gpy_symbol, giving access to the features defined here.
		Note: 	The alias, and alias_domains statements are particularly important when utilizing the writing facitilities.
				alias: an integer, referring to the list of alias' of the given symbol.
		"""
		return gpy_symbol(self[x],name=x,param=param,conditions=conditions,alias=self.get_alias(x,alias),alias_domains=self.get_alias_domains(x,alias_domains),level=level)

	def get_alias(self,x,alias):
		"""
		if alias is None, return None, else:
			x 		= name of symbol,
			alias 	= integer that returns an alias from a list (see method 'self.alias').
		"""
		if alias is None:
			return None
		else:
			return self.alias(x,alias)

	def get_alias_domains(self,x,alias_domains):
		"""
		If alias_domains is None, return None, else:
			x				= name of symbol,
			alias_domains	= 	list of integers, that returns a list of domain names (see method 'self.alias_domain'),
								or dict with names to replace with IF they appear in the domains.
		"""
		if alias_domains is None:
			return None
		else:
			return self.alias_domain(x,alias_domains)

	@property
	def db(self):
		"""
		Returns the database defined under 'default_db'.
		"""
		return eval('self.{x}'.format(x=self.default_db))

	@property
	def db_other(self):
		"""
		Returns the 'other' database not defined as 'default_db'.
		"""
		return eval('self.{x}'.format(x=self.re_other))

	@property
	def re_other(self):
		if self.default_db=='db_pd':
			return 'db_Gdx'
		else:
			return 'db_pd'

	def __getattr__(self,item):
		return self.db.__getattr__(item)

	def __getitem__(self,item):
		return self.db.__getitem__(item)

	def __setitem__(self,name,value):
		return self.db.__setitem__(name,value)

	def items(self):
		return self.db.items()

	def keys(self):
		return self.db.keys()

	def values(self):
		return self.db.values()

	def __iter__(self):
		return self.db.__iter__()

	def __len__(self):
		return self.db.__len__()
			
	###################################################################################################
	###									 1: A LIST OF PROPERTIES 									###
	###################################################################################################

	@property
	def sets(self):
		"""
		All sets in GamsPandasDatabase or Pandas database, on 'set', 'subset','mapping' types.
		"""
		return {x+'s': [name_ for name_ in self.db if self.get(name_).type==x] for x in ('set','subset','mapping')}

	@property
	def sets_flat(self):
		return [name for name in self.db if self.get(name).type_agg=='set']

	@property
	def variables(self):
		"""
		All variables in GamsPandasDatabase, split into 'scalar_variables' (scalars) and 'variables' (defined over sets). 
		"""
		return {x+'s': [name for name in self.db if self.get(name).type==x] for x in ('scalar_variable','variable')}

	@property
	def variables_flat(self):
		return [name for name in self.db if self.get(name).type_agg=='variable']

	@property
	def parameters(self):
		"""
		All parameters in GamsPandasDatabase, split into 'scalar_par' (scalars) and 'parameters' (defined over sets). 
		"""
		return {x+'s': [name for name in self.db if self.get(name).type==x] for x in ('scalar_parameter','parameter')}

	@property 
	def parameters_flat(self):
		return [name for name in self.db if self.get(name).type_agg=='parameter']

	@property
	def types(self):
		"""
		Dictionary of all symbols in GamsPandasDatabase with 'type' as values.
		"""
		return {name: self.get(name).type for name in self.db}

	def symbols_over_set(self,setname,type_=['variable','parameter']):
		"""
		Return a list of symbols that are defined over the relevant set, considering types included in 'type_'.
		"""
		return [name for name in [x for x in self.types if self.types[x] in type_] if setname in idx(self[name]).names]


	###################################################################################################
	###									 2: DEALING WITH ALIASES 									###
	###################################################################################################

	@property
	def alias_all(self):
		"""
		Returns dictionary with set names w. alias' as keys, and their corresponding alias' names in an index as values.
		"""
		return {} if self['alias_'] is None else {name: self['alias_'].get_level_values(1)[self['alias_'].get_level_values(0)==name] for name in self['alias_'].get_level_values(0).unique()}

	@property
	def aliased_sets_all(self):
		"""
		Return list with all set values that are aliased. 
		"""
		return list(traverse([self.alias_all[key] for key in self.alias_all if key in self.sets['sets']]))

	@property
	def aliased_maps_all(self):
		"""
		Return list of all maps that are aliased 
		"""
		return list(traverse([self.alias_all[key] for key in self.alias_all if key in self.sets['mappings']]))

	@property
	def aliased_all_all(self):
		"""
		Return list of all sets/maps that are aliased.
		"""
		return list(traverse([self.alias_all[key] for key in self.alias_all]))

	###################################################################################################
	###									 2.1: ALIAS METHODS' 										###
	###################################################################################################

	def alias_list(self,x):
		if x in self['alias_set']:
			key_= x
			return [key_]+self['alias_'].get_level_values(1)[self['alias_'].get_level_values(0)==key_].to_list()
		elif x in self['alias_map2']:
			key_ = self['alias_'].get_level_values(0)[self['alias_'].get_level_values(1)==x][0]
			return [key_]+self['alias_'].get_level_values(1)[self['alias_'].get_level_values(0)==key_].to_list()
		elif x in self.sets_flat:
			return [x]
		else: 
			return TypeError(f"{x} is not a set, and can thus not be aliased")

	def alias(self,x,index_):
		"""
		Return list of symbols that are aliased with x, with index_ denoting the integer-index of the list that should be returned.
		If the set is not aliased, it simply returns the set itself. If the symbol is not a set, return TypeError.
		"""
		return self.alias_list(x)[index_]

	def alias_domain(self,x,map_):
		"""
		Return list of symbols in domains with indices map_.
		E.g.: Let x be a variable defined over sets [setname1,setname2]. Both sets have aliases. 
		"""
		if isinstance(map_,(list,tuple,int,pd.Index)):
			return [self.alias(py_db.index(self,x).names[i],map_[i]) for i in range(len(py_db.index(self,x).names))]
		elif isinstance(map_,dict):
			return [x if x not in map_ else map_[x] for x in py_db.index(self,x).names]

	###################################################################################################
	###									3: CREATE/MERGE SYMBOLS/DB	 								###
	###################################################################################################

	@staticmethod
	def create_set(db,name,index,explanatory_text="",texts=None,domains=None):
		"""
		Adjusts the method 'create_set' from GamsPandasDatabase, to define a subset 
		when the index that is passed is not a multiindex, and the name of the symbol 
		does not correspond to the name of the index being passed.
		"""
		if isinstance(index,pd.Index) and not isinstance(index,pd.MultiIndex) and name not in ['index_0',index.name]:
			db.database.add_set_dc(name,[index.name],explanatory_text)
			db.series[name] = index
			return db.series[name]
		else:
			db.create_set(name,index,explanatory_text,texts,domains)

	def merge_internal(self,priority='first'):
		"""
		Merge db_default into db_other.
		"""
		py_db.merge_dbs(self.db_other,self,priority)

	@staticmethod
	def merge_dbs(db1,db2,priority='first'):
		"""
		Merge db2 into db1, with the priority 'first','second' or 'replace'. 
			- 	'first' implies that combining symbols in db1 and db2,
				 the db1 database is primary. 
			- 	'second' implies db2. 
			-	'replace' implies that symbols in db1 are replaced w. db2 when the names overlap. 
		"""
		if isinstance(db1,GamsPandasDatabase):
			[py_db.add_or_merge(db1,db2[name],name,priority) for name in db2.sets['sets']]; # Fundamental sets
			if 'alias_' in db2:
				[py_db.add_or_merge(db1,py_db.create_alias(db2,name,alias),alias,priority) for name in db2.alias_all for alias in db2.alias_all[name]]; # alias'
			[py_db.add_or_merge(db1,db2[name],name,priority) for name in db2 if name not in db2.sets['sets']]; # other symbols
		else:
			[py_db.add_or_merge(db1,db2[name],name,priority) for name in db2];
			if 'alias_' in db2:
				[py_db.add_or_merge(db1,py_db.create_alias(db2,name,alias),alias,priority) for name in db2.alias_all for alias in db2.alias_all[name]];

	@staticmethod
	def create_alias(db,name,alias):
		temp=db[name].copy()
		temp.name = alias
		return temp

	@staticmethod
	def add_or_merge(db1,symbol,name,priority):
		if name in db1:
			if priority=='first':
				db1[name]=merge_symbols(db1[name],symbol)
			elif priority=='second':
				db1[name]=merge_symbols(symbol,db1[name])
			elif priority=='replace':
				db1[name] = symbol
		else:
			py_db.add_symbol(db1,symbol,name)

	@staticmethod
	def add_symbol(db1,symbol,name,param=False):
		if isinstance(db1,GamsPandasDatabase):
			if type_py(symbol,name=name) in ('set','subset','mapping'):
				py_db.create_set(db1,name,symbol)
			elif type_py(symbol,param=param) in ('parameter', 'scalar_parameter'):
				db1.create_parameter(name,data=symbol)
			elif type_py(symbol) in ('variable','scalar_variable'):
				db1.create_variable(name,data=symbol)
		elif isinstance(db1,(db_pd,py_db)):
			db1[name] = symbol

	###################################################################################################
	###									3.1: READ IN FROM EXCEL	 									###
	###################################################################################################

	def read_from_excel(self,xlsx_file,read_type):
		wb = openpyxl.load_workbook(filename=xlsx_file, read_only=True, data_only=True)
		if '1dvars' in read_type:
			py_db.read_1dvars_from_excel(self.db_pd,wb,read_type['1dvars'])
		if 'vars_matrix' in read_type:
			py_db.read_2dvars_from_excel_matrix(self.db_pd,wb,read_type['vars_matrix'])
		if 'vars_panel' in read_type:
			py_db.read_vars_from_excel_panel(self.db_pd,wb,read_type['vars_panel'])
		if 'maps_matrix' in read_type:
			py_db.read_maps_from_excel_matrix(self.db_pd,wb,read_type['maps_matrix'])
		if 'maps_panel' in read_type:
			py_db.read_maps_from_excel_panel(self.db_pd,wb,read_type['maps_panel'])
		if 'subsets' in read_type:
			py_db.read_subsets_from_excel(self.db_pd,wb,read_type['subsets'])
		wb.close()

	@staticmethod 
	def read_subsets_from_excel(db,wb,sheets,priority='second'):
		for sheet in sheets:
			temp = pd.DataFrame(wb[sheet].values)
			symbol = pd.Index(temp.iloc[1:,0],name=temp.iloc[0,0])
			py_db.add_or_merge(db,symbol,sheet,priority)

	@staticmethod
	def read_1dvars_from_excel(db,wb,sheets,priority='second'):
		for sheet in sheets:
			temp = pd.DataFrame(wb[sheet].values)
			if min(temp.shape)>1:
				for x in range(1,temp.shape[1]):
					namevar = temp.iloc[0,1:][x]
					symbol = pd.Series(temp.iloc[1:,x].values, index=pd.Index(temp.iloc[1:,0], name=temp.iloc[0,0].split('/')[0]), name=namevar)
					py_db.add_or_merge(db,symbol,namevar,priority)

	@staticmethod
	def read_2dvars_from_excel_matrix(db,wb,sheets,priority='second'):
		for sheet in sheets:
			temp = pd.DataFrame(wb[sheet].values)
			if min(temp.shape)>1:
				tappy = pd.DataFrame(temp.iloc[1:,1:].values, index = temp.iloc[1:,0], columns=temp.iloc[0,1:]).stack()
				tappy.index.names = temp.iloc[0,0].split('/')
				tappy.name = sheet
				py_db.add_or_merge(db,tappy,sheet,priority)

	@staticmethod
	def gindex_excel(frame,dim_index):
		if dim_index==1:
			return pd.Index(frame.iloc[1:,0], name=frame.iloc[0,0])
		if dim_index>1:
			return pd.MultiIndex.from_frame(frame.iloc[1:,:dim_index], names = list(frame.iloc[0,:dim_index]))

	@staticmethod
	def read_vars_from_excel_panel(db,wb,sheets_nsets,priority='second'):
		for sheet in sheets_nsets:
			temp = pd.DataFrame(wb[sheet].values)
			if temp.shape[0]>1:
				if sheets_nsets[sheet]==0:
					for var in range(len(temp.iloc[0,:])):
						py_db.add_or_merge(db,temp.iloc[1,var],var,priority)
				else:
					index_ = py_db.gindex_excel(temp,sheets_nsets[sheet])
					for var in range(sheets_nsets[sheet], len(temp.iloc[0,:])):
						symbol = pd.Series(temp.iloc[1:,var].values, index=index_, name=temp.iloc[0,var])
						py_db.add_or_merge(db,symbol,temp.iloc[0,var],priority)

	@staticmethod
	def read_maps_from_excel_matrix(db,wb,sheets,priority='second'):
		for sheet in sheets:
			temp = pd.DataFrame(wb[sheet].values)
			if temp.shape[0]>1:
				common_set = temp.iloc[0,0].split('/')[0]
				for x in range(1,len(temp.iloc[0,1:])):
					maps_to = temp.iloc[0,x]
					symbol = pd.MultiIndex.from_frame(temp.iloc[1:,[0,x]], names=[common_set,maps_to])
					py_db.add_or_merge(db,symbol,common_set+'2'+maps_to,priority)

	@staticmethod
	def read_maps_from_excel_panel(db,wb,sheets,priority='second'):
		for sheet in sheets:
			temp = pd.DataFrame(wb[sheet].values)
			if temp.shape[0]>1:
				sets = list(pd.DataFrame(wb[sheet].values).iloc[0,:])
				symbol = pd.MultiIndex.from_frame(pd.DataFrame(wb[sheet].values).iloc[1:,:], names = sets)
				py_db.add_or_merge(db,symbol,'2'.join(sets),priority)

	###################################################################################################
	###								4: METHODS FOR AGGREGATING A DATABASE	 						###
	###################################################################################################

	###################################################################################################
	###								4.1: UPDATE DOMAINS FROM OTHER SYMBOLS	 						###
	###################################################################################################

	def upd_sets_from_vars(self,db=None,clean_up=True,include_mappings=False,exemptions=[]):
		"""
		Only keep elements in 'sets', if they are used in variables, parameters or mappings (optional). 
		"""
		if clean_up:
			for x in self.sets['sets']:
				if x not in exemptions:
					self.db[x] = None
		[self.upd_index(self.db,name) for name in self.variables['variables']]
		[self.upd_index(self.db,name) for name in self.parameters['parameters']]
		if include_mappings:
			[self.upd_index(self.db,name) for name in self.sets['mappings']]

	@staticmethod
	def index(db,name):
		if isinstance(db[name],pd.Series):
			return db[name].index
		elif isinstance(db[name],pd.Index):
			return db[name]

	@staticmethod
	def upd_index(db,name):
		if isinstance(db[name],(pd.Series,pd.Index)):
			for x in py_db.index(db,name).names:
				if isinstance(db[x],pd.Index):
					db[x] = db[x].union(py_db.index(db,name).get_level_values(x).unique())
				else:
					db[x] = py_db.index(db,name).get_level_values(x).unique()

	def upd_ssets_from_sets(self):
		db = self.default_db
		for x in self.sets['subsets']:
			self[x] = self[x][self[x].isin(self[self[x].name])]

	def update_maps_from_sets(self):
		db = self.default_db
		for x in self.sets['mappings']:
			for y in self[x].names:
				self[x] = self[x][self[x].get_level_values(y).isin(self[y])]

	###################################################################################################
	###								4.2: AGGREGATE BASED ON MAPPING OF SETS	 						###
	###################################################################################################

	def agg_db_mapping(self,mapping):
		"""
		Input:
		 	-	'mapping':	A pandas series w. values corresponding to new index, and index as original index. 
		 					Name of series should be name of original index.
		Output (works 'inplace' on database):
		 	- 	Updates the relevant index, subsets defined over the relevant index, and all mappings defined over the relevant index.
		"""
		db = self.default_db
		self[mapping.name] = self[mapping.name].map(mapping).unique() # update the set itself
		for set_ in self.sets['subsets']: # update subsets
			if mapping.name==self[set_].name:
				self[set_] = self[set_].map(mapping).unique()
		for set_ in self.sets['mappings']: # update mappings
			if mapping.name in self[set_].names:
				self[set_] = self[set_].to_frame().rename(index=mapping).index.unique()

	def agg_db_mapping_vars(self,mapping,vars_,add_to_all_vars=['variable','parameter']):
		"""
		Input: 
			-	'mapping':			See "agg_db_mapping"-method.
			-	'vars_':			Dict with keys corresponding to relevant methods (currently 'sum','mean','weightedsum'), 
									values corresponding to relevant information for the method to be applied on the variables. 
			-	'add_to_all_vars': 	List w. types of symbols of the database to apply the function to. 
		Output (works 'inplace' on database):
			-	Aggregates variables/parameters of entire database according to the relevant method ('sum','mean','weightedsum'). 
				Applies the 'sum' method of aggregation on any parameters/variables where nothing else is specified.
				See methods agg_var_mapping_x, x∈{'sum','mean','weightedsum'} below for details.
		"""
		if add_to_all_vars:
			vars_['sum'] = vars_['sum']+list(set(self.symbols_over_set(mapping._name,add_to_all_vars))-set(vars_['mean']+vars_['sum']+list(vars_['weightedsum'].keys())))
		[self.agg_var_mapping_sum(mapping,varname) for varname in vars_['sum']]
		[self.agg_var_mapping_mean(mapping,varname) for varname in vars_['mean']]
		[self.agg_var_mapping_weightedsum(mapping,varname,vars_['weightedsum'][varname]) for varname in vars_['weightedsum']]

	def agg_var_mapping_weightedsum(self,mapping,varname,weights):
		"""
		Input:
			-	'mapping':	See "agg_db_mapping"-method.
			-	'varname':	String referring to relevant variable/parameter in 'self' database.
			-	'weights':	Pandas series w. values corresponding to weights applying in weighted sum, and index (can be multiindex)
							that should be (part) of the index the relevant variable is defined over. Index.name = 'weights'.
		Output (works 'inplace' on database):
			-	Apply weighted sum of the variable/parameter according to mapping. Specifically the function (x[varname]*x[weights]).sum() 
				is applied. 
		"""
		self[varname] = self.agg_var_mapping(self[varname].to_frame().join(weights),mapping, lambda x: (x[varname]*x['weights']).sum())
		self[varname].name = varname

	def agg_var_mapping_sum(self,mapping,varname):
		"""
		Similar to agg_var_mapping_weightedsum, but with a simple 'sum' instead of 'weights'.
		"""
		self[varname] = self.agg_var_mapping(self[varname],mapping,lambda x: x.sum())
		self[varname].name = varname

	def agg_var_mapping_mean(self,mapping,varname):
		"""
		Similar to agg_var_mapping_weightedsum, but with 'mean' applied instead of 'weights'.
		"""
		self[varname] = self.agg_var_mapping(self[varname],mapping,lambda x: x.mean())
		self[varname].name = varname

	@staticmethod
	def agg_var_mapping(df,mapping,lambda_):
		return df.rename(index=mapping).groupby(df.index.names).apply(lambda_)

