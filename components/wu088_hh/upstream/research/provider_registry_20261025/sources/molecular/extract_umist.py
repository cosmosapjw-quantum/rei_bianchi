#!/usr/bin/env python3
"""Extract actual UMIST Rate22 rows without evaluating or admitting rates."""
from pathlib import Path
import csv
import hashlib
import json

BASE = Path(__file__).resolve().parent
RAW = BASE / 'raw'
SOURCE = RAW / 'rate22_final.rates'
SPECIES = RAW / 'rate22_revised_CtoO_0.44.specs'
ALLOWED = {'H', 'H+', 'H-', 'H2', 'H2+', 'H3+', 'He', 'He+', 'HeH+',
           'D', 'D+', 'D-', 'HD', 'HD+', 'Li', 'Li+', 'LiH', 'LiH+',
           'e-', 'PHOTON', 'CRP', 'CRPHOT', ''}
ONE_BODY = {'CP', 'CR', 'PH'}
FIT_FIELDS = ['alpha', 'beta', 'gamma', 'Tmin_K', 'Tmax_K',
              'method', 'accuracy_code', 'original_reference', 'notes']

def sha(b):
    return hashlib.sha256(b).hexdigest()

def main():
    source = SOURCE.read_bytes()
    parsed = []
    subset = []
    for lineno, raw in enumerate(source.splitlines(keepends=True), 1):
        row = next(csv.reader([raw.decode('utf-8')], delimiter=':', quotechar='"'))
        if not set(row[2:8]) <= ALLOWED:
            continue
        ntr = int(row[8])
        fields = 9 + 9 * ntr
        if len(row) != fields + 1 or row[-1].strip():
            raise ValueError(('source row layout', lineno, len(row), fields))
        segments = [dict(zip(FIT_FIELDS, row[9 + 9*i:18 + 9*i])) for i in range(ntr)]
        typ = row[1]
        item = {
            'provider': 'UMIST_Rate22_final',
            'provider_row_id': row[0],
            'provider_line': lineno,
            'provider_url': 'https://umistdatabase.uk/react/' + row[0],
            'raw_row_sha256': sha(raw),
            'raw_row_utf8': raw.decode('utf-8'),
            'reaction_type': typ,
            'reactants_ordered': [v for v in row[2:4] if v],
            'products_ordered': [v for v in row[4:8] if v],
            'temperature_fit_count': ntr,
            'fits_original_decimal_strings': segments,
            'rate_unit': 's^-1' if typ in ONE_BODY else 'cm^3 s^-1',
            'formula': {'CP': 'k=alpha; source cosmic-ray normalization retained',
                        'CR': 'k=alpha*(T/300)^beta*gamma/(1-omega); source cosmic-ray normalization retained',
                        'PH': 'k=alpha*exp(-gamma*A_V); source radiation-field normalization retained'}.get(typ, 'k=alpha*(T/300)^beta*exp(-gamma/T)'),
            'gamma_is_Q': False,
            'Q_value': None,
            'Q_status': 'NOT_SUPPLIED_BY_RATE22',
            'state_qualification': 'UNRESOLVED_ELECTRONIC_ROVIBRATIONAL_STATE',
            'isotope_source_labels': 'H and He elemental labels; atomic mass indices 1 and4 in companion species file; isotope substitutions are not supplied',
            'rate_admission': False,
            'source_coefficient_ingested': True,
            'covariance': None,
            'uncertainty_status': 'PROVIDER_CATEGORY_ONLY_NO_COVARIANCE',
            'branch_fraction': None,
            'branch_status': 'PARTIAL_REACTION_COEFFICIENT_NO_COMPLETE_BRANCH_NORMALIZATION',
            'temperature_extrapolation': False,
            'external_driver': {'CP': 'CRP is prescribed cosmic-ray-rate driver, not an explicit consumed proton',
                                'CR': 'CRPHOT is prescribed secondary-photon-rate driver, spectrum unbound',
                                'PH': 'PHOTON field is source ISRF attenuated by A_V, arbitrary cosmological spectrum unbound'}.get(typ),
        }
        parsed.append(item)
        subset.append(raw)
    species_main = []
    for line in SPECIES.read_text().splitlines()[1:]:
        cols = line.split()
        if not cols:
            continue
        if cols[0] == '9999':
            break
        if cols[1] in ALLOWED:
            species_main.append({'provider_index': int(cols[0]), 'provider_label': cols[1],
                                 'provider_nominal_mass_number': int(cols[2]), 'raw_line': line,
                                 'state': None, 'isomer': None,
                                 'isotope_qualification': 'NOMINAL_MASS_INDEX; no isotope-shift or isomer data supplied'})
    payload = {
        'schema_version': 1,
        'purpose': 'actual provider row ingestion candidates; no empirical-rate, isotope-substitution or Q admission',
        'source': {'url': 'https://umistdatabase.uk/files/rate22_final.rates',
                   'bytes': len(source), 'sha256': sha(source), 'total_rows': len(source.splitlines())},
        'species_source': {'url': 'https://umistdatabase.uk/files/rate22_revised_CtoO_0.44.specs',
                           'bytes': SPECIES.stat().st_size, 'sha256': sha(SPECIES.read_bytes()),
                           'excluded_tail': 'Conserved H2/e and Parents initial abundances are not adopted'},
        'format_reference': 'Millar et al.2024 A&A682 A109 doi:10.1051/0004-6361/202346908 §§2.1–2.2',
        'accuracy_code_definitions': {
            'A': {'meaning': '<25%', 'source': 'https://umistdatabase.uk/react/74'},
            'B': {'meaning': '<50%', 'source': 'https://umistdatabase.uk/react/998'},
            'C': {'meaning': 'within a factor2', 'source': 'https://umistdatabase.uk/react/8267'},
            'D': {'meaning': 'within an order of magnitude', 'source': 'https://umistdatabase.uk/react/6353'},
            'warning': 'Provider-specific categories; do not use Leiden A/B/C meanings for UMIST',
        },
        'environment_contract': {
            'cosmic_ray_reference_zeta0_s-1': '1.36e-17',
            'cosmic_ray_scaling': 'Multiply CP/CR coefficients by zeta/zeta0 only when this source convention is deliberately selected',
            'CR_gamma_density_convention': 'relative to H2 density; paper notes factor2 difference from Heays2017 gamma to account for1/(1-omega)',
            'omega': None,
            'omega_status': 'CONSUMER_UNBOUND; paper example0.5 is not adopted',
            'PH_reference_field': 'unshielded interstellar UV with exponential visible dust attenuation',
            'self_shielding_supplied': False,
        },
        'selection': 'All reactant/product labels in the explicit H/He/D/Li/e/photon/CR label allow-list',
        'allowed_labels': sorted(ALLOWED),
        'selected_count': len(parsed),
        'selected_species_rows': species_main,
        'rows': parsed,
        'missing_families_in_this_source': ['HD', 'LiH', 'D-bearing species', 'T-bearing species',
                                           'He3-bearing species', 'isomers', 'rovibrational resolution', 'nuclear/weak channels'],
        'pitfalls': [
            'Keep repeated identical products and colliders as stoichiometric multiplicities.',
            'Reaction74 has two ranges10–100K and101–3000K; preserve the open100–101K gap.',
            'CRP/CRPHOT are environment drivers; not fictitious particles for charge/baryon checks.',
            'Gamma is a fitting parameter; it is not a reaction Q or threshold.',
            'Two H3+ DR rows1577,1578 have common reactants but no full branch-completeness guarantee is inferred.',
            'PH/CR coefficients carry source-specific radiation and cosmic-ray normalization; no arbitrary-spectrum admission.',
            'All rate/Q approvals remain false after exact finite compiler structural checks.',
        ],
    }
    (BASE / 'umist_light_provider_rows.json').write_text(json.dumps(payload, indent=2, ensure_ascii=False)+'\n')
    (RAW / 'umist_selected_rows_exact.rates').write_bytes(b''.join(subset))
    print(json.dumps({'source_rows': len(source.splitlines()), 'selected_rows': len(parsed),
                      'fit_segments': sum(x['temperature_fit_count'] for x in parsed),
                      'species': sorted(set(v for x in parsed for v in x['reactants_ordered']+x['products_ordered'])),
                      'output': str(BASE/'umist_light_provider_rows.json')},ensure_ascii=False))

if __name__ == '__main__':
    main()
