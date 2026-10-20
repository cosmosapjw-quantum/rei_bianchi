//! Persistent local process. Frozen BASS121 x=.7 fixture, native48 source.
#[path = "common/mod.rs"]
mod common;
use rei_iso_couple_reference::{
    full_network::{FullState, NetworkError},
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    joint_slab::{SlabSpectrum, joint_rhs},
    mixture_eos::MixtureState,
};
use std::io::{self, BufRead, Write};
fn array(v: &[f64]) -> String {
    format!(
        "[{}]",
        v.iter()
            .map(|x| format!("{x:.17e}"))
            .collect::<Vec<_>>()
            .join(",")
    )
}
fn main() -> io::Result<()> {
    let g = common::load("SIGNED_MINUS", 121);
    let x = 0.7;
    let point = g.point_at_x(x).unwrap();
    let (initial, mut conf, source) = common::fixture(&g, x);
    conf.use_photo = false;
    conf.cmb_temperature_k = 2.7255 / point.a;
    let rate = source.at_redshift(1. / point.a - 1.).unwrap();
    let angle_sum: f64 = source.angular_cells.iter().map(|s| s.count_fraction).sum();
    let en = source.spectral_cells.iter().map(|s| s.energy_ev).collect();
    let j = source
        .spectral_cells
        .iter()
        .map(|s| rate.proper_photons_cm3_s * 1e6 * s.photon_fraction * angle_sum)
        .collect();
    let sp = SlabSpectrum::native(en, j, &conf).unwrap();
    let m = sp.energies().len();
    let dt = g.point_at_x(0.7004).unwrap().time_s - point.time_s;
    let mut init = S::ALL
        .iter()
        .map(|s| initial.gas.nuclei.density_m3(*s))
        .collect::<Vec<_>>();
    init.push(initial.gas.thermal_j_m3);
    let mut out = io::BufWriter::new(io::stdout().lock());
    for line in io::stdin().lock().lines() {
        let line = line?;
        if line == "QUIT" {
            break;
        }
        if line == "INIT" {
            let sig = sp
                .cross_sections()
                .iter()
                .map(|v| array(v))
                .collect::<Vec<_>>()
                .join(",");
            writeln!(
                out,
                "{{\"schema\":\"rei.run07.native48.frozen.local.v1\",\"case\":\"SIGNED_MINUS\",\"x\":{x},\"a\":{:.17e},\"H_per_s\":{:.17e},\"signed_s_over_H\":{:.17e},\"Tcmb_K\":{:.17e},\"dt_s\":{dt:.17e},\"source_id\":\"MD14_Z002_FESC_BB50K_13P6_100_V1\",\"state\":{},\"energies_eV\":{},\"source_m3_s\":{},\"sigma_m2\":[{}],\"chi_eV\":{},\"angle_weight_sum\":{angle_sum:.17e}}}",
                point.a,
                point.h,
                point.s / point.h,
                conf.cmb_temperature_k,
                array(&init),
                array(sp.energies()),
                array(sp.sources()),
                sig,
                array(&sp.thresholds())
            )?;
        } else {
            let result = (|| -> Result<Vec<f64>, NetworkError> {
                let w = line.split_whitespace().collect::<Vec<_>>();
                if w.len() != 17 + m || w[0] != "RHS" {
                    return Err(NetworkError::InvalidInput);
                }
                let mask = w[1].parse::<u8>().map_err(|_| NetworkError::InvalidInput)?;
                let photo = match w[2] {
                    "0" => false,
                    "1" => true,
                    _ => return Err(NetworkError::InvalidInput),
                };
                let v = w[3..]
                    .iter()
                    .map(|v| v.parse::<f64>().map_err(|_| NetworkError::InvalidInput))
                    .collect::<Result<Vec<_>, _>>()?;
                if v.iter().any(|x| !x.is_finite()) {
                    return Err(NetworkError::NonFinite);
                }
                let mut n = [0.; 13];
                n.copy_from_slice(&v[..13]);
                let s = FullState {
                    gas: MixtureState {
                        nuclei: IsotopeNumberState::new(n)
                            .map_err(|_| NetworkError::NegativePopulation)?,
                        thermal_j_m3: v[13],
                    },
                    photon_bins: vec![],
                    escaped_j_m3: 0.,
                    cmb_reservoir_j_m3: 0.,
                    elapsed_s: 0.,
                };
                joint_rhs(&s, &conf, &sp, &v[14..], mask, photo)
            })();
            match result {
                Ok(v) => {
                    write!(out, "OK")?;
                    for a in v {
                        write!(out, " {a:.17e}")?;
                    }
                    writeln!(out)?;
                }
                Err(e) => writeln!(out, "ERR {e:?}")?,
            }
        }
        out.flush()?;
    }
    Ok(())
}
