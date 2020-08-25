import pandas as pd
import DataBase

class nt:
	"""
	Small class of nesting trees
	"""
	def __init__(self,tree_name="",tree=None,**kwargs):
		self.name=tree_name
		self.tree=tree
		self.type_io = 'input'
		self.version = 'std'
		self.setname = 'n'
		self.alias   = 'nn'
		self.alias2  = 'nnn'
		self.map = 'map_'+self.name # map branches to knots
		self.kno = 'kno_'+self.name # knots 
		self.bra = 'bra_'+self.name # branches
		self.inp = 'inp_'+self.name # inputs: Branch, not knot
		self.out = 'out_'+self.name # outputs: Knot, not branch.
		self.update(kwargs)
		if self.type_io=='input' and 'type_f' not in kwargs:
			self.type_f = 'CES' # set default type to ces
		elif self.type_io=='output' and 'type_f' not in kwargs:
			self.type_f = 'CET' # set default type to cet
		self.database = DataBase.py_db(name=self.name,alias=pd.MultiIndex.from_tuples([(self.setname,self.alias), (self.setname, self.alias2)]))

	def run_all(self,Q2P=None,**kwargs):
		self.mapping_from_tree()
		self.set_from_tree()
		self.knots_from_tree()
		self.branches_from_tree()
		self.inputs_from_tree()
		self.outputs_from_tree()
		self.add_alias()
		if self.version =='QPS':
			self.version_QPS(Q2P,**kwargs)

	def mapping_from_tree(self):
		temp = []
		for key in self.tree:
			temp += [(value,key) for value in self.tree[key]]
		self.database[self.map] = pd.MultiIndex.from_tuples(temp,names=[self.setname,self.alias])
		self.database[self.map].name = self.map

	def set_from_tree(self):
		temp = []
		for key in self.tree:
			temp += self.tree[key]+[key]
		self.database[self.setname] = pd.Index(temp,name=self.setname).unique()

	def knots_from_tree(self):
		self.database[self.kno] = pd.Index(set(self.database[self.map].get_level_values(1)),name=self.setname)

	def branches_from_tree(self):
		self.database[self.bra] = pd.Index(set(self.database[self.map].get_level_values(0)),name=self.setname)

	def inputs_from_tree(self):
		self.database[self.inp] = pd.Index(set(self.database[self.map].get_level_values(0))-set(self.database[self.map].get_level_values(1)),name=self.setname)

	def outputs_from_tree(self):
		self.database[self.out] = pd.Index(set(self.database[self.map].get_level_values(1))-set(self.database[self.map].get_level_values(0)),name=self.setname)

	def add_alias(self):
		self.database[self.alias] = self.database[self.setname].copy()
		self.database[self.alias].name = self.alias
		self.database[self.alias2]= self.database[self.setname].copy()
		self.database[self.alias2].name = self.alias2

	def update(self,kwargs):
		for key,value in kwargs.items():
			setattr(self,key,value)

	def write2db(self,db,priority='second'):
		"""
		Merge into database (db).
		"""
		DataBase.py_db.merge_dbs(db,self.database,priority)
		return db

	@staticmethod
	def tree_from_mu(mu):
		return {x: mu.index.get_level_values(0)[mu.index.get_level_values(1)==x].to_list() for x in mu.index.get_level_values(1).unique()}

	def version_QPS(self,q2p,q2pname='q2p',q2p_agg_name = 'q2p_agg',OnlyQname='OnlyQ'):
		"""
		Adjusts the tree to a version where prices and quantities are not defined over the same sets.
		A mapping q2p indicates a subset of q-elements, that are essentially the same, and thus they face the same price. 
		The following adjustments are made:
			- q2p are added to the database, as well as its name (mapping).
			- The aggregates that q-elements are mapped to are defined.
			- Create new subset of elements, that prices are not defined over. 
			- The mapping q2p are automatically updated to include '(x,x)' mappings, in case the (p,q) sets are overlapping.
			- Update the set of all elements in the sector, to include the (potentially) new ones from q2p. 
			- Add the new elements that prices are defined over to 'inputs'.
			- Update 'version' of tree (default is 'std') to 'QPS'.
		"""
		self.q2p = q2pname
		self.q2p_agg = q2p_agg_name
		self.OnlyQ = OnlyQname # name of subset with only Q defined over it - not P.
		self.database[self.q2p_agg] = pd.Index(q2p.get_level_values(1).unique(), name=self.setname) # add aggregate part.
		self.database[self.inp] = pd.Index(set(self.database[self.inp]) - set(q2p.get_level_values(0)), name =self.setname)
		self.database[self.OnlyQ] = pd.Index(set(q2p.get_level_values(0))-set(self.database[self.setname]), name=self.setname)
		# Expand mapping n2nn with ('x'-'x') elements for overlapping combinations of the two sets (p,q):
		self.database[self.q2p] = q2p.union(pd.MultiIndex.from_tuples([(x,x) for x in set(self.database[self.setname])-set(q2p.get_level_values(0))], names = [self.setname, self.alias]))
		self.database[self.setname] = pd.Index( self.database[self.setname].union(
												self.database[self.q2p].get_level_values(0)).union(
												self.database[self.q2p].get_level_values(1)),
												name = self.setname).unique()
		self.database[self.inp] = self.database[self.inp].union(self.database[OnlyQ])
		self.version='QPS'

class tree_from_data(nt):
	"""
	Initialize tree from data, where data is the file-path for an excel file.
	"""
	def __init__(self,data_path,mu='mu',setdim=2,tree_name="",**kwargs):
		db = DataBase.py_db(name=tree_name)
		db.read_from_excel(data_path,{'vars_panel': {mu: setdim}})
		super().__init__(tree_name=tree_name,tree=nt.tree_from_mu(db[mu]),**{**{'setname':db[mu].index.names[0], 'alias': db[mu].index.names[1]}, **kwargs})


### OLD VERSION:
# class nt_base:
# 	"""
# 	Small class of nesting tree.
# 	"""
# 	def __init__(self,tree_name="",tree=None,**kwargs):
# 		self.name=tree_name
# 		self.tree = tree
# 		self.type_io = 'input'
# 		self.version = 'std'
# 		self.setname = 'n'
# 		self.alias = 'nn'
# 		self.alias2 = 'nnn'
# 		self.mapname = 'map_'+self.name
# 		self.aggname = 'agg_'+self.name
# 		self.inpname = 'inp_'+self.name
# 		self.outname= 'out_'+self.name
# 		self.sector = 'sec_'+self.name
# 		self.update(kwargs)
# 		self.database = DataBase.py_db(name=self.name,alias=pd.MultiIndex.from_tuples([(self.setname,self.alias), (self.setname, self.alias2)]))

# 	def update(self,kwargs):
# 		for key,value in kwargs.items():
# 			setattr(self,key,value)

# 	def write2db(self,db,priority='second'):
# 		"""
# 		Merge into database (db).
# 		"""
# 		DataBase.py_db.merge_dbs(db,self.database,priority)
# 		return db

# 	def run_all(self,**kwargs):
# 		self.mapping_from_tree()
# 		self.set_from_tree()
# 		self.aggregates_from_tree()
# 		self.inputs_from_tree()
# 		self.outputs_from_tree()
# 		self.add_alias()
# 		self.sector_from_tree()
# 		if self.version=='QPSets':
# 			self.Q_and_P_over_different_sets()
# 		else:
# 			self.p_all = self.setname
# 			self.q_all = self.setname

# 	def sector_from_tree(self):
# 		self.database[self.sector] = self.database[self.inpname].union(self.database[self.aggname])

# 	def add_alias(self):
# 		self.database[self.alias] = self.database[self.setname].copy()
# 		self.database[self.alias].name = self.alias
# 		self.database[self.alias2]= self.database[self.setname].copy()
# 		self.database[self.alias2].name = self.alias2

# 	def mapping_from_tree(self):
# 		temp = []
# 		for key in self.tree:
# 			temp += [(value,key) for value in self.tree[key]]
# 		self.database[self.mapname] = pd.MultiIndex.from_tuples(temp,names=[self.setname,self.alias])
# 		self.database[self.mapname].name = self.mapname

# 	def set_from_tree(self):
# 		temp = []
# 		for key in self.tree:
# 			temp += self.tree[key]+[key]
# 		self.database[self.setname] = pd.Index(temp,name=self.setname).unique()

# 	def aggregates_from_tree(self):
# 		self.database[self.aggname] = pd.Index(set(self.database[self.mapname].get_level_values(1)),name=self.setname)

# 	def inputs_from_tree(self):
# 		self.database[self.inpname] = pd.Index(set(self.database[self.mapname].get_level_values(0))-set(self.database[self.mapname].get_level_values(1)),name=self.setname)

# 	def outputs_from_tree(self):
# 		self.database[self.outname] = pd.Index(set(self.database[self.mapname].get_level_values(1))-set(self.database[self.mapname].get_level_values(0)), name=self.setname)

# 	@staticmethod
# 	def tree_from_mu(mu):
# 		return {x: mu.index.get_level_values(0)[mu.index.get_level_values(1)==x].to_list() for x in mu.index.get_level_values(1).unique()}

# 	def Q_and_P_over_different_sets(self,n2nn='n2nn',n2nn_agg='n2nn_agg',p_all='p_all',q_all='q_all',q2p='q2p'):
# 		self.n2nn = n2nn
# 		self.n2nn_agg = n2nn_agg
# 		self.database[n2nn_agg] = pd.Index(self.database[n2nn].get_level_values(1).unique(), name=self.setname)
# 		self.p_all=p_all # set of all prices.
# 		self.q_all=q_all # set of all quantities.
# 		self.q2p = q2p # mapping of quantity-elements to price-element.
# 		# Expand n2nn with ('x'-'x')-elements for overlapping combinations of the two sets: 
# 		self.database[q2p] = self.database[self.n2nn].union(pd.MultiIndex.from_tuples([(x,x) for x in set(self.database[self.setname])-set(self.database[self.n2nn].get_level_values(0))], names=[self.setname,self.alias]))
# 		# Update set with all elements from quantity-2-price elements from n2nn:
# 		self.database[self.setname] = pd.Index(	self.database[self.setname].union(
# 												self.database[self.n2nn].get_level_values(0)).union(
# 												self.database[self.n2nn].get_level_values(1)),
# 												name=self.setname).unique()
# 		self.database[p_all] = pd.Index(set(self.database[self.setname])-set(self.database[self.n2nn].get_level_values(0)),name=self.setname)
# 		self.database[q_all] = pd.Index(set(self.database[self.setname])-set(self.database[self.n2nn].get_level_values(1)),name=self.setname)
# 		# Update inputs with the ones in n2nn:
# 		self.database[self.inpname] = pd.Index((set(self.database[self.inpname])-set(self.database[self.n2nn].get_level_values(0))).union(set(self.database[self.n2nn].get_level_values(1))),name=self.setname)


# class tree_from_data(nt_base):
# 	"""
# 	Initialize tree from data, where data is the file-path for an excel file.
# 	"""
# 	def __init__(self,data_path,mu='mu',setdim=2,tree_name="",**kwargs):
# 		db = DataBase.py_db(name=tree_name)
# 		db.read_from_excel(data_path,{'vars_panel': {mu: setdim}})
# 		super().__init__(tree_name=tree_name,tree=nt_base.tree_from_mu(db[mu]),**{**{'setname':db[mu].index.names[0], 'alias': db[mu].index.names[1]}, **kwargs})

