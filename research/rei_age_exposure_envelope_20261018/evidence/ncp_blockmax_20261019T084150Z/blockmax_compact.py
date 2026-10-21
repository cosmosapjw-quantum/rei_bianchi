"""Compact, read-only summary of the q0 age64 block-max follow-up (no gate changes)."""
import hashlib, json, sys
from fractions import Fraction
from pathlib import Path

task = Path(sys.argv[1]); src = Path(sys.argv[2]); out = Path(sys.argv[3])
run = task / 'run'; att = run / 'results/age64/attempt001'; data = att / 'data'
J = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
frac = lambda f: Fraction(int(f['numerator']), int(f['denominator']))

receipt = J(att / 'RECEIPT.json'); ret = J(data / 'solver_return.json'); led = J(data / 'ledgers.json')
end = J(data / 'endpoint.json'); diag = J(run / 'PHOTON_LEDGER_DIAGNOSIS.json')
build = J(run / 'native/BUILD_RECEIPT.json'); prep = run / 'native/PREPARED_IDENTITY.json'
prior = J(src / 'evidence/AGE64_PHOTON_LEDGER_COMPACT_20261019.json')

recs = diag['intervals']['records']
deltas = []
for r in recs:
    b = r['budget']
    if b.get('local_delta_status') == 'AVAILABLE':
        d = frac(b['signed_local_delta_exact_fraction'])
        deltas.append((abs(d), r['event'], b['signed_local_delta_decimal80'], b['decimal80']['normalized']))
deltas.sort(reverse=True)
obs = diag['observations']['records']
obs_pass = [o['budget']['decimal80']['fixed_gate_pass'] for o in obs]
sides = sorted({o['side'] for o in obs})
L = end['ledgers']
timev = {}
for line in (task / 'TIME_V.txt').read_text().splitlines():
    k, _, v = line.strip().partition(': ')
    if k in ('Maximum resident set size (kbytes)', 'Elapsed (wall clock) time (h:mm:ss or m:ss)',
             'User time (seconds)', 'System time (seconds)', 'Exit status'):
        timev[k] = v
retry_events = sorted({e['event'] for e in ret['errors']})

result = dict(
    schema='rei.age64.block_max.compact.v1',
    case='q0 age64 reference, --error-norm block-max --rpc-mode binary64',
    command='bash scripts/run_accuracy_followup.sh "$REI_REPO" "$NEW_SCRATCH" age64-block-max',
    ncp_task=str(task), rei_repo=str(task / 'repo'), new_scratch=str(run),
    source_commit='18aae24bd1d102c50164bd6224a09ec5c4eaf45d',
    science_code_commit='db87456e6b2b528a046f7856c04c73c7b4b43a54',
    native_sha=receipt['identity']['native_sha'],
    start_utc=(task / 'START_UTC').read_text().strip(), end_utc=(task / 'END_UTC').read_text().strip(),
    process_exit=int((task / 'EXIT_CODE').read_text()),
    identity=dict(receipt['identity'], fingerprint=receipt['fingerprint'],
                  prepared_identity_sha256=sha(prep), prepared_files=len(J(prep)['outputs']),
                  build_exit=build['exit_code'], build_wall_s=build['wall_s'],
                  cargo=build['cargo_version'], binary_sha256=build['binary_sha256'],
                  error_norm=ret['error_norm'], error_control_identity=ret['error_control_identity'],
                  REI_TRANSPORT_THREADS_env='48', blas_threads=1, moment_rounding='none'),
    resources=dict(rhs_calls=ret['calls'], solver_wall_s=ret['wall_s'],
                   case_wall_s=receipt['execution']['wall_s'], case_cap_s=1800, total_cap_s=1800,
                   python_peak_RSS_KiB=ret['python_peak_RSS_KiB'], time_v=timev,
                   rejected_trial_retries=len(ret['errors']), retry_events=retry_events,
                   retry_message_set=sorted({e['message'] for e in ret['errors']})),
    original_gates=dict(
        rule='abs(residual) <= 1e-8 * gross for energy and photon (positive_solver assert; runner ORIGINAL_REFERENCE_LEDGER_GATE)',
        photon_normalized=led['photon_normalized'], photon_pass=led['photon_normalized'] <= 1e-8,
        energy_normalized=led['energy_normalized'], energy_pass=led['energy_normalized'] <= 1e-8,
        exact_fraction_photon_gate_pass=diag['original_gate']['fixed_gate_pass'],
        charge_residual=led['charge_residual'], species_residual=led['species_residual'],
        charge_species_policy='STORED_ONLY; no assertion exists in the frozen solver; not relabelled as a gate pass',
        receipt_status=receipt['status']),
    photon_ledger_diagnosis=dict(
        exact_endpoint_normalized=diag['endpoint']['decimal80']['normalized'],
        final_addition_roundoff_bound=diag['endpoint']['final_addition_roundoff_bound'],
        interval_count=len(recs),
        largest_abs_local_residual_changes=[dict(event=e, signed_local_delta=s, cumulative_normalized=n)
                                            for _, e, s, n in deltas[:5]],
        common_observations=dict(count=len(obs), sides=sides, fixed_gate_pass_all=all(x is True for x in obs_pass)),
        source_jumps=dict(status=diag['source_jumps']['status'], missing=diag['source_jumps']['missing'],
                          policy='MISSING_NOT_SUCCESS'),
        interpretation=diag['interpretation']),
    contrast_with_prior_rms_age64=dict(
        prior_source_commit=prior['source_commit'], prior_case=prior['case'],
        prior_photon_normalized=prior['original_gate']['photon_normalized'],
        prior_rhs_calls=15007, prior_wall_s=592.331,
        new_over_prior_photon_ratio=led['photon_normalized'] / prior['original_gate']['photon_normalized'],
        prior_largest_local_changes=[dict(event=x['event'], signed_local_delta=x['signed_local_delta'])
                                     for x in prior['largest_absolute_local_residual_changes'][:3]],
        scope='Same q0/age64 configuration, native SHA and gate; different controller (rms vs block-max) and solver bytes. '
              'Supports, but does not prove, the RMS ledger-dilution hypothesis for this case.'),
    endpoint_observables=dict(
        proper_time_s=end['proper_time_s'], N=end['N'], U=end['U'], temperature_K=end['temperature_K'],
        photo_events_species=L[4:7], RR_events_species=L[7:10], CI_events_species=L[10:13],
        DR_events_aggregate=L[13], DR_policy='AGGREGATE_SCALAR_ONLY; not species-wise success',
        Gamma_s=end['Gamma_s'], heat_erg_per_absorber_s=end['heat_erg_per_absorber_s'],
        cohorts=len(end['cohorts'])),
    age32_comparison=dict(
        status='NOT_RUN_IDENTITY_MISMATCH',
        candidate='research/rei_source_age_positive_native_intake_20261016/evidence/matrix/age32 (PR171 producer)',
        mismatch='PR171 RMS controller and solver/binary bytes differ from this block-max PR199 source; '
                 'no age32 run exists with solver_sha/binary_sha/error_norm of this case',
        age_convergence='HOLD'),
    scientific_accuracy='GATE_PASS_SINGLE_CASE_ONLY; AGE_CONVERGENCE_HOLD; NATIVE_TIME_HOLD',
    production_scientific_admission='NOT_ISSUED')
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(gates=result['original_gates'], top=result['photon_ledger_diagnosis']['largest_abs_local_residual_changes'][:3],
                      obs=result['photon_ledger_diagnosis']['common_observations'], res=result['resources'],
                      ratio=result['contrast_with_prior_rms_age64']['new_over_prior_photon_ratio']), indent=1))
