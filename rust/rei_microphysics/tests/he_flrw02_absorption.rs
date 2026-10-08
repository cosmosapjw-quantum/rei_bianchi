//! HE-FLRW02B owner-side proposal with independent fitted-source anchors.
//! NOT COMPILED or RUN in this BASS_HE chat; replaces, never coexists with, the older proposal.
//! Temporary matched-sigma fixture only; no source admission or model promotion.
use rei_microphysics::{
    hhe_rhs, homogeneous_photo_rates, Absorber, AtomicProvider, HHeModel, HHeState,
    HomogeneousPhotoRates, PhotonNode, MPC_CM,
};

fn near(a: f64, b: f64) {
    assert!(a.is_finite() && b.is_finite(), "nonfinite comparison");
    let absolute = (a - b).abs();
    let scale = a.abs().max(b.abs());
    let relative = if scale > 0.0 { absolute / scale } else { 0.0 };
    println!("FLRW02_RESIDUAL absolute={absolute:e} relative={relative:e} lhs={a:e} rhs={b:e}");
    assert!(absolute <= 5e-14 * scale + 1e-300, "{a:e} != {b:e}");
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
fn rates(
    p: &AtomicProvider,
    m: &HHeModel,
    s: &HHeState,
    a: f64,
    golden_index: usize,
) -> HomogeneousPhotoRates {
    let [h, y, z] = s.fractions;
    let lower = [
        m.n_h_cm3 * (1.0 - h),
        m.n_he_cm3 * (1.0 - (y + z)),
        m.n_he_cm3 * y,
    ];
    let volume = (a * MPC_CM).powi(3);
    let nodes: [PhotonNode; 3] = std::array::from_fn(|g| PhotonNode {
        energy_ev: m.photon_energy_ev[g],
        n_comoving_per_cmpc3: volume * s.photon_cm3[g],
    });
    let q = homogeneous_photo_rates(p, lower, a, &nodes).unwrap();
    let rhs = hhe_rhs(m, s).unwrap();
    for species in 0..3 {
        near(
            q.events_proper_per_cm3_s[species],
            rhs.photo_per_cm3_s[species].iter().sum(),
        );
    }
    near(
        q.photon_loss_comoving_per_cmpc3_s,
        volume * q.events_proper_per_cm3_s.iter().sum::<f64>(),
    );
    near(
        q.absorbed_erg_per_cm3_s,
        q.heat_erg_per_cm3_s.iter().sum::<f64>() + q.binding_erg_per_cm3_s.iter().sum::<f64>(),
    );
    let expected = GOLDEN[golden_index];
    for species in 0..3 {
        for g in 0..3 {
            reference_near(
                &format!("case{golden_index}/sigma/{species}/{g}"),
                m.sigma_cm2[species][g],
                SIGMA[species][g],
            );
            reference_near(
                &format!("case{golden_index}/photo/{species}/{g}"),
                rhs.photo_per_cm3_s[species][g],
                expected.photo[species][g],
            );
        }
        reference_near(
            &format!("case{golden_index}/gamma/{species}"),
            q.gamma_per_s[species],
            expected.gamma[species],
        );
        reference_near(
            &format!("case{golden_index}/event/{species}"),
            q.events_proper_per_cm3_s[species],
            expected.events[species],
        );
        reference_near(
            &format!("case{golden_index}/heat/{species}"),
            q.heat_erg_per_cm3_s[species],
            expected.heat[species],
        );
        reference_near(
            &format!("case{golden_index}/binding/{species}"),
            q.binding_erg_per_cm3_s[species],
            expected.binding[species],
        );
    }
    reference_near(
        &format!("case{golden_index}/loss"),
        q.photon_loss_comoving_per_cmpc3_s,
        expected.loss,
    );
    reference_near(
        &format!("case{golden_index}/absorbed"),
        q.absorbed_erg_per_cm3_s,
        expected.absorbed,
    );
    q
}

#[test]
fn flrw02_same_proper_state_changes_only_comoving_representation() {
    let (p, m, s) = fixture();
    let base = rates(&p, &m, &s, 0.25, 0);
    for (lambda, index) in [(0.5_f64, 1usize), (2.0, 2usize)] {
        let changed = rates(&p, &m, &s, 0.25 * lambda, index);
        for a in 0..3 {
            near(changed.gamma_per_s[a], base.gamma_per_s[a]);
            near(
                changed.events_proper_per_cm3_s[a],
                base.events_proper_per_cm3_s[a],
            );
            near(changed.heat_erg_per_cm3_s[a], base.heat_erg_per_cm3_s[a]);
            near(
                changed.binding_erg_per_cm3_s[a],
                base.binding_erg_per_cm3_s[a],
            );
        }
        near(
            changed.photon_loss_comoving_per_cmpc3_s,
            lambda.powi(3) * base.photon_loss_comoving_per_cmpc3_s,
        );
    }
}

#[test]
fn flrw02_same_comoving_inventories_fixed_energies_not_free_streaming() {
    let (p, m, s) = fixture();
    let base = rates(&p, &m, &s, 0.25, 0);
    for (lambda, index) in [(0.5_f64, 3usize), (2.0, 4usize)] {
        let factor = lambda.powi(3);
        let mut m2 = m;
        m2.n_h_cm3 /= factor;
        m2.n_he_cm3 /= factor;
        let mut s2 = s;
        s2.u_erg_cm3 /= factor;
        for g in 0..3 {
            s2.photon_cm3[g] /= factor;
        }
        let changed = rates(&p, &m2, &s2, 0.25 * lambda, index);
        for a in 0..3 {
            near(changed.gamma_per_s[a], base.gamma_per_s[a] / factor);
            near(
                changed.events_proper_per_cm3_s[a],
                base.events_proper_per_cm3_s[a] / factor.powi(2),
            );
            near(
                changed.heat_erg_per_cm3_s[a],
                base.heat_erg_per_cm3_s[a] / factor.powi(2),
            );
            near(
                changed.binding_erg_per_cm3_s[a],
                base.binding_erg_per_cm3_s[a] / factor.powi(2),
            );
        }
        near(
            changed.photon_loss_comoving_per_cmpc3_s,
            base.photon_loss_comoving_per_cmpc3_s / factor,
        );
    }
}

// Generated from GOLDEN.json using independent Decimal/mpmath reference values.
// Literals are nearest Python binary64 conversions, not actual Rust observations.
// Exact source-decimal values and input provenance remain in GOLDEN.json.
#[derive(Clone, Copy)]
struct Golden {
    photo: [[f64; 3]; 3],
    gamma: [f64; 3],
    events: [f64; 3],
    heat: [f64; 3],
    binding: [f64; 3],
    loss: f64,
    absorbed: f64,
}
fn reference_near(label: &str, actual: f64, reference: f64) {
    assert!(actual.is_finite() && reference.is_finite());
    let absolute = (actual - reference).abs();
    let scale = actual.abs().max(reference.abs());
    let relative = if scale > 0.0 { absolute / scale } else { 0.0 };
    println!("FLRW02_REFERENCE label={label} absolute={absolute:e} relative={relative:e} actual={actual:e} reference={reference:e}");
    assert!(
        absolute <= 5e-14 * scale + 1e-300,
        "source reference mismatch {label}"
    );
}
const SIGMA: [[f64; 3]; 3] = [
    [
        2.21110298403921285e-18,
        4.51016161329318124e-19,
        5.77342785243447843e-20,
    ],
    [
        0.00000000000000000e+00,
        4.06532624723736842e-18,
        9.60545746078131228e-19,
    ],
    [
        0.00000000000000000e+00,
        0.00000000000000000e+00,
        8.00711463442348000e-19,
    ],
];
const GOLDEN: [Golden; 5] = [
    Golden {
        photo: [
            [
                1.31248655698297562e-16,
                2.67718262333228806e-18,
                3.42704365139464749e-20,
            ],
            [
                0.00000000000000000e+00,
                1.98266924834252682e-18,
                4.68460437503514878e-20,
            ],
            [
                0.00000000000000000e+00,
                0.00000000000000000e+00,
                7.57109051019696371e-22,
            ],
        ],
        gamma: [
            1.35313241169842229e-12,
            2.49510117051005436e-13,
            4.80094515548317270e-15,
        ],
        events: [
            1.33960108758143797e-16,
            2.02951529209287809e-18,
            7.57109051019696371e-22,
        ],
        heat: [
            1.44103877394374898e-27,
            3.64850302905624768e-29,
            1.89016066441918923e-32,
        ],
        binding: [
            2.91860150515597468e-27,
            7.99493862704542505e-29,
            6.60099635211651004e-32,
        ],
        loss: 6.24280619570668280e+55,
        absorbed: 4.47615960723090587e-27,
    },
    Golden {
        photo: [
            [
                1.31248655698297562e-16,
                2.67718262333228806e-18,
                3.42704365139464749e-20,
            ],
            [
                0.00000000000000000e+00,
                1.98266924834252682e-18,
                4.68460437503514878e-20,
            ],
            [
                0.00000000000000000e+00,
                0.00000000000000000e+00,
                7.57109051019696371e-22,
            ],
        ],
        gamma: [
            1.35313241169842229e-12,
            2.49510117051005436e-13,
            4.80094515548317270e-15,
        ],
        events: [
            1.33960108758143797e-16,
            2.02951529209287809e-18,
            7.57109051019696371e-22,
        ],
        heat: [
            1.44103877394374898e-27,
            3.64850302905624768e-29,
            1.89016066441918923e-32,
        ],
        binding: [
            2.91860150515597468e-27,
            7.99493862704542505e-29,
            6.60099635211651004e-32,
        ],
        loss: 7.80350774463335350e+54,
        absorbed: 4.47615960723090587e-27,
    },
    Golden {
        photo: [
            [
                1.31248655698297562e-16,
                2.67718262333228806e-18,
                3.42704365139464749e-20,
            ],
            [
                0.00000000000000000e+00,
                1.98266924834252682e-18,
                4.68460437503514878e-20,
            ],
            [
                0.00000000000000000e+00,
                0.00000000000000000e+00,
                7.57109051019696371e-22,
            ],
        ],
        gamma: [
            1.35313241169842229e-12,
            2.49510117051005436e-13,
            4.80094515548317270e-15,
        ],
        events: [
            1.33960108758143797e-16,
            2.02951529209287809e-18,
            7.57109051019696371e-22,
        ],
        heat: [
            1.44103877394374898e-27,
            3.64850302905624768e-29,
            1.89016066441918923e-32,
        ],
        binding: [
            2.91860150515597468e-27,
            7.99493862704542505e-29,
            6.60099635211651004e-32,
        ],
        loss: 4.99424495656534624e+56,
        absorbed: 4.47615960723090587e-27,
    },
    Golden {
        photo: [
            [
                8.39991396469104394e-15,
                1.71339687893266436e-16,
                2.19330793689257440e-18,
            ],
            [
                0.00000000000000000e+00,
                1.26890831893921716e-16,
                2.99814680002249522e-18,
            ],
            [
                0.00000000000000000e+00,
                0.00000000000000000e+00,
                4.84549792652605678e-20,
            ],
        ],
        gamma: [
            1.08250592935873783e-11,
            1.99608093640804349e-12,
            3.84075612438653816e-14,
        ],
        events: [
            8.57344696052120303e-15,
            1.29888978693944198e-16,
            4.84549792652605678e-20,
        ],
        heat: [
            9.22264815323999344e-26,
            2.33504193859599851e-27,
            1.20970282522828111e-30,
        ],
        binding: [
            1.86790496329982379e-25,
            5.11676072130907203e-27,
            4.22463766535456643e-30,
        ],
        loss: 4.99424495656534624e+56,
        absorbed: 2.86474214862777976e-25,
    },
    Golden {
        photo: [
            [
                2.05076024528589940e-18,
                4.18309784895670009e-20,
                5.35475570530413671e-22,
            ],
            [
                0.00000000000000000e+00,
                3.09792070053519815e-20,
                7.31969433599241997e-22,
            ],
            [
                0.00000000000000000e+00,
                0.00000000000000000e+00,
                1.18298289221827558e-23,
            ],
        ],
        gamma: [
            1.69141551462302787e-13,
            3.11887646313756795e-14,
            6.00118144435396587e-16,
        ],
        events: [
            2.09312669934599683e-18,
            3.17111764389512202e-20,
            1.18298289221827558e-23,
        ],
        heat: [
            2.25162308428710777e-29,
            5.70078598290038700e-31,
            2.95337603815498318e-34,
        ],
        binding: [
            4.56031485180621043e-29,
            1.24920916047584766e-30,
            1.03140568001820469e-33,
        ],
        loss: 7.80350774463335350e+54,
        absorbed: 6.99399938629829042e-29,
    },
];
