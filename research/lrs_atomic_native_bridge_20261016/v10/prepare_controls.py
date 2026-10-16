"""Add V10 opt-in clocks to the isolated PR150 + PR167 donor copy.

Run after applying the checked-in PR167 driver/transport patches and the
V10 seed. All replacements require unique exact seams and fail closed.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def once(s: str, old: str, new: str) -> str:
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"expected one seam, found {count}: {old[:80]!r}")
    return s.replace(old, new, 1)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("owner_copy", type=Path)
    a = p.parse_args()
    path = a.owner_copy / "rust/rei_microphysics/src/axbi_driver.rs"
    s = path.read_text()
    s = once(s, "    prepared: Arc<PreparedAbsorption>,\n", "    prepared: Arc<PreparedAbsorption>,\n    half_opacity: bool,\n")
    s = once(s, "        let absorbers = [nh * (1.0 - x), nhe * (1.0 - y - z), nhe * y];", '''        let endpoint_absorbers = [nh * (1.0 - x), nhe * (1.0 - y - z), nhe * y];
        let [ox, oy, oz] = self.gas.fractions;
        let old_absorbers = [nh * (1.0 - ox), nhe * (1.0 - oy - oz), nhe * oy];
        let absorbers = if self.half_opacity {
            std::array::from_fn(|i| 0.5 * (old_absorbers[i] + endpoint_absorbers[i]))
        } else { endpoint_absorbers };''')
    s = once(s, "        let photo = absorption.photo;\n        let point = AxbiProvider.point(&gas, nh, nhe, 0.0, 2.7255 / self.a, photo)?;", '''        let mut photo = absorption.photo;
        if self.half_opacity {
            for i in 0..3 {
                if endpoint_absorbers[i] == 0.0 {
                    if absorbers[i] > 0.0 && photo.gamma_s[i] > 0.0 {
                        return Err(err("V10_ZERO_ENDPOINT_ABSORBER"));
                    }
                } else {
                    let factor = absorbers[i] / endpoint_absorbers[i];
                    photo.gamma_s[i] *= factor;
                    photo.heat_erg_per_absorber_s[i] *= factor;
                }
            }
        }
        let point = AxbiProvider.point(&gas, nh, nhe, 0.0, 2.7255 / self.a, photo)?;''')
    s = once(s, "    research_numerics: BassResearchNumerics,\n", "    research_numerics: BassResearchNumerics,\n    v10_no_radiation: bool,\n    v10_half_opacity: bool,\n")
    s = once(s, "    pub excluded_dr_ev: f64,\n", '''    pub excluded_dr_ev: f64,
    pub v10_rr_cooling_ev: [f64; 3],
    pub v10_dr_cooling_ev: f64,
    pub v10_ci_cooling_ev: [f64; 3],
    pub v10_ce_cooling_ev: [f64; 3],
    pub v10_freefree_cooling_ev: f64,
    pub v10_photo_heat_ev: f64,
    pub v10_photo_binding_ev: f64,
''')
    s = once(s, "            research_numerics: BassResearchNumerics::Legacy,\n", "            research_numerics: BassResearchNumerics::Legacy,\n            v10_no_radiation: false,\n            v10_half_opacity: false,\n")
    s = once(s, "    pub fn new(config: DriverConfig) -> Result<(Self, DriverState), ForwardError> {", '''    /// Research-only controls on the isolated frozen owner copy.
    pub fn v10_set_control(&mut self, numerics: BassResearchNumerics,
        no_radiation: bool, half_opacity: bool) {
        self.research_numerics = numerics;
        self.v10_no_radiation = no_radiation;
        self.v10_half_opacity = half_opacity;
    }
    pub fn v10_initial_energy(&self) -> f64 { self.initial_energy }
    pub fn new(config: DriverConfig) -> Result<(Self, DriverState), ForwardError> {''')
    s = once(s, "            prepared: Arc::new(prepared),\n", "            prepared: Arc::new(prepared),\n            half_opacity: self.v10_half_opacity,\n")
    s = once(s, "        if self.research_numerics.split_birth() {\n            let birth = self.inject_birth(&mut s, dt)?;", '''        if self.v10_no_radiation {
            self.chemical_stage(&mut s, dt, counter)?;
        } else if self.research_numerics.split_birth() {
            let birth = self.inject_birth(&mut s, dt)?;''')
    s = once(s, '''                next.ledgers.escaped_u += rhs.escape_erg_cm3_s * dt / (nh * c.ev_erg);''', '''                next.ledgers.escaped_u += rhs.escape_erg_cm3_s * dt / (nh * c.ev_erg);
                for k in 0..3 {
                    next.ledgers.v10_rr_cooling_ev[k] += rhs.rr_thermal_sink_erg_cm3_s[k] * dt / (nh * c.ev_erg);
                    next.ledgers.v10_ci_cooling_ev[k] += rhs.ci_thermal_sink_erg_cm3_s[k] * dt / (nh * c.ev_erg);
                    next.ledgers.v10_ce_cooling_ev[k] += rhs.ce_thermal_sink_erg_cm3_s[k] * dt / (nh * c.ev_erg);
                }
                next.ledgers.v10_dr_cooling_ev += rhs.dr_thermal_sink_erg_cm3_s * dt / (nh * c.ev_erg);
                next.ledgers.v10_freefree_cooling_ev += rhs.freefree_thermal_sink_erg_cm3_s * dt / (nh * c.ev_erg);
                next.ledgers.v10_photo_heat_ev += (rhs.photo_input_erg_cm3_s
                    - rhs.photo_events_cm3_s.iter().enumerate().map(|(k,e)|
                        e * c.threshold_ev[k] * c.ev_erg).sum::<f64>()) * dt / (nh * c.ev_erg);
                next.ledgers.v10_photo_binding_ev += rhs.photo_events_cm3_s.iter().enumerate().map(|(k,e)|
                    e * c.threshold_ev[k]).sum::<f64>() * dt / nh;''')
    s = once(s, "        ci_floor_events: array(21),\n    })", "        ci_floor_events: array(21),\n        ..Ledgers::default()\n    })")
    path.write_text(s)


if __name__ == "__main__":
    main()
