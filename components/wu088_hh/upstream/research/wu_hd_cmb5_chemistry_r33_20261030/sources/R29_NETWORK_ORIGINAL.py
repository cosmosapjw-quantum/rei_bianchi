"""WU R29: source-locked five-level HD absorption / rotational transfer physical atlas.

All input rates come from immutable JCP2022 GL SQM printed original data.
Upward HD collisions are detailed-balance DERIVED using REC162 displayed CDMS2011 v2
term energies, not independently tabulated GL2022 source rates. Spontaneous A from
REC161 text transcription, not original 2021 file-byte identity.

This is a fixed-T, fixed-n(H+) HD-tracer, selected-channels Markov generator.
Do NOT interpret as a full astrochemical network, source-native physical Q,
measurements, or production rate adapter. No unprinted vibrational products.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,re
from dataclasses import dataclass
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parent.parent
SHA = {
 'reactive':'f49312061552513ffdef5aa6d144f7edb9727f8b8cb3ce6e29bd262f15845db9',
 'inelastic':'58c252a1c3f62995ed748c7620e342bc98d8aabb307271bff48f7711e4f1cd7c',
 'radiative':'887383f3978de55ed82079feeff13361ff3910d9a1c384fa2d3b9c982bdb5ef8',
 'energies':'769834947ec6630887ad3b9eae2f4d487c0dffecc268a0512521ee2a79127cca',
}
FILES={'reactive':'GL2022_700_SOURCE.json','inelastic':'GL2022_1560_INELASTIC_SOURCE_TOKENS.csv',
       'radiative':'REC161_LAMDA_A_TRANSCRIPTION_REF.json','energies':'REC162_CDMS2011V2_PRINTED_LEVELS.json'}
TEMPS=(55,105,255,505,1005,2005,3005)
LEVELS=range(5)
POLICIES=('raw_SQM','Eq6-7_spin_effective')
DENSITY_RATIOS=(0.1,1.,10.)
SPEED_LIGHT=299792458.
PLANCK=6.62607015e-34
BOLTZMANN=1.380649e-23
LIT_RE=re.compile(r'^(?:\d+(?:\.\d*)?|\.\d+)\((\d{1,2})\)$')

class SourceError(ValueError):pass

def read_verified(name):
    b=(BASE/'sources'/FILES[name]).read_bytes()
    h=hashlib.sha256(b).hexdigest()
    if h!=SHA[name]:raise SourceError(f'{name}: immutable source bytes mismatch: {h}')
    return b

def decode_token(token):
    m=LIT_RE.fullmatch(token)
    if not m or token.startswith(('0.00(','.000(')):raise SourceError(f'unqualified rate token {token!r}')
    x=float(token.split('(')[0])*10**(-int(m.group(1)))
    if x<=0 or not math.isfinite(x):raise SourceError('not positive printed source rate')
    return x

@dataclass(frozen=True)
class Grid:
    q:dict
    down:dict
    A:dict
    energies_cm1:dict
    source_meta:dict

def load_grid():
    chem=json.loads(read_verified('reactive'))
    if chem['temperature_nodes_K']!=[15,55,105,255,505,1005,1505,2005,2505,3005]:
        raise SourceError('changed reactive temperature support')
    if chem['pdf_sha256']!='a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754':
        raise SourceError('original PDF claim changed')
    for flag in chem.get('source_suspect_cells',[]):
        # Source suspect flags always remain visible in source; currently selected domain never J5 or 2505 K.
        pass
    rad=json.loads(read_verified('radiative'))
    ens=json.loads(read_verified('energies'))
    if rad['source_head']!='5bf22a4258ba571e8aebb1cfedab9cafe7ac6481' or ens['source_HEAD']!='4d60f74db02d7435add062eaefb15739e68c4b55':
        raise SourceError('changed REC source author')
    energies={int(x['J']):float(x['E_cm1']) for x in ens['levels']}
    A={int(j):float(x) for j,x in rad['radiative_j_to_j_minus_1_A_per_second'].items() if int(j) in LEVELS}
    assert len(A)==4 and len(energies)>=5
    rows=list(csv.DictReader(read_verified('inelastic').decode('ascii').splitlines()))
    if len(rows)!=1560:raise SourceError('source 1560 cell shape changed')
    down={}
    for r in rows:
        j,i,v,vout,T=map(int,[r['initial_J'],r['final_J'],r['initial_v'],r['final_v'],r['T_K']])
        if T not in TEMPS or v!=0 or vout!=0 or j not in LEVELS or i>=j:continue
        if r['status']!='SOURCE_PRINTED_VALID' or r['source_token_valid']!='True':
            raise SourceError(f'source flag in chosen domain: {(T,j,i)}')
        key=(T,j,i)
        if key in down:raise SourceError(f'duplicate down {key}')
        down[key]=decode_token(r['token'])
    if len(down)!=len(TEMPS)*10:raise SourceError(f'incomplete 5-state source edges: {len(down)}')
    q={}
    for T in TEMPS:
        ti=chem['temperature_nodes_K'].index(T)
        for j in LEVELS:
            for h2 in range(10):
                tok=chem['tokens_jprime_j_T'][h2][j][ti]
                key=(T,j,h2)
                if key in q:raise SourceError('duplicate chemical rate')
                q[key]=decode_token(tok)
    if len(q)!=len(TEMPS)*5*10:raise SourceError('incomplete chemical source')
    return Grid(q,down,A,energies,{
        'reactive_DOI':chem['doi'],'source_PDF_SHA':chem['pdf_sha256'],
        'temperatures_K':list(TEMPS),'J':list(LEVELS),
        'source_printed_reactive_cells_used':len(q),'source_printed_downward_cells_used':len(down),
        'upward_rates':'derived_detailed_balance_not_original_printed',
        'levels':'REC162_CDMS2011_V2_rendered_official_text_NOT_RAW_BYTES',
        'EinsteinA':'REC161_Leiden2021_visible_transcription_NOT_RAW_BYTES'})

def reaction_vector(grid,T,j,policy):
    if policy not in POLICIES or T not in TEMPS or j not in LEVELS:raise ValueError('source scope')
    return np.array([grid.q[(T,j,k)]*(1 if policy=='raw_SQM' else (.75 if k%2 else .25)) for k in range(10)])

def reference_density(grid,T,policy):
    k=float(reaction_vector(grid,T,2,policy).sum())
    if k<=0:raise SourceError('zero reaction')
    return grid.A[2]/k  # cm^-3, from A s^-1 and k cm^3 s^-1

def assemble(grid,T,policy,proton_density_cm3):
    if T not in TEMPS or policy not in POLICIES or proton_density_cm3<=0 or not math.isfinite(proton_density_cm3):
        raise ValueError('exact temperature / chosen policy / positive proton density required')
    n=proton_density_cm3
    # Column convention: G[target J, origin J]; exponential transient dynamics x'(t)=G x(t).
    G=np.zeros((5,5));GC=np.zeros((5,5)); G_first_photon=np.zeros((5,5));
    chem=np.array([n*reaction_vector(grid,T,j,policy).sum() for j in LEVELS]);
    # GC pure collisional generator, detailed balance reversible at fixed T.
    for j in range(1,5):
        for i in range(j):
            down=n*grid.down[(T,j,i)]
            de=(grid.energies_cm1[j]-grid.energies_cm1[i])*100*PLANCK*SPEED_LIGHT
            up=down*((2*j+1)/(2*i+1))*math.exp(-de/(BOLTZMANN*T))
            for M in [GC,G,G_first_photon]:
                M[i,j]+=down;M[j,j]-=down
                M[j,i]+=up;M[i,i]-=up
    for j in range(1,5):
        rad=grid.A[j]
        G[j-1,j]+=rad
        G[j,j]-=rad
        G_first_photon[j,j]-=rad  # photon is absorbing as a *first* event
    for j in LEVELS:
        G[j,j]-=chem[j]
        G_first_photon[j,j]-=chem[j]
    return G,GC,G_first_photon,chem

def run_case(grid,T,policy,ratio,start_J):
    if start_J not in LEVELS or ratio not in DENSITY_RATIOS:raise ValueError('source case')
    n=reference_density(grid,T,policy)*ratio
    G,GC,G_first_photon,chem=assemble(grid,T,policy,n)
    e=np.zeros(5);e[start_J]=1
    m=np.linalg.solve(-G,e)  # seconds of integrated occupancy in each level
    m_first=np.linalg.solve(-G_first_photon,e)
    if min(m)<-1e-5:raise AssertionError('negative occupancy')
    product=np.array([sum(n*reaction_vector(grid,T,j,policy)[k]*m[j] for j in LEVELS) for k in range(10)])
    rx_level=chem*m
    first_photon_prob=sum(grid.A[j]*m_first[j] for j in range(1,5))
    photons=sum(grid.A[j]*m[j] for j in range(1,5))
    waiting=float(m.sum())
    weights=np.array([(2*j+1)*math.exp(-(grid.energies_cm1[j]-grid.energies_cm1[0])*100*PLANCK*SPEED_LIGHT/(BOLTZMANN*T)) for j in LEVELS]);weights/=weights.sum()
    detailed=float(np.linalg.norm(GC@weights,ord=np.inf))
    if abs(sum(rx_level)-1)>1e-9 or abs(product.sum()-1)>1e-9 or not (0<=first_photon_prob<=1+1e-8) or detailed>1e-16:
        raise AssertionError(f'bad physical invariant: {T,policy,ratio,start_J,product.sum(),first_photon_prob,detailed}')
    return dict(T_K=T,policy=policy,ratio_n_over_ncrit_J2=ratio,initial_J=start_J,nHplus_cm3=n,
        expected_time_to_restricted_exchange_s=waiting,
        probability_one_or_more_photons_before_exchange=float(first_photon_prob),
        expected_photons_before_exchange=float(photons),
        restricted_exchange_reaction_level_probabilities=rx_level.tolist(),
        restricted_H2_v0_product_Jprime_probabilities=product.tolist(),
        restricted_H2_v0_odd_Jprime_probability=float(sum(product[k] for k in range(1,10,2))),
        initial_HD_J2_ncrit_cm3=reference_density(grid,T,policy),
        col_boltzmann_reversible_residual_per_second=detailed,
        validity='CONDITIONAL_SOURCE_SQM_TRACER_FIXED_T_NHP_5LEVEL')

def make_atlas(grid):
    return [run_case(grid,T,policy,ratio,J) for T in TEMPS for policy in POLICIES for ratio in DENSITY_RATIOS for J in LEVELS]

def write_atlas(out):
    grid=load_grid();data=make_atlas(grid);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    meta={'schema':'wu.r29.source_qualified_hd5_detailed_balance_absorption_v1','source_status':grid.source_meta,
          'row_count':len(data),'physical_scope':'5-level HD J0..4 at T original seven source-grid nodes; fixed nHplus tracer; detailed balance upward derived from rendered 2011 CDMS energies; 2022 SQM printed downward and chemistry; REC161 printed A; no full network cosmology',
          'canonical_DAG':[34,49],'auxiliary_scoped_new_physics':[1,1],
          'PES_native_Q':None,'owner_ACK':None,'HH_R10':'OFF','L4':False,'full_A':None,'production':'NOT_ISSUED','R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN'}
    content={'metadata':meta,'rows':data}
    (out/'ATLAS_210_STATE_CASES.json').write_text(json.dumps(content,indent=2,ensure_ascii=False)+'\n')
    columns=['T_K','policy','ratio_n_over_ncrit_J2','initial_J','nHplus_cm3','expected_time_to_restricted_exchange_s','probability_one_or_more_photons_before_exchange','expected_photons_before_exchange','restricted_H2_v0_odd_Jprime_probability','initial_HD_J2_ncrit_cm3','validity']
    with (out/'ATLAS_210_STATE_CASES.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(data)
    summaries={'schema':'wu.r29.science_summary.v1','num_cases':len(data),'temperatures_K':list(TEMPS),'levels':list(LEVELS),'example_cases':[x for x in data if x['initial_J']==2 and x['ratio_n_over_ncrit_J2']==1.0 and x['T_K'] in [105,255,1005]],
               'first_photon_vs_reaction_extension':'full_5level_detailed_balance_master_vs_previous_first_event',
               'source_authority':meta['source_status'],'canonical_DAG':[34,49]}
    (out/'SUMMARY.json').write_text(json.dumps(summaries,indent=2)+'\n')
    return summaries

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default=str(BASE/'results'));a=p.parse_args();s=write_atlas(a.out)
    for x in s['example_cases']:
        print('T',x['T_K'],'policy',x['policy'],'p_photon',x['probability_one_or_more_photons_before_exchange'],
          'mean_nphotons',x['expected_photons_before_exchange'],'oddJp',x['restricted_H2_v0_odd_Jprime_probability'])
if __name__=='__main__':main()
