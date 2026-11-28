"""Matched proper-cell experiments and consumers of the native R118 histories."""
from __future__ import annotations

import csv
import math
from pathlib import Path
import subprocess

from . import cr, he, hh

EV_J = 1.602176634e-19
Y_HE = 0.2454
F_HE = Y_HE / (4 * (1 - Y_HE))


def closed_cx_extent(n_h_cm3, x, eta, y, temperature_k, duration_s):
    """Exact constant-T, finite-D net extent in proper m^-3 for a closed H/D pair."""
    if not all(map(math.isfinite, (n_h_cm3, x, eta, y, temperature_k, duration_s))):
        raise ValueError('Nonfinite charge exchange input')
    if n_h_cm3 <= 0 or not 0 <= x <= 1 or not 0 <= y <= 1 or eta < 0 or duration_s < 0:
        raise ValueError('Invalid closed charge exchange inventory or duration')
    if eta == 0 or duration_s == 0:
        return 0.0
    kf, kr = hh.savin_rates(temperature_k)
    # Evolve the increment u=y(t)-y(0). At u=0 the signed source c contains
    # physical reactant populations, giving exactly zero for exhausted reactants.
    forward = kf * x
    reverse = kr * (1 - x)
    c = forward * (1 - y) - reverse * y
    if c == 0.0:
        return 0.0
    h_sum = forward + reverse
    d_sum = eta * (kf * (1 - y) + kr * y)
    # For u'=n_H*(a*u²-b*u+c), b=h_sum+d_sum. The discriminant equals
    # (h_sum-d_sum)²+4*eta*kf*kr, including the linear kf==kr case.
    gap = math.hypot(h_sum - d_sum, 2 * math.sqrt(eta) * math.sqrt(kf * kr))
    q = -math.expm1(-(gap * n_h_cm3) * duration_s)
    denominator = gap * (2 - q) + (h_sum + d_sum) * q
    dy = 2 * c * q / denominator
    extent = n_h_cm3 * (eta * dy) * 1e6
    if not math.isfinite(extent):
        raise ValueError('Charge exchange extent exceeds the finite density domain')
    return extent


def native_ledger(executable, packet):
    result = subprocess.run([str(Path(executable).resolve())], input=packet, text=True,
                            capture_output=True, check=False, timeout=60)
    if result.returncode:
        raise ValueError(f'Native cell rejected inputs: {result.stderr.strip()}')
    return {key: float(value) for key, value in (line.split('\t') for line in result.stdout.splitlines())}


def late_cell(executable, case='SHEAR_PLUS', duration_s=1e10, eta_d=2.5e-5, y_d_initial=0., enabled=True):
    """Separate finite perturbation of an original AXBI sample, with frozen input fields.

    Use an initially empty optional proton source in the frozen volume. Electrons born in
    CR ionizations enter a nonthermal stock. The input H/He history includes its already-paid
    primary photoabsorptions. They are deliberately consumed via the diagnostic reader.
    """
    if not math.isfinite(duration_s) or duration_s <= 0 or not 0 <= eta_d <= 0.01:
        raise ValueError('Positive finite exposure and 0<=D/H<=0.01 required')
    snapshots = cr.axbi_snapshots()['rows']
    if case not in snapshots:
        raise ValueError(f'Unknown AXBI case {case!r}, expected one of {sorted(snapshots)}')
    if not math.isfinite(y_d_initial) or not 0 <= y_d_initial <= 1:
        raise ValueError('Initial DII fraction must be within [0,1]')
    row = snapshots[case]
    rates = cr.snapshot_primary_ionization(row, duration_s, enabled=enabled)
    x, density, temp = (float(row[k]) for k in ('x_HII', 'nH_proper_cm3', 'temperature_K'))
    j = closed_cx_extent(density, x, eta_d, y_d_initial, temp, duration_s)
    start = float(row['time_s'])
    # Consume proper-volume time-integrated source moments. Endpoint rates grow during buildup.
    debit = math.fsum(rates['window_projectile_debit_J_m3_by_target'].values()) / EV_J
    partition_residual = math.fsum(
        [value for field in ('window_owner_binding_J_m3_by_target',
                             'window_fast_birth_J_m3_by_target',
                             'window_threshold_offset_J_m3_by_target')
         for value in rates[field].values()]
        + [-value for value in rates['window_projectile_debit_J_m3_by_target'].values()]
    ) / EV_J
    # Apply the explicitly modeled losses to the active-band collisionless endpoint stock.
    # The source-wide total also contains inert low/high-energy tails.
    stock = rates['storage']['final_CR_energy_J_m3'] / EV_J
    collision_stock = rates['storage']['active_CR_energy_J_m3'] / EV_J
    fields = ['CELL', 'AXBI_frozen_CX_CR', start, start + duration_s, density, density * F_HE,
              density * eta_d, x, row['x_HeII'], row['x_HeIII'], y_d_initial, temp, 0., collision_stock]
    lines = [' '.join(map(str,fields)), f'wu-cx new CX {j:.17g}']
    for target, native in [('H','HI'),('He','HeI')]:
        count = rates['window_primary_ions_m3_by_target'][target]
        kinetic = rates['window_fast_birth_J_m3_by_target'][target] / EV_J
        offset = rates['window_threshold_offset_J_m3_by_target'][target] / EV_J
        lines.append(f'cr-{target} new CR {native} {count:.17g} {kinetic:.17g} {offset:.17g}')
    result = native_ledger(executable,'\n'.join(lines) + '\n')
    return {'case':case,'zbar':float(row['zbar']),'T_initial_K':temp,'time_start_s':start,
            'duration_s':duration_s,'D_over_H':eta_d,'initial_DII_fraction':y_d_initial,
            'signed_CX_extent_m3':j,'CX_gas_energy_eV_m3':-hh.CX_THRESHOLD_EV*j,
            'CR_model':rates['frame'],'CR_enabled':enabled,
            'CR_window_births_m3':sum(rates['window_primary_ions_m3_by_target'].values()),
            'CR_window_projectile_debit_eV_m3':debit,
            'active_band_initial_reference_eV_m3':collision_stock,
            'CR_transfer_partition_residual_eV_m3':partition_residual,
            'source_spectrum_endpoint_kinetic_eV_m3':stock,
            'native':result, 'input_packet':lines,
            'scope':'Finite fixed-volume source experiment. D/H and initial DII are prescribed, the H/He snapshot is held for the rate evaluation; no source-on cosmological reintegration.'}


def consume_live(history_path, exchange_path):
    """Resolve the existing host's UV binding work by absorber and evolve a passive D tracer."""
    def load(path, fields):
        with Path(path).open(newline='') as stream:
            reader = csv.DictReader(stream, delimiter='\t')
            missing = set(fields).difference(reader.fieldnames or ())
            if missing:
                raise ValueError(f'Missing native fields in {path}: {sorted(missing)}')
            rows = []
            for index, row in enumerate(reader, 2):
                if any(row[name] is None for name in fields):
                    raise ValueError(f'Missing native value in {path} at row {index}')
                values = {name: float(row[name]) for name in fields}
                if not all(map(math.isfinite, values.values())):
                    raise ValueError(f'Nonfinite native value in {path} at row {index}')
                rows.append(values)
            return rows
    hist = load(history_path, ('eta', 'time_s', 'x_HII', 'Tm_K', 'nH_m3',
                               'photo_HI', 'photo_HeI', 'photo_HeII'))
    uv = load(exchange_path, ('eta', 'binding_U', 'absorbed_U', 'heat_U'))
    if len(hist)<2 or len(hist)!=len(uv) or any(r['eta']!=f['eta'] for r,f in zip(hist,uv)):
        raise ValueError('Expected matched native material and UV epochs')
    # Native ledgers store cumulative events per H. Thresholds multiply actual resolved counts.
    # The fraction in each absorber needs no invented per-event photon energy.
    y=hist[0]['x_HII']; gap=0.; energy_gap=0.
    first=hist[0]; bindings={}
    for prev,cur,radiation in zip(hist,hist[1:],uv[1:]):
        dt=cur['time_s']-prev['time_s']
        if dt<=0: raise ValueError('Nonmonotone native clock')
        mid=lambda name:(prev[name]+cur[name])/2
        y=hh.trace_step(y,dt,mid('Tm_K'),mid('nH_m3')*1e-6,mid('x_HII'))
        bindings={s:(cur['photo_'+s]-first['photo_'+s])*threshold for s,threshold in he.BINDING_EV.items()}
        gap=max(gap,abs(math.fsum(bindings.values())-(radiation['binding_U']-uv[0]['binding_U'])))
        energy_gap=max(energy_gap,abs(radiation['absorbed_U']-radiation['heat_U']-radiation['binding_U']))
    dr=uv[-1]; total=dr['absorbed_U']-uv[0]['absorbed_U']; heat=dr['heat_U']-uv[0]['heat_U']
    return {'native_rows':len(hist),'end_proper_s':hist[-1]['time_s'],'end_x_HII':hist[-1]['x_HII'],
            'trace_DII_initial':hist[0]['x_HII'],'trace_DII_final':y,'binding_eV_per_H_by_absorber':bindings,
            'native_absorbed_eV_per_H':total,'native_heat_eV_per_H':heat,
            'energy_fraction_to_heat':heat/total if total else None,
            'max_binding_difference_eV_per_H':gap,'max_absorbed_partition_difference_eV_per_H':energy_gap,
            'energy_sinks_reapplied':0,'CR_source':'OFF', 'scope':'Native BASS–REC–REI bounded window, passive D reconstruction and HE energy account on original photon events.'}
