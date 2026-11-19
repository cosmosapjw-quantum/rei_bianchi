#!/usr/bin/env python3
"""Consume original T0/T1 data; no integration, source replacement or extrapolation."""
import argparse, csv, gzip, hashlib, importlib.util, io, json, math, platform, time
from pathlib import Path
import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator

UNIT=Path(__file__).resolve().parents[1]
REPO=UNIT.parents[1]
T1=REPO/'research/rei_ax11_t1_wave_20261116'
FHE=.2454/(4*(1-.2454))
EV=1.602176634e-12
KB=1.380649e-16
CHI=np.array([13.598434599702,24.587389011,54.41776])
YEAR=31557600.
GAS=['x_HI','x_HII','x_HeI','x_HeII','x_HeIII','xe_per_H','temperature_K']
EXTRA=['Gamma_HI_per_s','Gamma_HeI_per_s','Gamma_HeII_per_s','photon_n_per_H',
       'photon_u_eV_per_H','J0_photon_u_eV_per_H','J1_photon_u_eV_per_H','J2_photon_u_eV_per_H',
       'H_per_s','nH_proper_cm3','ne_proper_cm3','b','Sigma']
LNAMES=['source_N_per_H','source_U_eV_per_H','absorbed_N_per_H','escape_U_eV_per_H',
        'boundary_N_per_H','boundary_U_eV_per_H','thermal_work_eV_per_H','photon_work_eV_per_H',
        'signed_CMB_input_eV_per_H','DR_events_per_H','CE_cap_eV_per_H','excluded_DR_eV_per_H']
LNAMES += [f'{family}_{i}_per_H' for family in ['RR_events','CI_events','photo_events','CI_floor_events'] for i in range(3)]

def require(condition,message):
    if not condition: raise ValueError(message)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load_json(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f: return json.load(f)

def dump(p,x):
    require(not p.exists(),'OUTPUT_EXISTS:'+str(p))
    p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')

def table(p,rows):
    require(rows and not p.exists(),'TABLE_EMPTY_OR_EXISTS')
    if p.suffix=='.gz':
        with p.open('xb') as raw, gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as packed, io.TextIOWrapper(packed,encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    else:
        with p.open('x',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def csv_rows(p):
    with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return list(csv.DictReader(f))

def checkpoint(p):
    lines=p.read_text().splitlines();require(len(lines)==6 and lines[0]=='AXBI_CHECKPOINT_V2','CHECKPOINT_FORMAT')
    state=list(map(float,lines[1].split()));counts=list(map(int,lines[2].split()));ledger=list(map(float,lines[3].split()));photons=list(map(float,lines[4].split()))
    require(len(state)==11 and len(counts)==6 and len(ledger)==24,'CHECKPOINT_SHAPE')
    return {'a':state[0],'time_s':state[1],'b':state[2],'x_HII':state[3],'x_HeII':state[4],'x_HeIII':state[5],
            'w_erg_per_H':state[6],'counts':counts,'ledger':dict(zip(LNAMES,ledger)),'photons':photons,
            'initial_energy_eV_per_H':float(lines[5]),'sha256':sha(p)}

def binding(cp):
    return CHI[0]*cp['x_HII']+FHE*(CHI[1]*cp['x_HeII']+(CHI[1]+CHI[2])*cp['x_HeIII'])

def endpoint(level,case,cp,history,ledger_native):
    require(cp['a']==.2 and cp['counts'][0]>0,'NOT_NATIVE_ENDPOINT')
    for k in ['a','time_s','b','x_HII','x_HeII','x_HeIII']:require(float(history[k])==cp[k],'ENDPOINT_STATE:'+k)
    l=cp['ledger']
    for k,v in l.items(): require(v==ledger_native[k],'CHECKPOINT_LEDGER:'+k)
    xe=cp['x_HII']+FHE*(cp['x_HeII']+2*cp['x_HeIII'])
    temp=cp['w_erg_per_H']/(1.5*KB*(1+FHE+xe))
    require(abs(temp-float(history['temperature_K']))<5e-11,'EOS')
    N=float(history['photon_n_per_H']);U=float(history['photon_u_eV_per_H']);W=cp['w_erg_per_H']/EV;B=float(binding(cp));E0=cp['initial_energy_eV_per_H']
    photon_res=math.fsum([N,l['absorbed_N_per_H'],l['boundary_N_per_H'],-l['source_N_per_H']])
    energy_res=math.fsum([W,B,U,l['escape_U_eV_per_H'],l['boundary_U_eV_per_H'],l['thermal_work_eV_per_H'],l['photon_work_eV_per_H'],-l['source_U_eV_per_H'],-l['signed_CMB_input_eV_per_H'],-E0])
    require(abs(photon_res)<=1e-8*max(1,l['source_N_per_H']),'ORIGINAL_PHOTON_GATE')
    require(abs(energy_res)<=1e-8*max(1,l['source_U_eV_per_H']),'ORIGINAL_ENERGY_GATE')
    require(abs(math.fsum(cp['photons'])-N)<1e-12*max(1,N),'CHECKPOINT_PHOTON_STOCK')
    A=[l[f'photo_events_{i}_per_H']+l[f'CI_events_{i}_per_H']-l[f'RR_events_{i}_per_H'] for i in range(3)]
    net=[A[0],A[1]-l['DR_events_per_H'],A[2]]
    residuals={'HII':cp['x_HII']-.0002-net[0],
               'HeII_plus_HeIII_per_H':FHE*(cp['x_HeII']+cp['x_HeIII'])-net[1],
               'HeIII_per_H':FHE*cp['x_HeIII']-net[2],
               'electron_per_H':xe-.0002-sum(net)}
    base={'level':level,'case':case,'a':cp['a'],'time_s':cp['time_s'],'temperature_K':temp,
          'x_HII':cp['x_HII'],'x_HeII':cp['x_HeII'],'x_HeIII':cp['x_HeIII'],'xe_per_H':xe,
          'gas_thermal_eV_per_H':W,'gas_binding_eV_per_H':B,'photon_n_per_H':N,'photon_u_eV_per_H':U,
          'mean_photon_energy_eV':U/N,'source_mean_energy_eV':l['source_U_eV_per_H']/l['source_N_per_H'],
          'initial_energy_eV_per_H':E0,**l,**{k:float(history[k]) for k in EXTRA if k not in ['photon_n_per_H','photon_u_eV_per_H']}}
    checks={'photon_residual_reconstructed':photon_res,'photon_residual_native':ledger_native['photon_count'],
            'energy_residual_reconstructed':energy_res,'energy_residual_native':ledger_native['augmented_energy_eV_per_H'],
            'event_balance_residuals':residuals,'event_residual_status':'MEASURED; no new cumulative tolerance invented',
            'absorbed_minus_photo_event_sum':l['absorbed_N_per_H']-sum(l[f'photo_events_{i}_per_H'] for i in range(3)),
            'checkpoint_sha256':cp['sha256']}
    fractions={'stock':N/l['source_N_per_H'],'absorbed':l['absorbed_N_per_H']/l['source_N_per_H'],'grid_boundary':l['boundary_N_per_H']/l['source_N_per_H']}
    energy={'photon_stock':U,'thermal_gas':W,'binding_gas':B,'escaped_thermal_radiation':l['escape_U_eV_per_H'],
            'grid_boundary':l['boundary_U_eV_per_H'],'thermal_expansion_work':l['thermal_work_eV_per_H'],
            'photon_expansion_work':l['photon_work_eV_per_H'],'CMB_cooling':-l['signed_CMB_input_eV_per_H']}
    return base,checks,{'photon_partition':fractions,'energy_eV_per_H':energy,
                       'energy_fraction_of_source_plus_initial':{k:v/(l['source_U_eV_per_H']+E0) for k,v in energy.items()}}

def column_window(data,item):
    return {h:np.array([r[i] for r in item['rows']],float) for i,h in enumerate(data['headers']) if h!='case_id'}

def sample(owner,data,item,mode):
    c=column_window(data,item);u=np.log(c['a']);c['xe_per_H']=c['ne_proper_cm3']/c['nH_proper_cm3']
    query=item['query']['ln_a'] if mode=='fixed_a' else float(owner.interp(item['query']['elapsed_time_s'],c['time_s'],u))
    tol=8*np.finfo(float).eps*max(1,abs(u[0]),abs(u[-1]));require(u[0]-tol<=query<=u[-1]+tol,'NO_EXTRAPOLATION')
    query=float(np.clip(query,u[0],u[-1]));res={k:float(owner.interp(query,u,c[k])) for k in GAS+EXTRA+['time_s']}
    res.update(ln_a=query,a=float(np.exp(query)),zbar=float(np.exp(-query)-1));return res

def find_native_window(data,index,u):
    for name in ['fixed_t','fixed_a']:
        w=data['samples'][name]['windows'][index];x=np.log([r[data['headers'].index('a')] for r in w['rows']])
        tol=8*np.finfo(float).eps*max(1,abs(x[0]),abs(x[-1]))
        if x[0]-tol<=u<=x[-1]+tol:return name,w
    return None,None

def histories(owner,native,out):
    summaries={};clockrows=[];missing=[];roundtrip=0.;old_gas_exact=0
    for mode in ['fixed_a','fixed_t']:
        rows=[];old=csv_rows(T1/f'results_v1/comparison_{mode}.csv.gz')
        for i in range(1001):
            q={c:sample(owner,native[c],native[c]['samples'][mode]['windows'][i],mode) for c in ['ZERO','PLUS']}
            for c in ['ZERO','PLUS']:
                for k in GAS:
                    require(q[c][k]==float(old[i][k+'_T1_'+c]),'UNCHANGED_GAS_CONSUMER');old_gas_exact+=1
            row={'sample_index':i,'coordinate':float(old[i]['coordinate']),
                 'ZERO_a':q['ZERO']['a'],'PLUS_a':q['PLUS']['a'],'ZERO_time_s':q['ZERO']['time_s'],'PLUS_time_s':q['PLUS']['time_s']}
            for k in EXTRA:
                row.update({k+'_ZERO':q['ZERO'][k],k+'_PLUS':q['PLUS'][k],k+'_pair':q['PLUS'][k]-q['ZERO'][k]})
            rows.append(row)
            if mode!='fixed_t':continue
            u0=q['ZERO']['ln_a'];kind,w=find_native_window(native['PLUS'],i,u0)
            cr={'sample_index':i,'elapsed_time_s':float(old[i]['coordinate']),'ZERO_a':q['ZERO']['a'],'PLUS_a':q['PLUS']['a'],
                'delta_ln_a':q['PLUS']['ln_a']-u0,'represented':w is not None,'native_window':kind or '',
                'native_lower_a':None,'native_upper_a':None}
            for k in GAS:
                for suffix in ['total_fixed_t','same_a_at_ZERO_a','clock_displacement','identity_residual','same_a_PCHIP_minus_linear']:
                    cr[k+'_'+suffix]=None
            if w is None:missing.append(i);clockrows.append(cr);continue
            columns=column_window(native['PLUS'],w);columns['xe_per_H']=columns['ne_proper_cm3']/columns['nH_proper_cm3'];u=np.log(columns['a'])
            uq=float(np.clip(u0,u[0],u[-1]));cr.update(native_lower_a=float(columns['a'][0]),native_upper_a=float(columns['a'][-1]))
            for k in GAS:
                middle=float(owner.interp(uq,u,columns[k]));alt=float(PchipInterpolator(u,columns[k])(uq))
                total=q['PLUS'][k]-q['ZERO'][k];same=middle-q['ZERO'][k];clock=q['PLUS'][k]-middle
                cr.update({k+'_total_fixed_t':total,k+'_same_a_at_ZERO_a':same,k+'_clock_displacement':clock,
                           k+'_identity_residual':total-same-clock,k+'_same_a_PCHIP_minus_linear':alt-middle})
            clockrows.append(cr)
        table(out/f'T1_radiation_rates_{mode}.csv.gz',rows)
        summaries[mode]={}
        for k in EXTRA:
            n=max(range(1001),key=lambda i:abs(rows[i][k+'_pair']));summaries[mode][k]={'max_abs_pair':abs(rows[n][k+'_pair']),'signed_at_peak':rows[n][k+'_pair'],'coordinate':rows[n]['coordinate'],'sample_index':n,'endpoint_pair':rows[-1][k+'_pair']}
    table(out/'T1_clock_decomposition.csv.gz',clockrows)
    clocks={}
    valid=[r for r in clockrows if r['represented']]
    for k in GAS:
        at=max(valid,key=lambda r:abs(r[k+'_total_fixed_t']))
        clocks[k]={'at_max_abs_total_fixed_time':{n:at[n] for n in ['sample_index','elapsed_time_s','ZERO_a','PLUS_a','delta_ln_a']+[k+'_'+x for x in ['total_fixed_t','same_a_at_ZERO_a','clock_displacement','identity_residual']]},
                   'max_abs_identity_residual':max(abs(r[k+'_identity_residual']) for r in valid),
                   'max_abs_same_a_PCHIP_minus_linear':max(abs(r[k+'_same_a_PCHIP_minus_linear']) for r in valid),
                   'opposite_sign_same_a_and_total_samples':sum(r[k+'_same_a_at_ZERO_a']*r[k+'_total_fixed_t']<0 for r in valid)}
    return {'new_radiation_rate_samples_per_mode':1001,'unchanged_gas_values_bit_equal':old_gas_exact,'radiation_rates':summaries,
            'clock':{'represented':len(valid),'queries':1001,'excluded_indices':missing,'reason':'No retained consecutive native window brackets a_ZERO(t) in PLUS; not extrapolated','observables':clocks}}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);a=parser.parse_args();require(not a.output.exists(),'OUTPUT_ALREADY_EXISTS')
    t,cpu=time.monotonic(),time.process_time();a.output.mkdir();native={}
    for case,expected in [('ZERO','40e536713e4cd8d872060a1213e3caaa21af8dab0bb48257bde747aab3e7c2f2'),('PLUS','90d31e9acd3eba8286ad34fcdcd45696c35c0ce41b1500f2d751d0edddf7b91f')]:
        p=T1/f'native_inputs/{case}_sample_brackets.json.gz';require(sha(p)==expected,'NATIVE_INPUT_IDENTITY');native[case]=load_json(p)
    owner_path=REPO/'research/rei_axbi_owner_loop_20261115/physics_consumer.py';require(sha(owner_path)=='36ab1556010cd182790e924b1042227b36496c7a17d6d55ddfbff5935a58cfb8','OWNER_HELPER_IDENTITY')
    spec=importlib.util.spec_from_file_location('owner',owner_path);owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
    rows=[];checks={};partitions={}
    for level in ['T0','T1']:
        for case in ['ZERO','PLUS']:
            if level=='T0':
                cp=checkpoint(UNIT/f'native_inputs/T0_{case}_checkpoint.txt');history=csv_rows(UNIT/f'native_inputs/T0_{case}_terminal_history.csv')[0]
                ledger={r['ledger_name']:float(r['residual']) for r in csv_rows(UNIT/f'native_inputs/T0_{case}_terminal_ledgers.csv')}
            else:
                cp=checkpoint(T1/f'checkpoints/{case}_757073.txt');d=native[case];history=dict(zip(d['headers'],d['last_row']));ledger=d['segments'][-1]['ledgers']['terminal_values']
            row,ck,part=endpoint(level,case,cp,history,ledger);rows.append(row);checks[level+'_'+case]=ck;partitions[level+'_'+case]=part
    table(a.output/'endpoint_inventory.csv',rows);lookup={(r['level'],r['case']):r for r in rows};deltas=[]
    for k in rows[0]:
        if k in ['level','case','a','time_s']:continue
        z0,p0,z1,p1=[lookup[x][k] for x in [('T0','ZERO'),('T0','PLUS'),('T1','ZERO'),('T1','PLUS')]]
        deltas.append({'quantity':k,'T0_ZERO':z0,'T1_ZERO':z1,'D01_ZERO':z1-z0,'T0_PLUS':p0,'T1_PLUS':p1,'D01_PLUS':p1-p0,
                       'pair_T0':p0-z0,'pair_T1':p1-z1,'D01_pair':(p1-z1)-(p0-z0),'D01_pair_over_abs_T1_pair':((p1-z1)-(p0-z0))/abs(p1-z1) if p1!=z1 else None})
    table(a.output/'endpoint_inventory_D01.csv',deltas)
    epochs=[]
    for case in ['ZERO','PLUS']:
        for count in [250000,500000,750000,757073]:
            cp=checkpoint(T1/f'checkpoints/{case}_{count}.txt');l=cp['ledger'];xe=cp['x_HII']+FHE*(cp['x_HeII']+2*cp['x_HeIII'])
            epochs.append({'case':case,'accepted':count,'a':cp['a'],'zbar':1/cp['a']-1,'time_s':cp['time_s'],
                           'x_HII':cp['x_HII'],'x_HeII':cp['x_HeII'],'x_HeIII':cp['x_HeIII'],
                           'temperature_K':cp['w_erg_per_H']/(1.5*KB*(1+FHE+xe)),**l})
    table(a.output/'T1_native_cumulative_epochs.csv',epochs)
    paired=[];old=csv_rows(T1/'results_v1/milestone_T0_T1.csv')
    for level in [.1,.5,.9]:
        z,p=[next(r for r in old if r['case']==case and float(r['x_HII_level'])==level) for case in ['ZERO','PLUS']]
        row={'x_HII_level':level}
        for k in ['T0','T1']:
            row[k+'_PLUS_minus_ZERO_years']=(float(p[k+'_time_s'])-float(z[k+'_time_s']))/YEAR
            row[k+'_PLUS_minus_ZERO_zbar']=float(p[k+'_zbar'])-float(z[k+'_zbar'])
        row['D01_paired_years']=row['T1_PLUS_minus_ZERO_years']-row['T0_PLUS_minus_ZERO_years']
        widths=[float(r['T1_native_bracket_years']) for r in [z,p]]
        row.update(T1_ZERO_bracket_years=widths[0],T1_PLUS_bracket_years=widths[1],T1_sum_bracket_widths_years=sum(widths),D01_paired_over_bracket_sum=abs(row['D01_paired_years'])/sum(widths));paired.append(row)
    table(a.output/'paired_milestone_shifts.csv',paired)
    sampled=histories(owner,native,a.output)
    summary={'schema':'rei.ax11.owner.actual-inventory-consumption.v1','status':'SOURCE_QUALIFIED_NATIVE_SAVED_PHYSICAL_DATA','source_corpus_sha256':'d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185',
             'baseline_pin':'56dc609ea9b801c88d3364aed3eee140b3a20d46','T1_science_pin':'f75c35360d64420a840df6454c88ef0c7f1f2d4c',
             'normalization':'Events and energies per H; helium element fractions per He nucleus','endpoint_coordinate':'a=0.2,zbar4; distinct elapsed proper times',
             'endpoint_checks':checks,'endpoint_partitions':partitions,'endpoint_D01':deltas,'paired_milestones':paired,**sampled,
             'science_scope':'Saved T0/T1 physical inventories and two-level differences; no D12, observed order or trajectory error certificate',
             'new_evolution_runs':0,'new_completed_DAG_nodes':0,'original_DAG':'10/17','expansion_DAG':'28/88',
             'execution':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'CPU_s':time.process_time()-cpu,'wall_s':time.monotonic()-t,'script_sha256':sha(__file__)}}
    summary['outputs']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in a.output.iterdir() if p.is_file()};dump(a.output/'SUMMARY.json',summary)
    print(json.dumps({'status':summary['status'],'clock_represented':sampled['clock']['represented'],'new_physical_tables':len(summary['outputs']),'execution':summary['execution']}))

if __name__=='__main__':main()
