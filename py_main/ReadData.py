import os, numpy as np, pandas as pd, DataBase

def clean(db,clean_data):
	for var in db.variables['variables']:
		db[var] = db[var][(x not in clean_data for x in db[var])]
		if np.nan in clean_data:
			db[var] = db[var].dropna()
	return db

def read_data(data,export_to,clean_data=[np.nan,'NA',0]):
	"""
	Read in production values/prices/quantities from 'data', and export to 'export_to'.
	"""
	# Input/output table, domestic sectors/goods:
	db_dom = DataBase.py_db()
	db_dom.read_from_excel(data['Production_v'],{'vars_panel': {'sheets': {'sec_domestic': 2}, 'names': {}}})
	db_dom.upd_sets_from_vars()
	db_dom['s_prod'] = db_dom['s']
	# Trade:
	db_trade = DataBase.py_db()
	db_trade.read_from_excel(data['Production_v'],{'vars_panel': {'sheets': {'sec_trade': 2}, 'names': {}}})
	db_trade.upd_sets_from_vars()
	db_trade['n_for'] = db_trade['n']
	db_trade['s_for'] = pd.Index(db_trade['n'],name='s')
	# taxes:
	db_tax = DataBase.py_db()
	db_tax.read_from_excel(data['Production_v'],{'vars_panel': {'sheets': {'sec_tax': 2}, 'names': {}}})
	db_tax.upd_sets_from_vars()
	db_tax['n_tax'] = db_tax['n']
	# Investment, supply components:
	db_invest_s = DataBase.py_db()
	db_invest_s.read_from_excel(data['Production_v'],{'vars_panel': {'sheets': {'sec_invest_S': 2}, 'names': {}}})
	db_invest_s.upd_sets_from_vars()
	db_invest_s['n_dur'] = pd.Index(db_dom['n'].intersection(db_invest_s['itype']), name='n')
	# Investment, demand components:
	db_invest_d = DataBase.py_db()
	db_invest_d.read_from_excel(data['Production_v'],{'vars_panel': {'sheets': {'sec_invest_D': 2}, 'names': {}}})
	db_invest_d.upd_sets_from_vars()
	# Merge dbs:
	db = DataBase.py_db(alias=pd.MultiIndex.from_tuples([('s','ss'), ('n','nn'),('n','nnn')]))
	for db_i in [db_dom,db_trade,db_tax,db_invest_s,db_invest_d]:
		db.merge_dbs(db,db_i)
	# Clean data:
	clean(db,clean_data)
	# Define dummies:
	for var in db.variables['variables']:
	    dummy_name = 'd_'+var
	    db[dummy_name] = db[var].index
	# Assert that data is balanced:
	assert max(abs(db['vS'].groupby('s').sum()-db['vD'].groupby('s').sum()))<1e-9, "Data is not balanced."
	# Read in prices:
	db.read_from_excel(data['Production_p'], {'vars_panel': {'sheets': {'sec_goods': 2, 'sec_invest_S': 2, 'sec_invest_D': 2}, 'names': {}}})
	# clean data:
	clean(db,clean_data)
	# quantities:
	db['qD'] = db['vD']/db['PwT']
	db['qS'] = db['vS']/db['PwT']
	db['qID'] = db['vID']/db['pID']
	db['qIS'] = db['vIS']/db['pIS']
	for x in ('qD','qS','qID','qIS'):
		db[x].name = x
	# clean data:
	clean(db,clean_data)
	# export data:
	db.merge_internal()
	db.db_Gdx.export(export_to)