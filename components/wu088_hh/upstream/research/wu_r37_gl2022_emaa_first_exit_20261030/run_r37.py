"""WU R37: source-locked five-state chemistry vs first-exit from the documented HD subspace.

User-supplied GL2022 article and Velilla2008 article support the theoretical scope.
Numerical inputs are EXACT frozen original GL2022 SQM supplementary transcription and
user-uploaded EMAA RADEX bytes restored from R36. Do not treat missing channels as zero.
"""
from pathlib import Path
import csv, io, json, hashlib, math, re, zipfile
import numpy as np
import mpmath as mp
from scipy.constants import h, c, k as k_B
from sys import path as syspath

ROOT=Path(__file__).resolve().parent
SRC=ROOT/'sources'
RAW=SRC/'HD.Rovibration.805a7aa5.radex'
CHEM=SRC/'GL2022_700_SOURCE.json'
syspath.insert(0,str(ROOT/'r36_lib'))
from emaa_primary import parse_radex,bath_rates,HCK,HCJ

GL_TOKEN=re.compile(r'([0-9]+(?:\.[0-9]+)?)\(([0-9]+)\)')
T_GRID=(55,105,255,505,1005,1505,2005,3005)
DENS=(1e-2,1.0,1e3,1e6)
ZGRID=('OFF',0,10,30,100,300)
SPIN=('eq6_7_spin_weighted','unweighted_source_counterfactual')
EXPECTED={
 'EMAA':'b0db1613425e403889c3a74f6cd9e142c562a552f1ebf05e61cbf509cd429c94',
 'GL700':'f49312061552513ffdef5aa6d144f7edb9727f8b8cb3ce6e29bd262f15845db9',
 'GL_MAIN':'1eb1a42d0ef9148d86e6e39119f270e2adbcd3bab8926ec7077bf160c2575362',
 'VELILLA_MAIN':'ed6f0c7ab5af334b217f450b6cf90f6eaaf1afe34d4523e4cd08a09228c07dcd'
}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse_token(s):
 m=GL_TOKEN.fullmatch(s)
 if not m: raise ValueError(f'Untrusted or invalid SQM token {s!r} cannot be coerced to zero')
 return float(m.group(1))*10.0**(-int(m.group(2)))

def verify_inputs():
 assert sha(RAW)==EXPECTED['EMAA']
 assert sha(SRC/'214302_1_online.pdf')==EXPECTED['GL_MAIN']
 assert sha(SRC/'084307_1_online.pdf')==EXPECTED['VELILLA_MAIN']
 assert sha(CHEM)==EXPECTED['GL700'], 'GL2022 reaction source SHA mismatch'
 a=json.loads(CHEM.read_bytes()); assert a['shape']==[10,7,10]
 assert a['pdf_sha256']=='a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754'
 assert all(T in a['temperature_nodes_K'] for T in T_GRID)
 return a

def source_reaction(data,a,T,policy):
 """Raw GL2022 v0 J=0..4 -> H2 v0 J'=0..9, spin choice stated.

 Paper Eqs 6-7 impose 1/4 on even and 3/4 on odd product-J summands.
 No chemistry outside the selected 5-state region is inferred.
 """
 t=a['temperature_nodes_K'].index(T)
 Q=np.zeros((10,5)) # cm3/s, final H2 product, source HD
 for jp in range(10):
  for j in range(5):
   k=parse_token(a['tokens_jprime_j_T'][jp][j][t])
   if policy=='eq6_7_spin_weighted':k*=(.25 if jp%2==0 else .75)
   Q[jp,j]=k
 assert np.min(Q)>0
 return Q

def radex_all52(data,Tr):
 """HITRAN-pinned A coefficients in EMAA's original 52-level spectroscopic section.

 Include all radiative exits FROM the five selected HD states, including
 absorption to levels higher than the collisional 19-state domain. Those exits
 are censor events, not backfilled rates or physical zero channels.
 """
 R=np.zeros((52,52))
 lv=data['levels']
 for edge in data['radiative']:
  u=edge['up']-1;l=edge['low']-1
  de=lv[u+1]['E']-lv[l+1]['E'];g=lv[u+1]['g']/lv[l+1]['g']
  x=HCK*de/Tr if Tr>0 else math.inf
  occ=1/math.expm1(x) if x<700 else 0.0
  down=edge['A']*(1+occ);up=edge['A']*g*occ
  R[l,u]+=down;R[u,l]+=up
 np.fill_diagonal(R,-R.sum(axis=0))
 return R

def solve_case(data,a,T,n,z,policy):
 qcoeff=source_reaction(data,a,T,policy)
 q=n*qcoeff
 Cr=bath_rates(data,T,n)
 Tr=0.0 if z=='OFF' else 2.7255*(1+z)
 R=radex_all52(data,Tr)
 kill_chem=q.sum(axis=0)
 kill_coll=np.sum(Cr[5:,:5],axis=0)
 kill_rad=np.sum(R[5:,:5],axis=0)
 exit_coll_rot=np.sum(Cr[5:12,:5],axis=0)
 exit_coll_vib=np.sum(Cr[12:19,:5],axis=0)
 exit_rad_rot=np.sum(R[5:12,:5],axis=0)
 exit_rad_vib=np.sum(R[12:,:5],axis=0)
 assert np.allclose(exit_coll_rot+exit_coll_vib,kill_coll,atol=1e-20,rtol=1e-12)
 assert np.allclose(exit_rad_rot+exit_rad_vib,kill_rad,atol=1e-20,rtol=1e-12)
 G=Cr[:5,:5]+R[:5,:5]
 np.fill_diagonal(G,0.0)
 np.fill_diagonal(G,-np.sum(G,axis=0)-kill_chem-kill_coll-kill_rad)
 assert np.max(np.abs(np.sum(G,axis=0)+kill_chem+kill_coll+kill_rad))<1e-7
 # Build the diagonal in arbitrary precision from the documented outgoing
 # hazards; this avoids catastrophic cancellation at low proton density.
 with mp.workdps(65):
  A=mp.matrix(5,5)
  for jj in range(5):
   for ii in range(5):
    if ii!=jj:A[ii,jj]=mp.mpf(repr(float(G[ii,jj])))
   A[jj,jj]=-sum(A[ii,jj] for ii in range(5) if ii!=jj) \
             -mp.mpf(repr(float(kill_chem[jj]))) \
             -mp.mpf(repr(float(kill_coll[jj]))) -mp.mpf(repr(float(kill_rad[jj])))
  Nmp=mp.inverse(-A)
  chem_m=mp.matrix(10,5)
  for ii in range(10):
   for jj in range(5):chem_m[ii,jj]=mp.mpf(repr(float(q[ii,jj])))
  products_m=chem_m*Nmp
  c_m=mp.matrix([[mp.mpf(repr(float(kill_coll[j]))) for j in range(5)]])*Nmp
  r_m=mp.matrix([[mp.mpf(repr(float(kill_rad[j]))) for j in range(5)]])*Nmp
  collrot_m=mp.matrix([[mp.mpf(repr(float(exit_coll_rot[j]))) for j in range(5)]])*Nmp
  collvib_m=mp.matrix([[mp.mpf(repr(float(exit_coll_vib[j]))) for j in range(5)]])*Nmp
  radrot_m=mp.matrix([[mp.mpf(repr(float(exit_rad_rot[j]))) for j in range(5)]])*Nmp
  radvib_m=mp.matrix([[mp.mpf(repr(float(exit_rad_vib[j]))) for j in range(5)]])*Nmp
  mass_m=[sum(products_m[k,j] for k in range(10))+c_m[0,j]+r_m[0,j] for j in range(5)]
  defect=float(max(abs(s-1) for s in mass_m))
  N=np.array(Nmp.tolist(),dtype=float)
  probs=np.array(products_m.tolist(),dtype=float)
  pc=np.sum(probs,axis=0)
  peC=np.array(c_m.tolist(),dtype=float).reshape(-1)
  peR=np.array(r_m.tolist(),dtype=float).reshape(-1)
  collrot=np.array(collrot_m.tolist(),dtype=float).reshape(-1)
  collvib=np.array(collvib_m.tolist(),dtype=float).reshape(-1)
  radrot=np.array(radrot_m.tolist(),dtype=float).reshape(-1)
  radvib=np.array(radvib_m.tolist(),dtype=float).reshape(-1)
 if min(np.min(probs),np.min(N),np.min(pc),np.min(peC),np.min(peR))< -1e-12 or defect>2e-12:
  raise ValueError(f'Negative or non-normalized absorbing Markov probability: {defect}; T={T} n={n} z={z} policy={policy}')
 cases=[];branches=[]
 for init in range(5):
  case={'Tgas_K':T,'n_Hplus_cm_minus3':n,'z_boundary':z,'T_rad_K':Tr,
        'spin_policy':policy,'initial_v0_J':init,'P_H2_before_first_exit':float(pc[init]),
        'P_collision_exit_first':float(peC[init]),'P_radiative_exit_first':float(peR[init]),
        'P_total_exit_first':float(peC[init]+peR[init]),
        'P_collision_exit_v0_highJ':float(collrot[init]),
        'P_collision_exit_v1':float(collvib[init]),
        'P_radiative_exit_v0_highJ':float(radrot[init]),
        'P_radiative_exit_vib_or_higher':float(radvib[init]),
        'mean_time_to_first_termination_s':float(N[:,init].sum()),
        'max_probability_defect':defect}
  cases.append(case)
  for jp in range(10):
   branches.append({'Tgas_K':T,'n_Hplus_cm_minus3':n,'z_boundary':z,
                    'spin_policy':policy,'initial_v0_J':init,'H2_final_v':0,'H2_final_J':jp,
                    'P_H2_J_before_first_exit':float(probs[jp,init])})
 return cases,branches,G,N

def paper_eq5_partial(data,a):
 """Paper Eq5 restricted to trusted initial J<=4 plus 6, not full J<=8.

 Exclude J5 duplicated source row, J7-8 unpublished, 15K .000(00), 2505K
 malformed J3 jprime7 exponent. Full Zrot is J0..8, so this partial sum
 is a conditional nonnegative subset of the article's total thermal formula.
 """
 rows=[]
 for T in T_GRID:
  z9=sum((2*j+1)*math.exp(-HCK*data['levels'][j+1]['E']/T) for j in range(9))
  t=a['temperature_nodes_K'].index(T)
  partials={};
  for j in (0,1,2,3,4,6):
   rate=sum(parse_token(a['tokens_jprime_j_T'][jp][j][t])*(.25 if jp%2==0 else .75) for jp in range(10))
   partials[j]=(2*j+1)*math.exp(-HCK*data['levels'][j+1]['E']/T)*rate/z9
  subtotal=sum(partials.values())
  paper=parse_token(a['table11_thermal_nominal_tokens'][t])
  assert 0<subtotal<=paper*(1+1e-3) # observed diagnostic only; source energy basis differs
  rows.append({'Tgas_K':T,'Eq5_partial_J0to4_plus_J6_cm3_s':subtotal,
               'Eq5_partial_J0to4_cm3_s':sum(partials[j] for j in range(5)),
               'paper_table11_thermal_nominal_cm3_s':paper,
               'partial_fraction_of_printed_total':subtotal/paper,
               'paper_minus_EMAA_energy_hybrid_partial_cm3_s':paper-subtotal,
               'Zrot_J0to8':z9,'excluded_J':'5,7,8',
               'evidence':'paper Eq5-7 applied to source GL2022 700 cells and EMAA/HITRAN rotation energies; hybrid energy reference, no interpolation, not exact reproduction of author Zrot'})
 return rows

def dump(path,rows):
 path.parent.mkdir(exist_ok=True,parents=True)
 with path.open('w',newline='',encoding='utf-8') as fh:
  w=csv.DictWriter(fh,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def main(out):
 a=verify_inputs();data=parse_radex(RAW)
 assert set(T_GRID).issubset(data['partners'][7]['temps'])
 cases=[];products=[];examples={}
 for T in T_GRID:
  for n in DENS:
   for z in ZGRID:
    for policy in SPIN:
     cr,pr,G,N=solve_case(data,a,T,n,z,policy)
     cases.extend(cr);products.extend(pr)
     if T==105 and n==1e3 and z==30 and policy==SPIN[0]:examples={'matrix_G_s_inv':G.tolist(),'residence_s':N.tolist(),'cases':cr}
 eq5=paper_eq5_partial(data,a)
 out=Path(out);out.mkdir(exist_ok=True,parents=True)
 dump(out/'R37_CHEM_VS_EXIT_1920.csv',cases)
 dump(out/'R37_CHEM_H2_PRODUCT_19200.csv',products)
 dump(out/'R37_PAPER_EQ5_PARTIAL_8.csv',eq5)
 by={}
 for T in T_GRID:
  sel=[x for x in cases if x['Tgas_K']==T and x['spin_policy']==SPIN[0]]
  by[str(T)]={'pchem_min':min(x['P_H2_before_first_exit'] for x in sel),'pchem_max':max(x['P_H2_before_first_exit'] for x in sel),
             'max_P_radiative_exit':max(x['P_radiative_exit_first'] for x in sel),
             'max_P_collision_exit':max(x['P_collision_exit_first'] for x in sel)}
 summ={'scheme':'R37_RESTRICTED_SOURCE_GRAPH_CHEMISTRY_FIRST_EXIT','input_source_SHA256':{'EMAA':sha(RAW),'GL700':sha(CHEM),'GL_main':sha(SRC/'214302_1_online.pdf'),'Velilla_main':sha(SRC/'084307_1_online.pdf')},
       'science_bound':'Initial HD(v=0,J0..4), terminate at original GL2022 restricted H2 production or first exit via documented EMAA H+ inelastic or HITRAN A radiation; no physics after first exit. Missing other physical channels remain unknown.',
       'Tgrid':T_GRID,'densities_cm3':DENS,'radiation_boundaries':ZGRID,'spin_policies':SPIN,
       'rows':{'first_termination_cases':len(cases),'H2_product_rows':len(products),'Eq5_partial_rows':len(eq5)},
       'max_abs_mass_defect':max(x['max_probability_defect'] for x in cases),
       'min_pchem':min(x['P_H2_before_first_exit'] for x in cases),'max_pchem':max(x['P_H2_before_first_exit'] for x in cases),
       'min_p_escape_coll':min(x['P_collision_exit_first'] for x in cases),'max_p_escape_coll':max(x['P_collision_exit_first'] for x in cases),
       'min_p_escape_rad':min(x['P_radiative_exit_first'] for x in cases),'max_p_escape_rad':max(x['P_radiative_exit_first'] for x in cases),
       'by_T_spin_effective':by,'example_105_n1e3_z30':examples,
       'canonical_DAG':'34/49_UNCHANGED','auxiliary':'1/1_SCOPED','R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN',
       'PES_native_threshold':None,'PHYSICAL_Q':None,'OWNER_ACK':'NOT_OBTAINED','FULL_A':None,'L4':False,'PRODUCTION':'NOT_ISSUED'}
 (out/'SUMMARY.json').write_text(json.dumps(summ,indent=2,ensure_ascii=False,default=list)+'\n')
 print(json.dumps({k:v for k,v in summ.items() if k in ['rows','max_abs_mass_defect','min_pchem','max_pchem','min_p_escape_coll','max_p_escape_coll','min_p_escape_rad','max_p_escape_rad','by_T_spin_effective']},indent=2))
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--out',default=str(ROOT/'results'));args=p.parse_args();main(args.out)
