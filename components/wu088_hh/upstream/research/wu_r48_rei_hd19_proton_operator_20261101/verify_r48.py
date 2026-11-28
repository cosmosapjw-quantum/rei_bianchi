"""R48 independent output-table audit using stdlib CSV/math only where feasible.
Does NOT import the primary physics generator; same author, distinct implementation path.
"""
from __future__ import annotations
import csv, gzip, hashlib, json, math, os, pathlib, zipfile
from collections import Counter
ROOT=pathlib.Path(__file__).resolve().parent
S=ROOT/'results'
ORIGINAL=os.environ.get('WU_R48_EMAA_ZIP','/mnt/data/wu_r43_verify_library/WU_R43_RECOVERED_HD52_EMAA_GRACKLE_SOURCE_20261031.zip')
EMAA_SHA='b0db1613425e403889c3a74f6cd9e142c562a552f1ebf05e61cbf509cd429c94'

def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def check():
    summary=json.loads((S/'R48_RESULTS.json').read_text())
    with zipfile.ZipFile(ORIGINAL) as z:
        raw=z.read('source_private/HD.Rovibration.805a7aa5.radex')
    if hashlib.sha256(raw).hexdigest()!=EMAA_SHA:raise ValueError('invalid original input')
    lines=raw.decode().splitlines()
    plus={};neutral={}
    for i,line in enumerate(lines):
        if line.strip()!='! COLLISIONS BETWEEN':continue
        dest=plus if 'HD + H+' in lines[i+1] else neutral
        ns=int(lines[i+3]); temps=[float(v) for v in lines[i+7].split()]
        for rr in lines[i+9:i+9+ns]:
            r=rr.split();dest[int(r[1]),int(r[2])]=(temps,[float(t) for t in r[3:]])
    def scalar(T, data):
        t,r=data
        for i in range(len(t)-1):
            if t[i]<=T<=t[i+1]:
                w=math.log(T/t[i])/math.log(t[i+1]/t[i])
                return math.exp((1-w)*math.log(r[i])+w*math.log(r[i+1]))
        raise ValueError('out of native range')
    transcount=0; selected_nodes=set(); pair_seen=Counter(); lo_min=math.inf
    with gzip.open(S/'R48_ORIGINAL_19STATE_TRANSITION_RATIO_960336.csv.gz','rt',newline='') as f:
        for row in csv.DictReader(f):
            transcount+=1;node=int(row['node']);u=int(row['upper_original_level']);l=int(row['lower_original_level'])
            selected_nodes.add(node);pair_seen[(u,l)]+=1
            x=float(row['x_HII_mid']);T=float(row['T_gas_K_mid']);kH=float(row['kH_down_cm3_s']);kp=float(row['kHplus_down_cm3_s']);R=float(row['Gamma_Hplus_over_H_mid']);loB=float(row['ratio_rect_outer_lower']);hiB=float(row['ratio_rect_outer_upper'])
            if not (0<=x<1 and loB<=R*(1+3e-13)<=hiB*(1+3e-13) and loB>1):raise ValueError('ratio interval failed')
            if not math.isclose(R,x/(1-x)*kp/kH,rel_tol=4e-13):raise ValueError('source ratio equation')
            if transcount in (1,100,100000,250000,500000,750000,960336):
                if not math.isclose(kH,scalar(T,neutral[u,l]),rel_tol=2e-13):raise ValueError('independent H interpolation')
                if not math.isclose(kp,scalar(T,plus[u,l]),rel_tol=2e-13):raise ValueError('independent H+ interpolation')
            lo_min=min(lo_min,loB)
    if transcount!=960336 or len(selected_nodes)!=5616 or len(pair_seen)!=171 or set(pair_seen.values())!={5616}:
        raise ValueError('source pair/node counts')
    exit_count=0;exit_min=math.inf
    with gzip.open(S/'R48_REI_HD19_LEVEL_EXITS_106704.csv.gz','rt') as f:
        for r in csv.DictReader(f):
            exit_count+=1;h=float(r['H_exit_per_nHnuc_cm3_s']);p=float(r['Hplus_exit_per_nHnuc_cm3_s']);ratio=float(r['Hplus_over_H_level_exit'])
            if not(h>0 and p>0 and math.isclose(ratio,p/h,rel_tol=4e-13)):
                raise ValueError('exit rate row')
            exit_min=min(exit_min,ratio)
    if exit_count!=106704:raise ValueError('exit row count')
    with (S/'R48_REI_NODE_SUMMARY_5616.csv').open() as f:nodes=list(csv.DictReader(f))
    with (S/'R48_TRANSITION_SUMMARY_171.csv').open() as f:transitions=list(csv.DictReader(f))
    if len(nodes)!=5616 or len(transitions)!=171:raise ValueError('summary row count')
    if abs(lo_min-summary['physical_results']['minimum_rectangular_source_temperature_ionization_ratio_bound'])>3e-10:raise ValueError('original min ratio summary discrepancy')
    if abs(exit_min-summary['physical_results']['per_node_minimum_19state_exit_ratio']['min'])>4e-8:raise ValueError('exit min summary discrepancy')
    for i in [0,5615,2808]:
        row=nodes[i]; lo=float(row['LTE_Q52_outside_Hplus19_lo']);mid=float(row['LTE_Q52_outside_Hplus19_mid']);hi=float(row['LTE_Q52_outside_Hplus19_hi'])
        if not(0<lo<=mid<=hi<1):raise ValueError('LTE partition support')
        if float(row['ratio_gap_Hplus_over_H'])<float(row['ratio_min_171_outer_lower'])*(1-1e-7):raise ValueError('gap Dirichlet lower')
    result={'audit':'SOURCE_DERIVED_OUTPUT_STRICT','transition_rows':transcount,'unique_real_source_nodes':len(selected_nodes),'different_original_transition_pairs':len(pair_seen),'level_exit_rows':exit_count,'node_summary_rows':len(nodes),'transition_summary_rows':len(transitions),'global_rate_ratio_outer_min':lo_min,'exit_ratio_min':exit_min,'sampled_original_rate_interpolation':'PASS','source_SHA256':EMAA_SHA,'distinct_author':'NOT_RUN','DAG_WU':'34/49','DAG_REI':'28/88'}
    (ROOT/'INDEPENDENT_OUTPUT_AUDIT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':check()
