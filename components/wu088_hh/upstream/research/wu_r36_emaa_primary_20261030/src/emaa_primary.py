"""WU R36: raw EMAA H+ (171x25) versus frozen GL2022 and source-scoped HD19 physics.

No interpolation, inferred chemistry, or unmeasured gas histories. All inputs immutable.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from scipy.constants import h, c, k as k_B

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'sources/HD.Rovibration.805a7aa5.radex'
GL = ROOT / 'sources/GL2022_1560_INELASTIC_SOURCE_TOKENS.csv'
HCK = 100.0*h*c/k_B  # K per cm^-1
HCJ = 100.0*h*c     # J per cm^-1
EXPECTED_RAW_SHA = 'b0db1613425e403889c3a74f6cd9e142c562a552f1ebf05e61cbf509cd429c94'


def filehash(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def parse_radex(path=RAW):
    """Parse complete EMAA/LAMDA text using source-owned section and count grammar."""
    lines=[l.strip() for l in Path(path).read_text(encoding='utf-8').splitlines() if l.strip()]
    idx=0
    def header(text):
        nonlocal idx
        assert lines[idx].startswith('! ' + text),(idx,lines[idx],text)
        idx+=1
    header('MOLECULE');molecule=lines[idx];idx+=1
    header('MOLECULAR WEIGHT');mass=float(lines[idx]);idx+=1
    header('NUMBER OF ENERGY LEVELS');nlev=int(lines[idx].split()[0]);idx+=1
    assert lines[idx].startswith('! LEVEL');idx+=1
    levels={}
    for j in range(nlev):
        v=lines[idx].split();idx+=1
        assert len(v)>=4 and int(v[0])==j+1
        vv,jj=map(int,v[3].split('_'))
        levels[j+1]={'E':float(v[1]),'g':float(v[2]),'v':vv,'J':jj,'label':v[3]}
        assert abs(float(v[2])-(2*jj+1))<1e-9
    assert len({(z['v'],z['J']) for z in levels.values()})==nlev
    assert all(levels[i+1]['E']>levels[i]['E'] for i in range(1,nlev))
    header('NUMBER OF RADIATIVE TRANSITIONS');nrad=int(lines[idx]);idx+=1
    assert lines[idx].startswith('! TRANS');idx+=1
    radiative=[]
    for j in range(nrad):
        a=lines[idx].split();idx+=1
        assert int(a[0])==j+1 and len(a)>=6
        up,lo=int(a[1]),int(a[2]);a_rate=float(a[3]);freq=float(a[4]);upper_K=float(a[5])
        assert up>lo and a_rate>0 and levels[up]['E']>levels[lo]['E']
        radiative.append({'up':up,'low':lo,'A':a_rate,'freq_GHz':freq,'Eu_K':upper_K})
    header('NUMBER OF COLLISION PARTNERS');npart=int(lines[idx]);idx+=1
    partners={}
    for j in range(npart):
        header('COLLISIONS BETWEEN'); description=lines[idx];idx+=1
        partner_id=int(description.split()[0]);assert partner_id not in partners
        header('NUMBER OF COLLISIONAL TRANSITIONS');ncol=int(lines[idx]);idx+=1
        header('NUMBER OF TEMPERATURES');ntemp=int(lines[idx]);idx+=1
        header('TEMPERATURES');temperatures=[float(t) for t in lines[idx].split()];idx+=1
        assert len(temperatures)==ntemp and all(a<b for a,b in zip(temperatures,temperatures[1:]))
        assert lines[idx].startswith('! TRANS');idx+=1
        transitions={}
        for k in range(ncol):
            tok=lines[idx].split();idx+=1
            assert len(tok)==ntemp+3 and int(tok[0])==k+1
            up,lo=map(int,tok[1:3]);assert up>lo and (up,lo) not in transitions
            assert levels[up]['E']>levels[lo]['E']
            rates=np.array([float(t) for t in tok[3:]],dtype=float)
            assert np.all(np.isfinite(rates)) and np.all(rates>0)
            transitions[(up,lo)]=rates
        assert len(transitions)==ncol
        partners[partner_id]={'description':description,'temps':temperatures,'rates':transitions,'ncol':ncol,'ntemp':ntemp}
    assert idx==len(lines),(idx,len(lines))
    assert mass==3.0 and nlev==52 and nrad==368 and set(partners)=={5,7}
    hplus=partners[7]
    assert hplus['ncol']==171 and hplus['ntemp']==25
    assert {i for edge in hplus['rates'] for i in edge}==set(range(1,20))
    assert set(hplus['rates']) == {(i,j) for i in range(2,20) for j in range(1,i)}
    return {'levels':levels,'radiative':radiative,'partners':partners,'molecule':molecule,'mass':mass}


def raw_crosswalk(data,glpath=GL):
    """Compare *printed numeric* values, not rounded relative proximity or interpolated rates."""
    lv=data['levels'];src=data['partners'][7]; lookup={(l['v'],l['J']):i for i,l in lv.items()}
    temperatures=src['temps'];out=[]; GLvalid={}
    with open(glpath,newline='',encoding='utf-8') as input_gl:
        source_rows=list(csv.DictReader(input_gl))
    for r in source_rows:
        initi=(int(r['initial_v']),int(r['initial_J']));fin=(int(r['final_v']),int(r['final_J']));T=float(r['T_K']);rate=r['rate_cm3_s'];status=r['status']
        ui,li=lookup[initi],lookup[fin]
        assert T in temperatures
        if ui==li:
            etarget='SOURCE_DIAGONAL_NOT_A_TRANSITION';newrate=None;rel=None
        else:
            assert lv[ui]['E']>lv[li]['E'],(initi,fin)
            newrate=float(src['rates'][(ui,li)][temperatures.index(T)])
            if not rate:
                etarget='SOURCE_PRINTED_UNRELIABLE_EMAA_CANDIDATE';rel=None
            else:
                val=float(rate)
                rel=(val-newrate)/newrate
                etarget='PRINTED_NUMERIC_MATCH' if val==newrate else 'PRINTED_NUMERIC_MISMATCH'
                GLvalid[(ui,li,T)]=val
        out.append({'T_K':T,'initial_v':initi[0],'initial_J':initi[1],'final_v':fin[0],'final_J':fin[1],
                    'GL_table':r['table'],'GL_source_token':r['token'],'GL_status':status,'GL_rate_cm3_s':rate,
                    'EMAA_up_id':ui,'EMAA_low_id':li,'EMAA_rate_cm3_s':newrate,'ratio_GL_over_EMAA':float(rate)/newrate if rel is not None else None,
                    'relative_GL_minus_EMAA':rel,'crosswalk_status':etarget})
    summary=Counter(r['crosswalk_status'] for r in out)
    assert len(out)==1560 and summary==Counter({'PRINTED_NUMERIC_MATCH':1498,'PRINTED_NUMERIC_MISMATCH':50,'SOURCE_PRINTED_UNRELIABLE_EMAA_CANDIDATE':2,'SOURCE_DIAGONAL_NOT_A_TRANSITION':10}),summary
    original_pairs={(r['EMAA_up_id'],r['EMAA_low_id']) for r in out if r['crosswalk_status']!='SOURCE_DIAGONAL_NOT_A_TRANSITION'}
    emaa_only=sorted(set(src['rates'])-original_pairs)
    assert len(emaa_only)==16
    return out,GLvalid,emaa_only


def bath_rates(data,T,n_Hplus,overrides=None):
    """Column generator of 19 HD levels from H+ collisions at exact source temperature."""
    lv=data['levels'];raw=data['partners'][7];temperatures=raw['temps'];j=temperatures.index(float(T))
    Q=np.zeros((19,19),dtype=float)
    for (up,lo),rates in raw['rates'].items():
        k=float(rates[j]) if overrides is None else overrides.get((up,lo,T),float(rates[j]));
        eup,elo=lv[up]['E'],lv[lo]['E'];gu,gl=lv[up]['g'],lv[lo]['g']
        kup=k*(gu/gl)*math.exp(-HCK*(eup-elo)/T)
        u,l=up-1,lo-1
        Q[l,u]+=n_Hplus*k
        Q[u,l]+=n_Hplus*kup
    np.fill_diagonal(Q,-Q.sum(axis=0))
    return Q


def radiative_generator(data,T_rad):
    """Prescribed Planck blackbody; only source radiative transitions within 19 states."""
    lv=data['levels'];Q=np.zeros((19,19));lines=[]
    for line in data['radiative']:
        up,lo=line['up'],line['low']
        if up>19 or lo>19:continue
        u,l=up-1,lo-1;de=lv[up]['E']-lv[lo]['E'];g=lv[up]['g']/lv[lo]['g']
        x=HCK*de/T_rad if T_rad>0 else float('inf')
        occ=1.0/math.expm1(x) if x<700 else 0.0
        down=line['A']*(1+occ);upward=line['A']*g*occ
        Q[l,u]+=down;Q[u,l]+=upward
        lines.append({'up':up,'low':lo,'delta_E_J':HCJ*de,'down_s':down,'up_s':upward,'A':line['A']})
    np.fill_diagonal(Q,-Q.sum(axis=0))
    return Q,lines


def stationary(G):
    """Nonnegative stationary measure from a grounded M-matrix, p_0=1 before norm.

    For a finite irreducible CTMC, -G on states 1..18 is a nonsingular M-matrix;
    solving (-G_rr)x=G_r0 gives x>=0 without clamping tiny negative linear-solve
    artifacts from naive row replacement. At extreme cold T, underflow in tiny
    physical Boltzmann factors can produce representational zeros (documented).
    """
    x=np.linalg.solve(-G[1:,1:],G[1:,0])
    if np.any(x < -1e-24):
        raise ValueError(f'M-matrix stationary solution negative: {x.min()}')
    p=np.concatenate(([1.0],x));p/=p.sum()
    residual=float(np.max(np.abs(G@p)));mass=abs(float(p.sum())-1)
    if np.min(p)<0 or mass>2e-10 or residual>2e-8:
        raise ValueError(f'stationary failed {np.min(p)}, {mass}, {residual}')
    return p,residual


def energy_flux(data,G,p):
    E=np.array([data['levels'][i]['E']*HCJ for i in range(1,20)])
    return -float(E@(G@p)) # positive if energy lost by HD into chosen bath


def compute_atlas(data,temperatures=None,densities=(1.0,1e3,1e6,1e9),zgrid=(0,10,30,100,300),glvalid=None):
    temperatures=data['partners'][7]['temps'] if temperatures is None else temperatures
    results=[];lines_out=[];hybrid=[];L=data['levels']
    energies=np.array([L[i]['E']*HCJ for i in range(1,20)])
    for Tg in temperatures:
        for dens in densities:
            C=bath_rates(data,Tg,dens)
            for z in zgrid:
                T_rad=2.7255*(1+z)
                R,lines=radiative_generator(data,T_rad)
                Q=C+R
                p,res=stationary(Q)
                P_rad=energy_flux(data,R,p);P_coll=energy_flux(data,C,p)
                denom=max(abs(P_rad),abs(P_coll),1e-40)
                assert abs(P_rad+P_coll)/denom < 2e-6, (Tg,dens,z,P_rad,P_coll)
                pv1=sum(p[i-1] for i in range(1,20) if L[i]['v']==1)
                evib=float(sum(p[i-1]*energies[i-1] for i in range(1,20) if L[i]['v']==1))
                row={'T_gas_K':Tg,'n_Hplus_cm3':dens,'z_radiation_boundary':z,'T_rad_K':T_rad,'pv1':pv1,'mean_E_internal_J':float(energies@p),
                     'mean_E_v1_selected_J':evib,'P_rad_positive_out_J_s_molecule':P_rad,'P_coll_positive_out_J_s_molecule':P_coll,
                     'energy_flux_balance_J_s':P_rad+P_coll,'generator_residual_max_s_inv':res,'p_min':float(min(p))}
                results.append(row)
                for line in lines:
                    u,l=line['up']-1,line['low']-1
                    net=line['down_s']*p[u]-line['up_s']*p[l]
                    lines_out.append({'T_gas_K':Tg,'n_Hplus_cm3':dens,'z':z,'up_id':u+1,'low_id':l+1,
                     'up_label':L[u+1]['label'],'low_label':L[l+1]['label'],'net_photon_count_s_inv':float(net),
                     'net_energy_J_s':float(line['delta_E_J']*net)})
                if glvalid is not None and Tg in (15,55,105,255,505,1005,1505,2005,2505,3005):
                    C_gl=bath_rates(data,Tg,dens,overrides=glvalid)
                    p2,_=stationary(C_gl+R)
                    P2=energy_flux(data,R,p2)
                    hybrid.append({'T_gas_K':Tg,'n_Hplus_cm3':dens,'z':z,'L1_population_difference':float(sum(abs(p2-p))),
                        'delta_pv1_hybrid_minus_EMAA':float(sum((p2-p)[i-1] for i in range(1,20) if L[i]['v']==1)),
                        'P_rad_EMAA_J_s':P_rad,'P_rad_GLhybrid_J_s':P2,'delta_P_rad_J_s':P2-P_rad})
    return results,lines_out,hybrid


def first_v1_quench(data):
    """First landing in any v=0 J0..11 by H+ collision, exact source 25 T.

    Rates are per unit n(H+): mean integrated fluence cm^-3 s. Photons and chemical loss
    are *excluded by construction*, not assigned a physical zero in the Universe.
    """
    lv=data['levels'];idx_v1=[i-1 for i in range(1,20) if lv[i]['v']==1]
    idx_v0=[i-1 for i in range(1,20) if lv[i]['v']==0]
    assert len(idx_v1)==7 and len(idx_v0)==12
    cases=[];branches=[]
    for T in data['partners'][7]['temps']:
        C=bath_rates(data,T,1.0)
        K=C[np.ix_(idx_v1,idx_v1)]
        S=C[np.ix_(idx_v0,idx_v1)]
        assert max(abs(np.sum(K,axis=0)+np.sum(S,axis=0)))<1e-23
        occup=np.linalg.solve(-K,np.eye(7))
        prob=S@occup
        assert min(prob.flat)>=-1e-12 and max(abs(np.sum(prob,axis=0)-1))<1e-10
        for m,source in enumerate(idx_v1):
            j0=lv[source+1]['J'];p=prob[:,m];fl=float(sum(occup[:,m]));
            cases.append({'T_gas_K':T,'initial_v1_J':j0,'mean_fluence_cm_minus3_s':fl,'k_effective_cm3_s':1/fl,
                'p_land_v0_J0to4':float(sum(p[k] for k,q in enumerate(idx_v0) if lv[q+1]['J']<=4)),
                'p_land_v0_J5to11':float(sum(p[k] for k,q in enumerate(idx_v0) if lv[q+1]['J']>=5)),
                'total_branch_mass':float(sum(p))})
            for k,q in enumerate(idx_v0):
                branches.append({'T_gas_K':T,'initial_v1_J':j0,'final_v0_J':lv[q+1]['J'],'branch_probability':float(p[k])})
    return cases,branches


def write_csv(path,rows):
    if not rows:return
    with open(path,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def main(outdir):
    if filehash(RAW)!=EXPECTED_RAW_SHA:raise RuntimeError('RAW BYTES CHANGED')
    data=parse_radex();cross,glvalid,missing=raw_crosswalk(data)
    atlas,photons,hybrid=compute_atlas(data,glvalid=glvalid)
    quenches,branches=first_v1_quench(data)
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'GL2022_EMAA_CROSSWALK_1560.csv',cross)
    write_csv(out/'GL2022_EMAA_MISMATCH_50.csv',[r for r in cross if r['crosswalk_status']=='PRINTED_NUMERIC_MISMATCH'])
    extras=[{'up_label':data['levels'][up]['label'],'down_label':data['levels'][lo]['label'],'T_K':T,'rate_cm3_s':float(data['partners'][7]['rates'][(up,lo)][t])} for up,lo in missing for t,T in enumerate(data['partners'][7]['temps'])]
    write_csv(out/'EMAA_16_UNPRINTED_PAIRS_400.csv',extras)
    rate_rows=[{'up_id':up,'low_id':lo,'up_label':data['levels'][up]['label'],'low_label':data['levels'][lo]['label'],'T_K':T,'k_down_cm3_s':float(vals[t])}
                for (up,lo),vals in sorted(data['partners'][7]['rates'].items()) for t,T in enumerate(data['partners'][7]['temps'])]
    write_csv(out/'EMAA_HPLUS_4275_PRIMARY.csv',rate_rows)
    write_csv(out/'EMAA_HD19_NLTE_ATLAS_500.csv',atlas)
    write_csv(out/'EMAA_HD19_NLTE_PHOTON_LINES.csv',photons)
    write_csv(out/'EMAA_GLhybrid_SOURCE_SENSITIVITY_200.csv',hybrid)
    write_csv(out/'EMAA_V1_FIRST_QUENCH_175.csv',quenches)
    write_csv(out/'EMAA_V1_FIRST_QUENCH_BRANCHES_2100.csv',branches)
    from collections import Counter
    groups=defaultdict(list)
    for r in cross:
        if r['crosswalk_status']=='PRINTED_NUMERIC_MISMATCH':groups[f"{r['initial_v']}_{r['initial_J']}->{r['final_v']}_{r['final_J']}"].append(r)
    src={'schema':'WU_R36_EMAA_PRIMARY_SOURCE_V1','source_filename':RAW.name,'source_bytes':RAW.stat().st_size,'source_sha256':filehash(RAW),
        'gl2022_source_sha256':filehash(GL),'EMAA_DOI':'10.17178/emaa_hd_rovibration_805a7aa5','GL2022_DOI':'10.1063/5.0128598',
        'Nlev':len(data['levels']),'Nrad':len(data['radiative']),'H_transitions':1326,'Hplus_transitions':171,'Hplus_temps':data['partners'][7]['temps'],
        'compared':Counter(r['crosswalk_status'] for r in cross),'mismatch_pair_count':len(groups),'mismatch_groups':{g:{'n':len(rows),'min_ratio':min(r['ratio_GL_over_EMAA'] for r in rows),'max_ratio':max(r['ratio_GL_over_EMAA'] for r in rows)} for g,rows in groups.items()},
        'EMAA_only_pairs':[f"{data['levels'][up]['label']}->{data['levels'][lo]['label']}" for up,lo in missing],
        'nonLTE_lines_with_both_ends_under_19':len(photons)//len(atlas),
        'model_limits':'H+ inelastic rates for 19-state subset, HITRAN-based radiation within same subset, prescribed Planck bath, no chemistry/transport; source-scoped only'}
    (out/'SOURCE_DISCOVERY.json').write_text(json.dumps(src,indent=2,ensure_ascii=False,default=lambda x:dict(x))+ '\n')
    rowexample=next(r for r in atlas if r['T_gas_K']==105 and r['n_Hplus_cm3']==1e6 and r['z_radiation_boundary']==30)
    summary={'rows':{'crosswalk':len(cross),'mismatch':sum(r['crosswalk_status']=='PRINTED_NUMERIC_MISMATCH' for r in cross),'primary_rates':len(rate_rows),
             'previously_unprinted_at_25_T':len(extras),'nlte':len(atlas),'nlte_photon_lines':len(photons),'gl_hybrid':len(hybrid),'quench':len(quenches),'quench_branches':len(branches)},
        'mismatch_groups':src['mismatch_groups'], 'new_pairs':len(missing),
        'quench_landing_lowJ_min':min(r['p_land_v0_J0to4'] for r in quenches),'quench_landing_lowJ_max':max(r['p_land_v0_J0to4'] for r in quenches),
        'p_v1_max':max(r['pv1'] for r in atlas),'p_v1_min':min(r['pv1'] for r in atlas),
        'rad_power_min':min(r['P_rad_positive_out_J_s_molecule'] for r in atlas),'rad_power_max':max(r['P_rad_positive_out_J_s_molecule'] for r in atlas),
        'max_energy_flux_abs_residual':max(abs(r['energy_flux_balance_J_s']) for r in atlas),
        'max_population_L1_hybrid':max(r['L1_population_difference'] for r in hybrid),
        'max_delta_Prad_abs':max(abs(r['delta_P_rad_J_s']) for r in hybrid),
        'example_Tg105_n1e6_z30':rowexample}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return summary

if __name__=='__main__':
    par=argparse.ArgumentParser();par.add_argument('--out',default=str(ROOT/'results'));args=par.parse_args()
    main(args.out)
