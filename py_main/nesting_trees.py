import pandas as pd
import DataBase

class nt_base:
	"""
	Small class of nesting tree.
	"""
	def __init__(self,name="",tree=None,**kwargs):
		self.name=name
		self.tree = tree
		self.setname = 'n'
		self.alias = 'nn'
		self.alias2 = 'nnn'
		self.mapname = 'map_'+self.name
		self.aggname = 'a_'+self.name
		self.inpname = 'input_'+self.name
		self.outname= 'output_'+self.name
		self.sector = 'sector_'+self.name
		self.update(kwargs)
		self.database = DataBase.py_db(name=self.name,alias=pd.MultiIndex.from_tuples([(self.setname,self.alias), (self.setname, self.alias2)]))

	def update(self,kwargs):
		for key,value in kwargs.items():
			setattr(self,key,value)

	def write2db(self,db,priority='second'):
		"""
		Merge into database (db).
		"""
		DataBase.py_db.merge_dbs(db,self.database,priority)
		return db

	def run_all(self):
		self.mapping_from_tree()
		self.set_from_tree()
		self.aggregates_from_tree()
		self.inputs_from_tree()
		self.outputs_from_tree()
		self.add_alias()
		self.sector_from_tree()

	def sector_from_tree(self):
		self.database[self.sector] = self.database[self.inpname].union(self.database[self.aggname])

	def add_alias(self):
		self.database[self.alias] = self.database[self.setname].copy()
		self.database[self.alias].name = self.alias
		self.database[self.alias2]= self.database[self.setname].copy()
		self.database[self.alias2].name = self.alias2

	def mapping_from_tree(self):
		temp = []
		for key in self.tree:
			temp += [(value,key) for value in self.tree[key]]
		self.database[self.mapname] = pd.MultiIndex.from_tuples(temp,names=[self.setname,self.alias])
		self.database[self.mapname].name = self.mapname

	def set_from_tree(self):
		temp = []
		for key in self.tree:
			temp += self.tree[key]+[key]
		self.database[self.setname] = pd.Index(temp,name=self.setname).unique()

	def aggregates_from_tree(self):
		self.database[self.aggname] = pd.Index(set(self.database[self.mapname].get_level_values(1)),name=self.setname)

	def inputs_from_tree(self):
		self.database[self.inpname] = pd.Index(set(self.database[self.mapname].get_level_values(0))-set(self.database[self.mapname].get_level_values(1)),name=self.setname)

	def outputs_from_tree(self):
		self.database[self.outname] = pd.Index(set(self.database[self.mapname].get_level_values(1))-set(self.database[self.mapname].get_level_values(0)), name=self.setname)

	@staticmethod
	def tree_from_mu(mu):
		return {x: mu.index.get_level_values(0)[mu.index.get_level_values(1)==x].to_list() for x in mu.index.get_level_values(1).unique()}

class tree_from_data(nt_base):
	"""
	Initialize tree from data, where data is the file-path for an excel file.
	"""
	def __init__(self,data_path,mu='mu',setdim=2,name="",**kwargs):
		db = DataBase.py_db(name=name)
		db.read_from_excel(data_path,{'vars_panel': {mu: setdim}})
		super().__init__(name=name,tree=nt_base.tree_from_mu(db[mu]),**{**{'setname':db[mu].index.names[0], 'alias': db[mu].index.names[1]}, **kwargs})

class nt_base_v2(tree_from_data,nt_base):
	"""
	Include CES in the nesting structure.
	This version allows for prices and quantities 
	to be defined over separate, but potentially 
	overlapping sets, and with a mapping that re-
	late the two. 
	"""
	def __init__(self,from_data,name="",tree=None,data_path=None,mu='mu',mu_out='mu_out',setdim=2,**kwargs):
		if from_data is False:
			nt_base.__init__(self,name=name,tree=tree,**kwargs)
		else:
			tree_from_data.__init__(self,data_path,mu=mu,setdim=setdim,name=name,**kwargs)

	def run_all_v2(self,n2nn='n2nn',n2nn_agg='n2nn_agg',p_all='p_all',q_all='q_all',q2p='q2p'):
		"""
		Get all sets and mappings from the nesting tree as in the standard version,
		and correct for the mapping from quantity-elements to price-elements.
		"""
		self.run_all()
		self.n2nn = n2nn
		self.n2nn_agg = n2nn_agg
		self.database[n2nn_agg] = pd.Index(self.database[n2nn].get_level_values(1).unique(), name=self.setname)
		self.p_all=p_all # set of all prices.
		self.q_all=q_all # set of all quantities.
		self.q2p = q2p # mapping of quantity-elements to price-element.
		# Expand n2nn with ('x'-'x')-elements for overlapping combinations of the two sets: 
		self.database[q2p] = self.database[self.n2nn].union(pd.MultiIndex.from_tuples([(x,x) for x in set(self.database[self.setname])-set(self.database[self.n2nn].get_level_values(0))], names=[self.setname,self.alias]))
		# Update set with all elements from quantity-2-price elements from n2nn:
		self.database[self.setname] = pd.Index(	self.database[self.setname].union(
												self.database[self.n2nn].get_level_values(0)).union(
												self.database[self.n2nn].get_level_values(1)),
												name=self.setname).unique()
		self.database[p_all] = pd.Index(set(self.database[self.setname])-set(self.database[self.n2nn].get_level_values(0)),name=self.setname)
		self.database[q_all] = pd.Index(set(self.database[self.setname])-set(self.database[self.n2nn].get_level_values(1)),name=self.setname)
		# Update inputs with the ones in n2nn:
		self.database[self.inpname] = pd.Index((set(self.database[self.inpname])-set(self.database[self.n2nn].get_level_values(0))).union(set(self.database[self.n2nn].get_level_values(1))),name=self.setname)

class nt_CET:
	"""
	Includes CET and CES in the nesting structure. 
	"""
	def __init__(self,name="",tree=None,**kwargs):
		self.name=name
		self.tree=tree
		self.setname = 'n'
		self.alias = 'nn'
		self.alias2 = 'nnn'
		self.alias3 = 'nnnn'
		self.in_map = 'i_map_'+self.name
		self.out_map = 'o_map_'+self.name
		self.all_map = 'a_map_'+self.name
		self.in_endo = 'i_endo_'+self.name
		self.out_endo = 'o_endo_'+self.name
		self.in_agg  =  'i_agg_'+self.name
		self.out_agg = 'o_agg_'+self.name
		self.inpname = 'input_'+self.name
		self.outname = 'output_'+self.name
		self.update(kwargs)
		self.database = DataBase.py_db(name=self.name,alias=pd.MultiIndex.from_tuples([(self.setname,self.alias), (self.setname, self.alias2),(self.setname,self.alias3)]))

	def update(self,kwargs):
		for key,value in kwargs.items():
			setattr(self,key,value)

	def write2db(self,db,priority='second'):
		"""
		Merge into database (db).
		"""
		DataBase.py_db.merge_dbs(db,self.database,priority)
		return db

	def run_all(self):
		self.in_map_from_tree()
		self.out_map_from_tree()
		self.all_map_from_maps()
		self.set_from_tree()
		self.in_inputs_from_maps()
		self.out_inputs_from_maps()
		self.inp_from_maps()
		self.out_from_maps()
		self.in_aggregates_from_map()
		self.out_aggregates_from_map()
		self.add_alias()

	# def all_agg_from_aggs(self):
	# 	self.database[self.aggname] = self.database[self.in_aggname].union(self.database[self.out_aggname])
	# 	return self.database[self.aggname]

	def in_inputs_from_maps(self):
		self.database[self.in_endo] = self.database[self.in_map].get_level_values(0).unique()
		return self.database[self.in_endo]

	def out_inputs_from_maps(self):
		self.database[self.out_endo] = self.database[self.out_map].get_level_values(0).unique()
		return self.database[self.out_endo]

	def in_map_from_tree(self):
		temp = []
		for key in self.tree['in']:
			temp += [(value,key) for value in self.tree['in'][key]]
		self.database[self.in_map] = pd.MultiIndex.from_tuples(temp,names=[self.setname, self.alias])
		self.database[self.in_map].name = self.in_map
		return self.database[self.in_map]

	def out_map_from_tree(self):
		temp = []
		for key in self.tree['out']:
			temp += [(value,key) for value in self.tree['out'][key]]
		self.database[self.out_map] = pd.MultiIndex.from_tuples(temp,names=[self.setname, self.alias])
		self.database[self.out_map].name = self.out_map
		return self.database[self.out_map]

	def all_map_from_maps(self):
		self.database[self.all_map] = self.database[self.in_map].union(self.database[self.out_map])
		return self.database[self.all_map]

	def set_from_tree(self):
		temp = []
		for key in self.tree['in']:
			temp += self.tree['in'][key]+[key]
		for key in self.tree['out']:
			temp += self.tree['out'][key]+[key]
		self.database[self.setname] = pd.Index(temp,name=self.setname).unique()
		return self.database[self.setname]

	def inp_from_maps(self):
		self.database[self.inpname] = pd.Index(set(self.database[self.in_map].get_level_values(0).to_list()+self.database[self.out_map].get_level_values(1).to_list())-set(self.database[self.in_map].get_level_values(1).to_list()+self.database[self.out_map].get_level_values(0).to_list()),name=self.setname)
		return self.database[self.inpname]

	def out_from_maps(self):
		self.database[self.outname] = pd.Index(set(self.database[self.in_map].get_level_values(1).to_list()+self.database[self.out_map].get_level_values(0).to_list())-set(self.database[self.in_map].get_level_values(0).to_list()+self.database[self.out_map].get_level_values(1).to_list()),name=self.setname)
		return self.database[self.outname]

	def in_aggregates_from_map(self):
		self.database[self.in_agg] = pd.Index(set(self.database[self.in_map].get_level_values(1)),name=self.setname)
		return self.database[self.in_agg]

	def out_aggregates_from_map(self):
		self.database[self.out_agg] = pd.Index(set(self.database[self.out_map].get_level_values(1)),name=self.setname)
		return self.database[self.out_agg]

	def add_alias(self):
		self.database[self.alias] = self.database[self.setname].copy()
		self.database[self.alias].name = self.alias
		self.database[self.alias2]= self.database[self.setname].copy()
		self.database[self.alias2].name = self.alias2
		self.database[self.alias3] = self.database[self.setname].copy()
		self.database[self.alias3].name = self.alias3

	@staticmethod
	def tree_from_mu(mu):
		return {x: mu.index.get_level_values(0)[mu.index.get_level_values(1)==x].to_list() for x in mu.index.get_level_values(1).unique()}

class tree_from_data_CET(nt_CET):
	"""
	Initialize tree from data, where data is the file-path for an excel file.
	"""
	def __init__(self,data_path,mu='mu',mu_out='mu_out',setdim=2,name="",**kwargs):
		db = DataBase.py_db(name=name)
		db.read_from_excel(data_path,{'vars_panel': {mu: setdim, mu_out: setdim}})
		super().__init__(name=name,tree={'in': nt_CET.tree_from_mu(db[mu]),
										 'out': nt_CET.tree_from_mu(db[mu_out])},
										 **{**{'setname':db[mu].index.names[0], 'alias': db[mu].index.names[1]}, **kwargs})


class nt_CET_v2(tree_from_data_CET,nt_CET):
	"""
	Include CET and CES in the nesting structure.
	This version allows for prices and quantities 
	to be defined over separate, but potentially 
	overlapping sets, and with a mapping that re-
	late the two. 
	"""
	def __init__(self,from_data,name="",tree=None,data_path=None,mu='mu',mu_out='mu_out',setdim=2,**kwargs):
		if from_data is False:
			nt_CET.__init__(self,name=name,tree=tree,**kwargs)
		else:
			tree_from_data_CET.__init__(self,data_path,mu=mu,mu_out=mu_out,setdim=setdim,name=name,**kwargs)

	def run_all_v2(self,n2nn='n2nn',n2nn_agg='n2nn_agg',p_all='p_all',q_all='q_all',q2p='q2p'):
		"""
		Get all sets and mappings from the nesting tree as in the standard version,
		and correct for the mapping from quantity-elements to price-elements.
		"""
		self.run_all()
		self.n2nn = n2nn
		self.n2nn_agg = n2nn_agg
		self.database[n2nn_agg] = pd.Index(self.database[n2nn].get_level_values(1).unique(), name=self.setname)
		self.p_all=p_all # set of all prices.
		self.q_all=q_all # set of all quantities.
		self.q2p = q2p # mapping of quantity-elements to price-element.
		# Expand n2nn with ('x'-'x')-elements for overlapping combinations of the two sets: 
		self.database[q2p] = self.database[self.n2nn].union(pd.MultiIndex.from_tuples([(x,x) for x in set(self.database[self.setname])-set(self.database[self.n2nn].get_level_values(0))], names=[self.setname,self.alias]))
		# Update set with all elements from quantity-2-price elements from n2nn:
		self.database[self.setname] = pd.Index(	self.database[self.setname].union(
												self.database[self.n2nn].get_level_values(0)).union(
												self.database[self.n2nn].get_level_values(1)),
												name=self.setname).unique()
		self.database[p_all] = pd.Index(set(self.database[self.setname])-set(self.database[self.n2nn].get_level_values(0)),name=self.setname)
		self.database[q_all] = pd.Index(set(self.database[self.setname])-set(self.database[self.n2nn].get_level_values(1)),name=self.setname)
		# Update inputs with the ones in n2nn:
		self.database[self.inpname] = pd.Index((set(self.database[self.inpname])-set(self.database[self.n2nn].get_level_values(0))).union(set(self.database[self.n2nn].get_level_values(1))),name=self.setname)
