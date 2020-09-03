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
		self.version = 'std'
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

	def run_all(self,Q2Ps={},**kwargs):
		"""
		For all nesting trees in self.trees, retrieve information on inputs, aggregates, outputs, and mappings.
		"""
		[self.trees[tree].run_all(**kwargs) if tree not in Q2Ps else self.trees[tree].run_all(Q2P=Q2Ps[tree],**kwargs) for tree in self.trees];
		self.aggregate_sector(**kwargs)
		self.prune_trees()

	def aggregate_sector(self,**kwargs):
		"""
		Aggregate sector from combination of trees.
		"""
		self.setname,self.alias, self.alias2 = list(self.trees.values())[0].setname, list(self.trees.values())[0].alias, list(self.trees.values())[0].alias2
		self.inp = df('inp',kwargs) # inputs in sector,
		self.out = df('out',kwargs) # outputs from sector, 
		self.int = df('int',kwargs) # intermediate goods used in nesting,
		self.fg = df('fg',kwargs) # final goods (inputs+outputs),
		self.wT = df('wT',kwargs) # intermediate goods + inputs.
		self.map_all = df('map_all',kwargs) # merged mappings from all sectors
		self.kno_out = df('kno_out',kwargs) # knots in nests of type_io == 'output'.
		self.kno_inp = df('kno_inp',kwargs) # knots in nests of type_io == 'input'.
		self.aggregate_sector_sets(**kwargs) # define main sets/subsets of the aggregate sector.
		self.tree_subsets() # define subsets of the aggregate-sector-sets in each tree
		self.adjust_trees_from_agg() # adjust some of the sets in individual trees with information from aggregate sector sets.
		if 'Q2P' in (tree.version for tree in self.trees.values()):
			self.adjust_for_Q2P(**kwargs)

	def aggregate_sector_sets(self,**kwargs):
		# Define inputs/outputs from all trees:
		inputs_all = set.union(*[set(tree.database[tree.inp]) if tree.type_io=='input' else set(tree.database[tree.out]) for tree in self.trees.values()])
		outputs_all = set.union(*[set(tree.database[tree.inp]) if tree.type_io=='output' else set(tree.database[tree.out]) for tree in self.trees.values()])
		# Define database, and add inputs,outputs,intermediates,all,final goods, and withoutTax types, all for the aggregate sector:
		self.database = DataBase.py_db(name=self.name,alias=pd.MultiIndex.from_tuples([(self.setname,self.alias), (self.setname, self.alias2)]))
		self.database[self.setname] = pd.Index(set.union(*[set(tree.database[tree.setname]) for tree in self.trees.values()]), name=self.setname)
		self.database[self.inp] = pd.Index(inputs_all-outputs_all, name = self.setname)
		self.database[self.out] = pd.Index(outputs_all-inputs_all, name = self.setname)
		self.database[self.int] = pd.Index(set(self.database[self.setname])-set(self.database[self.inp])-set(self.database[self.out]), name = self.setname)
		self.database[self.fg] = pd.Index(set(self.database[self.inp]).union(set(self.database[self.out])), name = self.setname)
		self.database[self.wT] = pd.Index(set(self.database[self.inp]).union(set(self.database[self.int])), name = self.setname)
		# Mapping:
		self.database[self.map_all] = pd.MultiIndex.from_tuples(set.union(*[set(tree.database[tree.map_]) for tree in self.trees.values()]), names = [self.setname,self.alias])
		# Aggregates in output-types, and input-types (if they exists):
		if 'output' in (tree.type_io for tree in self.trees.values()):
			self.database[self.kno_out] = pd.Index(set.union(*[set(tree.database[tree.kno]) for tree in self.trees.values() if tree.type_io=='output']), name = self.setname)
		else:
			self.database[self.kno_out] = pd.Index([], name=self.setname)
		if 'input' in (tree.type_io for tree in self.trees.values()):
			self.database[self.kno_inp] = pd.Index(set.union(*[set(tree.database[tree.kno]) for tree in self.trees.values() if tree.type_io=='input']), name = self.setname)
		else:
			self.database[self.kno_inp] = pd.Index([], name=self.setname)

	def tree_subsets(self,**kwargs):
		# Define subsets of the aggregate version in each tree:
		for tree in self.trees.values():
			tree.tree_out = 't_'+self.out+'_'+tree.name
			if tree.type_io=='input':
				tree.database[tree.tree_out] = pd.Index(set(tree.database[tree.out]).intersection(set(self.database[self.out])), name = tree.setname)
			elif tree.type_io=='output':
				tree.database[tree.tree_out] = pd.Index(set(tree.database[tree.inp]).intersection(set(self.database[self.out])), name = tree.setname)

	def adjust_trees_from_agg(self):
		for tree in self.trees.values():
			tree.i_tree_kno = 'i_kno_'+tree.name # knots in tree
			tree.i_tree_kno_no = 'i_kno_no_'+tree.name # not output version
			tree.i_tree_bra_o  = 'i_bra_o_'+tree.name # branch, output
			tree.i_tree_bra_no = 'i_bra_no_'+tree.name # branch, not output
			tree.database[tree.i_tree_kno] = tree.database[tree.kno]
			if tree.type_io=='input':
				tree.database[tree.i_tree_kno_no] = pd.Index(set(tree.database[tree.kno])-set(self.database[self.out]),name=tree.setname)
				tree.database[tree.i_tree_bra_o] = pd.Index(tree.database[tree.map_].get_level_values(0)[tree.database[tree.map_].get_level_values(1).isin(self.database[self.out])].unique(), name=tree.setname)
			elif tree.type_io=='output':
				tree.database[tree.i_tree_bra_o] = pd.Index(set(tree.database[tree.bra]).intersection(set(self.database[self.out])), name=tree.setname)
			tree.database[tree.i_tree_bra_no] = pd.Index(set(tree.database[tree.bra])-set(tree.database[tree.i_tree_bra_o]), name=tree.setname)

	def adjust_for_Q2P(self,**kwargs):
		self.version = 'Q2P'
		self.PwT_dom = df('PwT_dom',kwargs)
		self.database[self.PwT_dom] = pd.Index(set(self.database[self.wT])-set.union(*[set(tree.database[tree.OnlyQ]) for tree in self.trees.values() if tree.version=='Q2P']), name = self.setname)

	def prune_trees(self):
		"""
		Create set of sets/attributes from nesting trees that are not needed once the information has been applied in model.
		"""
		self.prune_trees = set(['kno','bra','inp','out','OnlyQ'])