import pandas as pd
import DataBase
import nesting_trees

def df(x,kwargs):
	"""
	Modify x using kwargs.
	"""
	return x if x not in kwargs else kwargs[x]

class nesting_tree:
	"""
	Collection of nesting_trees that can be initialized from data or trees.
	"""
	def __init__(self,name="",**kwargs):
		self.name=name
		self.trees = {}

	def add_tree(self,tree,name="",**kwargs):
		"""
		Add a nesting tree to the collection of trees.
		"""
		if type(tree) is str:
			self.trees[name] = nesting_trees.tree_from_data(tree,tree_name=name,**kwargs)
		elif type(tree) is dict:
			self.trees[name] = nesting_trees.nt(tree=tree,name=name,**kwargs)
		elif isinstance(tree,nt):
			self.trees[tree.name] = tree
		else:
			raise TypeError("'tree' must be either a string (file-path for excel data), a dictionary (w. tree-structure), or a nesting_tree (python class).")

	def run_all(self,**kwargs):
		"""
		For all nesting trees in self.trees, retrieve information on inputs, aggregates, outputs, and mappings.
		"""
		[self.trees[tree].run_all(**kwargs) for tree in self.trees];
		self.aggregate_sector(**kwargs)

	def aggregate_sector(self,**kwargs):
		"""
		Aggregate sector from combination of trees.
		"""
		# Names:
		self.setname,self.alias, self.alias2 = list(self.trees.values())[0].setname, list(self.trees.values())[0].alias, list(self.trees.values())[0].alias2
		self.inp = df('inp',kwargs) # inputs in sector,
		self.out = df('out',kwargs) # outputs from sector, 
		self.int = df('int',kwargs) # intermediate goods used in nesting,
		self.fg = df('fg',kwargs) # final goods (inputs+outputs),
		self.wT = df('wT',kwargs) # intermediate goods + inputs.
		self.map_all = df('map_all',kwargs) # merged mappings from all sectors
		self.kno_out = df('kno_out',kwargs) # knots in nests of type_io == 'output'.
		self.kno_inp = df('kno_inp',kwargs) # knots in nests of type_io == 'input'.
		# Define inputs/outputs from all trees:
		inputs_all = set.union(*[set(tree.database[tree.inp]) if tree.type_io=='input' else set(tree.database[tree.out]) for tree in self.trees.values()])
		outputs_all = set.union(*[set(tree.database[tree.inp]) if tree.type_io=='output' else set(tree.database[tree.out]) for tree in self.trees.values()])
		# Define database, and add inputs,outputs,intermediates,all,final goods, and withoutTax types, all for the aggregate sector:
		self.database = DataBase.py_db(name=self.name,alias=pd.MultiIndex.from_tuples([(self.setname,self.alias), (self.setname, self.alias2)]))
		self.database[self.inp] = pd.Index(inputs_all-outputs_all, name = self.setname)
		self.database[self.out] = pd.Index(outputs_all-inputs_all, name = self.setname)
		self.database[self.int] = pd.Index(outputs_all.intersection(inputs_all), name = self.setname)
		self.database[self.setname] = pd.Index(inputs_all.union(outputs_all), name = self.setname)
		self.database[self.fg] = pd.Index(set(self.database[self.inp]).union(set(self.database[self.out])), name = self.setname)
		self.database[self.wT] = pd.Index(set(self.database[self.inp]).union(set(self.database[self.int])), name = self.setname)
		# Mapping: 
		self.database[self.map_all] = pd.MultiIndex.from_tuples(set.union(*[set(tree.database[tree.map]) for tree in self.trees.values()]), names = [self.setname,self.alias])
		# Aggregates in output-types, and input-types (if they exists):
		if 'output' in (tree.type_io for tree in self.trees.values()):
			self.database[self.kno_out] = pd.Index(set.union(*[set(tree.database[tree.kno]) for tree in self.trees.values() if tree.type_io=='output']), name = self.setname)
		else:
			self.database[self.kno_out] = pd.Index([], name=self.setname)
		if 'input' in (tree.type_io for tree in self.trees.values()):
			self.database[self.kno_inp] = pd.Index(set.union(*[set(tree.database[tree.kno]) for tree in self.trees.values() if tree.type_io=='input']), name = self.setname)
		else:
			self.database[self.kno_inp] = pd.Index([], name=self.setname)
		# Define subsets of the aggregate version in each tree:
		for tree in self.trees.values():
			tree.tree_inp = 't_'+self.inp+'_'+tree.name
			tree.tree_out = 't_'+self.out+'_'+tree.name
			tree.tree_int = 't_'+self.int+'_'+tree.name
			tree.tree_fg  = 't_'+self.fg+'_'+tree.name
			tree.tree_wT  = 't_'+self.wT+'_'+tree.name
			if tree.type_io=='input':
				tree.database[tree.tree_inp] = pd.Index(set(tree.database[tree.inp]).intersection(set(self.database[self.inp])), name = tree.setname)
				tree.database[tree.tree_out] = pd.Index(set(tree.database[tree.out]).intersection(set(self.database[self.out])), name = tree.setname)
				tree.database[tree.tree_int] = pd.Index(set(tree.database[tree.setname]).intersection(set(self.database[self.int])), name = tree.setname)
			elif tree.type_io=='output':
				tree.database[tree.tree_inp] = pd.Index(set(tree.database[tree.out]).intersection(set(self.database[self.inp])), name = tree.setname)
				tree.database[tree.tree_out] = pd.Index(set(tree.database[tree.inp]).intersection(set(self.database[self.out])), name = tree.setname)
				tree.database[tree.tree_int] = pd.Index(set(tree.database[tree.setname]).intersection(set(self.database[self.int])), name = tree.setname)
			tree.database[tree.tree_fg ] = pd.Index(set(tree.database[tree.tree_inp]).union(set(tree.database[tree.tree_out])), name = tree.setname)
			tree.database[tree.tree_wT ] = pd.Index(set(tree.database[tree.tree_inp]).union(set(tree.database[tree.tree_int])), name = tree.setname)		
		# Define 'i_tree_' subsets: These are elements from the original tree (map,kno,bra,inp,out) that are corrected for using aggregate tree information:
		for tree in self.trees.values():
			tree.i_tree_kno = 'i_kno_'+tree.name # knots in tree
			tree.i_tree_kno_no = 'i_kno_no_'+tree.name # not output version
			tree.i_tree_bra_o  = 'i_bra_o_'+tree.name # branch, output
			tree.i_tree_bra_no = 'i_bra_no_'+tree.name # branch, not output
			tree.database[tree.i_tree_kno] = tree.database[tree.kno]
			if tree.type_io=='input':
				tree.database[tree.i_tree_kno_no] = pd.Index(set(tree.database[tree.kno])-set(self.database[self.out]),name=tree.setname)
				tree.database[tree.i_tree_bra_o] = pd.Index(tree.database[tree.map].get_level_values(0)[tree.database[tree.map].get_level_values(1).isin(self.database[self.out])].unique(), name=tree.setname)
			elif tree.type_io=='output':
				tree.database[tree.i_tree_bra_o] = pd.Index(set(tree.database[tree.bra]).intersection(set(self.database[self.out])), name=tree.setname)
			tree.database[tree.i_tree_bra_no] = pd.Index(set(tree.database[tree.bra])-set(tree.database[tree.i_tree_bra_o]), name=tree.setname)
		# Finally, create empty sets in case the trees does not include any input or output-type trees:
