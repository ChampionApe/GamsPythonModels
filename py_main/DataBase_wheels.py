import openpyxl
import pandas as pd
from gams import *
from dreamtools.gams_pandas import *
import DataBase

class small_updates:
	"""
	Collection of auxiliary database methods. 
	"""
	@staticmethod
	def set_values(db,set_,ns,inplace=True):
		"""
		For all symbols in database 'db', update the values of the set 'set_', according to the namespace 'in' (python dict).
		Do this for all symbols where 'set_' is relevant, including subsets, mappings, parameters, variables.
		"""
		full_map = {x: x if x not in ns else ns[x] for x in db[set_]}
		aliases = [set_] if set_ not in db.alias_all else [set_]+db.alias_all[set_].to_list()
		for set_i in aliases:
			if set_i in db:
				db[set_i] = db[set_i].map(full_map).unique()
			for set_ij in db.sets['subsets']:
				if db[set_ij].name == set_i:
					db[set_ij] = db[set_ij].map(full_map).unique()
			for map_ij in db.sets['mappings']:
				if set_i in db[map_ij].names:
					db[map_ij] = db[map_ij].set_levels(db[map_ij].levels[db[map_ij].names.index(set_i)].map(full_map),level=set_i,verify_integrity=False)
			for var in db.variables['variables']+db.parameters['parameters']:
				if set_i in db[var].index.names:
					if len(db[var].index.names)==1:
						db[var].index = db[var].index.map(full_map)
					else:
						db[var].index = db[var].index.set_levels(db[var].index.levels[db[var].index.names.index(set_i)].map(full_map),level=set_i,verify_integrity=False)
		return db