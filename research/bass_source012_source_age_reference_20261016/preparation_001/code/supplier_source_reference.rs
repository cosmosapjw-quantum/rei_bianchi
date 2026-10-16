//! Actual MD14 schedule plus signed native geometry, continuous tagged moments.
use crate::{driver, native_owner::*};
use rei_microphysics::{
    axbi_covariant_transport::PhotonState,
    axbi_driver::Driver,
    axbi_rates::AxbiProvider,
    igm_state::{w_erg_per_h_to_ev, w_ev_per_h_to_erg, IgmGasState},
    igm_thermal::IgmPhotoInput,
};
use std::{
    fs,
    io::{self, BufRead},
    path::Path,
};
fn flat(s: &Accepted) -> Result<Vec<f64>, Box<dyn std::error::Error>> {
    let g = &s.gas_owner.gas;
    let mut v = vec![
        g.fractions[0],
        g.fractions[1],
        g.fractions[2],
        w_erg_per_h_to_ev(g.w_erg_per_h)?,
    ];
    for c in &s.cohorts {
        v.extend(&c.surviving.number);
        v.extend(&c.surviving.energy_ref);
    }
    Ok(v)
}
fn setup(
    q: f64,
) -> Result<(Driver, Accepted, Vec<f64>, Vec<PhotonState>), Box<dyn std::error::Error>> {
    let (d0, s0) = driver(q, 8, 16)?;
    let mut cfg = d0.config.clone();
    cfg.energy_subdivisions = 8;
    let (d, _) = Driver::new(cfg)?;
    let x0 = s0.gas_owner.a.ln();
    let width = 0.002;
    let mut births = vec![];
    let mut templates = vec![];
    for i in 0..8 {
        let x = x0 + width * (i as f64 + 0.5) / 8.;
        let a = x.exp();
        let g = d.geometry_point(a)?.geometry()?;
        let h = d.geometry_point(a)?.h_per_s;
        let mut p = d.transport.empty_state();
        d.transport
            .inject(&mut p, &g, 1. / a - 1., width / 8. / h)?;
        births.push(x);
        templates.push(p);
    }
    Ok((d, s0, births, templates))
}
pub fn native(q: f64, out: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let (d, s0, _births, _) = setup(q)?;
    let to = s0.gas_owner.a * 0.002f64.exp();
    fs::create_dir_all(out)?;
    for level in [1, 2, 4] {
        let mesh = common_mesh(s0.gas_owner.a, to, &[8], level);
        let s = trial_on_mesh(&d, &s0, to, 8, &mesh, &mut 0)?;
        fs::write(
            out.join(format!("source_native_q{q}_level{level}.json")),
            format!("{{\"q\":{q},\"level\":{level},\"state\":{:?}}}", flat(&s)?),
        )?;
    }
    Ok(())
}
pub fn server(q: f64) -> Result<(), Box<dyn std::error::Error>> {
    let (d, s0, births, templates) = setup(q)?;
    let x0 = s0.gas_owner.a.ln();
    let x1 = x0 + 0.002;
    let cells = d.transport.cell_count();
    let initial = flat(&s0)?;
    let inject = templates
        .iter()
        .map(|p| {
            let mut v = p.number.clone();
            v.extend(&p.energy_ref);
            v
        })
        .collect::<Vec<_>>();
    println!("{{\"x0\":{x0},\"x1\":{x1},\"births\":{:?},\"initial\":{:?},\"inject\":{:?},\"cells\":{cells}}}",births,initial,inject);
    for line in io::stdin().lock().lines() {
        let v = line?
            .split_whitespace()
            .map(str::parse::<f64>)
            .collect::<Result<Vec<_>, _>>()?;
        let x = v[0];
        let y = &v[1..];
        let a = x.exp();
        let point = d.geometry_point(a)?;
        let geometry = point.geometry()?;
        let h = point.h_per_s;
        let gas = IgmGasState::new([y[0], y[1], y[2]], w_ev_per_h_to_erg(y[3])?)?;
        let nh = d.n_h0_cm3 / a.powi(3);
        let nhe = d.n_he0_cm3 / a.powi(3);
        let ab = [nh * (1. - y[0]), nhe * (1. - y[1] - y[2]), nhe * y[1]];
        let mut photo = IgmPhotoInput::default();
        let mut moments = vec![];
        for (i, template) in templates.iter().enumerate() {
            let off = 4 + 2 * cells * i;
            let mut state = template.clone();
            state.number = y[off..off + cells].to_vec();
            state.energy_ref = y[off + cells..off + 2 * cells].to_vec();
            for k in 0..cells {
                if state.number[k] == 0. {
                    state.support_lo[k] = 0.;
                    state.support_hi[k] = 0.;
                }
            }
            let prep = d.transport.prepare(&state, &geometry)?;
            let (dn, du, p) = prep.research_continuous_moment_rhs(ab, nh)?;
            for k in 0..3 {
                photo.gamma_s[k] += p.gamma_s[k];
                photo.heat_erg_per_absorber_s[k] += p.heat_erg_per_absorber_s[k];
            }
            moments.extend(dn.into_iter().map(|r| r / h));
            moments.extend(du.into_iter().map(|r| r / h));
        }
        let rhs = AxbiProvider.point(&gas, nh, nhe, h, 2.7255 / a, photo)?.rhs;
        let mut dy = rhs.fraction_dt.map(|r| r / h).to_vec();
        dy.push(rhs.w_dt_erg_per_h_s / rei_microphysics::HHeModel::controlled_fixture().ev_erg / h);
        dy.extend(moments);
        println!(
            "{}",
            dy.iter()
                .map(|v| format!("{v:.17e}"))
                .collect::<Vec<_>>()
                .join(" ")
        );
    }
    Ok(())
}
