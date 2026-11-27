"""PHYS84 instantaneous source from immutable saved PHYS83 rows only.

No parent scientific module is imported. Positive-product/output underflow is a
domain refusal, including a zero intermediate in the prescribed Tdot division.
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import math

UNIT = Path(__file__).resolve().parents[1]
REPO = UNIT.parents[1]
CONTRACT_SHA = '01528db5b31bd27cb0a9ae623b92cd0821ac4b42bfb4b3792ce3cc56c6e8280f'
PARENT = REPO / 'research/hh_phys83_ce_completion_20261023'
PINS = {
    'results/rate_grid.csv': '64e53e02b776db2aee6d67ce03201cbc0b90404d7cdf40e52cccaaecd2fc3017',
    'CONTRACT.json': 'd9eb980df5236e2b2ca3da313813c3ca2b21562f90486f1173d0ea509bc4dcc5',
    'results/SCIENCE_IDENTITY.json': 'ca2ceebb71bff3e682dcf01761e3f5e2770d220a27bf38ac4817d8aad6622d46',
    'results/COMPLETE.json': '6a69c5552a9a311c14c55575ae1ee058d746fd377a23a21f7636ad3cc7854761',
}
EVENTS = ('CE_up_2S', 'CE_up_2P', 'CE_down_2S', 'CE_down_2P',
          'RAD_2S_2gamma', 'RAD_2S_M1', 'RAD_2P_E1')
LEVELS = ('1S', '2S', '2P')
INCIDENCE = ((-1,-1,1,1,1,1,1), (1,0,-1,0,-1,-1,0), (0,1,0,-1,0,0,-1))
DELTA, KB = 10.20435, 8.617333262145179e-5
A2G, AM1, AE1 = 8.229, 2.496e-6, 626000000.0
ROUTES = ('immediate_escape', 'emissivity_handoff')
STATE_KEYS = ('T_K', 'n1s', 'n2s', 'n2p', 'ne', 'Nthermal')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked_number(value, name, lower=0.0, upper=1e18, strict=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError('INVALID_NUMBER:' + name)
    try:
        x = float(value)
    except (OverflowError, ValueError):
        raise ValueError('INVALID_NUMBER:' + name) from None
    if not math.isfinite(x) or x < lower or x > upper or (strict and x == lower):
        raise ValueError('OUT_OF_DOMAIN:' + name)
    return x


def product(*factors):
    """Nonnegative finite factors; largest first, no silent positive zero."""
    if any(not math.isfinite(x) or x < 0 for x in factors):
        raise ValueError('INVALID_PRODUCT_FACTOR')
    if 0.0 in factors:
        return 0.0
    value = 1.0
    for x in sorted(factors, reverse=True):
        value *= x
        if not math.isfinite(value):
            raise ValueError('POSITIVE_PRODUCT_OVERFLOW')
        if value == 0:
            raise ValueError('POSITIVE_PRODUCT_UNDERFLOW')
    return value


def temperature_source(q, density):
    if q == 0:
        return 0.0
    quotient = q / density
    if quotient == 0:
        raise ValueError('TEMPERATURE_DIVISION_UNDERFLOW')
    value = (2.0 / (3.0 * KB)) * quotient
    if not math.isfinite(value) or value == 0:
        raise ValueError('TEMPERATURE_OUTPUT_RANGE')
    return value


class SavedSource:
    """Validate byte pins and all 132 saved rows before exposing any rate."""
    def __init__(self, parent=PARENT, contract=UNIT / 'CONTRACT.json'):
        cb = Path(contract).read_bytes()
        if sha(cb) != CONTRACT_SHA:
            raise ValueError('ADAPTER_CONTRACT_PIN_MISMATCH')
        self.contract = json.loads(cb)
        buffers = {}
        for name, expected in PINS.items():
            buffers[name] = (Path(parent) / name).read_bytes()
            if sha(buffers[name]) != expected:
                raise ValueError('PARENT_INPUT_PIN_MISMATCH:' + name)
        self.rows = self._parse(buffers['results/rate_grid.csv'])
        self.identity = {
            'parent_scientific_identity': self.contract['parent_scientific_identity'],
            'parent_input_SHA256': dict(PINS), 'adapter_contract_SHA256': CONTRACT_SHA,
            'adapter_source_SHA256': sha(Path(__file__).read_bytes()),
            'source_mode': 'saved_PHYS83_exact_temperature_rows_only',
        }

    @staticmethod
    def _parse(raw):
        table = {}
        count = 0
        for row in csv.DictReader(io.StringIO(raw.decode('utf-8'))):
            count += 1
            level, label = row['upper_level'], row['temperature_K']
            t = checked_number(float(label), 'stored_T', 255., 50000.)
            qu = checked_number(float(row['q_up_cm3_s']), 'q_up', 0., 1e18, True)
            qd = checked_number(float(row['q_down_cm3_s']), 'q_down', 0., 1e18, True)
            if level not in ('2S', '2P') or level in table.get(t, {}):
                raise ValueError('INVALID_OR_DUPLICATE_RATE_ROW')
            if row['finite_source_only'] != 'True':
                raise ValueError('SOURCE_MODE_MISMATCH')
            if row['float64_underflow_up'] != 'False' or row['float64_underflow_down'] != 'False':
                raise ValueError('SAVED_RATE_UNDERFLOW')
            if t in table and any(x['label'] != label for x in table[t].values()):
                raise ValueError('PAIRED_T_LABEL_MISMATCH')
            table.setdefault(t, {})[level] = {'label': label, 'up': qu, 'down': qd}
        if count != 132 or len(table) != 66 or any(set(x) != {'2S', '2P'} for x in table.values()):
            raise ValueError('EXPECTED_66_PAIRED_TEMPERATURES')
        return table

    def evaluate(self, state, *, radiation_route, radiative_owner,
                 excited_state_owner, native_radiative_owner_active):
        if radiation_route not in ROUTES:
            raise ValueError('UNSUPPORTED_RADIATION_ROUTE')
        if radiative_owner != 'detached_own_spontaneous':
            raise ValueError('UNSUPPORTED_RADIATIVE_OWNER')
        if native_radiative_owner_active is not False:
            raise ValueError('RADIATIVE_OWNER_CONFLICT')
        if excited_state_owner != 'explicit_1S_2S_2P':
            raise ValueError('EXPLICIT_EXCITED_STATE_OWNER_REQUIRED')
        if not isinstance(state, dict) or set(state) != set(STATE_KEYS):
            raise ValueError('EXPLICIT_SIX_FIELD_STATE_REQUIRED')
        st = {k: checked_number(state[k], k, 255., 50000.) if k == 'T_K'
              else checked_number(state[k], k, 0., 1e20, True) if k == 'Nthermal'
              else checked_number(state[k], k) for k in STATE_KEYS}
        if st['Nthermal'] < math.fsum(st[k] for k in ('n1s','n2s','n2p','ne')):
            raise ValueError('NTHERMAL_BELOW_SUPPLIED_PARTICLES')
        t = st['T_K']
        if t not in self.rows:
            raise ValueError('EXACT_SAVED_T_REQUIRED')
        n0, ns, np, ne = (st[k] for k in ('n1s','n2s','n2p','ne'))
        rs, rp = self.rows[t]['2S'], self.rows[t]['2P']
        r = (product(ne,n0,rs['up']), product(ne,n0,rp['up']),
             product(ne,ns,rs['down']), product(ne,np,rp['down']),
             product(ns,A2G), product(ns,AM1), product(np,AE1))
        dn = tuple(math.fsum(s*x for s,x in zip(row,r)) for row in INCIDENCE)
        er = tuple(product(DELTA, x) for x in r)
        qth = math.fsum((-er[0],-er[1],er[2],er[3]))
        uexc = math.fsum((er[0],er[1],-er[2],-er[3],-er[4],-er[5],-er[6]))
        emit = math.fsum(er[4:])
        energy = {'gas_thermal':qth, 'chemical_binding':0., 'atomic_excitation':uexc,
                  'radiation_injected':emit if radiation_route == 'emissivity_handoff' else 0.,
                  'escaped_radiation':emit if radiation_route == 'immediate_escape' else 0.,
                  'source_reservoir':0.}
        ge = math.fsum(r)
        genergy = product(DELTA,ge)
        gthermal = product(DELTA,math.fsum(r[:4]))
        gt = temperature_source(gthermal,st['Nthermal'])
        photons = (product(2.,r[4]),r[5],r[6])
        record = {'schema':'WU_HI_CE_INSTANTANEOUS_SOURCE_RECORD_V1',
                  'identity':dict(self.identity), 'stored_temperature_label_K':rs['label'],
                  'state':st, 'ownership':{'radiation_route':radiation_route,
                    'radiative_owner':radiative_owner,'excited_state_owner':excited_state_owner,
                    'native_radiative_owner_active':False},
                  'event_intensities_cm3_s':dict(zip(EVENTS,r)),
                  'level_sources_cm3_s':dict(zip(LEVELS,dn)),
                  'electron_source_cm3_s':0.,'thermal_particle_source_cm3_s':0.,
                  'nuclei_source_cm3_s':math.fsum(dn),'charge_source_cm3_s':0.,
                  'energy_columns_eV_cm3_s':energy,'emitted_energy_diagnostic_eV_cm3_s':emit,
                  'photon_sources_cm3_s':dict(zip(('2gamma','M1','E1'),photons)),
                  'total_photon_source_cm3_s':math.fsum(photons),
                  'temperature_source_K_s':temperature_source(qth,st['Nthermal']),
                  'residuals':{'nuclei_cm3_s':math.fsum(dn),
                               'energy_eV_cm3_s':math.fsum(energy.values())},
                  'gross':{'G_event':ge,'G_energy':genergy,'G_thermal':gthermal,'G_temperature':gt},
                  'units':self.contract['source']['units'],
                  'limitations':{'new_rate_evaluations':0,'population_solves':0,'ODE':0,
                     'continuum_certificate':False,'physical_uncertainty_enclosure':False,
                     'production_admission':'NOT_ISSUED','HH_R10':'OFF'}}
        # json allow_nan=False is an additional recursive finite-output guard.
        json.dumps(record, allow_nan=False)
        return record
