#!/usr/bin/env python3
"""REI F4 BASS193 source-owned finite-net F/J, electron and conditional thermal ports.

No new cosmological IVP: 193 original BASS snapshots and already integrated PR287
causal first-flight arrays. The conditional Li II 2E1 all-singlet scenario is NOT
licensed as actual heating or an observational prediction. No REI17 native Rust.
"""
from __future__ import annotations
import csv, hashlib, io, json, os, pathlib, sys, zipfile, importlib.util
import numpy as np
from scipy.integrate import simpson

ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=ROOT/'source'
RES=ROOT/'results'
EV_J=1.602176634e-19
KB_J_K=1.380649e-23
KB_EV_K=KB_J_K/EV_J
C=299792458.0
ARCH={
'REI_F4_BASS193_SELFCONSISTENT_20261030_FULL.zip':'df871a18f297da15d05a5dadbad55e2aa29571217ad9136d9c4826921d1a11db',
'REI_F4_BASS193_COMMON_BATH_RATE_DELTA_20261030_FULL.zip':'58815601324ade9871077236dccee25cbbfe126141ee9af3d7da9ed9ffdb56f2',
'REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030_FULL.zip':'cb7593462c228278c3bdea79338271a1c1518b1b32632d4806aea6ca1ce683ef',
}
TRAJ='37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086'
BASE='REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030/'
COMMON='rei_f4_bass193_common_bath_20261030/'
S21=np.r_[np.arange(13),np.arange(17,21)]
S6=np.arange(13,17)
HHE=np.array([1,2,10,11,12])


def digest(raw:bytes):return hashlib.sha256(raw).hexdigest()

def load_archive(name):
    p=SRC/name
    raw=p.read_bytes()
    if digest(raw)!=ARCH[name]:raise ValueError('SOURCE_ARCHIVE_SHA256:'+name)
    z=zipfile.ZipFile(io.BytesIO(raw))
    if z.testzip() is not None:raise ValueError('SOURCE_ARCHIVE_CRC:'+name)
    for n in z.namelist():
        q=pathlib.PurePosixPath(n)
        if q.is_absolute() or '..' in q.parts:raise ValueError('SOURCE_ARCHIVE_PATH:'+n)
    return z

def read_csv(z,path):return list(csv.DictReader(io.StringIO(z.read(path).decode('utf8'))))

def net_and_trajectory(z):
    """Load original owner Python source byte-identical with its locked numerical projections."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d=pathlib.Path(td)
        for p in ('code/native_full_rate.py','source/BASS_ATOMIC_NETWORK.py','source/BASS_ATOMIC_MODEL.json',
                  'source/COEFF_NUMERIC_PROJECTION.json','source/P19_13_KNOTS.json','source/REI_SAVED7.json'):
            f=d/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(p))
        spec=importlib.util.spec_from_file_location('original_rei_bass193_owner',d/'code/native_full_rate.py')
        owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
        owner.source_manifest_check()
        net=owner.new_native_network()
        with zipfile.ZipFile(io.BytesIO(z.read('source/PR276_IMMUTABLE_FULL.zip'))) as donor:
            if donor.testzip() is not None:raise ValueError('NESTED_SOURCE_CRC')
        raw=z.read('trajectory.npz')
        if digest(raw)!=TRAJ:raise ValueError('TRAJ_SHA256')
        with np.load(io.BytesIO(raw),allow_pickle=False) as n:
            trajectory={key:n[key].copy() for key in n.files}
        rei=json.loads((d/'source/REI_SAVED7.json').read_text())
    return net,trajectory,rei

def calc():
    bz=load_archive('REI_F4_BASS193_SELFCONSISTENT_20261030_FULL.zip')
    cz=load_archive('REI_F4_BASS193_COMMON_BATH_RATE_DELTA_20261030_FULL.zip')
    pz=load_archive('REI_F4_LII_2E1_CAUSAL_REDSHIFT_20261030_FULL.zip')
    try:
        net,s,rei=net_and_trajectory(bz)
        x=s['x'];z=s['z'];Y=s['Y'];q=np.asarray(net.q,float);A=np.asarray(net.A,float)
        if Y.shape!=(193,21) or len(x)!=193 or not np.all(np.diff(x)>0):raise ValueError('BASS_193_SHAPE')
        di={str(n):s['diagnostics'][:,i] for i,n in enumerate(s['diagnostic_names'])}
        H=di['H'];nb=di['nb_m3'];T=di['T_K'];uv=di['uv_scale'];t=di['elapsed_s']
        if not(np.all(H>0) and np.all(nb>0) and np.all(T>0) and np.all(np.diff(t)>0)):
            raise ValueError('BAD_OWNER_BACKGROUND')
        nb_a3=nb*di['a']**3
        if np.max(abs(nb_a3/nb_a3[0]-1))>2.e-13:raise AssertionError('NB_SCALE_A3')
        xe=Y@q
        if np.max(abs(nb*xe-di['ne_m3']))>2.e-12:raise AssertionError('NE_OWNER_DIAGNOSTIC')
        if np.max(abs(A@Y.T-1))>4e-13:raise AssertionError('BARYON_MASS_BUDGET')
        bath_rows=[];F=[];J=[];F17=[];J17=[];J_UV=[]
        absF=0.;absJ=0.;absEnergy=0.;max_Af=0.;max_AJ=0.
        original=np.load(io.BytesIO(cz.read(COMMON+'results/HHE_CHEMICAL_F_J_STATIC_193.npz')),allow_pickle=False)
        if np.max(abs(original['x']-x))>1e-13:raise AssertionError('BASS_REI_ARCHIVE_CLOCK_GRID')
        for k in range(193):
            rates=net.rates(T[k],uv[k]);r=net.evaluate(Y[k],T[k],uv[k],nb[k]);
            dY=np.asarray(r['dY_dt'],float);jac=np.asarray(r['jac'],float)
            F.append(dY);J.append(jac);F17.append(dY[S21]);J17.append(jac[np.ix_(S21,S21)])
            # BASS-only 17-state projection: preserve all 21-state free-electron bath.
            ne17=nb[k]*float(q[S21]@Y[k,S21]);Gne=rates['Gne'];G0=rates['G0'];D=rates['D']
            M_uu=Gne[np.ix_(S21,S21)];G_uu=(G0+D)[np.ix_(S21,S21)]
            keep=G_uu@Y[k,S21]+ne17*(M_uu@Y[k,S21]);
            j_keep=G_uu+ne17*M_uu+nb[k]*np.outer(M_uu@Y[k,S21],q[S21]);
            delta_charge=(q[S6]@Y[k,S6]);
            delta_f=dY[S21]-keep
            expected_f=nb[k]*delta_charge*(M_uu@Y[k,S21])
            residual=np.max(abs(delta_f-expected_f));absF=max(absF,float(residual))
            expected_j=nb[k]*delta_charge*M_uu
            residual_j=np.max(abs(jac[np.ix_(S21,S21)]-j_keep-expected_j));absJ=max(absJ,float(residual_j))
            # The off-manifold 17x4 Jacobian cross-block is charge-coupled.
            Ju_v=jac[np.ix_(S21,S6)]
            pred=nb[k]*np.outer(M_uu@Y[k,S21],q[S6])
            if np.max(abs(Ju_v-pred))>1e-25:raise AssertionError('J_UV_COUPLING')
            J_UV.append(Ju_v)
            ef0=abs(r['photo_absorbed_power_W_m3']-di['photo_absorbed_W_m3'][k]);
            ef1=abs(r['primary_kinetic_power_W_m3']-di['primary_photoelectron_W_m3'][k]);
            absEnergy=max(absEnergy,float(max(ef0,ef1)))
            rhhe=r['dY_dt'][HHE];jhhe=jac[np.ix_(HHE,HHE)]
            absF=max(absF,float(np.max(abs(rhhe-original['F_BASS_HHe'][k]))))
            absJ=max(absJ,float(np.max(abs(jhhe-original['J_BASS_HHe'][k]))))
            max_Af=max(max_Af,abs(float(A@dY)));max_AJ=max(max_AJ,float(np.max(abs(A@jac))))
            N=float(np.sum(Y[k])+xe[k]);n_he_ref=float(np.sum(Y[k,[1,2]]))
            Cv_per_b=1.5*KB_J_K*N
            qX=float(q@dY)
            photo_rhs=np.asarray(r['photo_rhs'],float)
            bath_rows.append({
              'epoch':k,'z':float(z[k]),'x':float(x[k]),'elapsed_s':float(t[k]),'H_s':float(H[k]),
              'b_bianchi':float(di['b'][k]),'nb_m3':float(nb[k]),'T_K':float(T[k]),'UV_scale':float(uv[k]),
              'n_H1_reference_over_nb':n_he_ref,'nuclei_per_baryon':float(np.sum(Y[k])),
              'xe_BASS_per_baryon':float(xe[k]),'ne_m3':float(r['ne']),
              'N_thermal_particles_per_baryon':N,'Cv_J_per_baryon_per_K':Cv_per_b,
              'F_e_native_per_baryon_s':qX,
              'F_e_photo_per_baryon_s':float(q@photo_rhs),
              'F_e_RR_DR_per_baryon_s':float(q@(r['rr_rhs']+r['dr_rhs'])),
              'F_e_decay_per_baryon_s':float(q@r['decay_rhs']),
              'native_photo_absorbed_eV_per_baryon_s':float(r['photo_absorbed_power_W_m3']/nb[k]/EV_J),
              'native_primary_kinetic_eV_per_baryon_s':float(r['primary_kinetic_power_W_m3']/nb[k]/EV_J),
              'native_unresolved_core_eV_per_baryon_s':float(r['unresolved_core_power_W_m3']/nb[k]/EV_J),
              'native_primary_max_thermal_port_K_per_s':float(r['primary_kinetic_power_W_m3']/nb[k]/Cv_per_b),
              'source_required_gas_input_eV_per_baryon_s':float(di['net_required_gas_input_W_m3'][k]/nb[k]/EV_J),
              'REI_restricted_HHe_charge_rate_defect_per_baryon_s':float((original['F_REI_HHe_only_ne'][k]-original['F_BASS_HHe'][k]) @ q[HHE]),
              'BASS21_minus_BASS17_Fmax_per_baryon_s':float(np.max(abs(delta_f))),
              'BASS21_minus_BASS17_Jmax_per_s':float(np.max(abs(jac[np.ix_(S21,S21)]-j_keep))),
              'BASS21_BASS17_cross_J17x4_max_per_s':float(np.max(abs(Ju_v))),
              'BASS_Li6_removed_xe':float(delta_charge),
              'background_K_native':'UNBOUND',
            })
        F=np.asarray(F);J=np.asarray(J)
        if max_Af>4e-21 or max_AJ>5e-18:raise AssertionError('BARYON_STOICHIOMETRIC_DRIFT')
        if absEnergy>1.e-30:raise AssertionError('OWNER_POWER_MISMATCH')
        if absF>2.e-24 or absJ>1.e-24:raise AssertionError('HHE_FJ_PARITY_OR_LI6_PROJECTION')
        # Causal PR287 emissions were propagated on prescribed BASS193 gas (conditional all-singlet).
        ar=read_csv(pz,BASE+'results/ABSORPTION_ARRIVALS_192.csv')
        em=read_csv(pz,BASE+'results/EMISSIONS_193.csv')
        summ=json.loads(pz.read(BASE+'results/RESULT.json'))
        if len(ar)!=192 or len(em)!=193:raise ValueError('CAUSAL_EPOCH_SHAPE')
        arrivals=[]
        fields=['incoming_integrated_H_I_per_baryon','incoming_integrated_He_I_per_baryon',
                'incoming_integrated_He_II_per_baryon','incoming_integrated_Li_I_per_baryon']
        for i,row in enumerate(ar):
            if int(row['first_absorption_interval'])!=i:raise AssertionError('ARRIVAL_INDEX')
            tt=float(t[i+1]-t[i]);
            ni=.5*(bath_rows[i]['N_thermal_particles_per_baryon']+bath_rows[i+1]['N_thermal_particles_per_baryon'])
            cv=1.5*KB_EV_K*ni
            count=float(sum(float(row[f]) for f in fields))
            kinetic=float(row['primary_electron_eV_per_baryon']);binding=float(row['binding_eV_per_baryon'])
            if min(count,kinetic,binding)<-1.e-25:raise AssertionError('NEGATIVE_FIRSTFLIGHT')
            eint=count/tt; rate_e=kinetic/tt; rate_bind=binding/tt
            arr_z=float(row['arrival_z_low']);
            if abs(arr_z-z[i+1])>1.e-9:raise AssertionError('CAUSAL_CLOCK_MATCH')
            arrivals.append({
             'arrival_interval':i,'z_high':float(z[i]),'z_low':float(z[i+1]),'z_mid':float(np.sqrt((1+z[i])*(1+z[i+1]))-1),
             'x_mid':float(.5*(x[i]+x[i+1])),'proper_interval_s':tt,
             'H_mid_s':float(np.sqrt(H[i]*H[i+1])), 'nb_mid_m3':float(np.sqrt(nb[i]*nb[i+1])),
             'T_mid_K':float(.5*(T[i]+T[i+1])),
             'xe_mid':float(.5*(xe[i]+xe[i+1])),
             'N_thermal_mid':ni,'Cv_eV_per_baryon_per_K':cv,
             'conditional_absorptions_per_baryon':count,
             'conditional_primary_e_eV_per_baryon':kinetic,
             'conditional_binding_eV_per_baryon':binding,
             'conditional_first_abs_H_I_per_baryon':float(row[fields[0]]),
             'conditional_first_abs_He_I_per_baryon':float(row[fields[1]]),
             'conditional_first_abs_He_II_per_baryon':float(row[fields[2]]),
             'conditional_first_abs_Li_I_per_baryon':float(row[fields[3]]),
             'conditional_electron_count_source_per_baryon_s':eint,
             'conditional_primary_kinetic_source_eV_per_baryon_s':rate_e,
             'conditional_binding_source_eV_per_baryon_s':rate_bind,
             'conditional_temperature_heat_operator_K_per_s_at_efficiency_1':rate_e/cv,
             'conditional_temperature_number_operator_K_per_s_if_electrons_thermalize':-float(.5*(T[i]+T[i+1]))*eint/ni,
             'actual_deposition_efficiency':'UNBOUND',
             'background_source_clock':'BASS193_SAVED_ELAPSED_PROPER_SECONDS',
            })
        # Direct measured 7 REI rows have separate 17-component history and clock, not shared IC.
        cross=[]
        for r in rei['rows']:
            zz=float(r['z']); tr=float(r['elapsed_proper_s'])
            tb=float(np.interp(zz,z[::-1],t[::-1]))
            f_h=float(r['y'][1]+r['y'][2])
            cross.append({'z_REI':zz,'t_REI_saved_s':tr,'t_BASS_interpolated_s':tb,
                          'z_matched_relative_time_difference':(tr-tb)/tb,
                          'REI_saved_H1_total_per_nHref':f_h,
                          'BASS_H1_total_per_nb':float(np.interp(zz,z[::-1],[b['n_H1_reference_over_nb'] for b in bath_rows][::-1])),
                          'same_initial_condition_or_background':'NOT_ESTABLISHED'})
        def sumkey(k):return float(sum(v[k] for v in arrivals))
        totals={k:sumkey(k) for k in ['conditional_absorptions_per_baryon','conditional_primary_e_eV_per_baryon','conditional_binding_eV_per_baryon']}
        # Compare independent original integrated causal terminal event summary if exposed, else check emissions weighted.
        e_sum=sum(float(r['conditional_event_source_count_per_baryon']) for r in em)
        if e_sum<0 or not np.isfinite(e_sum):raise AssertionError('INVALID_SOURCE_EPOCHS')
        if totals['conditional_absorptions_per_baryon']>2*e_sum*(1+1e-10):raise AssertionError('MORE_THAN_TWO_PHOTONS')
        # Existing PR287 source ledger is the ground truth for arrived electron/energy totals.
        origsums=summ.get('source_integrated',{})
        if origsums:print('SOURCE_SUMMARY_KEYS',list(origsums))
        out_arrays={'x':x,'z':z,'F21_per_baryon_s':F,'J21_per_s':J,
                    'F17_BASS_restriction_per_baryon_s':np.array(F17),
                    'J17_BASS_restriction_per_s':np.array(J17),'J17xLi6_cross_per_s':np.array(J_UV),
                    'q21':q,'A21':A,'index_REI17_BASS_projection':S21,'index_Li6':S6}
        results={
         'schema':'REI_F4_BASS193_FJ_ELECTRON_THERMAL_CLOCK_BRIDGE_V1',
         'science_node':'REI_F4_COMMON_FJ_ELECTRON_THERMAL_CLOCK_BRIDGE_20261030',
         'input_sha256':ARCH,'trajectory_sha256':TRAJ,
         'provenance':{'chemistry':'BASS21 original native Python evaluate; 193 saved states, 21 chemistry species',
           'REI_comparison':'PR276 originally REI Grackle formula-translated HHe matched state, not native Rust/full17',
           'REI_saved7':'distinct original seven-state sampled 17-vector; no identical initial composition or common clock',
           'radiation':'PR287 original prescribed-gas 2E1 all-singlet conditional first-flight',
           'thermal':'instantaneous source-port coefficient only; no local secondary thermalization closure',
           'background':'native saved H,nb,T,b and elapsed proper time; anisotropic K/directional radiation unbound'},
         'counts':{'saved_epochs':193,'original_species':21,'BASS_restricted_17_species':17,
                   'native_F21_rows':193*21,'native_J21_entries':193*21*21,
                   'arrival_intervals':192,'REI_different_owner_comparisons':len(cross),'new_IVP':0},
         'independent_regression':{'max_HHe_F_and_projection_residual':absF,'max_HHe_J_and_projection_residual':absJ,
                                   'max_saved_power_density_residual_W_m3':absEnergy,
                                   'max_A_dot_F':max_Af,'max_A_dot_J':max_AJ,
                                   'nb_a3_rel_range':float(np.ptp(nb_a3)/nb_a3[0]),
                                   'max_ne_relative_saved_vs_native':float(np.max(np.abs((nb*xe-di['ne_m3'])/di['ne_m3']))),
                                   'max_temperature_port_efficiency':'NOT_COMPUTED'},
         'conditional_causal':{**totals,
           'max_local_electron_rate_per_baryon_s':float(max(a['conditional_electron_count_source_per_baryon_s'] for a in arrivals)),
           'max_local_primary_energy_rate_eV_per_baryon_s':float(max(a['conditional_primary_kinetic_source_eV_per_baryon_s'] for a in arrivals)),
           'max_local_heat_equivalent_K_per_s_for_efficiency_1':float(max(a['conditional_temperature_heat_operator_K_per_s_at_efficiency_1'] for a in arrivals)),
           'integral_of_instantaneous_temperature_operator_K_if_unit_deposit_no_dilution_or_cooling':float(sum(a['conditional_temperature_heat_operator_K_per_s_at_efficiency_1']*a['proper_interval_s'] for a in arrivals)),
           'actual_heat':'UNBOUND'},
         'native_source':{'BASS21_source_electrons_per_baryon_after_the_fact_exposure':float(simpson([r['F_e_native_per_baryon_s']/r['H_s'] for r in bath_rows],x=x)),
              'max_REI_HHe_rate_defect_per_baryon_s':float(max(abs(r['REI_restricted_HHe_charge_rate_defect_per_baryon_s']) for r in bath_rows)),
              'max_Li6_electron_pool_omission':float(max(abs(r['BASS_Li6_removed_xe']) for r in bath_rows)),
              'max_Li6_F17_defect_per_baryon_s':float(max(r['BASS21_minus_BASS17_Fmax_per_baryon_s'] for r in bath_rows)),
              'max_Li6_J17x4_cross_per_s':float(max(r['BASS21_BASS17_cross_J17x4_max_per_s'] for r in bath_rows))},
         'cross_history':{'REI_saved7_relative_clock_offset_range':[float(min(r['z_matched_relative_time_difference'] for r in cross)),float(max(r['z_matched_relative_time_difference'] for r in cross))],
                          'warning':'not equivalent initial conditions, no claim that offsets are coding errors'},
         'gates':{'WORKING_DAG':'33/88','CENTRAL_DAG':'28/88','PHYSICAL_FAST':'4/7','CANONICAL_DELTA':0,
                  'AUXILIARY_NODE':'1/1_SCOPED','F4':'PARTIAL','L4_ready':False,'PRODUCTION':'HOLD',
                  'NO_MORE_IVPS':True,'NO_MERGE':True,'NO_FORCE_PUSH':True,'NO_BUDGET_RESET':True,'AUTO_NEXT_NODE':False,
                  'REI17_FULL_OWNER':'UNBOUND','PHOTON_TRANSPORT_DIRECTION':'UNBOUND',
                  'ELECTRON_SECONDARY_ENERGY_DEPOSITION':'UNBOUND','N_HREF_CLOCK_COMMON':'UNBOUND',
                  'R6_C9_DISTINCT_AUTHOR':'NOT_RUN'}
        }
        return bath_rows,arrivals,cross,out_arrays,results
    finally:
        bz.close();cz.close();pz.close()

def write():
    bath,arrivals,cross,arr,result=calc();RES.mkdir(exist_ok=True)
    for f,rows in [('BASS21_FJ_ELECTRON_CLOCK_193.csv',bath),('CONDITIONAL_FIRSTFLIGHT_THERMAL_192.csv',arrivals),('REI7_BASS193_CLOCK_COMPARE.csv',cross)]:
        with (RES/f).open('w',newline='',encoding='utf8') as fp:
            w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    np.savez_compressed(RES/'SOURCE_FJ21_193.npz',**arr)
    (RES/'RESULT.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':write()
