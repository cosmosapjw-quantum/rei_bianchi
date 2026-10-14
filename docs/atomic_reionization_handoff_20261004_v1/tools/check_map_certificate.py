"""Recompute the static FT03 proof using MPFI, without a production evaluator."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PACKET=ROOT/'docs/atomic_reionization_handoff_20261004_v1'


def main():
    p=argparse.ArgumentParser();p.add_argument('certificate',type=Path);p.add_argument('--receipt',required=True,type=Path);a=p.parse_args()
    source=PACKET/'runtime_returns/evidence/F04_certificate/checker.py'
    s=importlib.util.spec_from_file_location('independent_mpfi_checker',source);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    manifest=json.loads((ROOT/'runs/rei_fastest_v1/map_certificate/parent_manifest.json').read_text())
    constants=json.loads((PACKET/'runtime_inputs/ft03_map_constants.json').read_text())
    stored=json.loads(a.certificate.read_text());computed=m.check(stored['producer_data'],manifest,constants)
    # These are contractually deterministic generated proof coefficients/bounds,
    # not secondary estimates for a numerical-equivalence admission claim.
    assert computed==stored['bound_proof'], 'DETERMINISTIC_PROOF_RECOMPUTATION_MISMATCH'
    receipt={'status':'PASS','production_evaluator_called':False,'precision_bits':200,
             'model_id':computed['model_id'],'site_q':[x['q_weighted'] for x in computed['sites']],
             'local_bounds':computed['joint_full_half_local_bounds'],
             'max_public_width':max(x['public_width'] for x in computed['full_observables']+computed['two_half_observables']),
             'scope':'Pinned static FT03 numerical domain only, not original history or expanding S0',
             'scientific_admission':'HOLD','physical_fit_error':'NOT_MEASURED'}
    a.receipt.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))


if __name__=='__main__':
    main()
