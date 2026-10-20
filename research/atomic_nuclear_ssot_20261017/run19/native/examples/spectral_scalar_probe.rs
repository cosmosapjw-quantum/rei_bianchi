use rei_iso_couple_reference::{
    Absorber, AtomicProvider, HHeModel,
    axbi_sources::AxbiSource,
    spectral_edge_support::{Cell, refine_cell},
};
fn main() {
    let s = AxbiSource::new(1e-7, 0.2, 16, 8).unwrap();
    let p = s.spectral_cells[0];
    let h = HHeModel::controlled_fixture();
    let d = h.threshold_ev[0] + 0.0037;
    let eta = (-0.0004_f64).exp();
    let cell = Cell {
        lower_ev: p.lower_ev,
        upper_ev: p.upper_ev,
        owner_mean_ev: p.energy_ev,
        photon_fraction: p.photon_fraction,
    };
    println!(
        "m,E_ev,weight,panel_lower,panel_upper,sigma_H,sigma_D,H_heat,D_heat,count_residual,mean_residual,mean_shift"
    );
    for m in [1, 2, 4] {
        let q = refine_cell(cell, eta, &[13.6, d], m, h.kb_erg_k / h.ev_erg * 50000.).unwrap();
        for n in q.nodes {
            let e = eta * n.energy_ev;
            let sh = AtomicProvider::reference()
                .cross_section(Absorber::HI, e)
                .unwrap()
                * 1e-4;
            let sd = if e >= d { sh } else { 0. };
            println!(
                "{m},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                n.energy_ev,
                n.photon_fraction / p.photon_fraction,
                n.panel_lower_ev,
                n.panel_upper_ev,
                sh,
                sd,
                sh * (e - h.threshold_ev[0]),
                sd * (e - d),
                q.photon_fraction_residual / p.photon_fraction,
                q.mean_residual_ev,
                q.continuous_minus_owner_mean_ev
            );
        }
    }
}
