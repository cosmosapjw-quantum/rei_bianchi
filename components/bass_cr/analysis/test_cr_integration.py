import math
import pytest
from rei_bianchi.microphysics import cr
from rei_bianchi.microphysics.cr_sources.ports import ContractError, claim_injection


def test_physical_source_population_energy_and_cutoff_against_donor():
    expected = [(8.583703187582436e-16, 5.47033142884169e-34),
                (8.304211765519884e-16, 8.459279749254517e-33),
                (1.6887914953102317e-15, 9.006312892138684e-33)]
    rows = []
    for population, (n, u) in zip(('direct_0p1_10', 'direct_10_900', 'selected_total'),expected):
        result = cr.integrate_phys02(population=population, include_spectrum=True)
        rows.append(result)
        assert math.isclose(result['number_m3'], n, rel_tol=2e-14)
        assert math.isclose(result['coordinate_energy_J_m3'], u, rel_tol=2e-14)
        assert math.isclose(sum(atom['count_m3'] for atom in result['spectrum']), n, rel_tol=2e-13)
    registry = []
    claim_injection(rows[0],registry)
    claim_injection(rows[1],registry)
    with pytest.raises(ContractError,match='OVERLAPPING'):
        claim_injection(rows[2],registry)


def test_linear_source_exposure_and_time_boundary():
    first = cr.integrate_phys02(0,5e9)
    second = cr.integrate_phys02(5e9,1e10)
    assert second['number_m3'] == pytest.approx(3*first['number_m3'], rel=2e-14,abs=0)
    with pytest.raises(ContractError,match='TIME_SUPPORT'):
        cr.integrate_phys02(stop_s=1.1e10)


def test_snapshot_binding_partition_and_no_implicit_heat():
    row = cr.axbi_snapshots()['rows']['SHEAR_PLUS']
    base = cr.snapshot_primary_ionization(row)
    rates = base['primary_ion_rates_m3_s']
    assert base['shear_s_inv'] > 0 and 0 < base['sampled_thin_loss_fraction'] < 1e-3
    assert base['fast_electron_births_m3_s'] == sum(rates.values())
    assert base['prompt_gas_heat_J_m3_s'] is None and base['thermal_electron_source_m3_s'] is None
    assert 0 < base['threshold_model_offset_J_m3_s'] < base['binding_power_J_m3_s']
    assert abs(base['partition_residual_J_m3_s']) <= 5e-15*base['modeled_proton_loss_J_m3_s']
    for key, total in [('fast_birth_J_m3_s_by_target','fast_electron_birth_power_J_m3_s'),
                       ('threshold_offset_J_m3_s_by_target','threshold_model_offset_J_m3_s'),
                       ('projectile_debit_J_m3_s_by_target','modeled_proton_loss_J_m3_s')]:
        assert math.fsum(base[key].values()) == base[total]
    denser = dict(row, nH_proper_cm3=2*float(row['nH_proper_cm3']))
    larger = cr.snapshot_primary_ionization(denser)
    assert all(larger['primary_ion_rates_m3_s'][t] == 2*rates[t] for t in rates)


def test_source_off_no_exposure_and_density_zero():
    for kwargs in ({'enabled':False},{'proper_exposure_s':0}):
        result = cr.snapshot_primary_ionization('SHEAR_MINUS',**kwargs)
        assert result['modeled_proton_loss_J_m3_s'] == result['fast_electron_births_m3_s'] == 0
    row = dict(cr.axbi_snapshots()['rows']['ZERO'], x_HI=0.0, x_HeI=0.0)
    assert cr.snapshot_primary_ionization(row)['modeled_proton_loss_J_m3_s'] == 0
    with pytest.raises(ValueError):
        cr.snapshot_primary_ionization(dict(row,zbar=9.0))


def test_fubini_weights_against_time_integration_of_endpoint_rate():
    import numpy as np
    nodes, weights = np.polynomial.legendre.leggauss(6)
    t = 1e10
    final = cr.snapshot_primary_ionization('SHEAR_PLUS',t)
    clock = 0.5*t*(nodes+1)
    direct = [cr.snapshot_primary_ionization('SHEAR_PLUS',float(tt)) for tt in clock]
    for species in ('H','He'):
        rates = np.array([v['primary_ion_rates_m3_s'][species] for v in direct]); h = final['H_s_inv']
        plain = 0.5*t*np.dot(weights,rates)
        cell = 0.5*t*np.dot(weights,rates*np.exp(-3*h*(t-clock)))
        assert math.isclose(plain, final['window_primary_ions_m3_by_target'][species], rel_tol=2e-14)
        assert math.isclose(cell, final['comoving_window_final_volume_primary_ions_m3_by_target'][species], rel_tol=2e-14)
        assert 0 < cell < plain < 0.51*t*final['primary_ion_rates_m3_s'][species]
