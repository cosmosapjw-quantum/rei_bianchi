use rei_microphysics::axbi_covariant_driver::{compiled_identity, Driver, DriverConfig};
use std::{fs, path::Path};
fn pad(v: &mut Vec<f64>, n: usize, m: usize) {
    assert_eq!(v.len() % n, 0);
    let mut x = Vec::with_capacity(v.len() / n * m);
    for row in v.chunks_exact(n) {
        x.extend(row);
        x.resize(x.len() + m - n, 0.);
    }
    *v = x;
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let v = std::env::args().skip(1).collect::<Vec<_>>();
    if v.len() != 4 {
        return Err("usage OLD_CONFIG ADJUSTED_COPY_CHECKPOINT NEW_CONFIG NEW_DIR".into());
    }
    let c0 = fs::read_to_string(&v[0])?;
    let c1 = fs::read_to_string(&v[2])?;
    let d0 = Driver::new(DriverConfig::read(&c0)?)?.0;
    let d1 = Driver::new(DriverConfig::read(&c1)?)?.0;
    let n = d0.transport.n_energy();
    let m = d1.transport.n_energy();
    if m <= n
        || !d0.config.reactive_hi
        || !d1.config.reactive_hi
        || d0.transport.edges() != &d1.transport.edges()[..=n]
        || c1 != format!("{c0}reactive_extra_high_cells={}\n", m - n)
    {
        return Err("migration domain".into());
    }
    let q = d1.required_source_q_bounds()?;
    let edges = d1.transport.edges();
    if q[0] < edges[0] || q[1] > edges[m] {
        return Err("source envelope not covered".into());
    }
    let mut s = d0.read_checkpoint(Path::new(&v[1]))?;
    let old = d0.photon_pool_inventory(&s)?;
    let r0 = d0.residuals(&s)?;
    let p0 = d0.endpoint_photo(&s)?;
    for x in [
        &mut s.photons,
        &mut s.photon_energy_ref,
        &mut s.photon_support_lo,
        &mut s.photon_support_hi,
        &mut s.photon_inactive_number,
        &mut s.photon_inactive_energy_ref,
    ] {
        pad(x, n, m);
    }
    for p in [&mut s.heii_above, &mut s.hei_middle, &mut s.hi_below] {
        let p = p.as_mut().ok_or("missing pool")?;
        for x in [
            &mut p.number,
            &mut p.energy_ref,
            &mut p.support_lo,
            &mut p.support_hi,
        ] {
            pad(x, n, m);
        }
    }
    d1.validate(&s, 1e-8)?;
    let new = d1.photon_pool_inventory(&s)?;
    let r1 = d1.residuals(&s)?;
    let p1 = d1.endpoint_photo(&s)?;
    for (a, b) in old.iter().zip(new) {
        if (a - b).abs() > 1e-13 * a.abs().max(1.) {
            return Err("inventory migration mismatch".into());
        }
    }
    for (a, b) in p0
        .gamma_s
        .iter()
        .chain(p0.heat_erg_per_absorber_s.iter())
        .zip(p1.gamma_s.iter().chain(p1.heat_erg_per_absorber_s.iter()))
    {
        if (a - b).abs() > 1e-12 * a.abs().max(1e-300) {
            return Err("rate migration mismatch".into());
        }
    }
    let out = Path::new(&v[3]);
    fs::create_dir(out)?;
    fs::write(out.join("config.cfg"), &c1)?;
    fs::write(out.join("source_identity.txt"), compiled_identity())?;
    d1.save_checkpoint(&out.join("checkpoint.txt"), &s)?;
    fs::write(out.join("MIGRATION.txt"),format!("old_cells={n}\nnew_cells={m}\nrequired_q_min={}\nrequired_q_max={}\nnew_grid_max={}\nold_inventory={old:?}\nnew_inventory={new:?}\nold_residual={r0:?}\nnew_residual={r1:?}\naccepted={}\n",q[0],q[1],edges[m],s.accepted))?;
    println!("MIGRATED {n}->{m} source q {q:?} max={}", edges[m]);
    Ok(())
}
