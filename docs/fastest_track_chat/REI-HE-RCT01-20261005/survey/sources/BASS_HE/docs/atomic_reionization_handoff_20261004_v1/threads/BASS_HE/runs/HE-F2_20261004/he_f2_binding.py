"""Compile source-preserving HE-F2 offers against the observed FT03 policy.

This is an offline atomic handoff, never a consumer admission engine. It does not
execute the consumer RHS, multiply densities, choose a photon closure, enable a
reaction, or re-run any previous scientific campaign. Exit 0 means the report was
successfully produced; its explicit state can still be BLOCKED_CONSUMER_CONTRACT.
"""
from __future__ import annotations
import argparse
import ast
import copy
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor'))
from bass_he_atomic_export import export_packet, validate_packet, loads_strict
from bass_he_atomic_export._io import write_json_create_only

HE_COMMIT = 'cbc654cf6037a4a0dad2f60fb138964cfff62ada'
REI_COMMIT = '64bc3aa0871bb324817afd3d36db018dd34181cf'
REACTION = 'R_CX:He2+_H1s:He+1s_H+'
UNSELECTED = 'UNRESOLVED_RCT_CLOSURE_NOT_SELECTED'


def number(x: Any) -> Fraction:
    if isinstance(x, bool) or not isinstance(x, (str, int, float, Decimal)):
        raise ValueError('FINITE_DECIMAL_NUMBER_REQUIRED')
    try:
        d = Decimal(str(x))
        if not d.is_finite():
            raise ValueError('FINITE_DECIMAL_NUMBER_REQUIRED')
        return Fraction(d)
    except (ArithmeticError, ValueError) as exc:
        raise ValueError('FINITE_DECIMAL_NUMBER_REQUIRED') from exc


def token(x: Fraction) -> str:
    with localcontext() as ctx:
        ctx.prec = 40
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def interval(x: Any) -> tuple[Fraction, Fraction]:
    if not isinstance(x, (list, tuple)) or len(x) != 2:
        raise ValueError('ORDERED_FINITE_INTERVAL_REQUIRED')
    a, b = map(number, x)
    if a > b:
        raise ValueError('ORDERED_FINITE_INTERVAL_REQUIRED')
    return a, b


def intersection(a: Any, b: Any) -> list[str] | None:
    alo, ahi = interval(a)
    blo, bhi = interval(b)
    lo, hi = max(alo, blo), min(ahi, bhi)
    return None if lo > hi else [token(lo), token(hi)]


def canonical_hash(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()


def provider_candidate(packet: dict[str, Any]) -> dict[str, Any]:
    """Adapt a validated thermal-rate view to the consumer's actual research schema.

    The schema does not support event_count_coefficients as observable_kind. A
    count packet therefore cannot be silently relabelled as a rate record. The
    stoichiometric view is exported separately in REACTION_BINDING.json.
    """
    validate_packet(packet)
    if packet['request']['quantity'] != 'thermal_rate':
        raise ValueError('THERMAL_RATE_VIEW_REQUIRED')
    p = copy.deepcopy(packet)
    src, r = p['source'], p['records'][0]
    if p['reaction_id'] != REACTION:
        raise ValueError('UNSUPPORTED_REACTION')
    lo, hi = interval(r['reported_domain_K'])
    url = src.get('rate_source_url', 'https://doi.org/' + src.get('rate_source_doi', ''))
    kind = r.get('rate_semantics', 'LITERATURE_CONSTANT_FIT_NOT_TRUE_RATE_CERTIFICATE')
    return {
        'provider_id': src['source_id'], 'process_id': REACTION,
        'observable_kind': 'thermal_rate',
        'source_identity': {
            'url': url, 'version': src['source_id'],
            'read_status': 'HE_F1_PINNED_IMPLEMENTATION_AND_SOURCE_RECORD',
            'sha256': src['core_sha256'], 'sha256_kind': 'provider_code_not_paper',
            'supplier_commit': HE_COMMIT,
            'b3_canonical_packet_sha256': canonical_hash(p)},
        'units': r['unit'], 'frame': 'local_gas_rest_frame',
        'particle_distribution': r['distribution'],
        'domain': {'variable': 'temperature', 'units': 'K',
                   'minimum': int(lo), 'maximum': int(hi),
                   'status': 'source_supported',
                   'status_ceiling': 'reported_fit_or_nominal_prescription_window_only'},
        'species_in': {'HI': 1, 'HeIII': 1},
        'species_out': {'HII': 1, 'HeII': 1},
        'density_prefactor': 'n_HI * n_HeIII',
        'density_already_applied': False,
        'branches_and_floors': [{'outside_domain': 'ERROR_NO_CLAMP_NO_EXTRAPOLATION'}],
        'uncertainty': {'kind': 'unresolved_source_and_closure',
                        'rigorous_physical_bound': None,
                        'fit_error_bound': r['fit_error_bound'],
                        'source_uncertainty': r['source_uncertainty']},
        'energy_photon_closure': {'status': 'unresolved', 'owner': 'rei_bianchi',
                                  'photon_number_per_event_in_selected_W82_scenario': 1,
                                  'photon_energy_moment': r['photon_energy_moment'],
                                  'heat_moment': r['heat_moment'],
                                  'recoil_moment': r['recoil_moment']},
        'implementation_status': 'SUPPLIER_RECORD_ADAPTER_ONLY_NOT_CONSUMER_EXECUTION',
        'consumer_admission': False, 'closure_id': UNSELECTED,
        'coefficient': {'token': r['rate_token'], 'semantics': kind},
        'coefficient_samples': [{'T_K': x['T_K'], 'rate_token': x['rate_token']}
                                for x in p['records']],
        'b3_packet': p, 'alternatives_are_additive': False,
        'physical_accuracy_certified': False,
        'schema_validation_is_consumer_acceptance': False,
    }


def assess_consumer(candidate: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    """Report coverage and disabled state. This function never enables a process."""
    domain = candidate['domain']
    src = [domain['minimum'], domain['maximum']]
    guard = policy['T_guard_K']
    overlap = intersection(src, guard)
    s0, s1 = interval(src)
    g0, g1 = interval(guard)
    covered = s0 <= g0 and g1 <= s1
    disabled = 'charge_exchange' in policy['disabled_effective_channels']
    blockers = ['MISSING_CANONICAL_REI_SCOPE_AND_PROVIDER_INSTANCE', 'RCT_CLOSURE_NOT_SELECTED']
    if disabled:
        blockers.append('PROCESS_EXPLICITLY_EXCLUDED')
    else:
        blockers.append('NO_EXPLICIT_RCT_ENABLEMENT_IN_OBSERVED_POLICY')
    if not covered:
        blockers.append('SOURCE_DOMAIN_DOES_NOT_COVER_CONSUMER_GUARD')
    return {'provider_id': candidate['provider_id'], 'consumer_model_id': policy['id'],
            'consumer_commit': REI_COMMIT,
            'process_policy': ('EXPLICITLY_DISABLED_IN_CURRENT_CONSUMER' if disabled
                               else 'NOT_EXPLICITLY_SELECTED'),
            'source_domain_K': [token(s0), token(s1)],
            'consumer_guard_K': [token(g0), token(g1)],
            'source_domain_covers_consumer_guard': covered,
            'overlap_K': overlap, 'blockers': blockers,
            'action': 'NO_INJECTION', 'replacement_rate': None,
            'consumer_admission': False,
            'disabled_is_source_zero': False,
            'recombination_escape_auto_applies_to_RCT': False}


def reaction_ledger(helium_per_h: Any, thresholds: dict[str, Any]) -> dict[str, Any]:
    """Exact event and fraction-normalization algebra, without density evaluation.

    Let r_H = k*n_H*y*(1-x_HII)*x_HeIII, where y=n_He/n_H>0.
    dx/dt = r_H*(1,1/y,-1/y), in consumer proper time. This compiler outputs
    that mapping only; it does not evaluate r_H or change the consumer state.
    """
    y = number(helium_per_h)
    if y <= 0 or set(thresholds) != {'HI', 'HeI', 'HeII'}:
        raise ValueError('POSITIVE_ABUNDANCE_AND_EXPLICIT_THRESHOLDS_REQUIRED')
    h, he1, he2 = (number(thresholds[k]) for k in ('HI','HeI','HeII'))
    if min(h, he1, he2) <= 0:
        raise ValueError('POSITIVE_BINDING_THRESHOLDS_REQUIRED')
    nu = [-1,1,0,1,-1,0]
    weights = {'H':[1,1,0,0,0,0], 'He':[0,0,1,1,1,0],
               'charge':[0,1,0,1,2,-1]}
    w = [Fraction(0),h,Fraction(0),he1,he1+he2,Fraction(0)]
    q = sum(a*b for a,b in zip(w,nu))
    return {'reaction_id': REACTION, 'supplier_commit': HE_COMMIT,
            'species_order':['HI','HII','HeI','HeII','HeIII','e'],
            'stoichiometry': nu,
            'conservation_dots':{k:sum(a*b for a,b in zip(v,nu)) for k,v in weights.items()},
            'fraction_order':['x_HII','x_HeII','x_HeIII'],
            'fraction_pushforward_per_event_per_H':['1',str(1/y),str(-1/y)],
            'helium_abundance_nHe_over_nH': str(y),
            'event_rate_per_H_formula':'r_H = k * n_H * y * (1-x_HII) * x_HeIII',
            'density_multiplication_owner':'rei_bianchi',
            'density_and_time_scaling_applied':False,
            'direct_electron_delta':0, 'photon_birth_per_RCT_scenario':1,
            'primary_absorption_from_RCT_birth':None,
            'chemical_energy_change_eV':token(q),
            'Q_binding_eV':token(-q),
            'energy_model_id':'FT03_BINDING_CHI_LITERALS_NOT_AN_RCT_CLOSURE',
            'photon_energy_eV':None, 'prompt_heat_eV':None,
            'energy_ownership_equation':'Delta_E_thermal + Delta_E_primary + Delta_E_escape + Delta_E_other = Q_binding',
            'energy_units':'eV per event; multiply r_H once for eV per H per proper second',
            'implementation_applies_event':False,
            'consumer_enabled':False, 'binding_state':'ATOMIC_OFFER_NOT_CONSUMER_ACCEPTANCE'}


def verify_inputs(root: Path) -> dict[str, Any]:
    lock = loads_strict((root/'INPUT_LOCK.json').read_bytes())
    for row in lock['files']:
        rel = Path(row['path'])
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('INVALID_LOCK_PATH')
        p = root / rel
        if p.is_symlink():
            raise ValueError('INPUT_IDENTITY_MISMATCH: symlink')
        b = p.read_bytes()
        if len(b) != row['bytes'] or hashlib.sha256(b).hexdigest() != row['sha256']:
            raise ValueError('INPUT_IDENTITY_MISMATCH: '+str(rel))
    return lock


def build_products(root: str | Path) -> dict[str, Any]:
    root = Path(root)
    verify_inputs(root)
    policy = loads_strict((root/'inputs/rei_ft03/MODEL_POLICY.json').read_bytes())
    fixture = loads_strict((root/'inputs/rei_ft03/CONTROLLED_FIXTURE.json').read_bytes())
    chi = fixture['constants']['threshold_eV']
    # Recover literals, not imported executable consumer code or a new history run.
    tree = ast.parse((root/'inputs/rei_ft03/closure_model.py').read_text())
    found = [n.value.args[0] for n in tree.body if isinstance(n,ast.Assign)
             and any(isinstance(t,ast.Name) and t.id=='CHI' for t in n.targets)
             and isinstance(n.value,ast.Call)]
    if len(found)!=1 or list(map(number,ast.literal_eval(found[0]))) != [number(chi[s]) for s in ('HI','HeI','HeII')]:
        raise ValueError('CONSUMER_BINDING_THRESHOLDS_DO_NOT_MATCH')
    candidates = []
    for source in ('GM25','KF96'):
        req = loads_strict((root/'inputs'/f'{source}_REQUEST.json').read_bytes())
        req.update(unit='cm3 s-1',quantity='thermal_rate')
        candidates.append(provider_candidate(export_packet(req)))
    checks = [assess_consumer(c,policy) for c in candidates]
    pair = intersection(checks[0]['source_domain_K'],checks[1]['source_domain_K'])
    paired_current = intersection(pair,policy['T_guard_K']) if pair is not None else None
    ledger = reaction_ledger(policy['initial']['n_He_over_n_H'],chi)
    ledger.update(consumer_model_id=policy['id'], consumer_commit=REI_COMMIT,
                  consumer_emission_note=policy['recombination_emission'])
    return {
      'PROVIDER_CANDIDATES.json':{'schema':'bass-he.consumer-candidates.v1',
                                'records':candidates,'not_additive':True,
                                'target_schema':'AtomicProviderRecordV1 research schema; not Rust runtime'},
      'REACTION_BINDING.json':ledger,
      'SOURCE_DOMAIN_ASSESSMENT.json':{'consumer_model_id':policy['id'],
                                      'source_assessments':checks,
                                      'pair_common_domain_K':pair,
                                      'paired_intersection_with_current_consumer_K':paired_current,
                                      'consumer_initial_T_K':policy['initial']['T_K'],
                                      'new_physical_evaluations':0},
      'CONSUMER_LEDGER_ACCEPTANCE.json':{
          'task_id':'HE-F2','state':'BLOCKED_CONSUMER_CONTRACT',
          'consumer_acceptance_issued':False, 'atomic_offer_generated':True,
          'consumer_model_id':policy['id'],'consumer_commit':REI_COMMIT,
          'external_dependencies':{
              'REI_SCOPE_LOCK':{'alias':'REI-F00','resolved':False,
                               'expected_path':'docs/atomic_reionization_handoff_20261004_v1/runtime_inputs',
                               'observation':'404 at consumer commit'},
              'REI_PROVIDER_CONTRACT':{'alias':'REI-F01','resolved':False,
                                      'expected_path':'rust/rei_microphysics/src/atomic_provider.rs',
                                      'observation':'404 at consumer commit; research JSON schema is not an admitted instance'}},
          'blockers':['CANONICAL_CONSUMER_CONTRACTS_NOT_RECOVERED',
                      'CURRENT_MODEL_EXPLICITLY_EXCLUDES_CHARGE_EXCHANGE',
                      'GM25_KF96_PAIRED_DOMAIN_DISJOINT_FROM_CURRENT_MODEL',
                      'RCT_ENERGY_PHOTON_CLOSURE_NOT_SELECTED'],
          'source_checks':checks,'paired_campaign_ready':False,
          'baseline_may_continue':True, 'consumer_changed':False,
          'source_defaults_changed':False,'legacy_reopen_triggered':False,
          'energy_model_choice_required_from':'rei_bianchi owner',
          'next_minimum_input':['owner-authored scope/model selection and whether RCT is included',
                                'single-source or paired-source domain plus out-of-domain policy',
                                'RCT photon/thermal/escape/absorption closure and ownership',
                                'actual provider instance/runtime adapter identity'],
          'possible_owner_decisions':['keep RCT excluded, explicitly defer optional REI-F09',
                                      'create a separate in-domain RCT sensitivity model with its own closure',
                                      'provide an independently supported source-domain extension'],
          'scientific_PROMOTE':'HOLD','EOR_THEORY_GATE':'NOT_SATISFIED','Eq55':'NOT_RUN'}}


def write_products(root: str | Path, out: str | Path) -> dict[str, Any]:
    out = Path(out)
    if out.exists() or out.is_symlink():
        raise FileExistsError(str(out))
    products = build_products(root)
    out.mkdir(exist_ok=False)
    for name, content in products.items():
        write_json_create_only(out/name,content)
    return products


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args(argv)
    try:
        products=write_products(args.root,args.out)
        print(json.dumps({'compiler_exit':'SUCCESS',
                          'HE_F2_state':products['CONSUMER_LEDGER_ACCEPTANCE.json']['state'],
                          'consumer_admission':False}))
        return 0
    except (ValueError,OSError) as exc:
        print(f'{type(exc).__name__}: {exc}',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
