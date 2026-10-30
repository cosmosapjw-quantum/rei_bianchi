//! Native Rust on the original BASS193 source ledger already preserved at PR295.
//! No duplicate 193-state data is introduced into Git. No new cosmological IVP.
use std::collections::HashMap;

use rei_microphysics::igm_state::IgmGasState;
use rei_microphysics::igm_thermal::{igm_point_rhs, IgmPhotoInput};

const THERMAL: &str = include_str!(
    "../../../research/rei_f4_rei_hhe_thermal_source_20261030/results/HHE_IGM_THERMAL_193.csv"
);
const EVENTS: &str = include_str!(
    "../../../research/rei_f4_rei_hhe_thermal_source_20261030/results/HHE_IGM_EVENTS_579.csv"
);

type Row<'a> = Vec<&'a str>;
struct Table<'a> {
    columns: HashMap<&'a str, usize>,
    rows: Vec<Row<'a>>,
}
impl<'a> Table<'a> {
    fn new(text: &'a str) -> Self {
        let mut lines = text.lines();
        let header = lines.next().expect("source header");
        let columns = header.split(',').enumerate().map(|(i, k)| (k, i)).collect();
        let rows = lines
            .filter(|line| !line.is_empty())
            .map(|line| line.split(',').collect())
            .collect();
        Self { columns, rows }
    }
    fn number(&self, row: usize, field: &str) -> f64 {
        self.rows[row][*self.columns.get(field).expect("source field")]
            .parse::<f64>()
            .expect("numeric source field")
    }
    fn label(&self, row: usize, field: &str) -> &str {
        self.rows[row][*self.columns.get(field).expect("source field")]
    }
}
fn same(name: &str, i: usize, a: f64, b: f64) {
    assert!(
        a.is_finite() && b.is_finite(),
        "{name}: nonfinite epoch {i}"
    );
    let gap = (a - b).abs();
    let scale = a.abs().max(b.abs());
    assert!(
        gap <= 5e-8 * scale + 1e-60,
        "{name}: epoch {i} native={a:e}, source={b:e}, relative={:e}",
        gap / scale.max(1e-300)
    );
}
fn input(t: &Table<'_>, e: &Table<'_>, i: usize) -> IgmPhotoInput {
    let nh = t.number(i, "nHref_cm3");
    let nhe = t.number(i, "nHe4_cm3");
    let x = t.number(i, "HII_fraction");
    let y = t.number(i, "HeII_fraction");
    let z = t.number(i, "HeIII_fraction");
    let absorbers = [nh * (1.0 - x), nhe * (1.0 - y - z), nhe * y];
    let mut gamma_s = [0.0; 3];
    let mut heat_erg_per_absorber_s = [0.0; 3];
    for a in 0..3 {
        let j = 3 * i + a;
        gamma_s[a] = e.number(j, "source_BASS_native_photo_gamma_s");
        let kinetic_per_h = e.number(j, "REI_point_primary_kinetic_erg_per_Href_s");
        if absorbers[a] > 0.0 {
            heat_erg_per_absorber_s[a] = kinetic_per_h * nh / absorbers[a];
        } else {
            assert_eq!(kinetic_per_h, 0.0);
        }
        assert!(gamma_s[a] >= 0.0 && heat_erg_per_absorber_s[a] >= 0.0);
    }
    IgmPhotoInput {
        gamma_s,
        heat_erg_per_absorber_s,
    }
}

#[test]
fn native_rei_igm_all_193_frozen_bass21_states() {
    let t = Table::new(THERMAL);
    let e = Table::new(EVENTS);
    assert_eq!(t.rows.len(), 193);
    assert_eq!(e.rows.len(), 579);
    let mut max_source_relative = 0.0_f64;
    for i in 0..193 {
        assert_eq!(t.number(i, "epoch") as usize, i);
        for (a, name) in ["H_I", "He_I", "He_II"].iter().enumerate() {
            assert_eq!(e.label(3 * i + a, "absorber"), *name);
            assert_eq!(e.number(3 * i + a, "epoch") as usize, i);
        }
        let nh = t.number(i, "nHref_cm3");
        let nhe = t.number(i, "nHe4_cm3");
        let h = t.number(i, "H_s");
        let f = [
            t.number(i, "HII_fraction"),
            t.number(i, "HeII_fraction"),
            t.number(i, "HeIII_fraction"),
        ];
        let state = IgmGasState::from_temperature(f, nh, nhe, t.number(i, "T_original_K"))
            .expect("original BASS193 input to unmodified REI Rust EOS");
        let result = igm_point_rhs(
            &state,
            nh,
            nhe,
            h,
            t.number(i, "T_CMB_external_K"),
            input(&t, &e, i),
        )
        .expect("native Rust H/He RHS accepts source-matched BASS state");
        for (j, key) in [
            "REI_source_translated_HII_fraction_dt_per_s",
            "REI_source_translated_HeII_fraction_dt_per_s",
            "REI_source_translated_HeIII_fraction_dt_per_s",
        ]
        .iter()
        .enumerate()
        {
            same(key, i, result.fraction_dt[j], t.number(i, key));
        }
        let matches = [
            (
                "REI_HHe_photon_photoevents_per_Href_s",
                result.photo_events_cm3_s.iter().sum::<f64>(),
            ),
            (
                "REI_HHe_photo_input_erg_per_Href_s",
                result.photo_input_erg_cm3_s,
            ),
            (
                "REI_HHe_thermal_micro_erg_per_Href_s",
                result.thermal_micro_erg_cm3_s,
            ),
            (
                "REI_HHe_binding_micro_erg_per_Href_s",
                result.binding_micro_erg_cm3_s,
            ),
            ("REI_HHe_escape_erg_per_Href_s", result.escape_erg_cm3_s),
            (
                "REI_HHe_cmb_exchange_erg_per_Href_s",
                result.cmb_to_gas_erg_cm3_s,
            ),
            ("REI_HHe_dNe_cm3_s", result.species_chemical_cm3_s[5]),
        ];
        for (key, val) in matches {
            let expected = if key == "REI_HHe_dNe_cm3_s" {
                t.number(i, key)
            } else {
                t.number(i, key) * nh
            };
            same(key, i, val, expected);
        }
        same(
            "point temperature",
            i,
            result.temperature_dt_k_s,
            t.number(i, "REI_HHe_Tdot_point_K_s"),
        );
        let d = result.species_chemical_cm3_s;
        assert!((d[0] + d[1]).abs() <= 1e-12 * (d[0].abs() + d[1].abs()).max(1e-60));
        assert!(
            (d[2] + d[3] + d[4]).abs() <= 1e-12 * (d[2].abs() + d[3].abs() + d[4].abs()).max(1e-60)
        );
        assert!(
            (d[5] - d[1] - d[3] - 2.0 * d[4]).abs()
                <= 1e-12 * (d[5].abs() + d[1].abs() + d[3].abs() + 2.0 * d[4].abs()).max(1e-60)
        );
        let energy = result.thermal_micro_erg_cm3_s
            + result.binding_micro_erg_cm3_s
            + result.escape_erg_cm3_s
            - result.photo_input_erg_cm3_s
            - result.cmb_to_gas_erg_cm3_s;
        assert!(energy.abs() <= 2e-43, "energy closure at epoch {i}");
        let omitted = t.number(i, "ne_omitted_isotopes_cm3");
        assert!(omitted >= 0.0, "other isotope electrons are not zeroed");
        let expected_photo = t.number(i, "REI_HHe_photo_input_erg_per_Href_s") * nh;
        let scale = expected_photo.abs().max(1e-99);
        max_source_relative =
            max_source_relative.max((result.photo_input_erg_cm3_s - expected_photo).abs() / scale);
        if i > 0 {
            let dt = t.number(i, "proper_elapsed_s") - t.number(i - 1, "proper_elapsed_s");
            let dx = t.number(i, "x") - t.number(i - 1, "x");
            let dt_mid = 2.0 * dx / (h + t.number(i - 1, "H_s"));
            assert!(dt > 0.0 && dx > 0.0 && (dt / dt_mid - 1.0).abs() < 5e-5);
        }
    }
    println!("NATIVE_193_PASS; MAX_REL_PHOTO={max_source_relative:e}; PRODUCTION_HOLD");
}

#[test]
fn duplicate_bass_photons_cannot_be_admitted_as_separate_rei_source() {
    let t = Table::new(THERMAL);
    let e = Table::new(EVENTS);
    let i = 100;
    let nh = t.number(i, "nHref_cm3");
    let nhe = t.number(i, "nHe4_cm3");
    let state = IgmGasState::from_temperature(
        [
            t.number(i, "HII_fraction"),
            t.number(i, "HeII_fraction"),
            t.number(i, "HeIII_fraction"),
        ],
        nh,
        nhe,
        t.number(i, "T_original_K"),
    )
    .unwrap();
    let p = input(&t, &e, i);
    let original = igm_point_rhs(&state, nh, nhe, 0.0, t.number(i, "T_CMB_external_K"), p).unwrap();
    let duplicated = igm_point_rhs(
        &state,
        nh,
        nhe,
        0.0,
        t.number(i, "T_CMB_external_K"),
        IgmPhotoInput {
            gamma_s: p.gamma_s.map(|x| 2.0 * x),
            heat_erg_per_absorber_s: p.heat_erg_per_absorber_s.map(|x| 2.0 * x),
        },
    )
    .unwrap();
    let one = original.photo_events_cm3_s.iter().sum::<f64>();
    let two = duplicated.photo_events_cm3_s.iter().sum::<f64>();
    assert!(one > 0.0);
    same("double photo", i, two, 2.0 * one);
    assert!(
        two > 1.5 * one,
        "additive source double counts the same photons"
    );
}
