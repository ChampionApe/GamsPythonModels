import os
main = os.getcwd().split('GamsPythonModels')[0]+'GamsPythonModels'
project = main+'\\'+os.getcwd().split('GamsPythonModels')[1].split('\\')[1]
py = {}
py['main'] = main+'\\py_main'
py['project'] = project+'\\py_project'
py['local'] = os.getcwd()
os.chdir(py['main'])
import DataBase, regex_gms, DB2Gams
os.chdir(py['local']) 
import COE_abate, COE_abate_settings

def apply_type(type_,version):
	return eval(f"COE_abate.{type_}")(version=version)

def apply_type_settings(type_,version):
	return eval(f"COE_abate_settings.{type_}")(version=version)

def df(x,kwargs):
	"""
	Modify x using kwargs.
	"""
	return x if x not in kwargs else kwargs[x]

def tech_calib(pm,data,map_k2t,map_u2c,map_c2e,map_q2p,**kwargs):
	"""
	(1) Create simple namespace for calibration variables, akin to 'global_sets', 'global_vars', and 'vars_domains' as defined for the ModelFrame_PE.production class. 
		calib['vars']: Mapping from default names to new names for technical parameters.
		calib['domains']: Mapping from default names of subsets to new names.
		calib['vars_domains']: Coupling of variable and domains. Call a variable from its default namespace yields the name of its domain.
	(2) Read in calibration data.
	(3) Define relevant subsets from the data.
	"""
	pm.calib = {'vars': {x: df(x,kwargs) for x in ('theta_c','theta_p','cbar')},
				'domains': {x: df(x,kwargs) for x in ('u_subset','c_subset','KT_subset')}, 
				'mappings': {x: df(x,kwargs) for x in ('k2t','u2c','c2e','mu_endo')}}
	pm.calib['vars_domains'] = {list(pm.calib['vars'].keys())[x]: list(pm.calib['domains'].values())[x] for x in range(0,len(pm.calib['vars']))}
	pm.calib['mappings']['q2p'] = map_q2p
	settings={'1dvars': {'sheets': ['theta_c','theta_p','cbar'], 'names': pm.calib['vars']}}
	pm.model.database.read_from_excel(data,settings) # read in technical variables
	if pm.model.database.default_db=='db_Gdx':
		pm.model.database.default_db = 'db_pd'
		pm.model.database.merge_internal()
	for key,dom in pm.calib['vars_domains'].items():
		pm.model.database[dom] = pm.model.database[key].index # define subsets from indices on relevant variables
	pm.model.database[pm.calib['mappings']['k2t']] = pm.model.database[map_k2t][pm.model.database[map_k2t].get_level_values(0).isin(pm.model.database[pm.calib['domains']['KT_subset']])]
	pm.model.database[pm.calib['mappings']['u2c']] = pm.model.database[map_u2c][pm.model.database[map_u2c].get_level_values(0).isin(pm.model.database[pm.calib['domains']['u_subset']])]
	pm.model.database[pm.calib['mappings']['c2e']] = pm.model.database[map_c2e][pm.model.database[map_c2e].get_level_values(0).isin(pm.model.database[pm.calib['domains']['c_subset']])]
	pm.model.database[pm.calib['mappings']['mu_endo']] = pm.model.database[pm.calib['mappings']['k2t']].union(pm.model.database[pm.calib['mappings']['u2c']]).union(pm.model.database[pm.calib['mappings']['c2e']])

def tech_calib_write(pm,repo=os.getcwd(),name='calib',type_='V1',export_settings=False):
	add_groups(pm)
	add_blocks(pm,name=name,type_=type_)
	pm.model.run_default(repo,export_settings=export_settings)

def def_groups(pm):
	return {'g_techcalib': {pm.calib['vars'][var]: pm.calib['vars_domains'][var] for var in pm.calib['vars']},
			'g_calibendo': {pm.globals['vars']['mu']: pm.calib['mappings']['mu_endo']}}

def add_groups(pm):
	groups = def_groups(pm)
	for g in groups:
		pm.groups[g] = {key: {'conditions': pm.model.database.get(val).to_str} for key,val in groups[g].items()}
		pm.model.add_group_to_groups(pm.groups[g],pm.model.settings.name+'_'+g)
	pm.model.settings.g_endo += [pm.model.settings.name+'_g_calibendo']
	pm.model.settings.g_exo += [pm.model.settings.name+'_g_techcalib']

def add_blocks(pm,name='calib',type_='V1'):
	pm.model.blocks += f"\n $BLOCK M_{name} \n\t{eqtext(pm,type_,name=name)}\n$ENDBLOCK\n"
	pm.model.settings.blocks += ['M_'+name]

def eqtext(pm,type_,name='calib'):
	fcoe = apply_type(type_,pm.version)
	return fcoe.run(ftype_settings(pm,type_)['vartext'],ftype_settings(pm,type_)['domains'],ftype_settings(pm,type_)['conditions'],name)

def ftype_settings(pm,type_):
	out = {'domains': None, 'conditions': None, 'vartext': None}
	settings = apply_type_settings(type_,pm.version)
	out['domains'] = {k: pm.aux_write(v,dom=True) for k,v in settings.doms.items()}
	out['conditions'] = {k: pm.model.database.get(v).to_str for k,v in settings.conds.items()}
	out['vartext'] =  {k: {pm.name_symbol(v['a'][i],v['l'][i]): pm.model.database.get(aux_map(pm,k),alias_domains=pm.alias(v['a'][i]), level=v['l'][i]).to_str for i in range(0,len(v['a']))} 
							for k,v in settings.vartext.items()}
	if 'n' in out['vartext']: # correct the alias of 'n'.
		v = settings.vartext['n']
		out['vartext']['n'] = {pm.name_symbol(v['a'][i],v['l'][i]): pm.aux_write('n',a=v['a'][i]) for i in range(0,len(v['a']))}
	return out

def aux_map(pm,k):
	"""
	Map k to the correct name in the database.
	"""
	for x in ['vars','domains','mappings']:
		if k in pm.calib[x]:
			return pm.calib[x][k]
	for x in ['sets','vars']:
		if k in pm.globals[x]:
			return pm.globals[x][k]