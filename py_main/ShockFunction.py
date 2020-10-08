import os, pandas as pd, numpy as np, DataBase
from gams import *
from dreamtools.gamY import Precompiler
from DB2Gams_l2 import gams_model_py

def IfInt(x):
	try:
		int(x)
		return True
	except ValueError:
		return False

def return_version(x,dict_):
	if x not in dict_:
		return x
	elif (x+'_0') not in dict_:
		return x+'_0'
	else:
		maxInt = max([int(y.split('_')[1]) for y in dict_ if (y.split('_')[0]==x and IfInt(y.split('_')[1]))])
		return x+'_'+str(maxInt+1)

def append_index_with_1dindex(index1,index2):
	"""
	index1 is a pandas index/multiindex. index 2 is a pandas index (not multiindex).
	Returns a pandas multiindex with the cartesian product of elements in (index1,index2). 
	NB: If index1 is a sparse multiindex, the cartesian product of (index1,index2) will keep this structure.
	"""
	return pd.MultiIndex.from_tuples([a+(b,) for a in index1 for b in index2],names=index1.names+index2.names) if isinstance(index1,pd.MultiIndex) else pd.MultiIndex.from_tuples([(a,b) for a in index1 for b in index2],names=index1.names+index2.names)

def add_grid_to_series(vals_init,vals_end,linspace_index,name,gridtype='linear',phi=1):
	"""
	vals_init and vals_end are pandas series defined over a common index.
	linspace_index is a pandas index of the relevant length of the desired linspace.
	The function returns a pandas series with a gridtype-spaced grid added to each element i in vals_init/vals_end.
	"""
	if gridtype=='linear':
		apply_grid = lambda x0,xN,N: np.linspace(x0,xN,num=N)
	elif gridtype=='rust':
		apply_grid = lambda x0,xN,N: rust_space(x0,xN,N,phi)
	elif gridtype=='pol':
		apply_grid = lambda x0,xN,N: pol_space(x0,xN,N,phi)
	return pd.concat([pd.Series(apply_grid(vals_init.values[i],vals_end.values[i],len(linspace_index)), index = append_index_with_1dindex(vals_init.index[vals_init.index==vals_init.index[i]],linspace_index),name=name) for i in range(len(vals_init))])

def add_linspace_to_series(vals_init,vals_end,linspace_index,name):
	return pd.concat([pd.Series(np.linspace(vals_init.values[i],vals_end.values[i],num=len(linspace_index)),index = append_index_with_1dindex(vals_init.index[vals_init.index==vals_init.index[i]],linspace_index),name=name) for i in range(len(vals_init))])

def rust_space(x0,xN,N,phi):
	x = np.empty(N)
	x[0] = x0
	for i in range(2,N+1):
		x[i-1] = x[i-2]+(xN-x[i-2])/((N-i+1)**phi)
	return x

def pol_space(x0,xN,N,phi):
	return np.array([x0+(xN-x0)*((i-1)/(N-1))**phi for i in range(1,N+1)])

def end_w_y(x,y):
	if x.endswith(y):
		return x
	else:
		return x+y
def end_w_gdx(x):
	return end_w_y(x,'.gdx')
def end_w_gms(x):
	return end_w_y(x,'.gms')
def end_w_gmy(x):
	return end_w_y(x,'.gmy')

def solve_sneaky_db(db0,db_star,shock_name='shock',n_steps=10,loop_name='l1',update_vars='all',clean_up=True,gridtype='linear',phi=1,return_dict=False):
    shock_db = DataBase.py_db(name=shock_name)
    shock_db[loop_name] = loop_name+'_'+pd.Index(range(1,n_steps+1),name=loop_name).astype(str)
    if update_vars=='all':
    	update_vars = [var for var in db0.variables['variables'] if var in db_star.variables['variables']]
    for var in update_vars:
    	symbol = db_star[var][((db0[var][db0[var].index.isin(db_star[var].index)]-db_star[var])!=0)] if clean_up is True else db_star[var]
    	shock_db[var+'_subset'] = symbol.index
    	shock_db[var+'_loopval'] = add_grid_to_series(db0[var][db0[var].index.isin(shock_db[var+'_subset'])], symbol, shock_db[loop_name], var+'_loopval',gridtype=gridtype,phi=phi)
    	shock_db[var+'_loopval'].attrs['type']='parameter'
    shock_db.upd_all_sets()
    shock_db.merge_internal()
    return shock_db if return_dict is False else shock_db,{'shock_name': shock_name, 'n_steps': n_steps, 'loop_name': loop_name, 'update_vars': update_vars, 'clean_up': clean_up, 'gridtype': gridtype, 'phi': phi}

class AddShocks:
	"""
	Class that includes various ways to write gams-files that adds shocks to a GAMS model.
	"""
	def __init__(self,name,shock_db,loop_name,prefix='sol_'):
		self.name = name # name of model to 'solve' in loop statement.
		self.shock_gm = gams_model_py(shock_db) # gams_model_py class with information on shocks. 
		self.loop_name = loop_name # name of mapping to loop over.
		self.loop_text = "" # text to write inside loop.
		self.prefix=prefix # prefix used in UEVAS part.
		self.write_components = {} # components used to write 'text'.

	def WriteResolve(self,type_='CNS'):
		return f"solve {self.name} using {type_};\n"

	@property
	def text(self):
		"""
		Return loop state with current state of attributes. 
		"""
		return ' '.join([self.write_components[x] for x in self.write_components])

	def write_sets(self):
		"""
		Write gams code for declaring loop-sets, and loading in values form database in self.shock_gm.database.
		"""
		self.write_components['sets'] = (self.shock_gm.write_sets()+
										self.shock_gm.write_aliased_sets()+
										self.shock_gm.write_sets_other()+
										self.shock_gm.write_aliased_sets_other()+
										self.shock_gm.write_sets_load(self.shock_gm.database.name))
		return self.write_components['sets']

	def write_pars(self):
		"""
		Write gams code for declaring parameters and load in values.
		"""
		self.write_components['pars'] = (self.shock_gm.write_parameters()+
										self.shock_gm.write_parameters_load(self.shock_gm.database.name))
		return self.write_components['pars']

	def write_loop_text(self):
		"""
		Write the loop text using the database with loop information + text from 'loop_text'.
		"""
		self.write_components['loop'] = """loop( ({sets}){cond}, {loop})
		""".format( sets = ', '.join(self.shock_gm.database[self.loop_name].names),
					cond = '$('+self.shock_gm.database.get(self.loop_name).to_str+')' if self.shock_gm.database.get(self.loop_name).to_str!=self.loop_name else '',
					loop = self.loop_text)
		return self.write_components['loop']

	def UpdateExoVarsAndSolve(self,model):
		"""
		(Shorthand: UEVAS, could in principle be a class.)
		Write a type of 'loop-text' that performs the following steps:
			(1) Update value of exogenous variable,
			(2) Resolve model,
			(3) Store solution in database.
		"""
		self.model = model
		self.name = self.model.settings.name
		self.UEVAS = {'sol': {}, 'adj': {}}

	@property 
	def UEVAS_text(self):
		self.write_components = {}
		self.write_sets()
		self.write_pars()
		if len(self.UEVAS['sol'])>0:
			self.UEVAS_WritePGroup()
		self.loop_text = self.UEVAS_UpdateExoVars()+self.WriteResolve()+self.UEVAS_WriteStoreSol()
		self.write_loop_text()
		return self.text

	def UEVAS_2gmy(self,file_name):
		with open(end_w_gms(file_name),"w") as file:
			file.write(self.UEVAS_text)
		with open(end_w_gmy(file_name),"w") as file:
			file.write(Precompiler(end_w_gms(file_name))())
		# os.remove(end_w_gms(file_name))
		self.gmy = end_w_gmy(file_name)
		self.gms = end_w_gms(file_name)

	def UEVAS_var2sol(self,var,loop_dom,conditions=None):
		"""
		Var_domains should be a list (potentially empty).
		"""
		self.UEVAS['sol'][return_version(self.prefix+var,self.UEVAS['sol'])] = 	{'dom': f"[{', '.join(self.shock_gm.database[loop_dom].names+self.model.out_db[var].index.names)}]",
											 		 							'cond': "" if conditions is None else f"$({conditions})",
											  		 							'var': var}
	def UEVAS_WritePGroup(self):
		self.write_components['UEVAS_sol'] = 'parameter\n'
		for x in self.UEVAS['sol']:
			self.write_components['UEVAS_sol'] += f"\t{x}{self.UEVAS['sol'][x]['dom']}\n" # add conditionals to param? {self.UEVAS['sol'][x]['cond']}
		self.write_components['UEVAS_sol'] += ';\n\n'		

	def UEVAS_WriteStoreSol(self):
		out_str = ""
		for x in self.UEVAS['sol']:
			out_str += "{solpar} = {solvar};\n".format(
						  solpar = x+self.UEVAS['sol'][x]['dom']+self.UEVAS['sol'][x]['cond'],
						  solvar = (self.model.out_db.get(self.UEVAS['sol'][x]['var'],level='.l').to_str))
		out_str += '\n'
		return out_str

	def UEVAS_adjVar(self,var,par,conditions=None,overwrite=False):
		self.UEVAS['adj'][return_version(var,self.UEVAS['adj'])] = {'varname': var, 'par': par, 'cond': conditions}

	def UEVAS_UpdateExoVars(self):
		out_str = "" 
		for x in self.UEVAS['adj']:
			out_str += "\t{var} = {par};\n".format(
							var = self.model.out_db.get(self.UEVAS['adj'][x]['varname'],conditions=self.UEVAS['adj'][x]['cond'],level='.fx').to_str,
							par = self.shock_gm.database.get(self.UEVAS['adj'][x]['par']).to_str)
		out_str += '\n\n'
		return out_str
