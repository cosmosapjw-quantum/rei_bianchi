"""Direct source-equation reference used for the one saved warm stage.

The original calculation was executed through Python stdin. This preserved
script keeps those equations and input interpretation. Its output filename is
EVENT_REFERENCE_REPLAY.json so rerunning it cannot overwrite the original
EVENT_REFERENCE_1STAGE.json evidence. It imports no candidate or native code.
"""
from pathlib import Path
from decimal import Decimal, localcontext
import json
import hashlib
import platform
import time
import numpy as np

root = Path(__file__).resolve().parent.parent
out = Path(__file__).resolve().parent
base = root / 'bass_he_rux03_work/screening/inputs'
raw = json.loads((base / 'extended.json').read_text())
h = raw['history'][0]
a = np.load(base / 'extended_dataset.npz', allow_pickle=False)
start = time.perf_counter()
D = lambda x: Decimal(str(x))

with localcontext() as ctx:
    ctx.prec = 60
    T = D(h['T_K'])
    nh = D(h['nH_cm3'])
    nhe = nh * D('.24') / (4 * D('.76'))
    x = [D(h[k]) for k in ['xHII', 'xHeII', 'xHeIII']]
    ne = nh * x[0] + nhe * (x[1] + 2 * x[2])
    lo = [nh * (1 - x[0]), nhe * (1 - x[1] - x[2]), nhe * x[1]]
    up = [nh * x[0], nhe * x[1], nhe * x[2]]
    ev = D('1.602176634e-12')
    kb = D('1.380649e-16')
    c = D('29979245800')
    chi = [D(v) for v in ['13.598434599702', '24.587389011', '54.41776']]
    lamb = list(map(D, ['315614', '570670', '1263030']))
    A = list(map(D, ['21.11', '32.38', '19.95']))
    P = list(map(D, ['-1.089', '-1.146', '-1.089']))
    C = list(map(D, ['.354', '.416', '.553']))
    R = list(map(D, ['.874', '.987', '.735']))
    M = list(map(D, ['1.101', '1.056', '1.275']))
    ar, gr, bc, kr = [], [], [], []
    for i in range(3):
        l = lamb[i] / T
        if i == 1:
            alpha = D('3e-14') * l ** D('.654')
            g = -D('.654')
        else:
            u = (l / D('.522')) ** D('.470')
            alpha = ((D(2) if i == 2 else D(1)) * D('1.269e-13')
                     * l ** D('1.503') / (1 + u) ** D('1.923'))
            g = -D('1.503') + D('1.923') * D('.470') * u / (1 + u)
        beta = (A[i] * T ** D('-1.5') * (-l / 2).exp() * l ** P[i]
                / (1 + (l / C[i]) ** R[i]) ** M[i])
        ar.append(alpha)
        gr.append(g)
        bc.append(beta)
        kr.append(kb * T * alpha * (D('1.5') + g))
    dr_a = D('1.54e-9') * D('11605') ** D('1.5')
    b1 = D('40.49664394833662') * D('11605')
    b2 = D('8.099328789667') * D('11605')
    ad = [dr_a * T ** D('-1.5') * (-b1 / T).exp(),
          D('.3') * dr_a * T ** D('-1.5') * (-(b1 + b2) / T).exp()]
    ed = [kb * b1, kb * (b1 + b2)]
    ci = [lo[i] * ne * bc[i] for i in range(3)]
    rr = [up[i] * ne * ar[i] for i in range(3)]
    dr = [up[1] * ne * z for z in ad]
    rr_kin = [up[i] * ne * kr[i] for i in range(3)]
    ftparams = [list(map(D, v)) for v in [
        ['13.60', '.4298', '54750', '32.88', '2.963', '0', '0', '0'],
        ['24.59', '13.61', '949.2', '1.469', '3.188', '2.039', '.4434', '2.136'],
        ['54.42', '1.720', '13690', '32.88', '2.963', '0', '0', '0']]]
    gamma, pi, pi_energy, pi_heat = ([D(0)] * 3 for _ in range(4))
    sigma_calls = active_sigmas = 0
    for e0, n0 in zip(a['q_eV'], a['initial_state'][4:4 + len(a['q_eV'])]):
        e, n = D(e0), D(n0)
        for i, ps in enumerate(ftparams):
            eth, e0p, s0, ya, p, yw, y0, y1 = ps
            sigma_calls += 1
            if e < eth:
                continue
            active_sigmas += 1
            xx = e / e0p - y0
            yy = (xx * xx + y1 * y1).sqrt()
            sigma = (s0 * ((xx - 1) ** 2 + yw * yw) * yy ** (p / 2 - D('5.5'))
                     * (1 + (yy / ya).sqrt()) ** (-p) * D('1e-18'))
            gm = c * sigma * n
            event = lo[i] * gm
            gamma[i] += gm
            pi[i] += event
            pi_energy[i] += event * e * ev
            pi_heat[i] += event * (e - chi[i]) * ev
    j = [pi[i] + ci[i] - rr[i] for i in range(3)]
    j[1] -= sum(dr)
    thermal_ci = [-ci[i] * chi[i] * ev for i in range(3)]
    thermal_rr = [-z for z in rr_kin]
    thermal_dr = [-dr[i] * ed[i] for i in range(2)]
    escape_rr = [rr[i] * chi[i] * ev + rr_kin[i] for i in range(3)]
    escape_dr = [dr[i] * (chi[1] * ev + ed[i]) for i in range(2)]
    binding = [pi[i] * chi[i] * ev + ci[i] * chi[i] * ev
               - rr[i] * chi[i] * ev for i in range(3)]
    binding[1] -= sum(dr) * chi[1] * ev
    th = sum(pi_heat + thermal_ci + thermal_rr + thermal_dr)
    ion, ph, esc = sum(binding), -sum(pi_energy), sum(escape_rr + escape_dr)
    closure = th + ion + ph + esc
    scale = sum(map(abs, [th, ion, ph, esc]))
    species = [-j[0], j[0], -j[1], j[1] - j[2], j[2], sum(j)]
    frac = [j[0] / nh, (j[1] - j[2]) / nhe, j[2] / nhe]
    net_scale = [pi[i] + ci[i] + rr[i] + (sum(dr) if i == 1 else 0)
                 for i in range(3)]

    def tokens(v):
        if isinstance(v, Decimal):
            return str(v)
        if isinstance(v, list):
            return [tokens(z) for z in v]
        if isinstance(v, dict):
            return {k: tokens(z) for k, z in v.items()}
        return v

    result = tokens({
        'task': 'HERE_RUX03_EVENT_BRIDGE_02_PREPARATION',
        'status': 'SOURCE_BASED_SINGLE_STAGE_ORACLE_NOT_RUNTIME_EXECUTION',
        'scope': ('One retained warm initial stage, high-precision primitive event/moment '
                  'reference; no candidate adapter, no ODE or history replay'),
        'input': {
            'epoch': 0, 'T_K': T, 'nH_cm3': nh, 'nHe_cm3': nhe,
            'nHe_definition': 'nH*Y/(4*(1-Y)), Y=0.24; decimal transcription of saved nH/fractions',
            'fractions': x, 'ne_cm3': ne, 'lower_cm3': lo, 'upper_cm3': up,
            'photon_nodes': len(a['q_eV']), 'q_eV_band': [10, 50000], 't_s': 0, 'a_rel': 1,
            'photon_measure': ('NPZ initial_state[4:2908] already weighted N_rel; '
                               'at initial a_rel=1 this equals proper node photon density'),
            'external_source': ('kept symbolic S_N,S_E; this reference isolates interactions '
                                'and does not replace actual HM12 emissivity with zero')},
        'constants': {'ev_erg': ev, 'kb_erg_K': kb, 'c_cm_s': c, 'binding_eV': chi},
        'coefficients': {
            'alpha_RR_cm3_s': ar, 'dln_alpha_dlnT': gr,
            'RR_kinetic_per_event_eV': [kr[i] / ar[i] / ev for i in range(3)],
            'RR_kinetic_coefficient_erg_cm3_s': kr, 'beta_CI_cm3_s': bc,
            'alpha_DR_cm3_s': ad, 'DR_captured_energy_erg': ed,
            'DR_captured_energy_eV': [z / ev for z in ed]},
        'events': {
            'photo_Gamma_s': gamma, 'PI_cm3_s': pi, 'CI_cm3_s': ci, 'RR_cm3_s': rr,
            'DR_HeII_to_HeI_cm3_s': dr, 'edge_net_J_cm3_s': j,
            'edge_abs_event_scale_cm3_s': net_scale,
            'net_to_abs_event_scale': [abs(j[i]) / net_scale[i] for i in range(3)],
            'species_source_cm3_s_HI_HII_HeI_HeII_HeIII_e': species,
            'fraction_dot_per_s_HII_HeII_HeIII': frac,
            'direct_electron_source_cm3_s': sum(j)},
        'energy_components_erg_cm3_s': {
            'PI_absorbed_energy_by_species': pi_energy, 'PI_heat_by_species': pi_heat,
            'CI_thermal_by_edge': thermal_ci, 'RR_thermal_by_edge': thermal_rr,
            'DR_thermal_by_resonance': thermal_dr, 'RR_escape_by_edge': escape_rr,
            'DR_escape_by_resonance': escape_dr, 'binding_by_edge': binding,
            'interaction_thermal_total': th, 'interaction_binding_total': ion,
            'interaction_photon_total': ph, 'escape_total': esc,
            'interaction_closure_residual': closure, 'interaction_closure_abs_scale': scale,
            'scaled_interaction_closure': closure / scale},
        'structural_invariants': {
            'H_nuclei_source': species[0] + species[1],
            'He_nuclei_source': species[2] + species[3] + species[4],
            'charge_source': species[1] + species[3] + 2 * species[4] - species[5]},
        'runtime': {
            'implementation': ('independent direct decimal equations from pinned '
                               'FT03/Verner source; not imported candidate/native'),
            'python': platform.python_version(), 'decimal_precision': 60,
            'sigma_evaluations': sigma_calls,
            'nonzero_supported_sigma_evaluations': active_sigmas,
            'new_saved_state_references': 1, 'native_builds': 0, 'native_RHS_calls': 0,
            'ODE': 0, 'old_campaign_replays': 0},
        'precision_scope': ('Decimal equations on decimal representations of saved float '
                            'data and published implementation constants, not bitwise Rust '
                            'parity or physical accuracy. Use componentwise/absolute-event '
                            'scales for cancellation-sensitive checks.')})

result['runtime']['elapsed_wall_s'] = time.perf_counter() - start
sources = []
for name, path in [
    ('extended.json', base / 'extended.json'),
    ('extended_dataset.npz', base / 'extended_dataset.npz'),
    ('ft03_rates.rs', root / 'recovery_drive/physical_v2/rust/rei_microphysics/src/ft03_rates.rs'),
    ('ft03_controlled.rs', root / 'recovery_drive/physical_v2/rust/rei_microphysics/src/ft03_controlled.rs'),
    ('atomic_provider.rs', root / 'recovery_drive/physical_v2/rust/rei_microphysics/src/atomic_provider.rs'),
    ('native_main.rs', root / 'recovery_drive/physical_v2/research/physical_provider_20261010/native/src/main.rs')]:
    sources.append({'name': name, 'path': str(path), 'bytes': path.stat().st_size,
                    'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
result['sources'] = sources
destination = out / 'EVENT_REFERENCE_REPLAY.json'
destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'output': str(destination), 'runtime': result['runtime']}, indent=2))
