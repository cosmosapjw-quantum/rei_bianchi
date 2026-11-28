#!/usr/bin/env python3
"""WU R41 physically source-qualified HD(v1)->first v0 radiative/collisional competition.
No scattering S-matrix, reaction or chemical heat, global NLTE or source-owner correction.
Standalone script in private master; original source file checks are mandatory.
"""
from __future__ import annotations
import csv, hashlib, json, sys, math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.constants import h,c,k as KB
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'source_private'))
import emaa_primary as owner

PARENT_HEAD='2d225e91040df59f45a158c7ba3d97e89741cfb1'
TGRID=(15.,55.,105.,255.,505.,1005.,1505.,2005.,2505.,3005.)
DENSITIES=(1.,1e3,1e4,1e5,1e6) # proton cm^-3; fixed prescribed controls only
ZGRID=('OFF','0','30','100','300')
T0=2.7255
EXPECTED={
 'emaa_primary.py':'c982bdd3a1dcf61bbd734295a68b2162b536068f4f65eb9e18ff188dd774252b',
 'HD.Rovibration.805a7aa5.radex':'b0db1613425e403889c3a74f6cd9e142c562a552f1ebf05e61cbf509cd429c94',
 'GL2022_1560_INELASTIC_SOURCE_TOKENS.csv':'58c252a1c3f62995ed748c7620e342bc98d8aabb307271bff48f7711e4f1cd7c'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def assert_sources(root):
    for f,d in EXPECTED.items():
        p=root/'source_private'/f
        if sha(p)!=d:raise AssertionError(f'source-byte identity failure {f}')

def store_csv(path,rows):
    if not rows:raise AssertionError('empty physical data')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');wr.writeheader();wr.writerows(rows)

def occupation(x):return 0.0 if x>700 else 1.0/math.expm1(x)

def radiative_components(data,z):
    """Source A_ul spontaneous, stimulated emission, and absorption, 19-state restriction.
    Columns source / rows destination, all generated from original EMAA radiative data.
    OFF retains spontaneous emission but no external photons.
    """
    lv=data['levels']; T=0. if z=='OFF' else T0*(1+int(z))
    dims=19
    sp=np.zeros((dims,dims));st=np.zeros_like(sp);ab=np.zeros_like(sp)
    active=[]
    for r in data['radiative']:
        up,lo=r['up'],r['low']
        if up>19 or lo>19:continue
        de=lv[up]['E']-lv[lo]['E']
        occ=occupation(owner.HCK*de/T) if T>0 else 0.0
        u,l=up-1,lo-1
        sp[l,u]+=r['A'];st[l,u]+=r['A']*occ;ab[u,l]+=r['A']*lv[up]['g']/lv[lo]['g']*occ
        active.append({'up_id':up,'low_id':lo,'up_v':lv[up]['v'],'low_v':lv[lo]['v'],
             'A_s_inv':r['A'],'E_photon_J':de*owner.HCJ,'freq_GHz':r['freq_GHz'],
             'occ':occ})
    def with_diagonal(x):
        y=x.copy();np.fill_diagonal(y,-np.sum(y,axis=0));return y
    return [with_diagonal(m) for m in (sp,st,ab)],active

def prepare(data):
    lv=data['levels'];a=[i-1 for i in range(1,20) if lv[i]['v']==0];u=[i-1 for i in range(1,20) if lv[i]['v']==1]
    assert len(a)==12 and len(u)==7
    E=np.array([lv[i]['E']*owner.HCJ for i in range(1,20)])
    return np.asarray(a),np.asarray(u),E

def solve_case(data,a,u,E,C,Rlist,mark=False):
    """N=-Kuu^-1, probability B_m=K^m_AU N. Count photons before first hitting."""
    K=C+sum(Rlist);Ku=K[np.ix_(u,u)]
    N=np.linalg.solve(-Ku,np.eye(len(u)))
    cause=[C,*Rlist]
    causeB=[M[np.ix_(a,u)]@N for M in cause]
    B=sum(causeB)
    if np.min(B)<-1.e-12 or max(abs(B.sum(axis=0)-1))>1.e-10:
        raise AssertionError('first hitting normalization failed')
    tau=N.sum(axis=0)
    if np.any(tau<=0):raise AssertionError('negative hitting time')
    # Gross microscopic energy release to each bath. Add all i in U -> j != i, including U->U and U->A.
    energy=[]
    for M in cause:
        delta=(E[u][None,:]-E[:,None])*M[:,u]
        energy.append(delta.sum(axis=0)@N)
    Qcoll=energy[0];Qrad=sum(energy[1:]);Qtotal=E[u]-(E[a]@B)
    if max(abs((Qcoll+Qrad)-Qtotal))>3e-32:
        raise AssertionError('energy partition not conserved')
    # photon path-counts from internal (U->U) and terminal (U->A) source-resolved transitions
    photon_counts=[]
    for M in Rlist:
        w=M[:,u].copy()
        for col,uc in enumerate(u):w[uc,col]=0.
        photon_counts.append(w.sum(axis=0)@N)
    return {'N':N,'B':B,'B_mechanisms':causeB,'tau':tau,'photon_counts':photon_counts,
            'Qcoll':Qcoll,'Qrad':Qrad,'Qtotal':Qtotal,'Qsp':energy[1],'Qstim':energy[2],'Qabs':energy[3]}

def source_owned_external_radiative_exit(data,u,z):
    """KNOWN 52-level radiative *upward* channels from U into outside 19.
    Stop at this source-coverage exit (absorbing), do not assign unknown collision rates.
    This extends first-exit bookkeeping but not post-exit kinetics or physical closure.
    """
    lv=data['levels'];radT=0. if z=='OFF' else T0*(1+int(z))
    outside=list(range(19,52)) # 0-index external HD levels with source-owned A_ul
    Eout=np.array([lv[j+1]['E']*owner.HCJ for j in outside])
    S=np.zeros((len(outside),len(u)))
    rows=[]
    for q in data['radiative']:
        high,low=q['up']-1,q['low']-1
        if high<19 or low not in u:continue
        x=owner.HCK*(lv[high+1]['E']-lv[low+1]['E'])/radT if radT>0 else float('inf')
        occ=occupation(x) if radT>0 else 0.
        rate=q['A']*lv[high+1]['g']/lv[low+1]['g']*occ
        S[high-19,list(u).index(low)]+=rate
        rows.append({'up_out':high,'low_U':low,'rate_s_inv':rate,'source_A_s_inv':q['A'],
            'photon_E_J':(lv[high+1]['E']-lv[low+1]['E'])*owner.HCJ})
    assert len(rows)==62
    return S,Eout,rows

def solve_source_open_boundary(data,a,u,E,C,Rlist,S,Eoutside):
    """First exit from 7 transient levels to v0 (12) or known 52-level radiation outside HD19.
    All source E levels stored, so event-weighted energy telescoping also checks the new exit.
    """
    K=C+sum(Rlist);Ku=K[np.ix_(u,u)].copy()
    Ku-=np.diag(S.sum(axis=0))
    N=np.linalg.solve(-Ku,np.eye(len(u)))
    causes=[C,*Rlist]
    Bmech=[M[np.ix_(a,u)]@N for M in causes]
    Bv0=sum(Bmech);Bext=S@N
    mass=Bv0.sum(axis=0)+Bext.sum(axis=0)
    if abs(mass-1).max()>2e-10 or Bext.min() < -1e-12:raise AssertionError('open source boundary normalization')
    e=[]
    for M in causes:
        e.append(((E[u][None,:]-E[:,None])*M[:,u]).sum(axis=0)@N)
    # Extra absorbed external photon: excitation U -> external higher HD level
    Eext=(E[u][None,:]-Eoutside[:,None])*S
    Qrad_external=Eext.sum(axis=0)@N
    Qrad=sum(e[1:])+Qrad_external
    Qtot=E[u]-(E[a]@Bv0)-(Eoutside@Bext)
    residual=e[0]+Qrad-Qtot
    if abs(residual).max()>3e-32:raise AssertionError('open marked energy identity')
    return {'B_v0':Bv0,'B_mech':Bmech,'B_out':Bext,'N':N,'tau':N.sum(axis=0),
            'Qrad':Qrad,'Qcoll':e[0],'Qtotal':Qtot,'Qrad_external':Qrad_external,
            'mass':mass,'residual':residual}

def data_model(root):
    assert_sources(root)
    data=owner.parse_radex(root/'source_private/HD.Rovibration.805a7aa5.radex')
    cross,valid,missing=owner.raw_crosswalk(data,root/'source_private/GL2022_1560_INELASTIC_SOURCE_TOKENS.csv')
    assert len(valid)==1548 and len(missing)==16
    assert len([r for r in cross if r['crosswalk_status']=='PRINTED_NUMERIC_MISMATCH'])==50
    return data,valid,missing

def compute(root,out, mode='all'):
    root=Path(root);out=Path(out);out.mkdir(exist_ok=True,parents=True)
    data,overrides,missing=data_model(root);A,U,E=prepare(data);lv=data['levels']
    summaries=[];branches=[];contrasts=[];lineevents=[];critical=[];rads=[];flags={}
    max_mass=max_balance=0.0;max_l1=0.;largest=None
    radcache={z:radiative_components(data,z) for z in ZGRID}
    assert all(len(v[1])==63 for v in radcache.values())
    Tstr=lambda z:str(z)
    for T in TGRID:
      for n in DENSITIES:
       base_C=owner.bath_rates(data,T,n)
       gl_C=owner.bath_rates(data,T,n,overrides=overrides)
       for z in ZGRID:
        Rlist,active=radcache[z]
        values={}
        for label,C in [('EMAA_primary',base_C),('GL_printed_hybrid',gl_C)]:
          result=solve_case(data,A,U,E,C,Rlist)
          values[label]=result
          B=result['B'];causes=result['B_mechanisms'];N=result['N'];
          max_mass=max(max_mass,float(np.max(np.abs(B.sum(axis=0)-1))))
          max_balance=max(max_balance,float(np.max(np.abs((result['Qcoll']+result['Qrad'])-result['Qtotal']))))
          for ji in range(7):
            ij=lv[U[ji]+1]['J'];pc=[float(x[:,ji].sum()) for x in causes]
            if min(pc)<-1e-12 or abs(sum(pc)-1)>2e-10:raise AssertionError('causal probability partition')
            ep=float(result['Qrad'][ji]);ec=float(result['Qcoll'][ji])
            summaries.append({'T_gas_K':T,'n_Hplus_cm_minus3':n,'z_boundary':z,'T_rad_K':0. if z=='OFF' else T0*(1+int(z)),
               'initial_HD_v':1,'initial_HD_J':ij,'source_lane':label,
               'P_first_v0_by_collision':f'{pc[0]:.17e}', 'P_first_v0_by_spontaneous':f'{pc[1]:.17e}',
               'P_first_v0_by_stimulated':f'{pc[2]:.17e}',
               'P_first_v0_by_radiative':f'{pc[1]+pc[2]:.17e}',
               'expected_photons_spontaneous':f'{result["photon_counts"][0][ji]:.17e}',
               'expected_photons_stimulated':f'{result["photon_counts"][1][ji]:.17e}',
               'expected_photons_absorbed':f'{result["photon_counts"][2][ji]:.17e}',
               'net_photons_to_radiation':f'{result["photon_counts"][0][ji]+result["photon_counts"][1][ji]-result["photon_counts"][2][ji]:.17e}',
               'Q_net_to_radiation_J_per_initial':f'{ep:.17e}',
               'Q_net_to_collisional_bath_J_per_initial':f'{ec:.17e}',
               'Q_net_internal_release_J_per_initial':f'{result["Qtotal"][ji]:.17e}',
               'mean_first_v0_time_s':f'{result["tau"][ji]:.17e}',
               'P_sum':f'{sum(pc):.17e}',
               'scope':'first_v0_event_only_fixed_T_blackbody_no_chemistry_source_conditional'})
            for ak,aidx in enumerate(A):
              for kind,M in zip(('collision','spontaneous','stimulated'),causes):
                branches.append({'T_gas_K':T,'n_Hplus_cm_minus3':n,'z_boundary':z,'initial_HD_J':ij,
                   'v0_final_J':lv[aidx+1]['J'],'source_lane':label,'terminal_mechanism':kind,
                   'P_terminal':f'{M[ak,ji]:.17e}'})
            # actual emitted/absorbed line outcomes for selective source grid only
            if T in (55.,1005.) and n in (1.e3,1.e5) and z in ('OFF','300'):
              dwell=N[:,ji]
              for line in active:
                up,lo=line['up_id']-1,line['low_id']-1
                if up not in U:continue
                du=np.where(U==up)[0][0]
                downsp=line['A_s_inv']*dwell[du];downstim=downsp*line['occ']
                uplow=(line['A_s_inv']*lv[up+1]['g']/lv[lo+1]['g']*line['occ']*dwell[np.where(U==lo)[0][0]]) if lo in U else 0.
                lineevents.append({'T_gas_K':T,'n_Hplus_cm_minus3':n,'z_boundary':z,'initial_HD_J':ij,
                   'source_lane':label,'line_up':lv[up+1]['label'],'line_low':lv[lo+1]['label'],
                   'freq_GHz':line['freq_GHz'],'E_photon_J':f'{line["E_photon_J"]:.17e}',
                   'count_spontaneous':f'{downsp:.17e}','count_stimulated':f'{downstim:.17e}',
                   'count_absorbed':f'{uplow:.17e}',
                   'net_energy_to_radiation_J':f'{(downsp+downstim-uplow)*line["E_photon_J"]:.17e}'})
        p1,p2=values['EMAA_primary'],values['GL_printed_hybrid']
        for j in range(7):
            bdelta=float(np.sum(abs(p1['B'][:,j]-p2['B'][:,j])));
            max_l1=max(max_l1,bdelta)
            if largest is None or bdelta>largest['P_first_v0_L1']:largest={'T_gas_K':T,'n':n,'z':z,'initial_J':j,'P_first_v0_L1':bdelta}
            contrasts.append({'T_gas_K':T,'n_Hplus_cm_minus3':n,'z_boundary':z,'initial_HD_J':j,
                 'P_first_v0_destination_L1_GL_minus_EMAA':f'{bdelta:.17e}',
                 'delta_collision_terminal_P_GL_minus_EMAA':f'{p2["B_mechanisms"][0][:,j].sum()-p1["B_mechanisms"][0][:,j].sum():.17e}',
                 'delta_Qrad_J_per_initial_GL_minus_EMAA':f'{p2["Qrad"][j]-p1["Qrad"][j]:.17e}',
                 'delta_mean_hitting_time_s':f'{p2["tau"][j]-p1["tau"][j]:.17e}',
                 'source_status':'GL_hybrid_source_choice_not_source_owner_correction'})
    # Adversarial physical boundary audit: source includes 52 levels and 62 radiative
    # upward links from v1 subset U to outside the collisional HD19 manifold.
    # Do not drop these as physical zero at high blackbody temperature; stop at first exit.
    external=[];exit_lines=[];max_extern=0.;max_open_balance=0.;max_open_mass=0.;max_extern_case=None
    for T in TGRID:
      for n in DENSITIES:
       source_coll=[('EMAA_primary',owner.bath_rates(data,T,n)),
           ('GL_printed_hybrid',owner.bath_rates(data,T,n,overrides=overrides))]
       for z in ZGRID:
        Rlist,_=radcache[z]
        S,Eoutside,escape_lines=source_owned_external_radiative_exit(data,U,z)
        for label,C in source_coll:
         d=solve_source_open_boundary(data,A,U,E,C,Rlist,S,Eoutside)
         max_open_balance=max(max_open_balance,float(np.max(abs(d['residual']))))
         max_open_mass=max(max_open_mass,float(np.max(abs(d['mass']-1))))
         for ji in range(7):
          pij=float(d['B_out'][:,ji].sum())
          if pij>max_extern:
              max_extern=pij;max_extern_case={'T_gas_K':T,'n_Hplus_cm_minus3':n,'z_boundary':z,
                  'initial_HD_J':ji,'source_lane':label,'P_escape':pij}
          probs=[float(x[:,ji].sum()) for x in d['B_mech']]
          external.append({'T_gas_K':T,'n_Hplus_cm_minus3':n,'z_boundary':z,
             'initial_HD_J':ji,'source_lane':label,
             'P_first_v0_collision':f'{probs[0]:.17e}',
             'P_first_v0_spontaneous':f'{probs[1]:.17e}',
             'P_first_v0_stimulated':f'{probs[2]:.17e}',
             'P_first_v0_any':f'{sum(probs):.17e}',
             'P_first_radiative_exit_outside_HD19':f'{pij:.17e}',
             'P_sum':f'{d["mass"][ji]:.17e}',
             'mean_first_any_exit_time_s':f'{d["tau"][ji]:.17e}',
             'net_energy_to_radiation_J_per_initial':f'{d["Qrad"][ji]:.17e}',
             'net_energy_to_collisional_bath_J_per_initial':f'{d["Qcoll"][ji]:.17e}',
             'net_internal_release_J_per_initial':f'{d["Qtotal"][ji]:.17e}',
             'known_outside_photon_absorption_J_per_initial':f'{d["Qrad_external"][ji]:.17e}',
             'boundary':'first_v0_or_known_radiative_outside_HD19; no_return_or_outside_collisional_model'})
          if T==55. and n==1e3 and z=='300' and ji==6:
             for ll in escape_lines:
                iout=ll['up_out'];
                outp=float(d['B_out'][iout-19,ji])
                # Multiple spectral lines can end at same outside state; each line's event prob is rate * dwell
                p_line=ll['rate_s_inv']*float(d['N'][list(U).index(ll['low_U']),ji])
                exit_lines.append({'source_lane':label,'T_gas_K':T,'n_Hplus_cm_minus3':n,
                    'z_boundary':z,'initial_HD_J':ji,
                    'source_low_HD':lv[ll['low_U']+1]['label'],
                    'external_high_HD':lv[iout+1]['label'],
                    'A_s_inv':f'{ll["source_A_s_inv"]:.17e}',
                    'stimulated_absorption_rate_s_inv':f'{ll["rate_s_inv"]:.17e}',
                    'P_exit_via_this_radiative_line':f'{p_line:.17e}',
                    'P_destination_outside_level':f'{outp:.17e}',
                    'photon_absorbed_J':f'{ll["photon_E_J"]:.17e}',
                    'scope':'first_exit_into_outside_52state_spectroscopic_source_only'})
    assert len(external)==3500 and len(exit_lines)==124
    store_csv(out/'R41_KNOWN_RADIATIVE_OUTSIDE_EXIT_3500.csv',external)
    store_csv(out/'R41_OUTSIDE_RADIATIVE_ESCAPE_LINES_124.csv',exit_lines)
    # Density at which first v0 cause = 50% radiative / 50% collision; true rooted conditional CTMC, not population equilibrium.
    for T in TGRID:
      for z in ZGRID:
       Rlist,_=radcache[z]
       for label,over in [('EMAA_primary',None),('GL_printed_hybrid',overrides)]:
        def p_rad(logn,j):
            n=10.**logn;C=owner.bath_rates(data,T,n,overrides=over)
            b=solve_case(data,A,U,E,C,Rlist)
            return float((b['B_mechanisms'][1]+b['B_mechanisms'][2])[:,j].sum())
        for j in range(7):
            lo,hi=-4.,9.
            f=lambda logn:p_rad(logn,j)-.5
            vlo,vhi=f(lo),f(hi)
            if vlo*vhi>=0: raise AssertionError(f'density crossover not bracketed {(T,z,label,j,vlo,vhi)}')
            root=brentq(f,lo,hi,xtol=1e-11)
            radval=p_rad(root,j)
            critical.append({'T_gas_K':T,'z_boundary':z,'initial_HD_J':j,'source_lane':label,
                  'nHplus_radiative_collision_equal_cm_minus3':f'{10.**root:.17e}',
                  'P_radiative_at_root':f'{radval:.16e}',
                  'definition':'first_v0_radiative_vs_collision_50pct_source_conditional'})
    store_csv(out/'R41_FIRST_V0_MECHANISM_SUMMARY_3500.csv',summaries)
    store_csv(out/'R41_FIRST_V0_TERMINAL_BRANCHES_126000.csv',branches)
    store_csv(out/'R41_SOURCE_CONTRAST_1750.csv',contrasts)
    store_csv(out/'R41_PHOTON_LINE_EVENTS_4704.csv',lineevents)
    store_csv(out/'R41_HALF_RADIATIVE_DENSITY_700.csv',critical)
    assert (len(summaries),len(branches),len(contrasts),len(lineevents),len(critical)) == (3500,126000,1750,4704,700),(len(summaries),len(branches),len(contrasts),len(lineevents),len(critical))
    # Frozen physically sourced A-line ledger for 19-level code range, no fabricated oscillator strengths
    lineledger=[]
    for x in radcache['OFF'][1]:
      lineledger.append({'up_id':x['up_id'],'low_id':x['low_id'],'up_v':x['up_v'],'low_v':x['low_v'],
        'A_s_inv':f'{x["A_s_inv"]:.16e}','E_photon_J':f'{x["E_photon_J"]:.16e}',
        'freq_GHz':f'{x["freq_GHz"]:.10f}',
        'source':'EMAA_805a7aa5_HITRAN_radiative_source'})
    matched={}
    for row in critical:
        key=(row['T_gas_K'],row['z_boundary'],row['initial_HD_J'])
        matched.setdefault(key,{})[row['source_lane']]=float(row['nHplus_radiative_collision_equal_cm_minus3'])
    contrast_half=[]
    for key,vals in sorted(matched.items(),key=lambda x:(x[0][0],str(x[0][1]),x[0][2])):
        a=vals['EMAA_primary'];b=vals['GL_printed_hybrid']
        contrast_half.append({'T_gas_K':key[0],'z_boundary':key[1],'initial_HD_J':key[2],
             'n_half_EMAA_cm_minus3':f'{a:.17e}','n_half_GL_printed_hybrid_cm_minus3':f'{b:.17e}',
             'relative_difference_GL_minus_EMAA':f'{b/a-1:.17e}',
             'source_status':'conditional_origin_not_corrected_rates'})
    assert len(contrast_half)==350
    store_csv(out/'R41_HALF_DENSITY_SOURCE_CONTRAST_350.csv',contrast_half)
    store_csv(out/'R41_19LEVEL_RADIATIVE_LINES_63.csv',lineledger)
    summary={'status':'SOURCE_CONDITIONAL_NUMERICALLY_VERIFIED','canonical_DAG':'34/49_UNCHANGED',
       'R41_auxiliary':'1/1_SCOPED','R_C_scoped':'18/20',
       'rows':{'mechanism_summary':len(summaries),'terminal_branches':len(branches),
          'source_contrasts':len(contrasts),'line_events':len(lineevents),
          'crossovers':len(critical),'density_source_contrasts':len(contrast_half),'source_spectroscopy':len(lineledger),
           'known_external_radiative_first_exit':len(external),'external_line_examples':len(exit_lines)},
       'source_originals':EXPECTED,'parent_PR':179,'parent_HEAD':PARENT_HEAD,
       'gas_T_grid_K':TGRID,'density_grid_cm_minus3':DENSITIES,'blackbody_boundaries':ZGRID,
       'U_initial':'HD_v1_J0..6','A_final':'HD_v0_J0..11',
       'max_probability_mass_defect':max_mass,'max_energy_identity_residual_J':max_balance,
       'max_GL_EMAA_destination_L1':max_l1,'max_L1_case':largest,
       'max_known_radiative_external_escape_P':max_extern,'max_external_case':max_extern_case,
       'max_open_probability_defect':max_open_mass,'max_open_energy_residual_J':max_open_balance,
       'physical_claim_limits':['fixed source temperature and blackbody boundary, density prescribed',
            'blackbody OFF means spontaneous retained','known 62 radiative upward links into outside HD19 treated as separate absorbing first-exit, no outside post-exit kinetics',
            'other outside HD19 proton collisional processes unknown and omitted, not physical zero',
            'collision rates source choices, no author correction',
            'first arrival into v0 only, no post-arrival return, no chemical reactions or H2 product',
            'gross emitted and absorbed path counts not net observed spectrum, no transfer/opacity',
            'no full reaction scattering S matrix or gas heating per volume'],
       'owner_ack':'NOT_OBTAINED','R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN',
       'HH_R10':'OFF','L4':False,'production':'NOT_ISSUED','new_canonical_nodes':0}
    (out/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    return summary

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,default=ROOT/'results')
 args=p.parse_args()
 print(json.dumps(compute(args.root,args.out),indent=2,ensure_ascii=False))
