//! Read-only probe controls. No library solver, opacity, or source changes.
use rei_microphysics::{
    coupled_primary::PrimaryPacket,
    igm_config::HistoryConfig,
    igm_photo::{igm_photo_rates, IgmPhotoRates},
};
use short_hhe_control::{
    coupled::State,
    err, material, positive, product,
    radiation::{self, Grid},
    Fallible,
};
#[derive(Debug)]
pub struct Readout {
    /// Original owner's per-absorber photoionization observable, s^-1.
    pub gamma: [f64; 3],
    /// The same weighted spectrum, routed through the original packet API.
    pub photo: IgmPhotoRates,
    /// Weighted stock in photons/H and erg/H. No time integration implied.
    pub inventory: [f64; 2],
}
/// Extend ONLY the probe's endpoint clock. Existing Grid::new keeps its old cuts.
/// The new denominator384 yields k/16 in the old 24-unit lattice, so even nodes
/// have exactly the same floating operations/values as the old N192 clock.
pub fn time_at(cfg: &HistoryConfig, k: usize, n: usize) -> Fallible<f64> {
    if ![1, 2, 3, 4, 6, 8, 12, 24, 48, 96, 192, 384].contains(&n) || k > n {
        return Err("E2_TIME_DOMAIN".into());
    }
    let s = if n == 384 {
        cfg.start + cfg.max_dln_a * (k as f64 / 16.0) / 24.0
    } else {
        radiation::time_at(cfg, k, n)
    };
    if !s.is_finite() {
        return Err("E2_TIME_NONFINITE".into());
    }
    Ok(s)
}
pub fn observe(cfg: &HistoryConfig, grid: &Grid, state: &State) -> Fallible<Readout> {
    if grid.nodes.len() != state.density.len() {
        return Err("E2_SHAPE".into());
    }
    let p = cfg.background.at_ln_a(state.s).map_err(err)?;
    let gas = material::gas(state.y)?;
    let mut packets = Vec::with_capacity(grid.nodes.len());
    for (&(eta, weight), &density) in grid.nodes.iter().zip(state.density.iter()) {
        positive(weight)?;
        let per_h = product(weight, density)?;
        let energy_ev = positive((eta - state.s).exp())?;
        packets.push(PrimaryPacket { energy_ev, per_h });
    }
    // Canonical rate output is the existing owner function, not moment closure.
    let gamma = radiation::gamma(grid, state.s, &state.density, p)?;
    let photo = igm_photo_rates(&gas, &packets, p.n_h_cm3, p.n_he_cm3).map_err(err)?;
    let inventory = radiation::inventory(grid, state.s, &state.density)?;
    Ok(Readout {
        gamma,
        photo,
        inventory,
    })
}
