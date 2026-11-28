"""New source-to-state and unit conversion checks; no WU compiler replay."""
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import mass_binding


class NeutralMassTests(unittest.TestCase):
    def test_selected_neutral_masses_exact_rational_oracle(self):
        packet = json.loads((ROOT/'sources/NEUTRAL_H1_HE4_MASS_CANDIDATES.json').read_text())
        result = mass_binding.convert_candidates()
        for source, output in zip(packet['mass_rows'], result['rows']):
            rational = Fraction(source['relative_atomic_mass'])*Fraction(packet['atomic_mass_constant']['kg'])
            self.assertEqual(Fraction(output['mass_kg_decimal']), rational)
            self.assertEqual(output['mass_kg_binary64'], float(rational))
            self.assertIsNone(output['combined_standard_uncertainty_kg'])
            self.assertFalse(output['independence_assumed'])
            self.assertFalse(output['nuclear_or_electronic_binding_added_again'])
        self.assertFalse(result['physical_provider_admitted'])
        self.assertFalse(result['raw_http_bytes_verified'])
        print(json.dumps({'neutral_mass_candidates':result},allow_nan=False,sort_keys=True))

    def test_bare_or_excited_state_cannot_take_neutral_mass(self):
        original=json.loads((ROOT/'sources/NEUTRAL_H1_HE4_MASS_CANDIDATES.json').read_text())
        for key,value in [('charge',1),('state','bare_nucleus'),('pool','electron_thermal')]:
            packet=deepcopy(original)
            packet['mass_rows'][0][key]=value
            with self.assertRaisesRegex(ValueError,'Neutral ground-state'):
                mass_binding.convert_candidates(packet)

    def test_source_decimal_contract(self):
        packet=json.loads((ROOT/'sources/NEUTRAL_H1_HE4_MASS_CANDIDATES.json').read_text())
        for invalid in (True, 1, 'NaN', 'Infinity', '-1', '0', 'bad', '1e400', '1e-400'):
            changed=deepcopy(packet)
            changed['mass_rows'][0]['relative_atomic_mass']=invalid
            with self.assertRaises(ValueError):
                mass_binding.convert_candidates(changed)

    def test_wrong_isotope_cannot_reuse_hydrogen_mass(self):
        packet=json.loads((ROOT/'sources/NEUTRAL_H1_HE4_MASS_CANDIDATES.json').read_text())
        authority=json.loads((ROOT/'sources/raw/WU_R1_species.json').read_text())['rows']
        deuterium='sp_e122664dacbd50a873e3'
        packet['mass_rows'][0]['wu_species_id']=deuterium
        packet['mass_rows'][0]['composition']=authority[deuterium]['compiler_record']['composition']
        with self.assertRaisesRegex(ValueError,'Selected isotope'):
            mass_binding.convert_candidates(packet)


if __name__=='__main__':
    unittest.main()
