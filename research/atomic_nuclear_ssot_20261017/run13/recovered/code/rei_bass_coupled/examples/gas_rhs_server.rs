//! Safe, offline line protocol for independent numerical integrators. No FFI/unsafe.
use rei_iso_couple_reference::{
    HHeModel,
    deuterium_atomic::DAtomicProvider,
    full_network::{self, FullState, NetworkConfig, NetworkError},
    gas_reference_rhs::gas_rates,
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::MixtureState,
};
use std::io::{self, BufRead, Write};
fn execute(line: &str) -> Result<Vec<f64>, NetworkError> {
    let words: Vec<_> = line.split_whitespace().collect();
    let tight = words.first() == Some(&"STEP_TIGHT");
    let step = words.first() == Some(&"STEP") || tight;
    if words.first() != Some(&"RHS") && !step {
        return Err(NetworkError::InvalidInput);
    }
    let vals = words[1..]
        .iter()
        .map(|w| w.parse::<f64>().map_err(|_| NetworkError::InvalidInput))
        .collect::<Result<Vec<_>, _>>()?;
    if vals.len() != 16 + usize::from(step) || !vals.iter().all(|v| v.is_finite()) {
        return Err(NetworkError::InvalidInput);
    }
    if vals[0] < 0. || vals[0] > 7. || vals[0].fract() != 0. {
        return Err(NetworkError::InvalidInput);
    }
    let mask = vals[0] as u8;
    let tcmb = vals[1];
    let offset = 2 + usize::from(step);
    let mut n = [0.; 13];
    n.copy_from_slice(&vals[offset..offset + 13]);
    let s = FullState {
        gas: MixtureState {
            nuclei: IsotopeNumberState::new(n).map_err(|_| NetworkError::NegativePopulation)?,
            thermal_j_m3: vals[offset + 13],
        },
        photon_bins: vec![],
        escaped_j_m3: 0.,
        cmb_reservoir_j_m3: 0.,
        elapsed_s: 0.,
    };
    let h = HHeModel::controlled_fixture().threshold_ev[0];
    let mut c = NetworkConfig::source_bound(
        DAtomicProvider::new(h, h + 0.0037, "MANUFACTURED_D_H_DELTA_CHI")
            .map_err(|_| NetworkError::SourceMismatch)?,
        "MD14_Z002_FESC_BB50K_13P6_100_V1",
    );
    c.use_photo = false;
    c.cmb_temperature_k = tcmb;
    c.use_collisions = mask & 1 != 0;
    c.use_cx = mask & 2 != 0;
    c.use_cmb = mask & 4 != 0;
    if tight {
        c.cx_controls.atol_normalized = 1e-15;
        c.cx_controls.rtol = 1e-11;
    }
    if step {
        let out = full_network::step(&s, &c, vals[2])?;
        let mut a = Vec::with_capacity(27);
        for sp in S::ALL {
            a.push(out.state.gas.nuclei.density_m3(sp));
        }
        a.extend([
            out.state.gas.thermal_j_m3,
            out.state.escaped_j_m3,
            out.state.cmb_reservoir_j_m3,
        ]);
        a.extend(out.budget.ci_events_m3);
        a.extend(out.budget.rr_events_m3);
        a.extend([
            out.budget.dr_hei_m3,
            out.budget.cx_signed_m3,
            out.budget.freefree_integrated_j_m3,
        ]);
        Ok(a)
    } else {
        let r = gas_rates(&s, &c, mask)?;
        let mut a = r.vector().to_vec();
        a.push(r.chemical);
        Ok(a)
    }
}
fn main() -> io::Result<()> {
    let mut out = io::BufWriter::new(io::stdout().lock());
    for line in io::stdin().lock().lines() {
        let line = line?;
        if line == "QUIT" {
            break;
        }
        match execute(&line) {
            Ok(v) => {
                write!(out, "OK")?;
                for x in v {
                    write!(out, " {x:.17e}")?;
                }
                writeln!(out)?;
            }
            Err(e) => writeln!(out, "ERR {e:?}")?,
        }
        out.flush()?;
    }
    Ok(())
}
