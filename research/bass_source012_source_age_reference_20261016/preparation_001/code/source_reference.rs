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
    n: usize,
) -> Result<(Driver, Accepted, Vec<f64>, Vec<PhotonState>), Box<dyn std::error::Error>> {
    let (d0, s0) = driver(q, 8, 16)?;
    let mut cfg = d0.config.clone();
    cfg.energy_subdivisions = 8;
    let (d, _) = Driver::new(cfg)?;
    let x0 = s0.gas_owner.a.ln();
    let a1 = s0.gas_owner.a * 0.002f64.exp();
    let width = a1.ln() - x0;
    let mut births = vec![];
    let mut templates = vec![];
    for i in 0..n {
        let x = x0 + width * (i as f64 + 0.5) / n as f64;
        let a = x.exp();
        let g = d.geometry_point(a)?.geometry()?;
        let h = d.geometry_point(a)?.h_per_s;
        let mut p = d.transport.empty_state();
        d.transport
            .inject(&mut p, &g, 1. / a - 1., width / n as f64 / h)?;
        births.push(x);
        templates.push(p);
    }
    Ok((d, s0, births, templates))
}
pub fn server(q: f64, n: usize) -> Result<(), Box<dyn std::error::Error>> {
    let (d, s0, births, templates) = setup(q, n)?;
    let x0 = s0.gas_owner.a.ln();
    let a1 = s0.gas_owner.a * 0.002f64.exp();
    let x1 = a1.ln();
    let mesh = common_mesh(s0.gas_owner.a, a1, &[8,16,32], 1);
    let cells = d.transport.cell_count();
    let mut initial = flat(&s0)?;
    initial.resize(4 + 2*cells*n, 0.);
    let inject = templates
        .iter()
        .map(|p| {
            let mut v = p.number.clone();
            v.extend(&p.energy_ref);
            v
        })
        .collect::<Vec<_>>();
    let supports_lo = templates.iter().map(|p| p.support_lo.clone()).collect::<Vec<_>>();
    let supports_hi = templates.iter().map(|p| p.support_hi.clone()).collect::<Vec<_>>();
    let f = d.n_he0_cm3 / d.n_h0_cm3;
    let model = rei_microphysics::HHeModel::controlled_fixture();
    let kb_ev = model.kb_erg_k / model.ev_erg;
    let width = x1-x0;
    let weight = width / n as f64;
    let config_debug = format!("{:?}", d.config);
    println!("{{\"protocol\":\"SOURCE012_RHS_ONLY_V1\",\"native_base\":\"35d9747a0bbedcafdb568467ce7c1e7a25f965b6\",\"overlay\":\"553ce556d9f8662290c000ec675c7e6007c9d895\",\"q\":{q},\"birth_count\":{n},\"width\":{width},\"quadrature_weight_dln_a\":{weight},\"config_debug\":{:?},\"x_units\":\"dimensionless ln(a)\",\"f_units\":\"nHe0/nH0\",\"w_units\":\"eV/H\",\"kb_units\":\"eV/K\",\"x0\":{x0},\"x1\":{x1},\"births\":{:?},\"mesh\":{:?},\"initial\":{:?},\"inject\":{:?},\"cells\":{cells},\"support_lo\":{:?},\"support_hi\":{:?},\"f\":{f},\"kb_eV_K\":{kb_ev},\"ev_erg\":{},\"state_order\":\"h,y,z,w_eV/H,cohort_N[],cohort_Uref[],...\",\"moment_units\":\"N/H,eV_reference/H\",\"source_config\":\"supplier_driver_q-0.1_nmu8_cells16_subdiv8_initial8000K\",\"Gamma_s\":null,\"heat\":null,\"prepared_nodes\":null,\"observations_status\":\"NOT_RUN\"}}",config_debug,births,mesh,initial,inject,supports_lo,supports_hi,model.ev_erg);
    for line in io::stdin().lock().lines() {
        let v = line?
            .split_whitespace()
            .map(str::parse::<f64>)
            .collect::<Result<Vec<_>, _>>()?;
        if v.len() != 1 + 4 + 2*cells*n || v.iter().any(|x| !x.is_finite()) {
            return Err("invalid RHS state shape/nonfinite".into());
        }
        let x = v[0];
        if x < x0 || x > x1 { return Err("RHS domain".into()); }
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
            if x < births[i] && y[off..off+2*cells].iter().any(|v| *v != 0.) {
                return Err("unborn cohort must be zero".into());
            }
            let mut state = template.clone();
            state.number = y[off..off + cells].to_vec();
            state.energy_ref = y[off + cells..off + 2 * cells].to_vec();
            for k in 0..cells {
                if state.number[k] == 0. {
                    if state.energy_ref[k] != 0. { return Err("zero N requires zero Uref".into()); }
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
