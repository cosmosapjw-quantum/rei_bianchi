//! RUN08 exact native finite source packet and retarded RHS verification server.
#[path = "common/mod.rs"]
mod common;
use rei_iso_couple_reference::{
    HHeModel,
    bass_optical_birth::{BassOpticalBirthBridge, LayerControls},
    bass_source_bridge::BassSourceBridge,
    isotope_state::{IsotopeNumberState, IsotopeSpecies as S},
    mixture_eos::MixtureState,
    positive_spectral::SpectralMode,
    retarded_joint::{RetardedContext, rhs_x},
    retarded_transport::RetardedControls,
};
use std::io::{self, BufRead, Write};
fn arr(v: &[f64]) -> String {
    format!(
        "[{}]",
        v.iter()
            .map(|x| format!("{x:.17e}"))
            .collect::<Vec<_>>()
            .join(",")
    )
}
fn main() -> io::Result<()> {
    let args = std::env::args().collect::<Vec<_>>();
    let case = args.get(1).map_or("SIGNED_MINUS", |v| v.as_str());
    let g = common::load(case, 121);
    let x0 = 0.7;
    let x1 = 0.7004;
    let p0 = g.point_at_x(x0).unwrap();
    let p1 = g.point_at_x(x1).unwrap();
    let (initial, mut conf, source) = common::fixture(&g, x0);
    conf.use_photo = false;
    let gm = g.point_at_time(0.5 * (p0.time_s + p1.time_s)).unwrap();
    let r = (p0.a / gm.a).powi(3);
    let n = S::ALL.map(|s| initial.gas.nuclei.density_m3(s) * r);
    let gas_mid = MixtureState {
        nuclei: IsotopeNumberState::new(n).unwrap(),
        thermal_j_m3: initial.gas.thermal_j_m3 * r.powf(5. / 3.),
    };
    let b = BassOpticalBirthBridge(
        BassSourceBridge::new(source, g.clone(), 2.7255).unwrap(),
        RetardedControls::new(4, 2, SpectralMode::OriginalCellMean)
            .unwrap()
            .with_threshold_events(),
        LayerControls::default(),
    );
    let (mut cohorts, seed, panels) = b
        .emit_births(p0.time_s, p1.time_s - p0.time_s, &conf, &gas_mid)
        .unwrap();
    cohorts.sort_by(|a, b| a.birth_time_s.total_cmp(&b.birth_time_s));
    if let Ok(path) = std::env::var("RUN08_PACKET_BITS") {
        let mut bits = Vec::new();
        for co in &cohorts {
            for f in [
                co.birth_time_s,
                co.energy_at_birth_ev,
                co.direction_at_birth[2],
                co.n_comoving_m3,
            ] {
                bits.extend_from_slice(&f.to_le_bytes());
            }
        }
        std::fs::write(path, bits)?;
    }
    let mut birth_x = Vec::new();
    let mut cached = (f64::NAN, 0.);
    for c in &cohorts {
        if c.birth_time_s != cached.0 {
            cached = (c.birth_time_s, g.x_at_time(c.birth_time_s).unwrap());
        }
        birth_x.push(cached.1);
    }
    let mut state = S::ALL.map(|s| initial.gas.nuclei.density_m3(s)).to_vec();
    state.push(initial.gas.thermal_j_m3);
    let mut out = io::BufWriter::new(io::stdout().lock());
    for line in io::stdin().lock().lines() {
        let line = line?;
        if line == "QUIT" {
            break;
        }
        if line == "INIT" {
            let rows = cohorts
                .iter()
                .zip(&birth_x)
                .map(|(c, x)| {
                    let a = c.birth_geometry.volume_factor().unwrap().cbrt();
                    let bp = (c.birth_geometry.scale_factors[2] / a).ln() / 2.;
                    arr(&[
                        *x,
                        c.birth_time_s,
                        a,
                        bp,
                        c.energy_at_birth_ev,
                        c.direction_at_birth[2],
                        c.n_comoving_m3 / p0.a.powi(3),
                        c.spectral_index as f64,
                        c.angular_index as f64,
                    ])
                })
                .collect::<Vec<_>>()
                .join(",");
            let chi = HHeModel::controlled_fixture().threshold_ev;
            writeln!(
                out,
                "{{\"schema\":\"rei.run08.finite-native-birth.v1\",\"case\":\"{case}\",\"x0\":{x0},\"x1\":{x1},\"a0\":{:.17e},\"t0_s\":{:.17e},\"t1_s\":{:.17e},\"tau_seed\":{seed:.17e},\"panels\":{panels},\"state\":{},\"chi_eV\":{},\"columns\":[\"x_birth\",\"t_birth_s\",\"a_birth\",\"b_birth\",\"E_birth_eV\",\"mu_birth\",\"count_per_initial_proper_m3\",\"spectral_index\",\"angular_index\"],\"cohorts\":[{rows}]}}",
                p0.a,
                p0.time_s,
                p1.time_s,
                arr(&state),
                arr(&[chi[0], chi[1], chi[2], conf.deuterium.chi_d_ev()])
            )?;
        } else if line.starts_with("RHS ") {
            let w = line.split_whitespace().collect::<Vec<_>>();
            let v = w[1..]
                .iter()
                .map(|s| s.parse::<f64>())
                .collect::<Result<Vec<_>, _>>();
            match v {
                Ok(v) if v.len() == 16 + cohorts.len() => {
                    let x = v[0];
                    let active = v[1] as usize;
                    let mut u = [0.; 14];
                    u.copy_from_slice(&v[2..16]);
                    let point = g.point_at_x(x).unwrap();
                    let ctx = RetardedContext {
                        point,
                        a_ref: p0.a,
                        cohorts: &cohorts,
                        active,
                        config: &conf,
                        gas_mask: 7,
                        photo: true,
                        expansion: true,
                    };
                    match rhs_x(&u, &v[16..], &ctx) {
                        Ok(o) => writeln!(
                            out,
                            "OK {}",
                            o.iter()
                                .map(|q| format!("{q:.17e}"))
                                .collect::<Vec<_>>()
                                .join(" ")
                        )?,
                        Err(e) => writeln!(out, "ERR {e:?}")?,
                    };
                }
                _ => writeln!(out, "ERR input")?,
            }
        } else {
            writeln!(out, "ERR command")?;
        }
        out.flush()?;
    }
    Ok(())
}
