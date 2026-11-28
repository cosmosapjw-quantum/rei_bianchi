"""R33: source-locked 5-level H+HD chemical absorption in a prescribed CMB blackbody.

New scientific output: integrated stimulated/spontaneous HD line emission, CMB
absorption, final H2(v=0,J'=0..9) exchange branching and exact event energy ledger.
Original GL2022 computed SQM rate cells, Leiden A transcription, Sung fitted
line centers, fixed gas T and proton density; no radiative transport, physical Q,
cosmic HD abundance or full astrophysical heating. R32 parent is immutable.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,sys,zipfile
from pathlib import Path
import numpy as np
from scipy.optimize import brentq

ROOT=Path(__file__).resolve().parents[1]
PARENT_ZIP_NAME='WU_R32_SOURCE_ORIGINAL_20261030.zip'
PARENT_SHA='01482fdefef303b8cc00bd0efe9b20c23d1886a69679d76eec9d67434fe643e7'
SOURCE_HASH={
'R29_NETWORK_ORIGINAL.py':'f042717e6dfe76f2570ec6204ec6c1f025e64a149bbe93a14e684bd4e6544dac',
'GL2022_700_SOURCE.json':'f49312061552513ffdef5aa6d144f7edb9727f8b8cb3ce6e29bd262f15845db9',
'GL2022_1560_INELASTIC_SOURCE_TOKENS.csv':'58c252a1c3f62995ed748c7620e342bc98d8aabb307271bff48f7711e4f1cd7c',
'REC161_LAMDA_A_TRANSCRIPTION_REF.json':'887383f3978de55ed82079feeff13361ff3910d9a1c384fa2d3b9c982bdb5ef8',
'REC162_CDMS2011V2_PRINTED_LEVELS.json':'769834947ec6630887ad3b9eae2f4d487c0dffecc268a0512521ee2a79127cca',
'REC164_SUNG2022_PRIMARY_TABLE4_LOCK.json':'50d4e6af5cc63afee44177cb0f46838f654f9ff127efe140014ade1e0c2d854f',
}
H=6.62607015e-34; C=299792458.; KB=1.380649e-23
CMJ=100*H*C; EVJ=1.602176634e-19
T0=2.7255
# None is the exact T_rad=0 limiting case, not a physical observable redshift.
REDSHIFTS=(None,0,5,10,30,100,300)
LABELS=('OFF','z0','z5','z10','z30','z100','z300')
MODES=('raw_SQM','Eq6-7_spin_effective')
TEMPS=(55,105,255,505,1005,2005,3005)
RATIOS=(0.1,1.0,10.0)
LEVELS=range(5)

class SourceError(ValueError):pass

def hashfile(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify_sources():
 p=ROOT/'archive'/PARENT_ZIP_NAME
 if not p.is_file() or hashfile(p)!=PARENT_SHA:raise SourceError('immutable R32 full source archive SHA mismatch')
 with zipfile.ZipFile(p) as z:
  if z.testzip() is not None:raise SourceError('original R32 CRC error')
 for n,sha in SOURCE_HASH.items():
  path=ROOT/'sources'/n
  if not path.is_file() or hashfile(path)!=sha:raise SourceError('source SHA mismatch: '+n)
 return True

def get_parent():
 verify_sources()
 modname='wu_r29_original_for_r33'
 spec=importlib.util.spec_from_file_location(modname,ROOT/'sources/R29_NETWORK_ORIGINAL.py')
 mod=importlib.util.module_from_spec(spec)
 sys.modules[modname]=mod
 spec.loader.exec_module(mod)
 # Source R29 code expects ORIGINAL files under its BASE/sources. These remain hash locked above.
 src=json.loads((ROOT/'sources/REC164_SUNG2022_PRIMARY_TABLE4_LOCK.json').read_text())
 if src['source_git_blob']!='23626dd9a77aa4e6214f6f9c792ea18270b3940c':raise SourceError('Sung source Git identity changed')
 centers=tuple(float(t['nu_cm_minus1']) for t in src['lines'])
 if centers!=(89.22792,177.84141,265.24055,350.85401):raise SourceError('source line quantum numbers changed')
 for j,l in enumerate(src['lines'],1):
  if (int(l['upper_J']),int(l['lower_J']))!=(j,j-1):raise SourceError('Sung J mapping')
 old=mod.load_grid()
 levels={0:0.}
 for j in range(1,5):levels[j]=levels[j-1]+centers[j-1]
 grid=mod.Grid(old.q,old.down,old.A,levels,dict(old.source_meta))
 return mod,old,grid,centers

def photon_occupation(delta_cm1,T_rad):
 if T_rad==0:return 0.
 if not (T_rad>0 and math.isfinite(T_rad)):raise ValueError('T_rad must be finite nonnegative')
 x=CMJ*delta_cm1/(KB*T_rad)
 return 1./math.expm1(x)

def assemble(parent,grid,T_kin,policy,nHp,T_rad):
 if T_kin not in TEMPS or policy not in MODES or nHp<=0:raise ValueError('invalid model domain')
 if T_rad<0 or not math.isfinite(T_rad):raise ValueError('T_rad out of scope')
 # R29 unperturbed collision block. Radiation is replaced, not double counted.
 _g,collision,_gfirst,_chem=parent.assemble(grid,T_kin,policy,nHp)
 K=collision.copy()
 chemical=np.column_stack([nHp*parent.reaction_vector(grid,T_kin,j,policy) for j in LEVELS])
 chemlevel=chemical.sum(axis=0)
 rad_rates=[]
 for j in range(1,5):
  cm1=grid.energies_cm1[j]-grid.energies_cm1[j-1]
  if cm1<=0:raise ValueError('non-positive photon energy')
  o=photon_occupation(cm1,T_rad)
  sp=grid.A[j]
  stim=grid.A[j]*o
  absr=grid.A[j]*(2*j+1)/(2*j-1)*o
  # j -> j-1, j-1 -> j ; columns are origin states
  K[j-1,j]+=sp+stim;K[j,j]-=sp+stim
  K[j,j-1]+=absr;K[j-1,j-1]-=absr
  rad_rates.append((j,cm1,sp,stim,absr,o))
 for j in LEVELS:K[j,j]-=chemlevel[j]
 # K0 removes ALL radiative transitions as first-marking events, but preserves collisional motion.
 K0=collision.copy()
 for j,cm1,sp,stim,absr,o in rad_rates:
  K0[j,j]-=sp+stim
  K0[j-1,j-1]-=absr
 for j in LEVELS:K0[j,j]-=chemlevel[j]
 if np.max(np.abs(np.sum(K,axis=0)+chemlevel))>1e-17:raise AssertionError('generator probability nonconservation')
 if np.max(np.abs(np.sum(K0,axis=0)+chemlevel+sum((np.eye(5)[j]*(sp+st)+np.eye(5)[j-1]*a) for j,cm1,sp,st,a,_ in rad_rates)))>1e-17:raise AssertionError('first-rad killed generator incorrect')
 return K,K0,collision,chemical,rad_rates

def evaluate(parent,grid,centers,Tgas,policy,ratio,J,rad_label,redshift):
 T_rad=0. if redshift is None else T0*(1.+redshift)
 nHp=parent.reference_density(grid,Tgas,policy)*ratio
 G,G0,Cp,react,rs=assemble(parent,grid,Tgas,policy,nHp,T_rad)
 e=np.eye(5)[:,J]
 m=np.linalg.solve(-G,e)
 m0=np.linalg.solve(-G0,e)
 if min(m)<-1e-8 or min(m0)<-1e-8:raise AssertionError('negative occupancy')
 p=react@m
 p0=react@m0
 cond=p-p0
 radfirst=0.
 lines=[]
 radenergy=0.
 for j,cm1,sp,st,ab,o in rs:
  counts=(sp*m[j],st*m[j],ab*m[j-1]); net=(counts[0]+counts[1]-counts[2])*CMJ*cm1
  first=(sp+st)*m0[j]+ab*m0[j-1]
  radfirst+=first
  radenergy+=net
  lines.append({'line_upper_J':j,'nu_cm-1':cm1,'nbar_CMB':o,'A_s-1':sp,'stim_s-1':st,'abs_s-1':ab,
      'expected_spontaneous_emissions':counts[0],'expected_stimulated_emissions':counts[1],
      'expected_CMB_absorptions':counts[2],'net_line_emitted_minus_absorbed_photons':sum(counts[:2])-counts[2],
      'net_line_radiation_J':net,'first_radiative_interaction_prob':first})
 # Physical collision energy to bath: collisional generator Cp has no sources/sinks.
 E=np.array([CMJ*grid.energies_cm1[k] for k in LEVELS])
 B=0.
 for j in LEVELS:
  for i in LEVELS:
   if i!=j:
    B+=Cp[i,j]*m[j]*(E[j]-E[i])
 terminal=np.dot((react.sum(axis=0)*m),E)
 start=E[J]
 residual=start-B-radenergy-terminal
 if abs(residual)>3.e-32:raise AssertionError('nonconserved internal energy')
 if abs(p.sum()-1)>1e-9 or min(p)<-1e-10 or min(cond)<-1e-10 or abs(radfirst+p0.sum()-1)>1e-9:
  raise AssertionError('first radiation / reaction hitting conservation failure')
 res={'Tgas_K':Tgas,'policy':policy,'n_over_ncrit_J2':ratio,'initial_HD_J':J,'CMB_label':rad_label,
      'redshift_parameter':(-1 if redshift is None else redshift),'T_rad_K':T_rad,'nHplus_cm-3':float(nHp),
      'mean_reaction_wait_s':float(m.sum()),'mean_no_radiation_wait_s':float(m0.sum()),
      'prob_any_radiative_interaction_before_reaction':float(radfirst),
      'prob_reaction_before_any_radiation':float(p0.sum()),
      'spont_emissions_per_initial':float(sum(x['expected_spontaneous_emissions'] for x in lines)),
      'stim_emissions_per_initial':float(sum(x['expected_stimulated_emissions'] for x in lines)),
      'CMB_absorptions_per_initial':float(sum(x['expected_CMB_absorptions'] for x in lines)),
      'net_radiative_transfer_J':float(radenergy),'collisional_proton_bath_gain_J':float(B),
      'pre_reaction_HD_rotational_J':float(terminal),'initial_HD_rotational_J':float(start),
      'energy_balance_residual_J':float(residual),'restricted_H2_odd_Jprime_share':float(sum(p[1::2])),
      'chemistry_type':'source_restricted_GL2022_2022_SQM_v0_H2_products',
      'full_cosmic_chemistry':False}
 prow=[dict((k,res[k]) for k in ('Tgas_K','policy','n_over_ncrit_J2','initial_HD_J','CMB_label','redshift_parameter','T_rad_K')) |
       {'H2_final_Jprime':k,'probability_all':float(p[k]),'joint_no_radiation':float(p0[k]),
        'joint_at_least_one_radiation':float(cond[k])} for k in range(10)]
 lrow=[dict((k,res[k]) for k in ('Tgas_K','policy','n_over_ncrit_J2','initial_HD_J','CMB_label','redshift_parameter','T_rad_K')) | rr for rr in lines]
 return res,lrow,prow

def write_csv(out,rows):
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def generate(out):
 parent,old,grid,centers=get_parent()
 rows=[];line=[];products=[]
 for T in TEMPS:
  for policy in MODES:
   for ratio in RATIOS:
    for J in LEVELS:
     for lab,z in zip(LABELS,REDSHIFTS):
      a,b,c=evaluate(parent,grid,centers,T,policy,ratio,J,lab,z)
      rows.append(a);line.extend(b);products.extend(c)
 assert (len(rows),len(line),len(products))==(1470,5880,14700)
 out=Path(out);out.mkdir(exist_ok=True,parents=True)
 write_csv(out/'R33_CMB_CASES_1470.csv',rows)
 write_csv(out/'R33_CMB_LINES_5880.csv',line)
 write_csv(out/'R33_H2_PRODUCTS_14700.csv',products)
 # pairs: fixed physical density within each original T and ratio in the original raw-SQM policy.
 pairs=[]
 for T in TEMPS:
  for ratio in RATIOS:
   for J in LEVELS:
    n=parent.reference_density(grid,T,'raw_SQM')*ratio
    for lab,z in zip(LABELS,REDSHIFTS):
     tr=0 if z is None else T0*(1+z)
     vals=[]
     for policy in MODES:
      G,_,C,chem,rad=assemble(parent,grid,T,policy,n,tr)
      m=np.linalg.solve(-G,np.eye(5)[:,J]);freq=chem@m
      rr=0.
      for j,cm1,sp,st,ab,o in rad:rr+=(sp*m[j]+st*m[j]-ab*m[j-1])*CMJ*cm1
      vals.append((rr,float(sum(freq[1::2])),float(m.sum())))
     pairs.append({'Tgas_K':T,'nHplus_cm-3':n,'initial_HD_J':J,'T_rad_K':tr,'redshift_parameter':(-1 if z is None else z),
                   'raw_net_radiation_J':vals[0][0],'spin_net_radiation_J':vals[1][0],
                   'spin_minus_raw_radiation_J':vals[1][0]-vals[0][0],
                   'raw_H2_odd_share':vals[0][1],'spin_H2_odd_share':vals[1][1],
                   'raw_wait_s':vals[0][2],'spin_wait_s':vals[1][2]})
 assert len(pairs)==735
 write_csv(out/'R33_FIXED_DENSITY_POLICY_735.csv',pairs)
 # New physical discriminant: radiation-collision-chemistry zero-transfer
 # redshift on 0 <= z <= 300, with fixed gas source T and proton density policy.
 # This is a root in an externally prescribed blackbody, not a cosmic thermal history.
 zero=[]
 for T in TEMPS:
  for policy in MODES:
   for ratio in RATIOS:
    for J in LEVELS:
     def er(z):
      return evaluate(parent,grid,centers,T,policy,ratio,J,'crossing',float(z))[0]['net_radiative_transfer_J']
     a=er(0);b=er(300)
     root=float(brentq(er,0,300,xtol=1e-9,rtol=1e-11)) if a*b<0 else None
     residual=er(root) if root is not None else None
     zero.append({'Tgas_K':T,'policy':policy,'n_over_ncrit_J2':ratio,'initial_HD_J':J,
       'Rnet_at_z0_J':a,'Rnet_at_z300_J':b,
       'zero_crossing_in_0_300':root is not None,
       'z_radiative_balance':root,'T_CMB_balance_K':None if root is None else T0*(1+root),
       'Rnet_root_residual_J':residual,'nHplus_cm-3':parent.reference_density(grid,T,policy)*ratio})
 assert len(zero)==210
 write_csv(out/'R33_RADIATIVE_BALANCE_Z_210.csv',zero)
 base=next(r for r in rows if r['Tgas_K']==105 and r['policy']=='Eq6-7_spin_effective' and r['initial_HD_J']==2 and r['n_over_ncrit_J2']==1. and r['CMB_label']=='OFF')
 examples=[r for r in rows if r['Tgas_K']==105 and r['policy']=='Eq6-7_spin_effective' and r['initial_HD_J']==2 and r['n_over_ncrit_J2']==1.]
 max_energy=max(abs(r['energy_balance_residual_J']) for r in rows)
 max_norm=max(abs(r['prob_any_radiative_interaction_before_reaction']+r['prob_reaction_before_any_radiation']-1) for r in rows)
 summary={'schema':'wu.r33.cmb5.source_conditioned.v1','source_lineage':'Original GL2022 printed SQM+REC161 Einstein A transcription+REC164 four fitted line centers from immutable nested R32',
          'n_cases':len(rows),'line_rows':len(line),'product_rows':len(products),'fixed_density_pairs':len(pairs),
          'radiative_balance_candidates':len(zero),'radiative_balance_root_count':sum(x['zero_crossing_in_0_300'] for x in zero),
          'max_balance_residual_J':max(abs(x['Rnet_root_residual_J']) for x in zero if x['zero_crossing_in_0_300']),
          'source_Tkin_K':list(TEMPS),'CMB_redshift_parameters':['OFF',0,5,10,30,100,300],
          'initial_reference':base,'CMB_contrast_105K_spin_J2':examples,
          'max_energy_residual_J':max_energy,'max_first_event_probability_defect':max_norm,
          'radiation':'blackbody optically thin external isotropic, no transfer, no cosmic history',
          'EMAA_raw_acquired':False,'PES_native_threshold':None,'physical_Q':None,'owner_ACK':None,
          'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN','canonical_DAG':'34/49_UNCHANGED',
          'aux_R33':'1/1_SCOPED_NOT_PROMOTED','full_A':None,'HH_R10':'OFF','L4':False,'production':'NOT_ISSUED'}
 (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 return summary

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results');args=p.parse_args()
 s=generate(args.out)
 print(json.dumps({k:s[k] for k in ('n_cases','line_rows','product_rows','fixed_density_pairs','radiative_balance_root_count','max_energy_residual_J','max_first_event_probability_defect')},indent=2))
 print('example_105K_J2',[(x['CMB_label'],x['net_radiative_transfer_J'],x['CMB_absorptions_per_initial'],x['restricted_H2_odd_Jprime_share']) for x in s['CMB_contrast_105K_spin_J2']])

if __name__=='__main__':main()
