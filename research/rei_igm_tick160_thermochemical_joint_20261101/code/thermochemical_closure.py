#!/usr/bin/env python3
"""Source-authentic REI IGM tick-160 H/He material-energy closure diagnostic.

No time integration, no new ionization model, no replacement for the locked
26-event full OTS/MPRK22(1)/SDIRK2 common-parent local-error certificate.
NIST ASD binding energies are a separate external atomic input. No CMB RT.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np

ARCHIVE_SHA256 = "48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7"
FROZEN_PARENT_SHA256 = "a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b"
STATE_ARRAY_SHA256 = "cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01"
SOURCE_RUN_ID = 41259585168
LANES = ("LOCAL_NEUTRAL_HAZARD_PRIMARY", "RECOMBINATION_WEIGHTED_AUDITOR", "SCRIPT_SELF_SHIELDING_AUDITOR")
N_NODES = 46080
Y_HE = 0.079  # independently inferred from both charge and thermal relations, see report
K_B_CGS = 1.380649e-16  # erg K^-1, SI-defined exact numerical constant
ERG_PER_EV = 1.602176634e-12  # erg eV^-1, SI-defined exact numerical constant
E_H_EV = 13.598434599702
E_HEI_EV = 24.587389011
E_HEII_EV = 54.4177655282
OLD_LOCAL_ERROR_LIMIT = 2.0e-4  # NOT a state-width admission criterion

FIELDS = ('node','x_HII_lo','x_HII_hi','x_HeII_lo','x_HeII_hi','x_HeIII_lo','x_HeIII_hi',
 'T_K_lo','T_K_hi','xe_per_H_lo','xe_per_H_hi','U_thermal_erg_per_H_lo','U_thermal_erg_per_H_hi')

def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def read_original(path: Path):
    raw = path.read_bytes()
    if digest(raw)!=ARCHIVE_SHA256:
        raise ValueError('PR320_ARTIFACT_SHA256_MISMATCH')
    with ZipFile(io.BytesIO(raw)) as archive:
        if archive.testzip() is not None: raise ValueError('PR320_ARTIFACT_CRC_FAILURE')
        meta=json.loads(archive.read('ORIGINAL_H_HE_T_ENERGY.json'))
        if meta['archive_sha256'] != FROZEN_PARENT_SHA256:raise ValueError('ORIGINAL_PARENT_SHA_MISMATCH')
        states=meta['physical_states']
        if len(states)!=3 or set(s['metadata']['lane'] for s in states)!=set(LANES):
            raise ValueError('SOURCE_LANES_MISMATCH')
        if any(s['state_array_sha256']!=STATE_ARRAY_SHA256 for s in states):
            raise ValueError('PARENT_SOURCE_STATE_IDENTITY_MISMATCH')
        datasets=[]
        for lane in LANES:
            name=f'NODEWISE_{lane}_46080_PHYSICAL.csv.gz'
            src=archive.read(name)
            with gzip.GzipFile(fileobj=io.BytesIO(src),mode='rb') as fh:
                reader=csv.DictReader(io.TextIOWrapper(fh,encoding='utf-8',newline=''))
                if not set(FIELDS).issubset(reader.fieldnames or []):raise ValueError('MISSING_ORIGINAL_COLUMNS')
                data={f:[] for f in FIELDS}
                for row in reader:
                    for f in FIELDS:data[f].append(float(row[f]) if f!='node' else int(row[f]))
            a={k:np.asarray(v,dtype=np.int64 if k=='node' else np.float64) for k,v in data.items()}
            if len(a['node']) != N_NODES or not np.array_equal(a['node'],np.arange(N_NODES)):
                raise ValueError('SOURCE_NODE_IDENTITY_MISMATCH')
            if any(not np.isfinite(a[k]).all() for k in FIELDS if k!='node'):
                raise ValueError('NONFINITE_SOURCE_FIELD')
            datasets.append(a)
        for other in datasets[1:]:
            for field in FIELDS:
                if not np.array_equal(datasets[0][field],other[field]):
                    raise ValueError('SOURCE_LANE_NUMERIC_MISMATCH:'+field)
        return datasets[0], meta

def mid(source,key):return (source[key+'_lo']+source[key+'_hi'])/2

def derived(source):
    xh=mid(source,'x_HII');x2=mid(source,'x_HeII');x3=mid(source,'x_HeIII')
    temp=mid(source,'T_K');xe=mid(source,'xe_per_H');uth=mid(source,'U_thermal_erg_per_H')
    if not (np.min(xh)>0 and np.max(xh)<1.000001 and np.min(x2)>0 and np.max(x2+x3)<1.00001 and np.min(x3)>0 and np.min(temp)>0 and np.min(uth)>0):
        raise ValueError('SOURCE_STATE_NOT_PHYSICAL')
    y_charge=(xe-xh)/(x2+2*x3)
    y_thermal=2*uth/(3*K_B_CGS*temp)-1-xe
    if max(np.max(np.abs(y_charge-Y_HE)),np.max(np.abs(y_thermal-Y_HE)))>5.e-8:
        raise ValueError('SOURCE_HE_ABUNDANCE_NOT_MATCHED')
    n=1+Y_HE+xe
    u_eV=uth/ERG_PER_EV
    ein=E_H_EV*xh+Y_HE*(E_HEI_EV*x2+(E_HEI_EV+E_HEII_EV)*x3)
    ein_lo=E_H_EV*source['x_HII_lo']+Y_HE*(E_HEI_EV*source['x_HeII_lo']+(E_HEI_EV+E_HEII_EV)*source['x_HeIII_lo'])
    ein_hi=E_H_EV*source['x_HII_hi']+Y_HE*(E_HEI_EV*source['x_HeII_hi']+(E_HEI_EV+E_HEII_EV)*source['x_HeIII_hi'])
    # Fixed total material energy E=U+Eion; derivative magnitudes of d ln T / d species.
    st_h=E_H_EV/u_eV+1/n
    st_heii=Y_HE*E_HEI_EV/u_eV+Y_HE/n
    st_heiii=Y_HE*(E_HEI_EV+E_HEII_EV)/u_eV+2*Y_HE/n
    st_he2_to_he3=Y_HE*E_HEII_EV/u_eV+Y_HE/n
    su_h=1/n;su_heii=Y_HE/n;su_heiii=2*Y_HE/n
    tlo=source['T_K_lo'];thi=source['T_K_hi']; ulo=source['U_thermal_erg_per_H_lo'];uhi=source['U_thermal_erg_per_H_hi']
    xe_lo=source['xe_per_H_lo'];xe_hi=source['xe_per_H_hi']
    # Monotone enclosure from independent U, xe intervals, deliberately discarding correlation.
    t_ind_lo=2*ulo/(3*K_B_CGS*(1+Y_HE+xe_hi))
    t_ind_hi=2*uhi/(3*K_B_CGS*(1+Y_HE+xe_lo))
    tol=5e-10
    if not (np.all(t_ind_lo<=tlo*(1+tol)) and np.all(t_ind_hi>=thi*(1-tol))):
        raise ValueError('LOST_PARENT_ENCLOSURE_VALIDITY')
    w_src=np.log(thi/tlo)
    w_ind=np.log(t_ind_hi/t_ind_lo)
    if not np.all(w_ind>=w_src-1e-11):raise ValueError('INDEPENDENT_WIDTH_NOT_ENCLOSING')
    closure_residual=np.abs(1.5*K_B_CGS*temp*n-uth)/uth
    return {
        'node':source['node'],'x_HII':xh,'x_HeII':x2,'x_HeIII':x3,'T_K':temp,'xe_per_H':xe,
        'y_He_by_charge':y_charge,'y_He_by_thermal':y_thermal,
        'U_thermal_eV_per_H':u_eV,'E_ion_eV_per_H':ein,'E_ion_lower_eV_per_H':ein_lo,'E_ion_upper_eV_per_H':ein_hi,
        'E_material_eV_per_H':u_eV+ein,'E_ion_over_U_thermal':ein/u_eV,
        'abs_dlnT_dx_HII_at_fixed_Ematerial':st_h,
        'abs_dlnT_dx_HeII_at_fixed_Ematerial':st_heii,
        'abs_dlnT_dx_HeIII_at_fixed_Ematerial':st_heiii,
        'abs_dlnT_dHeII_to_HeIII_at_fixed_Ematerial':st_he2_to_he3,
        'abs_dlnT_dx_HII_at_fixed_Uthermal':su_h,
        'abs_dlnT_dx_HeII_at_fixed_Uthermal':su_heii,
        'abs_dlnT_dx_HeIII_at_fixed_Uthermal':su_heiii,
        'parent_logT_width_from_source':w_src,'parent_logT_width_independent_U_xe':w_ind,
        'parent_width_inflation_ratio':w_ind/w_src,
        'T_from_marginal_lower_K':t_ind_lo,'T_from_marginal_upper_K':t_ind_hi,
        'thermal_closure_midpoint_relative_residual':closure_residual,
    }

def quant(arr):
    vals=np.quantile(np.asarray(arr,dtype=float),[0,.05,.50,.95,.99,1.])
    return dict(zip(['min','p05','p50','p95','p99','max'],map(float,vals)))

def summary(d, meta):
    keys=['y_He_by_charge','y_He_by_thermal','T_K','xe_per_H','U_thermal_eV_per_H','E_ion_eV_per_H',
          'E_ion_over_U_thermal','abs_dlnT_dx_HII_at_fixed_Ematerial',
          'abs_dlnT_dx_HeII_at_fixed_Ematerial','abs_dlnT_dx_HeIII_at_fixed_Ematerial',
          'abs_dlnT_dHeII_to_HeIII_at_fixed_Ematerial',
          'abs_dlnT_dx_HII_at_fixed_Uthermal','parent_logT_width_from_source',
          'parent_logT_width_independent_U_xe','parent_width_inflation_ratio']
    return {
      'source':'SOURCE_AUTHENTIC_PR320_TICK160_NODE_PHYSICS_CI_ARTIFACT',
      'source_ci_run':SOURCE_RUN_ID,'source_artifact_sha256':ARCHIVE_SHA256,
      'original_blocked_parent_sha256':FROZEN_PARENT_SHA256,
      'original_state_array_sha256':STATE_ARRAY_SHA256,
      'node_count_unique':N_NODES,'original_lanes':list(LANES),'lane_numeric_identity':'3_OF_3_EXACT',
      'original_accepted_tick':160,'total_interval_ticks':131072,'new_original_IVPs':0,
      'material_energy_scope':'H/He atomic ground-state ionization + ideal monatomic kinetic gas only; not full owner augmented photon/escape/gravity energy',
      'perturbation_scope':'local isochoric fixed-material-energy tangent; not an actual original 26-event time step',
      'source_effective_helium_ratio_He_over_H':Y_HE,
      'NIST_eV':{'HI':E_H_EV,'HeI':E_HEI_EV,'HeII':E_HEII_EV},
      'quantiles':{k:quant(d[k]) for k in keys},
      'max_helium_ratio_discrepancy':float(max(np.max(np.abs(d['y_He_by_charge']-Y_HE)),np.max(np.abs(d['y_He_by_thermal']-Y_HE)))),
      'max_thermal_midpoint_identity_relative_residual':float(np.max(d['thermal_closure_midpoint_relative_residual'])),
      'source_logT_parent_widths_above_original_local_error_numerical_scale':int(np.sum(d['parent_logT_width_from_source']>OLD_LOCAL_ERROR_LIMIT)),
      'independent_marginal_logT_parent_widths_above_original_local_error_numerical_scale':int(np.sum(d['parent_logT_width_independent_U_xe']>OLD_LOCAL_ERROR_LIMIT)),
      'WARNING_scale_not_a_width_gate':'2e-4 is original local-error acceptance bound, not a parent-state-width gate; these counts are only scale comparisons',
      'original_next_tick_local_error':2.1245050576368385e-4,'original_local_error_bound':OLD_LOCAL_ERROR_LIMIT,
      'central_dag':'28/88','working_dag':'33/88','physical_fast':'4/7','canonical_delta':0,
      'first_canonical_interval':'STILL_BLOCKED_MINIMUM_STEP',
      'new_joint_26event_step_correlation_certificate':'NOT_RUN',
    }

def deterministic_csv_gz(path:Path,d):
    keys=list(d.keys());path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('wb') as raw:
      with gzip.GzipFile(fileobj=raw,filename='',mode='wb',mtime=0,compresslevel=6) as gz:
        with io.TextIOWrapper(gz,encoding='utf-8',newline='') as txt:
          w=csv.writer(txt,lineterminator='\n');w.writerow(keys)
          for j in range(N_NODES):
            w.writerow([str(int(d[k][j])) if k=='node' else format(float(d[k][j]),'.17g') for k in keys])

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();source,meta=read_original(a.input);d=derived(source)
    a.output.mkdir(parents=True,exist_ok=True)
    out=a.output/'ORIGINAL_TICK160_46080_THERMOCHEMICAL_CLOSURE.csv.gz'
    deterministic_csv_gz(out,d)
    sum_path=a.output/'SCIENTIFIC_SUMMARY.json'
    sum_path.write_text(json.dumps(summary(d,meta),indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
    payload={'input_artifact_sha256':ARCHIVE_SHA256,'outputs':{x.name:{'size':x.stat().st_size,'sha256':digest(x.read_bytes())} for x in (out,sum_path)}}
    (a.output/'OUTPUT_SHA256_MANIFEST.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'nodes':N_NODES,'summary_file':str(sum_path),'outputs':payload['outputs']},sort_keys=True))

if __name__=='__main__':main()
