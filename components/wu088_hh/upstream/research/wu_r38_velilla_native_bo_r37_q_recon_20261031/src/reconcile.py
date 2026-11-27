"""Original-source R38 sibling reconciliation: native Velilla BO spectral
rovibrational energy levels joined with R37 GL2022/EMAA reaction first-exit.
NOT a scattering rate calculation or a new chemical reaction model.

Inputs are immutable archived results from two independent R38 construction
paths, whose source identity is verified by the driver before invocation.
"""
import argparse,csv,hashlib,json,math
from pathlib import Path
from collections import defaultdict

EH_J=4.3597447222071e-18
KB_J=1.380649e-23
EH_K=EH_J/KB_J


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    with open(path,encoding='utf-8',newline='') as f:
        return list(csv.DictReader(f))


def csv_out(path,rows,keys):
    with open(path,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys,lineterminator='\n')
        w.writeheader(); w.writerows(rows)


def compute(spectral,fd,output):
    spectral=Path(spectral);fd=Path(fd);output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    sp=load(spectral/'BO_ISOTOPE_THRESHOLDS_247.csv')
    old=load(fd/'R38_R37_H2_PRODUCT_ENERGY_19200.csv')
    old_summary=load(fd/'R38_R37_FIRST_EXIT_ENERGY_SUMMARY_1920.csv')
    assert len(sp)==247 and len(old)==19200 and len(old_summary)==1920
    keys={(int(r['HD_v']),int(r['HD_J']),int(r['H2_v']),int(r['H2_J'])):r for r in sp}
    assert len(keys)==247
    # Compare all 190 overlapping v0(H2) asymptote thresholds without mixing energy zero conventions.
    oldpair=load(fd/'R38_NATIVE_HD_H2_CHANNEL_THRESHOLDS_190.csv')
    diff=[]
    for r in oldpair:
        k=int(r['initial_v']),int(r['initial_J']),int(r['product_v']),int(r['product_J'])
        newer=keys[k]
        dnew=float(newer['delta_E_hartree']);dold=float(r['delta_E_Eh'])
        diff.append({'HD_v':k[0], 'HD_J':k[1], 'H2_v':k[2], 'H2_J':k[3],
                     'FD_delta_E_hartree':f'{dold:.16e}', 'spectral_delta_E_hartree':f'{dnew:.16e}',
                     'spectral_minus_FD_K':f'{(dnew-dold)*EH_K:.12e}',
                     'FD_threshold_K':r['threshold_K'], 'spectral_threshold_K':newer['threshold_K'],
                     'channel_exo_class_agrees':int((dold<=0)==(dnew<=0))})
    assert len(diff)==190
    csv_out(output/'BO_FD_SPECTRAL_CHANNEL_CROSSCHECK_190.csv',diff,list(diff[0]))

    # 19,200 source branch weights transported unchanged from R37 first-exit.
    newrows=[]
    cases=defaultdict(list)
    for r in old:
        ji=int(r['initial_v0_J']);jf=int(r['H2_final_J']);q=keys[(0,ji,0,jf)]
        p=float(r['P_H2_J_before_first_exit'])
        qnew=-float(q['delta_E_hartree'])*EH_J
        new={'Tgas_K':r['Tgas_K'],'n_Hplus_cm_minus3':r['n_Hplus_cm_minus3'],
             'z_boundary':r['z_boundary'],'spin_policy':r['spin_policy'],
             'initial_v0_J':r['initial_v0_J'],'H2_final_J':r['H2_final_J'],
             'P_H2_J_before_first_exit':r['P_H2_J_before_first_exit'],
             'Q_spectral_J':f'{qnew:.16e}',
             'Q_old_FD_J':r['Q_release_J'],
             'Q_spectral_minus_old_J':f'{qnew-float(r["Q_release_J"]):.16e}',
             'weighted_Q_spectral_J_per_initial_HD':f'{p*qnew:.16e}',
             'spectral_threshold_K':q['threshold_K'],
             'exo_at_zero_KE':q['exo_at_zero_energy']}
        newrows.append(new)
        key=tuple(r[z] for z in ('Tgas_K','n_Hplus_cm_minus3','z_boundary','spin_policy','initial_v0_J'))
        cases[key].append((p,qnew,float(r['Q_release_J'])))
    assert len(cases)==1920 and len(newrows)==19200
    csv_out(output/'R38_SPECTRAL_R37_H2_BRANCH_Q_19200.csv',newrows,list(newrows[0]))

    oldindex={(r['Tgas_K'],r['n_Hplus_cm_minus3'],r['z_boundary'],r['spin_policy'],r['initial_v0_J']):r for r in old_summary}
    out=[];max_p_err=0
    for case,terms in sorted(cases.items(),key=lambda x:(float(x[0][0]),float(x[0][1]),str(x[0][2]),x[0][3],int(x[0][4]))):
        pchem=sum(p for p,q,oldQ in terms)
        check=float(oldindex[case]['P_H2_before_first_exit'])
        max_p_err=max(max_p_err,abs(pchem-check))
        q=sum(p*q for p,q,oldQ in terms)
        oldq=sum(p*oldQ for p,q,oldQ in terms)
        endo=sum(p for p,qr,_ in terms if qr<0)
        exo=sum(p for p,qr,_ in terms if qr>=0)
        if pchem<=0: raise AssertionError('chemistry zero probability')
        assert abs((endo+exo)-pchem)<1e-10
        line={'Tgas_K':case[0],'n_Hplus_cm_minus3':case[1],'z_boundary':case[2],
              'spin_policy':case[3],'initial_v0_J':case[4],
              'P_H2_before_first_exit':f'{pchem:.16e}',
              'P_endo_branch_per_initial_HD':f'{endo:.16e}',
              'fraction_endo_given_reaction':f'{endo/pchem:.16e}',
              'P_exo_branch_per_initial_HD':f'{exo:.16e}',
              'expected_Q_spectral_J_per_initial_HD':f'{q:.16e}',
              'conditional_Q_spectral_J_per_reaction':f'{q/pchem:.16e}',
              'conditional_Q_spectral_K':f'{q/pchem/KB_J:.16e}',
              'expected_Q_FD_J_per_initial_HD':f'{oldq:.16e}',
              'spectral_minus_FD_conditional_Q_K':f'{(q-oldq)/pchem/KB_J:.16e}'}
        out.append(line)
    assert max_p_err<3e-13,max_p_err
    csv_out(output/'R38_SPECTRAL_R37_FIRST_EXIT_Q_1920.csv',out,list(out[0]))

    s0=keys[(0,0,0,0)];d0=next(x for x in diff if (x['HD_v'],x['HD_J'],x['H2_v'],x['H2_J'])==(0,0,0,0))
    maxdelta=max(abs(float(x['spectral_minus_FD_K'])) for x in diff)
    signchanges=sum(x['channel_exo_class_agrees']=='0' for x in diff)
    root=[x for x in out if x['Tgas_K']=='105' and x['n_Hplus_cm_minus3']=='1000.0' and x['z_boundary']=='300' and x['spin_policy']=='eq6_7_spin_weighted' and x['initial_v0_J']=='2']
    summary={'status':'numerically_checked_bounded_crosswalk', 'upstream_source':'Velilla 2008 original Fortran diatomic BO + R37 original first-exit probabilities',
      'source_scopes':['same PES bare-nucleus 1D radial BO approximation','no new state-to-state scattering rates','first-exit not full chemical fate','kinematic threshold not Arrhenius gamma'],
      'original_r38_spectral_threshold_00_K':float(s0['threshold_K']),
      'original_r38_FD_threshold_00_K':float(d0['FD_threshold_K']),
      'spectral_minus_FD_ground_K':float(d0['spectral_minus_FD_K']),
      'max_abs_spectral_minus_FD_threshold_K':maxdelta,'overlap_channel_count':len(diff),'source_chemistry_branch_rows':len(newrows),
      'source_first_exit_cases':len(out), 'exo_endothermic_channel_class_changes':signchanges,'max_first_exit_Pchem_identity_error':max_p_err,
      'Q_conditional_K_range':[min(float(x['conditional_Q_spectral_K']) for x in out),max(float(x['conditional_Q_spectral_K']) for x in out)],
      'delta_conditional_Q_K_range':[min(float(x['spectral_minus_FD_conditional_Q_K']) for x in out),max(float(x['spectral_minus_FD_conditional_Q_K']) for x in out)],
      'reference_T105_n1000_z300_J2':root[0] if len(root)==1 else None}
    (output/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    representative=[r for r in out if r['Tgas_K']=='105' and r['n_Hplus_cm_minus3']=='1000.0' and r['spin_policy']=='eq6_7_spin_weighted']
    order={'OFF':0,'0':1,'10':2,'30':3,'100':4,'300':5}
    representative.sort(key=lambda x:(int(x['initial_v0_J']),order[x['z_boundary']]))
    if len(representative)!=30:raise ValueError('representative source grid mismatch')
    csv_out(output/'Q_REFERENCE_105K_30.csv',representative,list(representative[0]))
    return summary

if __name__=='__main__':
    a=argparse.ArgumentParser()
    a.add_argument('--spectral',type=Path,required=True)
    a.add_argument('--fd',type=Path,required=True)
    a.add_argument('--out',type=Path,required=True)
    args=a.parse_args();print(json.dumps(compute(args.spectral,args.fd,args.out),indent=2,ensure_ascii=False))
