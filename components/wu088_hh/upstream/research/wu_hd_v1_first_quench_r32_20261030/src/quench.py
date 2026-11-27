"""WU R32: Source-locked H+ + HD(v=1,J=0..6) collisional first vibrational quench.

All 890 printed original 2022 GL source cells are retained; the single malformed 2005K
cell renders all 7 transient-state initial conditions at that T unqualified.
Detailed-balance re-excitation within v=1 is DERIVED from displayed historical CDMS
2011 v2 term energies, not separately supplied 2022 original transition rates.

This is a conditional *collision-only* first-passage system: no chemical exchange,
radiative vibrational loss, or v=0 re-excitation. These excluded processes must never
be silently called zero in physical gas. No production/owner or canonical DAG claim.
"""
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path
from collections import defaultdict
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA={
 'R31':'3286e22a7663ab3114685698e7653b00ac3ea1ec439af466b5c4ae5483e42078',
 'GL':'58c252a1c3f62995ed748c7620e342bc98d8aabb307271bff48f7711e4f1cd7c',
 'PDF':'a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754',
}
NATIVE_T=(15,55,105,255,505,1005,1505,2005,2505,3005)
QUALIFIED_T=tuple(t for t in NATIVE_T if t!=2005)
MODES=('DB_UPWARD_V1','DOWN_ONLY_COUNTERFACTUAL')
H=6.62607015e-34
C=299792458.0
KB=1.380649e-23
CM_TO_J=100*H*C

class SourceError(ValueError):pass

def filehash(path:Path)->str:
 return hashlib.sha256(path.read_bytes()).hexdigest()

def load_sources():
 paths={'R31':ROOT/'archive/WU_R31_SOURCE_ORIGINAL_20261030.zip',
        'GL':ROOT/'sources/GL2022_1560_INELASTIC_SOURCE_TOKENS.csv',
        'PDF':ROOT/'sources/GL2022_CSIC_supplement.pdf'}
 for k,p in paths.items():
  if not p.is_file() or filehash(p)!=SOURCE_SHA[k]:
   raise SourceError(f'original source SHA or file invalid: {k}')
 with (ROOT/'sources/CDMS2011V2_RENDERED_V0V1_LEVELS.json').open(encoding='utf8') as f: levels=json.load(f)
 if levels['representation']!='official_text_rendered_through_Exa_NOT_raw_file_bytes':
  raise SourceError('historical spectroscopy source must remain DISPLAYED not RAW')
 v0=np.array([float(levels['v0'][str(j)]) for j in range(11)])
 v1=np.array([float(levels['v1'][str(j)]) for j in range(7)])
 if not np.all(np.diff(v0)>0) or not np.all(np.diff(v1)>0):raise SourceError('level ordering')
 if abs(v0[0])>1e-15:raise SourceError('energy zero')
 with paths['GL'].open(newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
 if len(rows)!=1560:raise SourceError('original source table truncated')
 keep=[r for r in rows if int(r['initial_v'])==1]
 if len(keep)!=890:raise SourceError('v1 table cells unexpected')
 malformed=[r for r in keep if r['status']!='SOURCE_PRINTED_VALID']
 if len(malformed)!=1 or {k:malformed[0][k] for k in ('initial_v','initial_J','final_v','final_J','T_K','token')}!={'initial_v':'1','initial_J':'2','final_v':'0','final_J':'5','T_K':'2005','token':'1.58(10'}:
  raise SourceError('unexpected original printed source anomaly')
 for r in keep:
  if r['status']=='SOURCE_PRINTED_VALID':
   if not float(r['rate_cm3_s'])>0:raise SourceError('negative/zero source rate')
  if int(r['initial_J']) not in range(7) or int(r['final_v']) not in (0,1):raise SourceError('bad quantum state')
  i,j,v=int(r['initial_J']),int(r['final_J']),int(r['final_v'])
  if v==0 and not v1[i]>v0[j]:raise SourceError('inelastic transition energetically forbidden under displayed spectroscopy')
  if v==1 and not i>j:raise SourceError('source v1 rotational cell must be strictly downward')
 return keep,v0,v1

def build_generator(rows:list[dict],temp:int,v1:np.ndarray,mode:str):
 if temp not in QUALIFIED_T or mode not in MODES:raise SourceError('T and model must be named qualified case')
 # H_{i,j} is the transition rate *per proton density*, units cm3/s.
 h=np.zeros((7,7),dtype=float);q=np.zeros((11,7),dtype=float)
 downward=[];source_sink=[]; upward=[]
 for row in rows:
  if int(row['T_K'])!=temp:continue
  a,b,v=int(row['initial_J']),int(row['final_J']),int(row['final_v'])
  k=float(row['rate_cm3_s'])
  if v==0:
   q[b,a]+=k
   source_sink.append((a,b,k))
  else:
   h[b,a]+=k;downward.append((a,b,k))
   if mode==MODES[0]:
    # Microscopic reversal only in v=1 rotational block; energy cm^-1 -> joules
    kup=k*((2*a+1)/(2*b+1))*math.exp(-CM_TO_J*(v1[a]-v1[b])/(KB*temp))
    h[a,b]+=kup;upward.append((b,a,kup))
 for j in range(7):h[j,j]=-float(sum(h[:,j])+sum(q[:,j]))
 # For all column states, H is transient with strictly positive source-listed sinks
 if min(q.sum(axis=0))<=0:raise SourceError('missing sink')
 for j in range(7):
  if not (h[j,j]<0 and abs(h[:,j].sum()+q[:,j].sum())<1e-22):raise SourceError('generator conservation')
 return h,q,downward,upward,source_sink

def case_solve(h:np.ndarray,q:np.ndarray,v0:np.ndarray,v1:np.ndarray,initial_j:int):
 # Solve -H z = e_j; z is expected transient exposure in cm^-3*s.
 e=np.eye(7)[:,initial_j]
 z=np.linalg.solve(-h,e)
 if min(z)<-1e-3:raise SourceError('nonnegative fundamental matrix failure')
 p=q@z
 if not abs(p.sum()-1)<3e-11 or min(p)<-3e-12:raise SourceError('absorption probabilities invalid')
 fluence=float(np.sum(z)) # (cm^-3)*s
 # Sinks have source q but v0 population is a terminal event, not persistent steady state.
 e_init=CM_TO_J*v1[initial_j]
 e_final=float(CM_TO_J*(v0@p))
 bath=e_init-e_final
 edges=[]
 energy_direct=0.
 for src in range(7):
  for dst in range(7):
   if src==dst or h[dst,src]<=0:continue
   expected=h[dst,src]*z[src]
   heat=CM_TO_J*(v1[src]-v1[dst])*expected
   energy_direct+=heat
   edges.append((src,dst,expected,heat))
 for src in range(7):
  for dst in range(11):
   if q[dst,src]<=0:continue
   energy_direct+=CM_TO_J*(v1[src]-v0[dst])*q[dst,src]*z[src]
 residual=energy_direct-bath
 if abs(residual)>3e-32:raise SourceError('telescoping energy balance residual too large')
 return dict(z=z,p=p,fluence=fluence,k_eff=1./fluence,e_init=e_init,e_final=e_final,bath=bath,energy_direct=energy_direct,residual=residual,rot_edges=edges,
             total_rot_events=float(sum(e[2] for e in edges)))

def _write_csv(p:Path,cols:list[str],rows:list[list]):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf8') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(cols);w.writerows(rows)

def compute(out:Path|None=None):
 out=Path(out or ROOT/'results');out.mkdir(parents=True,exist_ok=True)
 cells,v0,v1=load_sources()
 case_rows=[];branches=[];edge_rows=[];source_rows=[];urows=[];held=[]
 for r in cells:
  source_rows.append([r[k] for k in ('table','initial_v','initial_J','final_v','final_J','T_K','token','status','rate_cm3_s')])
  if int(r['T_K'])==2005 and r['status']!='SOURCE_PRINTED_VALID':held.append({k:r[k] for k in ('table','initial_v','initial_J','final_v','final_J','T_K','token','status')})
 for T in QUALIFIED_T:
  for mode in MODES:
   h,q,downs,ups,sinks=build_generator(cells,T,v1,mode)
   if mode==MODES[0]:
    for src,dst,k in ups:urows.append([T,src,dst,k])
   for j in range(7):
    a=case_solve(h,q,v0,v1,j)
    case_rows.append([T,mode,j,a['fluence'],a['k_eff'],a['e_init'],a['e_final'],a['bath'],a['energy_direct'],a['residual'],a['total_rot_events'],len(sinks),len(downs),len(ups)])
    for dst,p in enumerate(a['p']):
     branches.append([T,mode,j,dst,p,float(v0[dst]),p*CM_TO_J*v0[dst]])
    for src,dst,count,heat in a['rot_edges']:
     edge_rows.append([T,mode,j,src,dst,count,heat])
 _write_csv(out/'SOURCE_V1_890.csv',['table','initial_v','initial_J','final_v','final_J','T_K','token','source_status','rate_cm3_s'],source_rows)
 _write_csv(out/'DERIVED_V1_UPWARD_189.csv',['T_K','initial_v1_J','final_v1_J','derived_rate_cm3_s'],urows)
 _write_csv(out/'ATLAS_QUENCH_126.csv',['T_K','mode','initial_v1_J','mean_proton_fluence_cm-3_s','effective_quench_coeff_cm3_s','initial_HD_energy_J','final_v0_energy_expect_J','proton_bath_heat_J','edge_heat_sum_J','energy_balance_residual_J','expected_v1_rot_events','n_sink_rates','n_down_rot_rates','n_derived_up_rates'],case_rows)
 _write_csv(out/'TERMINAL_V0_BRANCHES_1386.csv',['T_K','mode','initial_v1_J','terminal_v0_J','restricted_probability','terminal_E_cm-1','weighted_terminal_E_J'],branches)
 _write_csv(out/'ROTATIONAL_EVENTS_3969.csv',['T_K','mode','initial_v1_J','source_v1_J','target_v1_J','expected_transition_count','proton_bath_transfer_J'],edge_rows)
 sm={
 'schema':'wu.r32.quench.v1','temperatures_K':list(QUALIFIED_T),'held_temperature_K':[2005],
 'model_modes':list(MODES),'source_cells_v1_total':len(cells),'original_source_valid_rate_cells':sum(r['status']=='SOURCE_PRINTED_VALID' for r in cells),
 'source_cells_used_unique':sum(int(r['T_K']) in QUALIFIED_T for r in cells),
 'source_vibrational_quench_cells_9T':sum(int(r['T_K']) in QUALIFIED_T and r['final_v']=='0' for r in cells),
 'source_rotational_down_cells_9T':sum(int(r['T_K']) in QUALIFIED_T and r['final_v']=='1' for r in cells),
 'derived_rotational_up_cells':len(urows),'atlas_cases':len(case_rows),'sink_probability_rows':len(branches),'rotational_expectation_rows':len(edge_rows),
 'held_original_cells':held,'max_abs_energy_residual_J':max(abs(r[9]) for r in case_rows),
 'max_abs_probability_defect':max(abs(sum(b[4] for b in branches if (b[0],b[1],b[2])==(r[0],r[1],r[2]))-1) for r in case_rows),
 'sign_counts_bath_heat':{'positive':sum(r[7]>0 for r in case_rows),'negative':sum(r[7]<0 for r in case_rows)},
 'spectroscopy':'CDMS2011 v2 official rendered values, not byte-identical original',
 'source_pdf_sha256':SOURCE_SHA['PDF'],'source_inelastic_sha256':SOURCE_SHA['GL'],'immutable_parent_R31_sha256':SOURCE_SHA['R31'],
 'physical_Q':None,'PES_native_threshold':None,'EMAA_raw_171x25':None,'full_gas_heating':False,'new_canonical_DAG_nodes':0,'central_DAG':'34/49',
 'radiative_v1_loss':'NOT_INCLUDED_SOURCE_MISSING','reactive_v1_loss':'NOT_INCLUDED_SOURCE_MISSING','v0_reverse_reexcitation':'EXCLUDED_FIRST_PASSAGE_POLICY',
 'no_2005K_imputation':True,'distinct_author_R6':'NOT_RUN','distinct_author_C9':'NOT_RUN','production':'NOT_ISSUED'
 }
 (out/'SUMMARY.json').write_text(json.dumps(sm,ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x))+'\n',encoding='utf8')
 return sm

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results');args=p.parse_args()
 print(json.dumps(compute(args.out),ensure_ascii=False,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)))
