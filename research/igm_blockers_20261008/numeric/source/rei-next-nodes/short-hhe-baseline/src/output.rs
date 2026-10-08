use crate::{
    coupled::{self, State},
    err, material,
    radiation::{self, Grid},
    Fallible,
};
use rei_microphysics::igm_config::HistoryConfig;
use std::{fs::File, io::Write};
pub const HEADER:&str="ln_a,z,x_hii,x_heii,x_heiii,ne_per_h,T,Tcmb,w,Gamma_hi,Gamma_hei,Gamma_heii,Nactive,Eactive,emitted_N,emitted_E,abs_HI,abs_HeI,abs_HeII,out_N,out_E,redshift_E,escape_E,work_E,cmb_reservoir_E,ci_HI,ci_HeI,ci_HeII,rr_HII,rr_HeII,rr_HeIII,dr_HeII,ci_floor_HI,ci_floor_HeI,ci_floor_HeII,ce_cap_HI_E,ce_cap_HeI_E,ce_cap_HeII_E,excluded_dr_E,number_residual,energy_residual";
pub fn row(cfg: &HistoryConfig, grid: &Grid, s: &State, initial: f64) -> Fallible<Vec<f64>> {
    let p = cfg.background.at_ln_a(s.s).map_err(err)?;
    let eos = material::gas(s.y)?
        .eos(p.n_h_cm3, p.n_he_cm3)
        .map_err(err)?;
    let gamma = radiation::gamma(grid, s.s, &s.density, p)?;
    let l = s.radiation;
    let m = s.material;
    let b = coupled::budget(cfg, s, initial)?;
    let mut r = vec![
        s.s,
        p.redshift,
        s.y[0],
        s.y[1],
        s.y[2],
        eos.electron_density_cm3 / p.n_h_cm3,
        eos.temperature_k,
        p.tcmb_k,
        s.y[3],
    ];
    r.extend(gamma);
    r.extend(s.active);
    r.extend([l.qn, l.qe]);
    r.extend(l.an);
    r.extend([l.outn, l.oute, l.red, m.escape, m.work, m.cmb]);
    r.extend(m.ci);
    r.extend(m.rr);
    r.push(m.dr);
    r.extend(m.floor);
    r.extend(m.cap);
    r.extend([m.excluded_dr, b[0], b[1]]);
    assert_eq!(r.len(), 41);
    Ok(r)
}
pub fn write_row(f: &mut File, row: &[f64]) -> Fallible<()> {
    for (i, x) in row.iter().enumerate() {
        if i > 0 {
            write!(f, ",").map_err(err)?;
        }
        write!(f, "{x:.17e}").map_err(err)?;
    }
    writeln!(f).map_err(err)?;
    f.flush().map_err(err)
}
pub fn history(cfg: &HistoryConfig, grid: &Grid, m: usize, phases: bool) -> Fallible<()> {
    let n = if phases { 3 * m } else { m };
    let tag = if phases { "phases" } else { "endpoint" };
    let name = format!("results/B_{tag}_m{m}_g{}.csv", grid.order);
    let mut f = File::create(name).map_err(err)?;
    writeln!(f, "{HEADER}").map_err(err)?;
    let mut s = State::new(cfg, grid)?;
    let p = cfg.background.at_ln_a(cfg.start).map_err(err)?;
    let initial = s.y[3] + material::binding(s.y, p.n_he_cm3 / p.n_h_cm3);
    write_row(&mut f, &row(cfg, grid, &s, initial)?)?;
    let mut trace =
        File::create(format!("results/B_{tag}_m{m}_g{}_steps.csv", grid.order)).map_err(err)?;
    writeln!(
        trace,
        "step,ln_a,iterations,scaled_residual,number_allowance_ratio,energy_allowance_ratio"
    )
    .map_err(err)?;
    let mut branches =
        File::create(format!("results/B_{tag}_m{m}_g{}_branches.csv", grid.order)).map_err(err)?;
    writeln!(branches,"step,class,stage,count,Tmin,Tmax,branch_any,branch_all,continuity_checks,continuity_max_relative").map_err(err)?;
    for i in 1..=n {
        let end = radiation::time_at(cfg, i, n);
        s = coupled::advance(cfg, grid, &s, end, initial)
            .map_err(|e| format!("B {tag} m={m} g={} step={i}: {e}", grid.order))?;
        writeln!(
            trace,
            "{i},{:.17e},{},{:.17e},{:.17e},{:.17e}",
            s.s, s.iterations, s.norm, s.n_ratio, s.e_ratio
        )
        .map_err(err)?;
        trace.flush().map_err(err)?;
        for (class, t) in [("accepted", s.accepted_trace), ("trial", s.trial_trace)] {
            for (k, summary) in t.stages.iter().enumerate() {
                writeln!(
                    branches,
                    "{i},{class},{k},{},{:.17e},{:.17e},{},{},{},{:.17e}",
                    summary.count,
                    summary.min,
                    summary.max,
                    summary.any,
                    summary.all,
                    t.continuity_checks,
                    t.continuity_max_relative
                )
                .map_err(err)?;
            }
        }
        branches.flush().map_err(err)?;
        if i == n || (phases && i % m == 0) {
            write_row(&mut f, &row(cfg, grid, &s, initial)?)?;
        }
    }
    println!("ARRAY_PEAK density_vectors={} density_scalar_slots={} distinct_abscissae={} grid_coordinate_scalar_slots={}",crate::diagnostics::array_peak().0,crate::diagnostics::array_peak().1,grid.nodes.len(),2*grid.nodes.len());
    println!(
        "B {tag} m={m} order={} transactions={n} PASS per-step physical/nonlinear/original budgets",
        grid.order
    );
    Ok(())
}
