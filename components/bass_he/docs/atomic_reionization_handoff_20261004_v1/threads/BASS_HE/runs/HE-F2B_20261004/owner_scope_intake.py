"""Bind the observed REI-F00 exclusion, not an atomic provider or RHS.

This finite-scope evidence reader never calls a rate supplier. Changed scope
requires a new binding rather than a fallback to a synthetic zero coefficient.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import sys
from typing import Any

MODEL = 'R1HomogeneousSuccessor_SYNTHETIC_HHE_3GROUP_V1'
INPUTS = ('rei_model_lock.json', 'closure_process_decision.json',
          'parent_and_lane_applicability.json')

class ContractError(ValueError):
    """Scope or source identity changed; current binding is inapplicable."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def strict_load(raw: bytes) -> Any:
    def pairs(items):
        d = {}
        for k, v in items:
            require(k not in d, 'DUPLICATE_JSON_KEY')
            d[k] = v
        return d
    def invalid(token):
        raise ContractError('NONFINITE_JSON_TOKEN: ' + token)
    obj = json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)
    json.dumps(obj, allow_nan=False)
    return obj


def load_verified(root: Path) -> list[dict]:
    """Check pinned source bytes before semantic reading; no network or import."""
    root = Path(root)
    lock = strict_load((root/'INPUT_LOCK.json').read_bytes())
    try:
        entries = lock['sources']
        require(len({x['path'] for x in entries}) == len(entries), 'DUPLICATE_INPUT_PATH')
        loaded = {}
        for item in entries:
            rel = PurePosixPath(item['path'])
            require(not rel.is_absolute() and '..' not in rel.parts, 'UNSAFE_INPUT_PATH')
            path = root/str(rel)
            require(not path.is_symlink() and path.resolve().is_relative_to(root.resolve()), 'INPUT_SYMLINK')
            b = path.read_bytes()
            require(len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'],
                    'INPUT_IDENTITY_MISMATCH: '+str(rel))
            if 'git_blob' in item:
                git = hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
                require(git==item['git_blob'], 'GIT_BLOB_IDENTITY_MISMATCH')
            loaded[str(rel)] = b
        return [strict_load(loaded['inputs/rei_f00/'+n]) for n in INPUTS]
    except (KeyError, TypeError) as exc:
        raise ContractError('INCOMPLETE_INPUT_LOCK') from exc


def assess(model: dict, closure: dict, lanes: dict) -> dict:
    """Accept only the published synthetic no-RCT scope. No future opt-in here."""
    try:
        require(all(x['task_id']=='REI-F00' and x['model_id']==MODEL for x in (model,closure,lanes)),
                'MODEL_IDENTITY_MISMATCH')
        require(model['schema']=='rei.model-lock.v1'
                and closure['schema']=='rei.closure-process-decision.v1'
                and lanes['schema']=='rei.parent-lane-applicability.v1', 'SCHEMA_MISMATCH')
        require(closure['processes']['He2_H_CX_RCT'] is False
                and closure['processes']['He2_H_CX_NRCT'] is False, 'NEW_PROCESS_SCOPE_REQUIRES_NEW_BINDING')
        z = model['coefficients']['He2_H_CX_cm3_s']
        require(type(z) in (int,float) and math.isfinite(z) and z==0, 'SYNTHETIC_EXCLUSION_INCONSISTENT')
        require(model['coefficients']['synthetic_temperature_independent'] is True,
                'NOT_THE_SYNTHETIC_FIXTURE')
        require(model['provider_selection']['physical_admitted'] is False
                and closure['physical_provider_admitted'] is False
                and model['scientific_admission']=='HOLD', 'ADMISSION_SCOPE_CHANGED')
        require(model['geometry']['kind']=='STATIC_HOMOGENEOUS_MINKOWSKI_LIMIT', 'GEOMETRY_SCOPE_CHANGED')
        require(model['units']['thermal_state']=='u_th erg cm^-3'
                and model['units']['photons']=='proper cm^-3'
                and model['units']['rates']=='cm^3 s^-1', 'UNITS_SCOPE_CHANGED')
        require(lanes['independent_state_dimension']==7
                and lanes['state_coordinates'][3]=='u_th_erg_cm3'
                and lanes['inherited_node_history']['applies_to_selected_model'] is False
                and lanes['inherited_node_history']['gates_closed_by_successor'] is False,
                'LANE_SCOPE_CHANGED')
    except (KeyError, TypeError, IndexError) as exc:
        raise ContractError('INCOMPLETE_OWNER_SCOPE') from exc
    return {
        'schema':'bass-he.he-f2b.owner-scope-binding.v1',
        'task_id':'HE-F2B', 'consumer_model_id':MODEL,
        'REI_SCOPE_LOCK':'RECOVERED_AND_BOUND',
        'baseline_disposition':'RCT_EXCLUDED_BY_OWNER_SCOPE',
        'baseline_source_dependency':'NOT_REQUIRED_WHILE_EXCLUDED',
        'baseline_claim':'Declared exclusion recognized; no claim of physical negligibility',
        'selected_atomic_source_id':None, 'atomic_rate_coefficient':None,
        'source_zero_meaning':'F00 synthetic process selection; not k_true=0 or missing-data fill',
        'atomic_evaluator_calls':0, 'density_product_applied':False, 'consumer_mutations':0,
        'consumer_energy_coordinate':model['units']['thermal_state'],
        'consumer_photon_coordinate':model['units']['photons'],
        'temperature_domain_K':None,
        'source_domain_assessment':'NOT_EVALUATED_FOR_EXCLUDED_PROCESS',
        'previous_FT03_guard_applies':False,
        'RCT_photon_energy_eV':None, 'RCT_prompt_heat_eV':None,
        'RCT_recoil_eV':None, 'RCT_closure_id':None,
        'recombination_escape_is_RCT_closure':False,
        'implementation_acceptance':True, 'actual_RCT_binding_accepted':False,
        'physical_source_admission':False, 'historical_gate_transfer':False,
        'full_physical_interval_verified':False,
        'optional_RCT_state':'WAIT_OWNER_OPT_IN_AND_PROVIDER_CONTRACT',
        'optional_REI_F09_cancelled':False,
        'nonblocking':'REI-F08 and independent REI chat work do not depend on RCT opt-in',
        'next_trigger':'Changed RCT scope/source/closure or actual consumer provider contract',
        'legacy_reopen_triggered':False,
    }


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    p.add_argument('--out', type=Path, required=True)
    args=p.parse_args(argv)
    try:
        result=assess(*load_verified(args.root))
        b=(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
        fd=os.open(args.out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o644)
        with os.fdopen(fd,'wb') as f:
            f.write(b); f.flush(); os.fsync(f.fileno())
        print(json.dumps({'binding_write':'SUCCESS','baseline':result['baseline_disposition'],
                          'actual_RCT_binding_accepted':False}))
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(f'{type(exc).__name__}: {exc}',file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
