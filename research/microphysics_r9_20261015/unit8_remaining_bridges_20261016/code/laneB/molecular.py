"""Unit8 B frozen finite-curve LiH nuclear motion/E1 and ExoMol CLT LTE reuse."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
import bz2,csv,hashlib,json,math,signal,sys,time
from pathlib import Path
import numpy as np
import scipy
from scipy.interpolate import PchipInterpolator,CubicSpline
from scipy.linalg import eigh_tridiagonal
ROOT=Path(__file__).resolve().parents[2];CON=json.loads((ROOT/'spec/MOLECULAR_CONTRACT.json').read_text());C=CON['constants']
HB=C['h_J_s']/(2*np.pi);HARTREE_CM=C['Eh_J']/(C['h_J_s']*C['c_m_s']*100)

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj): (ROOT/p).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def csvout(path,rows):
    with (ROOT/path).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def readcsv(path):
    with path.open() as f:return list(csv.DictReader(f))

def curves():
    src=Path(CON['source_root']); tab=ROOT/'inputs/laneB/lih_curve_inputs.csv';manifestfile=ROOT/'inputs/laneB/lih_curve_extraction.json'
    cases=[(basis,tok,src/CON['local_inputs']['case_pattern'].format(basis=basis,R_token=tok)) for basis in CON['local_inputs']['bases'] for tok in CON['local_inputs']['R_tokens']]
    present=[(p/'receipt.json').exists() and (p/'data.npz').exists() for _,_,p in cases]
    if all(present):
        rows=[]; checks=[]
        for basis,tok,p in cases:
            rec=json.loads((p/'receipt.json').read_text());r=float(tok);sha=digest(p/'data.npz');case=rec['case']
            assert rec['finite_model_numerics_passed'] is True and case['molecule']=='LiH' and case['basis']==basis and case['R_a0']==r and rec['R_a0']==r
            assert sha==rec['data_sha256']
            with np.load(p/'data.npz') as a:
                np.testing.assert_array_equal(a['atom_charges'],[3,1]); np.testing.assert_array_equal(a['atom_coordinates_a0'],[[0,0,-r/2],[0,0,r/2]])
                dip=float(a['dipole_ea0'][2])
            v=rec['V_CP_Eh'];assert np.isfinite(v) and np.isfinite(dip)
            rows.append({'basis':basis,'R_a0':r,'V_CP_Eh':v,'signed_dipole_ea0_z':dip})
            checks.append({'case':p.name,'source_path':str(p),'receipt_sha256':digest(p/'receipt.json'),'data_sha256':sha,'case_sha256':rec['case_sha256'],'finite_model_numerics_passed':True,'molecule':'LiH','basis':basis,'R_a0':r,'atom_charges':[3,1],'atom_coordinates_a0':[[0,0,-r/2],[0,0,r/2]],'identity_geometry_field_checks':'PASS'})
        # If a compact extraction exists, available original inputs must agree with its identity.
        if manifestfile.exists():
            old=json.loads(manifestfile.read_text());assert all(a['data_sha256']==b['data_sha256'] and a['receipt_sha256']==b['receipt_sha256'] for a,b in zip(checks,old['source_checks']))
        csvout('inputs/laneB/lih_curve_inputs.csv',rows)
        manifest={'compact_table_sha256':digest(tab),'original_NPZ_recheck':'PASS_ALL20','source_checks':checks,'policy':'No large CI arrays copied; compact exact extraction; available mismatched sources must fail.'}
        dump('inputs/laneB/lih_curve_extraction.json',manifest)
    else:
        # A partially available or mismatched original cannot silently become a portable fallback.
        if any(present):raise ValueError('Partial original source availability; explicit authority required')
        if any((p/'receipt.json').exists() or (p/'data.npz').exists() for _,_,p in cases):raise ValueError('Partial original case files')
        manifest=json.loads(manifestfile.read_text());assert digest(tab)==manifest['compact_table_sha256']
        rows=readcsv(tab)
        manifest={**manifest,'original_NPZ_recheck':'NOT_AVAILABLE','recorded_checks':'historically_recorded; not re-executed'}
    csvout('evidence/lih_actual_curve_inputs.csv',rows)
    return {basis:np.array([[float(row[k]) for k in ('R_a0','V_CP_Eh','signed_dipole_ea0_z')] for row in rows if row['basis']==basis]) for basis in CON['local_inputs']['bases']},manifest

def mu_mass(atomic=False):
    li=C['mLi7_atom_u']*C['u_over_me']-(0 if atomic else 3);h=C['mH1_atom_u']*C['u_over_me']-(0 if atomic else 1)
    return li*h/(li+h)

def solve_curve(table,kind='PCHIP',N=4000,domain=(2.,12.),atomic=False):
    interp=PchipInterpolator if kind=='PCHIP' else CubicSpline
    V=interp(table[:,0],table[:,1],extrapolate=False);D=interp(table[:,0],table[:,2],extrapolate=False)
    rr=np.linspace(*domain,N+1)[1:-1];h=(domain[1]-domain[0])/N;mu=mu_mass(atomic);off=np.full(len(rr)-1,-1/(2*mu*h*h));dip=D(rr)
    eig={};res=[];orth=[]
    for J in (0,1,2):
        diag=1/(mu*h*h)+V(rr)+J*(J+1)/(2*mu*rr*rr)
        E,q=eigh_tridiagonal(diag,off,select='i',select_range=(0,2))
        for i in range(3):
            if q[np.argmax(abs(q[:,i])),i]<0:q[:,i]*=-1
        Hq=diag[:,None]*q;Hq[:-1]+=off[:,None]*q[1:];Hq[1:]+=off[:,None]*q[:-1]
        res.append(float(np.max(np.linalg.norm(Hq-q*E,axis=0))));orth.append(float(np.max(abs(q.T@q-np.eye(3)))))
        eig[J]=(E,q)
    return {'R':rr,'h':h,'mu':mu,'dip':dip,'eig':eig,'max_residual':max(res),'max_orth':max(orth),'ordering':all(np.all(np.diff(e[0])>0) for e in eig.values()),'kind':kind,'N':N,'domain':domain,'atomic':atomic}

def einstein(gap,M,Ji,Jf):
    if gap<=0 or abs(Ji-Jf)!=1: return 0.
    omega=gap*C['Eh_J']/HB
    return omega**3*(M*C['e_C']*C['a0_m'])**2/(3*np.pi*C['epsilon0_F_m']*HB*C['c_m_s']**3)*max(Ji,Jf)/(2*Ji+1)

def lines(run):
    out=[];eig=run['eig'];dip=run['dip']
    for Ji in (0,1):
        for vi in range(3):
            Ei,qi=eig[Ji][0][vi],eig[Ji][1][:,vi]
            for Jf in (0,1,2):
                if abs(Ji-Jf)!=1:continue
                for vf in range(3):
                    gap=Ei-eig[Jf][0][vf]
                    if gap<=0:continue
                    M=float(np.dot(eig[Jf][1][:,vf]*dip,qi));A=einstein(gap,M,Ji,Jf)
                    out.append({'vi':vi,'Ji':Ji,'vf':vf,'Jf':Jf,'gap_Eh':float(gap),'frequency_cm-1':float(gap*HARTREE_CM),'M_ea0':M,'angular_factor':max(Ji,Jf)/(2*Ji+1),'A_s-1':A,'A_global_sign_flipped_s-1':einstein(gap,-M,Ji,Jf)})
    return out

def keyline(r):return r['vi'],r['Ji'],r['vf'],r['Jf']
def lifetimes(lines):
    out={}
    for J in (0,1):
        for v in range(3):
            rate=math.fsum(l['A_s-1'] for l in lines if l['vi']==v and l['Ji']==J)
            out[v,J]={'Gamma_s-1':rate,'tau_s':1/rate if rate>0 else None,'dark_state':rate==0}
    return out

def public_LTE():
    p=ROOT/CON['public_inputs']['directory'];hashes={name:digest(p/name) for name in CON['public_inputs']['files_sha256']};assert hashes==CON['public_inputs']['files_sha256']
    with bz2.open(p/'7Li-1H__CLT.states.bz2','rt') as f:s=np.loadtxt(f)
    with bz2.open(p/'7Li-1H__CLT.trans.bz2','rt') as f:t=np.loadtxt(f)
    ids=s[:,0].astype(int);idx={v:i for i,v in enumerate(ids)};assert len(idx)==len(s)
    up=np.array([idx[v] for v in t[:,0].astype(int)]);lo=np.array([idx[v] for v in t[:,1].astype(int)])
    gap=s[up,1]-s[lo,1];A=t[:,2];deg=s[:,2];J=s[:,3].astype(int);freqerr=float(np.max(abs(gap-t[:,3])))
    energy=gap*C['h_J_s']*C['c_m_s']*100;Pu=np.bincount(up,weights=A*energy,minlength=len(s));Gamma=np.bincount(up,weights=A,minlength=len(s))
    cf=np.loadtxt(p/'7Li-1H__CLT.cf');cf=cf[cf[:,0]<=5000];pf=np.loadtxt(p/'7Li-1H__CLT.pf');pfmap={int(T):Q for T,Q in pf};cfmap={T:L for T,L in cf}
    temperatures=sorted(set(CON['LTE']['temperature_K'])|set(cf[:,0]));rows=[];internal=[];population=[];Qerrs=[];cferrs=[]
    for T in temperatures:
        w=deg*np.exp(-C['h_J_s']*C['c_m_s']*100*s[:,1]/(C['kB_J_K']*T));Q=float(w.sum());pop=w/Q
        bylines=float(np.sum(pop[up]*A*energy));bygroups=float(np.dot(pop,Pu));err=abs(bylines/bygroups-1);internal.append(err);population.append(abs(pop.sum()-1))
        qr=None;qe=None
        if T in CON['LTE']['temperature_K']:
            qr=pfmap[int(T)];qe=abs(Q/qr-1);Qerrs.append((qe,float(T)))
        cr=cfmap.get(T);ce=abs(bylines*1e7/cr-1) if cr is not None else None
        if ce is not None:cferrs.append((ce,float(T)))
        rows.append({'T_K':float(T),'Q':Q,'power_W_per_molecule':bylines,'power_erg_s-1_per_molecule':bylines*1e7,'grouped_power_W_per_molecule':bygroups,'sum_order_relative':err,'population_sum_residual':float(abs(pop.sum()-1)),'population_E_gt15000_fraction':float(pop[s[:,1]>15000].sum()),'power_E_gt15000_fraction':float(np.dot(pop[s[:,1]>15000],Pu[s[:,1]>15000])/bylines),'Q_reference':qr,'Q_reference_relative':qe,'cooling_reference_erg_s-1':cr,'cooling_reference_relative':ce})
    liferows=[{'id':int(s[i,0]),'v':int(s[i,4]),'J':int(s[i,3]),'E_cm-1':float(s[i,1]),'g_tot':float(s[i,2]),'Gamma_s-1':float(Gamma[i]),'tau_s':float(1/Gamma[i]) if Gamma[i]>0 else None,'dark_state':bool(Gamma[i]==0)} for i in range(len(s))]
    csvout('evidence/lih_CLT_LTE_cooling.csv',rows);csvout('evidence/lih_CLT_lifetimes.csv',liferows)
    checks={'state_transition_counts':len(s)==1086 and len(t)==18982,'unique_mapped_ids':len(idx)==len(s),'positive_downward_lines':bool(np.all(A>0) and np.all(gap>0)),'degeneracy':bool(np.all(deg==8*(2*J+1))),'frequency_agreement':freqerr<=2e-4,'partition_reference':max(Qerrs)[0]<=1e-4,'cooling_reference_formatting':max(cferrs)[0]<=.02,'independent_power_sums':max(internal)<=1e-12,'population_normalized':max(population)<=1e-13}
    diag={'files_sha256':hashes,'counts':{'states':len(s),'transitions':len(t)},'frequency_max_residual_cm-1':freqerr,'Q_reference_max_relative_and_T':max(Qerrs),'cf_reference_max_relative_and_T':max(cferrs),'cooling_sum_order_max_relative':max(internal),'population_sum_max_abs':float(max(population)),'metadata_discrepancy':{'def_max_energy_cm-1':20000,'actual_max_energy_cm-1':float(s[:,1].max()),'policy':'actual rows authoritative'},'selected_integer_temperature_rows':[r for r in rows if r['T_K'] in CON['LTE']['temperature_K']]}
    return checks,diag,liferows,t

def run():
    start=time.perf_counter()
    def timeout(*_):raise TimeoutError('Frozen30s numerical budget exhausted')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(30)
    tables,identity=curves();runs={};raw={};alllines={};levelrows=[];linerows=[]
    for basis,table in tables.items():
        plans=[('primary','PCHIP',4000,(2.,12.),False),('coarse','PCHIP',2000,(2.,12.),False),('left_domain','PCHIP',3980,(2.05,12.),False),('right_domain','PCHIP',2400,(2.,8.),False),('cubic','CubicSpline',4000,(2.,12.),False)]
        if basis=='aug-cc-pvdz':plans.append(('atomic_mass','PCHIP',4000,(2.,12.),True))
        for name,kind,N,domain,atomic in plans:
            label=basis+'__'+name;rs=solve_curve(table,kind,N,domain,atomic);runs[label]=rs;alllines[label]=lines(rs)
            for row in alllines[label]:linerows.append({'model':label,**row})
            raw[label+'__R']=rs['R'];raw[label+'__dipole']=rs['dip'];raw[label+'__E']=np.array([rs['eig'][J][0] for J in (0,1,2)]);raw[label+'__q']=np.array([rs['eig'][J][1] for J in (0,1,2)])
    mesh={};domains={};interpolation={};mass={};signerr=0.
    for basis in tables:
        fine=runs[basis+'__primary'];coarse=runs[basis+'__coarse'];left=runs[basis+'__left_domain'];right=runs[basis+'__right_domain'];cubic=runs[basis+'__cubic']
        enerr=max(float(np.max(abs(fine['eig'][J][0]-coarse['eig'][J][0]))) for J in (0,1,2))
        lf={keyline(r):r for r in alllines[basis+'__primary']};lc={keyline(r):r for r in alllines[basis+'__coarse']};Aerrs=[];Aabs=[]
        for k,r in lf.items():
            diff=abs(r['A_s-1']-lc[k]['A_s-1']);Aerrs.append(diff/r['A_s-1'] if r['A_s-1']>=1e-8 else 0);Aabs.append(diff if r['A_s-1']<1e-8 else 0)
        mesh[basis]={'energy_max_Eh':enerr,'A_max_relative_above_threshold':max(Aerrs),'A_max_absolute_below_threshold_s-1':max(Aabs),'line_identity_sets_equal':set(lf)==set(lc)}
        domains[basis]=[]
        for J in (0,1,2):
            for v in range(3):
                E=fine['eig'][J][0][v];q=fine['eig'][J][1][:,v];rr=fine['R'];pleft=float(np.sum(q[rr<=2.1]**2));pright=float(np.sum(q[rr>=11.9]**2));outside=float(np.sum(q[(rr<2.1)|(rr>8)]**2));dl=float(left['eig'][J][0][v]-E);dr=float(right['eig'][J][0][v]-E)
                local=E<0 and max(pleft,pright)<=1e-5 and max(abs(dl),abs(dr))<=1e-5
                domains[basis].append({'v':v,'J':J,'edge_left_probability':pleft,'edge_right_probability':pright,'probability_outside_2.1_8':outside,'left_domain_shift_Eh':dl,'right_domain_shift_Eh':dr,'qualification':'LOCALIZED_BOUND_CANDIDATE_FINITE_CURVE' if local else 'DOMAIN_SENSITIVE'})
        interpolation[basis]={'energy_CubicSpline_minus_PCHIP_Eh':{str(J):(cubic['eig'][J][0]-fine['eig'][J][0]).tolist() for J in (0,1,2)},'line_A_CubicSpline_minus_PCHIP_s-1':[{**dict(zip(('vi','Ji','vf','Jf'),keyline(r))),'difference_s-1':r['A_s-1']-lf[keyline(r)]['A_s-1']} for r in alllines[basis+'__cubic']]}
    for label,rs in runs.items():
        rates=lifetimes(alllines[label]);basis=label.split('__')[0];isprimary=label.endswith('__primary');Eground=rs['eig'][0][0][0]
        for J in (0,1,2):
            for v in range(3):
                E=rs['eig'][J][0][v];q=rs['eig'][J][1][:,v];Bv=float(np.dot(q*q,1/(2*rs['mu']*rs['R']**2))) if J==0 else None
                qualification=next(r['qualification'] for r in domains[basis] if r['v']==v and r['J']==J) if isprimary else 'SENSITIVITY_FINITE_BOX'
                life=rates.get((v,J),{'Gamma_s-1':None,'tau_s':None,'dark_state':None})
                levelrows.append({'model':label,'v':v,'J':J,'N_intervals':rs['N'],'R_min_a0':rs['domain'][0],'R_max_a0':rs['domain'][1],'mu_me':rs['mu'],'absolute_CP_E_Eh':float(E),'relative_to_model_v0J0_cm-1':float((E-Eground)*HARTREE_CM),'Bv_Eh':Bv,'J1_minus_J0_minus_2Bv_Eh':float(rs['eig'][1][0][v]-E-2*Bv) if J==0 else None,'qualification':qualification,**life})
        for line in alllines[label]:
            if line['A_s-1']>0:signerr=max(signerr,abs(line['A_global_sign_flipped_s-1']/line['A_s-1']-1))
    csvout('evidence/lih_levels.csv',levelrows);csvout('evidence/lih_E1_lines.csv',linerows);np.savez(ROOT/'evidence/lih_bound_wavefunctions.npz',**raw)
    lchecks,clt,cltlife,trans=public_LTE();ref={(r['v'],r['J']):r for r in cltlife};comp=[]
    for row in levelrows:
        if not row['model'].endswith('__primary'):continue
        rr=ref[row['v'],row['J']]
        comp.append({'model':row['model'],'v':row['v'],'J':row['J'],'model_relative_energy_cm-1':row['relative_to_model_v0J0_cm-1'],'CLT_relative_energy_cm-1':rr['E_cm-1'],'difference_cm-1':row['relative_to_model_v0J0_cm-1']-rr['E_cm-1'],'model_selected_low_space_Gamma_s-1':row['Gamma_s-1'],'CLT_all_list_Gamma_s-1':rr['Gamma_s-1'],'model_selected_low_space_tau_s':row['tau_s'],'CLT_all_list_tau_s':rr['tau_s'],'qualification':row['qualification']})
    csvout('evidence/lih_CLT_comparison.csv',comp)
    aug=runs['aug-cc-pvdz__primary'];cc=runs['cc-pvdz__primary'];atomic=runs['aug-cc-pvdz__atomic_mass']
    basis_sensitivity={str(J):(aug['eig'][J][0]-cc['eig'][J][0]).tolist() for J in (0,1,2)}
    mass={'mu_nuclear_me':mu_mass(),'mu_atomic_me':mu_mass(True),'atomic_minus_nuclear_Eh':{str(J):(atomic['eig'][J][0]-aug['eig'][J][0]).tolist() for J in (0,1,2)}}
    maxres=max(r['max_residual'] for r in runs.values());maxorth=max(r['max_orth'] for r in runs.values())
    checks={**lchecks,'eigenpair_residual':maxres<=1e-9,'eigenvector_orthonormality':maxorth<=1e-10,'eigenvalue_ordering':all(r['ordering'] for r in runs.values()),'grid_energy':max(r['energy_max_Eh'] for r in mesh.values())<=2e-6,'grid_A':all(r['A_max_relative_above_threshold']<=.002 and r['A_max_absolute_below_threshold_s-1']<=1e-10 and r['line_identity_sets_equal'] for r in mesh.values()),'global_dipole_sign':signerr<=1e-13,'E1_selection_rules':all(abs(r['Ji']-r['Jf'])==1 and r['gap_Eh']>0 and r['A_s-1']>=0 for r in linerows)}
    elapsed=time.perf_counter()-start;signal.alarm(0)
    result={'contract_id':CON['contract_id'],'authority_requested':'Astra','executor_requested':'gpt-6.1-sol','executor_observed':'UNKNOWN','input_identity_checks':identity,'mesh_errors':mesh,'eigenpair_residuals':{'max_Eh':maxres,'max_orthonormality_abs':maxorth},'domain_sensitivity':domains,'edge_probabilities':'reported per v,J in domain_sensitivity','interpolation_sensitivity':interpolation,'basis_sensitivity_aug_minus_cc_Eh':basis_sensitivity,'mass_sensitivity':mass,'CLT_reference_differences':comp,'CLT_diagnostics':clt,'Q_reference_error':clt['Q_reference_max_relative_and_T'],'cf_reference_error_and_temperature':clt['cf_reference_max_relative_and_T'],'cooling_internal_error':clt['cooling_sum_order_max_relative'],'metadata_discrepancy':clt['metadata_discrepancy'],'global_dipole_sign_A_max_relative':signerr,'checks':{k:bool(v) for k,v in checks.items()},'finite_model_counts':{'curve_points':20,'nuclear_solver_runs':len(runs),'level_rows':len(levelrows),'E1_rows':len(linerows)},'scope':'Finite sparse CP curves and signed dipoles; no extrapolation, extra nuclear repulsion or fragment energy. Localized level labels are finite-curve candidates, not physical precision; DOMAIN_SENSITIVE data retained. CLT LTE is literature-conditioned bound-molecule optically thin all-direction spontaneous emission, not collider kinetics, chemical formation, actual cosmological LTE validity or abundance cooling. No new electronic jobs, H or NCP.','wall_time_s':elapsed,'versions':{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__},'status':'NUMERICAL_CHECKS_PASS_REVIEW_PENDING' if all(checks.values()) else 'NUMERICAL_FAILURE_AUTHORITY_REQUIRED'}
    dump('evidence/MOLECULAR_RESULT.json',result);print(json.dumps(result,indent=2));return result
if __name__=='__main__':
    try:run()
    except BaseException as exc:
        dump('results/laneB/raw/failure.json',{'error_type':type(exc).__name__,'error':str(exc)});raise
