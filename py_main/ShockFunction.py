import os
from gams import *
from DB2Gams import *
import DataBase
from dreamtools.gamY import Precompiler
import pandas as pd

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
		self.write_components['loop'] = """loop( ({sets})$({cond}), {loop})
		""".format( sets = ', '.join(self.shock_gm.database[self.loop_name].names),
					cond = self.shock_gm.database.get(self.loop_name).to_str,
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
		self.name = self.model.model.name
		self.UEVAS = {'sol': {}, 'adj': {}}

	@property 
	def UEVAS_text(self):
		self.write_components = {}
		self.write_sets()
		self.write_pars()
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
