"""Create the opt-in native V10 seed in an isolated copy of PR150's owner.

The original owner's source is the input. This preparatory patch only exposes
the shared V7/V8 mixed H/He initial state and updates its energy reference;
clock controls are added separately after the scientific contract is frozen.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("owner_copy", type=Path)
    args = parser.parse_args()
    path = args.owner_copy / "rust/rei_microphysics/src/axbi_driver.rs"
    source = path.read_text()
    anchor = "impl Driver {\n    pub fn new(config: DriverConfig)"
    if source.count(anchor) != 1:
        raise SystemExit("owner Driver::new seam missing or ambiguous")
    seed = '''impl Driver {
    /// V10 opt-in source-on seed. No original production entry point calls it.
    pub fn v10_seed(config: DriverConfig) -> Result<(Self, DriverState), ForwardError> {
        let (mut driver, mut state) = Self::new(config)?;
        let nh = driver.n_h0_cm3 / state.a.powi(3);
        let nhe = driver.n_he0_cm3 / state.a.powi(3);
        state.gas = IgmGasState::from_temperature([0.075, 0.12, 0.03], nh, nhe, 15000.0)?;
        driver.initial_energy = driver.total_energy(&state)?;
        Ok((driver, state))
    }
    pub fn new(config: DriverConfig)'''
    path.write_text(source.replace(anchor, seed, 1))


if __name__ == "__main__":
    main()
