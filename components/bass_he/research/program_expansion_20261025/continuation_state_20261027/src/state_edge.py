"""Source-bound HD level edge; conditional scalar consumer, no physical admission."""
import hashlib, importlib.util, json, math, sys
from pathlib import Path
from numbers import Real
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'sources/HD.Rovibration.805a7aa5.radex'
RAW_SHA='feda215f1d75ee85de399903c77e18f62c8e323fe709015215634d6ccc7720b6'
LEGACY=ROOT.parent/'continuation_event_20261027/src/reactive_event.py'
LEGACY_SHA='89bbcb99cb1487b7e3c132ab6b6d6d0093fbeed2479b112078f6c94f81542ce7'
if hashlib.sha256(LEGACY.read_bytes()).hexdigest()!=LEGACY_SHA:raise RuntimeError('stable-product dependency changed')
# Previous stable exponent-separated product and its original error semantics.
spec=importlib.util.spec_from_file_location('he_state04_product_dependency',LEGACY)
legacy=importlib.util.module_from_spec(spec);sys.modules[spec.name]=legacy;spec.loader.exec_module(legacy)
product=legacy.product;ContractError=legacy.ContractError
H=6.62607015e-34;C=299792458.0;KB=1.380649e-23
CLOSURE='maxwellian_detailed_balance_same_composition'
def finite(x,label):
 if isinstance(x,bool) or not isinstance(x,Real):raise ContractError(label+' must be a finite real')
 try:x=float(x)
 except (OverflowError,ValueError) as e:raise ContractError(label+' not representable') from e
 if not math.isfinite(x):raise ContractError(label+' must be finite')
 return x
def parse(path=RAW):
 raw=path.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=RAW_SHA:raise ContractError('raw source identity mismatch')
 lines=raw.decode('utf-8').splitlines()
 if len(lines)!=612 or int(lines[5].split()[0])!=52 or int(lines[60])!=368 or int(lines[431])!=1 or int(lines[435])!=171 or int(lines[437])!=25:raise ContractError('unexpected source structure')
 levels=[x.split() for x in lines[7:59]];rad=[x.split() for x in lines[62:430]];temperatures=lines[439].split();collisions=[x.split() for x in lines[441:612]]
 if any(len(x)!=4 for x in levels) or any(len(x)!=6 for x in rad) or len(temperatures)!=25 or any(len(x)!=28 for x in collisions):raise ContractError('unexpected row shape')
 if [int(x[0]) for x in levels]!=list(range(1,53)) or [int(x[0]) for x in rad]!=list(range(1,369)) or [int(x[0]) for x in collisions]!=list(range(1,172)):raise ContractError('source row identity')
 for row in collisions:
  for x in row[3:]:
   if not math.isfinite(float(x)) or float(x)<0:raise ContractError('invalid rate cell')
 return {'levels':levels,'radiative':rad,'temperatures':temperatures,'collisions':collisions,'collision_partner':lines[433]}
def native(dataset,T):
 T=finite(T,'temperature')
 if T>3000:raise ContractError('native point outside article support; binding held')
 try:index=[float(x) for x in dataset['temperatures']].index(T)
 except ValueError as e:raise ContractError('temperature must be a supported native point') from e
 rows=[x for x in dataset['collisions'] if x[1:3]==['2','1']]
 if len(rows)!=1:raise ContractError('selected edge missing or duplicated')
 return {'T_K':T,'printed_cm3_s':rows[0][3+index],'down_m3_s':product(float(rows[0][3+index]),1e-6),'provenance':'native_downward'}
def pair(dataset,T,closure):
 if closure!=CLOSURE:raise ContractError('explicit thermal reciprocity closure required')
 n=native(dataset,T);delta=product(100.0,H,C,89.227900);ratio=product(3.0,math.exp(-delta/(KB*n['T_K'])))
 n.update(up_m3_s=product(n['down_m3_s'],ratio),equilibrium_ratio=ratio,delta_j=delta,up_provenance='derived_by_explicit_thermal_reciprocity');return n
def source(dataset,T,n_p,n_lower,n_upper,closure):
 p=pair(dataset,T,closure);d=[finite(x,n) for x,n in ((n_p,'collider density'),(n_lower,'lower density'),(n_upper,'upper density'))]
 if any(x<0 for x in d):raise ContractError('densities must be nonnegative')
 jp=product(d[0],d[1],p['up_m3_s']);jm=product(d[0],d[2],p['down_m3_s'])
 try:J=math.fsum((jp,-jm))
 except OverflowError as e:raise ContractError('flux difference not representable') from e
 internal=product(p['delta_j'],J)
 entropy=product(J,math.log(jp)-math.log(jm)) if jp>0 and jm>0 else None
 return {'consumer':'HE_NATIVE_HD_HPLUS_EXPLICIT_LEVEL_EDGE','j_up':jp,'j_down':jm,'entropy_production_over_kB':entropy,'zero_flux_log_diagnostic':'UNDEFINED_OR_LIMIT' if entropy is None else 'FINITE','Gamma_upper':J,'Gamma_lower':-J,'Gamma_Hplus':0.0,'population_internal_witness_W_m3':internal,'material_kinetic_compensation_W_m3':-internal,'independent_internal_rhs':None,'species_heat':None,'species_momentum':None,'species_stress':None,'birth_pool':'UNASSIGNED','radiative_photon_emitted':False,'physical_global_consumer_admitted':False}
def lih_select(version):
 if version!='BENNETT2008_CORRECTED':raise ContractError('explicit corrected source version required')
 data=json.loads((ROOT/'sources/BENNETT2008_CORRECTION.json').read_text())
 return {'version':version,'rows':data['native_table_1_pairs'],'source_doi':data['correction_doi'],'supersedes_doi':data['supersedes_doi'],'historical_rows_retained':True,'additive':False,'fit_evaluated':False,'physical_covariance':None,'RA_state_binding':False}
