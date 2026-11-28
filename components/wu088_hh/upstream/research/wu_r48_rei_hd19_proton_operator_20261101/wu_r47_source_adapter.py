#!/usr/bin/env python3
"""Original REI tick160 HD collider support and single-transition competition.

Independent source adapters only: does not rerun original REI IVP or admit a DAG node.
Input privately preserved source ZIPs; output contains no original third-party RADEX.
"""
from __future__ import annotations
import argparse, bisect, csv, gzip, hashlib, io, json, math, pathlib, statistics, zipfile

REI_SHA = '48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7'
EMAA_SHA = 'b0db1613425e403889c3a74f6cd9e142c562a552f1ebf05e61cbf509cd429c94'
SOURCE_PREFIX = 'source_private/HD.Rovibration.805a7aa5.radex'
NODES = 46080
BAND_H = (5.0, 5000.0)
BAND_P = (5.0, 3005.0)


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_rates(raw: bytes) -> dict:
    if sha256(raw) != EMAA_SHA:
        raise ValueError('EMAA source SHA256 mismatch')
    lines = raw.decode('utf-8').splitlines()
    blocks = {}
    for i, s in enumerate(lines):
        if s.strip() != '! COLLISIONS BETWEEN':
            continue
        partner = lines[i+1]
        who = 'HPLUS' if 'HD + H+' in partner else 'H' if 'HD + H ' in partner else None
        if who is None:
            raise ValueError('unknown collider source '+partner)
        assert lines[i+2].strip() == '! NUMBER OF COLLISIONAL TRANSITIONS'
        pairs = int(lines[i+3]); assert lines[i+4].strip() == '! NUMBER OF TEMPERATURES'
        ntemp = int(lines[i+5]); assert lines[i+6].strip() == '! TEMPERATURES'
        temperatures = [float(s) for s in lines[i+7].split()]
        assert len(temperatures)==ntemp
        assert lines[i+8].startswith('! TRANS')
        pair_rows = [lines[j].split() for j in range(i+9, i+9+pairs)]
        assert len(pair_rows)==pairs
        assert all(len(row)==3+ntemp for row in pair_rows)
        assert all(int(row[0])==k+1 for k,row in enumerate(pair_rows))
        transition = [row for row in pair_rows if int(row[1])==2 and int(row[2])==1]
        assert len(transition)==1
        rates = [float(x) for x in transition[0][3:]]
        assert all(r>0 for r in rates)
        blocks[who] = {'temps':temperatures,'rates':rates,'pairs':pairs,'name':partner.strip()}
    if len(blocks)!=2 or blocks['H']['pairs']!=1326 or blocks['HPLUS']['pairs']!=171:
        raise ValueError('unexpected source collider coverage')
    if blocks['H']['temps'][0]!=5 or blocks['H']['temps'][-1]!=5000 or blocks['HPLUS']['temps'][-1]!=3005:
        raise ValueError('unexpected temperature domain')
    return blocks


def interp(T, temps, values, *, method='loglog'):
    if not (temps[0] <= T <= temps[-1]):
        raise ValueError('outside source temperature range')
    j = max(0, min(bisect.bisect_right(temps, T)-1, len(temps)-2))
    t0,t1=temps[j],temps[j+1]
    k0,k1=values[j],values[j+1]
    if method=='loglog':
        w=math.log(T/t0)/math.log(t1/t0)
        return math.exp((1-w)*math.log(k0)+w*math.log(k1))
    if method=='linear':
        w=(T-t0)/(t1-t0)
        return (1-w)*k0+w*k1
    raise ValueError(method)


def ratio_rates(T, blocks, *, method='loglog'):
    return interp(T,blocks['HPLUS']['temps'],blocks['HPLUS']['rates'],method=method)/interp(T,blocks['H']['temps'],blocks['H']['rates'],method=method)


def quantile(seq, p):
    a=sorted(seq)
    x=(len(a)-1)*p; i=int(x); f=x-i
    return (1-f)*a[i]+f*a[min(len(a)-1,i+1)]


def classify(Tlo,Thi):
    if BAND_H[0]<=Tlo and Thi<=BAND_P[1]: return 'JOINT_T_RANGE'
    if BAND_H[0]<=Tlo and BAND_P[1]<Tlo and Thi<=BAND_H[1]: return 'H_ONLY_T_RANGE'
    if BAND_H[1]<Tlo: return 'OUTSIDE_H_T_RANGE'
    return 'CROSS_BOUNDARY_OR_BELOW_MIN'


def read_states(original_zip):
    if sha256(original_zip)!=REI_SHA: raise ValueError('REI source ZIP SHA256 mismatch')
    with zipfile.ZipFile(io.BytesIO(original_zip)) as z:
        if z.testzip(): raise ValueError('REI ZIP CRC mismatch')
        names=sorted(n for n in z.namelist() if n.endswith('.csv.gz'))
        assert len(names)==3
        sample,hashes=None,{}
        for n in names:
            h=hashlib.sha256(); state=[]
            reader=csv.DictReader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(z.read(n))),'utf-8',newline=''))
            for line,row in enumerate(reader):
                assert int(row['node'])==line
                # All source numeric columns must match across lanes; lane names are labels.
                h.update(('|'.join(row[k] for k in reader.fieldnames if k!='lane')+'\n').encode())
                if sample is None or len(state)<NODES:
                    state.append(row)
            assert len(state)==NODES
            hashes[n]=h.hexdigest()
            if sample is None: sample=state
        if len(set(hashes.values()))!=1: raise ValueError('3 source lanes have different numerical values')
        return sample, hashes


def analyze(rei_zip, emma_zip):
    with zipfile.ZipFile(emma_zip) as z:
        if z.testzip(): raise ValueError('EMAA ZIP CRC mismatch')
        original=z.read(SOURCE_PREFIX)
    rates=read_rates(original)
    source, lane_hashes=read_states(pathlib.Path(rei_zip).read_bytes())
    counts={s:0 for s in ('JOINT_T_RANGE','H_ONLY_T_RANGE','OUTSIDE_H_T_RANGE','CROSS_BOUNDARY_OR_BELOW_MIN')}
    output=[]; ratios=[]; perturb=[]; neutral=[]; neutral_joint=[]; neutral_h=[]; hx=[]
    for row in source:
        Tlo,Thi=(float(row[k]) for k in ('T_K_lo','T_K_hi'))
        xlo,xhi=(float(row[k]) for k in ('x_HII_lo','x_HII_hi'))
        xe_lo,xe_hi=(float(row[k]) for k in ('xe_per_H_lo','xe_per_H_hi'))
        if not (0<=xlo<=xhi<1 and 0<Tlo<=Thi and 0<=xe_lo<=xe_hi):
            raise ValueError('nonphysical original state enclosure at '+row['node'])
        state=classify(Tlo,Thi);counts[state]+=1
        xm=(xlo+xhi)/2; Tm=(Tlo+Thi)/2
        neutral.append(1-xm); hx.append(xm/(1-xm))
        if state != 'OUTSIDE_H_T_RANGE': neutral_h.append(1-xm)
        if state == 'JOINT_T_RANGE':
            # log(kp/kH) is affine in log(T) between each adjacent native knot.
            knots=[Tlo,Thi]+[t for who in ('H','HPLUS') for t in rates[who]['temps'] if Tlo<t<Thi]
            fac=[ratio_rates(t,rates) for t in knots]
            midfac=ratio_rates(Tm,rates)
            kH=interp(Tm,rates['H']['temps'],rates['H']['rates'])
            kp=interp(Tm,rates['HPLUS']['temps'],rates['HPLUS']['rates'])
            midpoint=xm/(1-xm)*midfac
            rlo=xlo/(1-xlo)*min(fac)
            rhi=xhi/(1-xhi)*max(fac)
            linear=xm/(1-xm)*ratio_rates(Tm,rates,method='linear')
            assert rlo<=midpoint*(1+1e-12) and midpoint<=rhi*(1+1e-12)
            ratios.append(midpoint); perturb.append(abs(linear/midpoint-1))
            neutral_joint.append(1-xm)
        else:
            kH=kp=midpoint=rlo=rhi=linear=None
        output.append({'node':row['node'],'T_K_lo':Tlo,'T_K_hi':Thi,'x_HII_lo':xlo,'x_HII_hi':xhi,
          'x_HI_mid':1-xm,'x_e_mid':(xe_lo+xe_hi)/2,'source_T_support':state,
          'HD_J1_to_J0_kH_cm3_s':kH,'HD_J1_to_J0_kp_cm3_s':kp,
          'Gamma_p_over_H_mid_loglog':midpoint,'Gamma_p_over_H_outer_lo':rlo,'Gamma_p_over_H_outer_hi':rhi,
          'Gamma_p_over_H_mid_linear':linear})
    assert sum(counts.values())==NODES
    keys=['node','T_K_lo','T_K_hi','x_HII_lo','x_HII_hi','x_HI_mid','x_e_mid','source_T_support',
          'HD_J1_to_J0_kH_cm3_s','HD_J1_to_J0_kp_cm3_s','Gamma_p_over_H_mid_loglog','Gamma_p_over_H_outer_lo','Gamma_p_over_H_outer_hi','Gamma_p_over_H_mid_linear']
    def stats(data):return {'min':min(data),'q05':quantile(data,.05),'median':quantile(data,.5),'q95':quantile(data,.95),'max':max(data)}
    summary={'schema':'R47_WU_TO_REI_ORIGINAL_TICK160_HD_COLLIDER_COMPETITION_V1',
      'rei_original_accepted_states_zip_SHA256':REI_SHA,'emaa_original_radex_SHA256':EMAA_SHA,
      'rei_original_accepted_tick':160,'rei_original_total_ticks':131072,
      'unique_original_spatial_nodes':NODES,'source_lane_numeric_SHA256':lane_hashes,
      'source_h_temperatures_K':rates['H']['temps'],'source_hp_temperatures_K':rates['HPLUS']['temps'],
      'tested_transition':'HD(v0,J1) -> HD(v0,J0) downward collision',
      'counts':counts,'joint_fraction':counts['JOINT_T_RANGE']/NODES,
      'H_supported_fraction':(counts['JOINT_T_RANGE']+counts['H_ONLY_T_RANGE'])/NODES,
      'mean_neutral_H_fraction_all_equal_nodes':statistics.fmean(neutral),
      'mean_neutral_H_fraction_joint_equal_nodes':statistics.fmean(neutral_joint),
      'neutral_H_sum_fraction_on_H_supported_nodes':sum(neutral_h)/sum(neutral),
      'ionized_to_neutral_ratio_all':stats(hx),'collision_frequency_ratio_joint':stats(ratios),
      'linear_vs_loglog_interpolation_fractional_abs_error':stats(perturb),
      'source_and_research_scope':{
      'data':'original accepted REI numerical MODEL states, not observations',
      'source':'EMAA authored coefficients at native nodes, derived two-interpolant values at actual temperatures',
      'conditional':'nH+ = xHII*nH_nuclei; nHI=(1-xHII)*nH_nuclei, no H2/other hydrogen carriers',
      'partial':'a single HD v0 J=1->0 collisional downward transition, not total HD cooling',
      'Hplus':'19 HD states only, 25 source T nodes, no inferred 52-level coverage',
      'missing':'nHD, actual total hydrogen density, chemical source/sink, photon occupation, Bianchi geometry and proper clock integration',
      'not_claimed':'full REI source consumer, full 52-level H+ closure, cosmological HD cooling, optical depth, F05 acceptance'},
      'DAG':{'WU_canonical_before':'34/49','WU_canonical_after':'34/49',
      'REI_central_before':'28/88','REI_central_after':'28/88',
      'REI_working':'33/88','delta':0}}
    return output,summary,keys


def write_results(results,summary,keys,dest):
    dest.mkdir(parents=True,exist_ok=True)
    with open(dest/'R47_HD_REI_SOURCE_SUPPORT_46080.csv.gz','wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0,compresslevel=6) as gz:
            w=io.TextIOWrapper(gz,encoding='utf-8',newline='')
            writer=csv.DictWriter(w,fieldnames=keys,lineterminator='\n')
            writer.writeheader()
            for row in results:
                writer.writerow({k:('%.17g'%v if isinstance(v,float) else '' if v is None else v) for k,v in row.items()})
            w.flush()
    selected=[]
    for cls in ('JOINT_T_RANGE','H_ONLY_T_RANGE','OUTSIDE_H_T_RANGE'):
        r=[x for x in results if x['source_T_support']==cls]
        selected.extend([r[0],r[len(r)//2],r[-1]])
    with (dest/'R47_PUBLIC_WITNESS_9.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n'); w.writeheader()
        for row in selected:
            w.writerow({k:('%.17g'%v if isinstance(v,float) else '' if v is None else v) for k,v in row.items()})
    (dest/'R47_RESULTS_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--rei-zip',type=pathlib.Path,required=True)
    p.add_argument('--emaa-zip',type=pathlib.Path,required=True)
    p.add_argument('--out',type=pathlib.Path,required=True)
    a=p.parse_args()
    result,summary,keys=analyze(a.rei_zip,a.emaa_zip)
    write_results(result,summary,keys,a.out)
    print(json.dumps({'counts':summary['counts'],'collision_frequency_ratio_joint':summary['collision_frequency_ratio_joint'],
    'linear_vs_loglog_interpolation_fractional_abs_error':summary['linear_vs_loglog_interpolation_fractional_abs_error']},indent=2))

if __name__=='__main__':main()
