//! HE-FLRW02 owner-side proposal; NOT COMPILED in the BASS_HE chat.
//! Temporary matched-sigma fixture only; no source admission or model promotion.
use rei_microphysics::{
    homogeneous_photo_rates, hhe_rhs, Absorber, AtomicProvider, HHeModel,
    HHeState, HomogeneousPhotoRates, PhotonNode, MPC_CM,
};

fn near(a: f64, b: f64) {
    assert!(a.is_finite() && b.is_finite(), "nonfinite comparison");
    let absolute = (a-b).abs();
    let scale = a.abs().max(b.abs());
    let relative = if scale > 0.0 { absolute/scale } else { 0.0 };
    println!("FLRW02_RESIDUAL absolute={absolute:e} relative={relative:e} lhs={a:e} rhs={b:e}");
    assert!(absolute <= 5e-14*scale+1e-300, "{a:e} != {b:e}");
}
fn fixture() -> (AtomicProvider, HHeModel, HHeState) {
    let p = AtomicProvider::reference();
    let mut m = HHeModel::controlled_fixture();
    m.photon_energy_ev = [20.0, 35.0, 70.0];
    let species = [Absorber::HI, Absorber::HeI, Absorber::HeII];
    for a in 0..3 {
        for g in 0..3 {
            m.sigma_cm2[a][g] = p.cross_section(species[a], m.photon_energy_ev[g]).unwrap();
        }
    }
    let s = HHeState::controlled_fixture(&m);
    (p, m, s)
}
fn rates(p: &AtomicProvider, m: &HHeModel, s: &HHeState, a: f64) -> HomogeneousPhotoRates {
    let [h,y,z] = s.fractions;
    let lower = [m.n_h_cm3*(1.0-h), m.n_he_cm3*(1.0-(y+z)), m.n_he_cm3*y];
    let volume = (a*MPC_CM).powi(3);
    let nodes: [PhotonNode;3] = std::array::from_fn(|g| PhotonNode {
        energy_ev: m.photon_energy_ev[g],
        n_comoving_per_cmpc3: volume*s.photon_cm3[g],
    });
    let q = homogeneous_photo_rates(p, lower, a, &nodes).unwrap();
    let rhs = hhe_rhs(m, s).unwrap();
    for species in 0..3 {
        near(q.events_proper_per_cm3_s[species], rhs.photo_per_cm3_s[species].iter().sum());
    }
    near(q.photon_loss_comoving_per_cmpc3_s,
         volume*q.events_proper_per_cm3_s.iter().sum::<f64>());
    near(q.absorbed_erg_per_cm3_s,
         q.heat_erg_per_cm3_s.iter().sum::<f64>()+q.binding_erg_per_cm3_s.iter().sum::<f64>());
    q
}

#[test]
fn flrw02_same_proper_state_changes_only_comoving_representation() {
    let (p,m,s) = fixture();
    let base = rates(&p,&m,&s,0.25);
    for lambda in [0.5_f64,2.0] {
        let changed = rates(&p,&m,&s,0.25*lambda);
        for a in 0..3 {
            near(changed.gamma_per_s[a],base.gamma_per_s[a]);
            near(changed.events_proper_per_cm3_s[a],base.events_proper_per_cm3_s[a]);
            near(changed.heat_erg_per_cm3_s[a],base.heat_erg_per_cm3_s[a]);
            near(changed.binding_erg_per_cm3_s[a],base.binding_erg_per_cm3_s[a]);
        }
        near(changed.photon_loss_comoving_per_cmpc3_s,
             lambda.powi(3)*base.photon_loss_comoving_per_cmpc3_s);
    }
}

#[test]
fn flrw02_same_comoving_inventories_fixed_energies_not_free_streaming() {
    let (p,m,s) = fixture();
    let base = rates(&p,&m,&s,0.25);
    for lambda in [0.5_f64,2.0] {
        let factor = lambda.powi(3);
        let mut m2 = m;
        m2.n_h_cm3 /= factor;
        m2.n_he_cm3 /= factor;
        let mut s2 = s;
        s2.u_erg_cm3 /= factor;
        for g in 0..3 { s2.photon_cm3[g] /= factor; }
        let changed = rates(&p,&m2,&s2,0.25*lambda);
        for a in 0..3 {
            near(changed.gamma_per_s[a],base.gamma_per_s[a]/factor);
            near(changed.events_proper_per_cm3_s[a],base.events_proper_per_cm3_s[a]/factor.powi(2));
            near(changed.heat_erg_per_cm3_s[a],base.heat_erg_per_cm3_s[a]/factor.powi(2));
            near(changed.binding_erg_per_cm3_s[a],base.binding_erg_per_cm3_s[a]/factor.powi(2));
        }
        near(changed.photon_loss_comoving_per_cmpc3_s,
             base.photon_loss_comoving_per_cmpc3_s/factor);
    }
}
