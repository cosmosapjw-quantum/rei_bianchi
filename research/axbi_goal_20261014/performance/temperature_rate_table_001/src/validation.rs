use crate::{
    columns, mask, temperature,
    thermal_adapter::{igm_point_rhs, IgmPhotoInput, IgmPointRhs},
    Table, N,
};
use rei_microphysics::{igm_rates::igm_rates, igm_state::IgmGasState, igm_thermal, HHeModel};
use std::path::Path;
#[derive(Default)]
pub struct Report {
    pub direct: u64,
    pub lookups: u64,
    pub fallback: u64,
    pub worst: [f64; 15],
    pub rhs_cases: u64,
    pub slopes: u64,
    pub saved: u64,
    pub invalid_rhs_cases: u64,
    pub invalid_rhs_records: Vec<String>,
    pub slope_candidates: u64,
    pub slope_skipped_guard: u64,
    pub slope_skipped_domain: u64,
}
pub const MIXED_NH: f64 = 1e-4;
pub fn mixed_fixture(t: f64) -> Result<(IgmGasState, f64, f64, f64, IgmPhotoInput), String> {
    let nh = MIXED_NH;
    let nhe = 0.08 * nh;
    let state = IgmGasState::from_temperature([0.5, 0.25, 0.25], nh, nhe, t)
        .map_err(|e| format!("MIXED_STATE t_bits={} {e:?}", t.to_bits()))?;
    let gamma = [1e-14, 2e-14, 3e-14];
    let photo = IgmPhotoInput {
        gamma_s: gamma,
        heat_erg_per_absorber_s: gamma.map(|v| v * 1e-12),
    };
    Ok((state, nh, nhe, 1e-17, photo))
}
fn err(g: &str, t: f64, k: usize, a: f64, b: f64) -> String {
    format!(
        "{{\"gate\":\"{g}\",\"t_bits\":{},\"field\":{k},\"reference\":{a:e},\"candidate\":{b:e}}}",
        t.to_bits()
    )
}
fn check_rates(table: &Table, t: f64, r: &mut Report) -> Result<(), String> {
    let a = igm_rates(t).map_err(|e| format!("canonical {t:e} {e:?}"))?;
    r.direct += 1;
    let b = table.query(t).map_err(|e| format!("table {t:e} {e:?}"))?;
    let x = columns(&a);
    let y = columns(&b);
    for k in 0..15 {
        let d = (x[k] - y[k]).abs();
        let rel = d / x[k].abs().max(1e-300);
        r.worst[k] = r.worst[k].max(rel);
        if !(d <= 1e-300 + 1e-6 * x[k].abs()) {
            return Err(err("coefficient", t, k, x[k], y[k]));
        }
    }
    if mask(&a) != mask(&b) {
        return Err(err("branch_mask", t, 15, mask(&a) as f64, mask(&b) as f64));
    }
    for k in 0..3 {
        if a.diagnostics.ci_floor_cm3_s[k].to_bits() != b.diagnostics.ci_floor_cm3_s[k].to_bits() {
            return Err(err(
                "ci_floor",
                t,
                k,
                a.diagnostics.ci_floor_cm3_s[k],
                b.diagnostics.ci_floor_cm3_s[k],
            ));
        }
        if a.diagnostics.ce_cap_erg[k] != b.diagnostics.ce_cap_erg[k]
            && (a.diagnostics.ce_cap_erg[k] - b.diagnostics.ce_cap_erg[k]).abs()
                > 1e-300 + 1e-6 * a.diagnostics.ce_cap_erg[k].abs()
        {
            return Err(err(
                "ce_cap",
                t,
                k,
                a.diagnostics.ce_cap_erg[k],
                b.diagnostics.ce_cap_erg[k],
            ));
        }
    }
    if a.diagnostics.dr_low_branch != b.diagnostics.dr_low_branch
        || a.dr_cooling_erg_cm3_s == 0.0 && b.dr_cooling_erg_cm3_s.to_bits() != 0
        || a.diagnostics.dr_excluded_erg_cm3_s == 0.0
            && b.diagnostics.dr_excluded_erg_cm3_s.to_bits() != 0
    {
        return Err(err(
            "derived_mask",
            t,
            15,
            a.dr_cooling_erg_cm3_s,
            b.dr_cooling_erg_cm3_s,
        ));
    }
    Ok(())
}
fn fields(x: &IgmPointRhs) -> Vec<f64> {
    let mut v = vec![];
    v.extend(x.fraction_dt);
    v.extend(x.species_chemical_cm3_s);
    v.extend([x.w_dt_erg_per_h_s, x.temperature_dt_k_s]);
    for a in [
        x.photo_events_cm3_s,
        x.ci_events_cm3_s,
        x.rr_events_cm3_s,
        x.ci_thermal_sink_erg_cm3_s,
        x.rr_thermal_sink_erg_cm3_s,
        x.ce_thermal_sink_erg_cm3_s,
        x.ci_floor_events_cm3_s,
        x.ce_cap_cooling_erg_cm3_s,
    ] {
        v.extend(a)
    }
    v.extend([
        x.dr_events_cm3_s,
        x.dr_thermal_sink_erg_cm3_s,
        x.freefree_thermal_sink_erg_cm3_s,
        x.thermal_micro_erg_cm3_s,
        x.binding_micro_erg_cm3_s,
        x.escape_erg_cm3_s,
        x.cmb_to_gas_erg_cm3_s,
        x.photo_input_erg_cm3_s,
        x.expansion_work_erg_cm3_s,
        x.excluded_dr_cooling_erg_cm3_s,
    ]);
    v
}
fn gross_and_conservation(
    x: &IgmPointRhs,
    state: &IgmGasState,
    nh: f64,
    nhe: f64,
    t: f64,
    p: IgmPhotoInput,
) -> Result<[f64; 45], String> {
    let mut g = [0.0_f64; 45];
    let c = HHeModel::controlled_fixture();
    let chi = c.threshold_ev.map(|v| v * c.ev_erg);
    let mut event = [0.0; 3];
    let mut photo_bind = 0.0;
    let mut ci_bind = 0.0;
    let mut capture_bind = 0.0;
    let mut photo_heat = 0.0;
    let abs = [
        nh * (1.0 - state.fractions[0]),
        nhe * (1.0 - state.fractions[1] - state.fractions[2]),
        nhe * state.fractions[1],
    ];
    for i in 0..3 {
        event[i] = x.photo_events_cm3_s[i].abs()
            + x.ci_events_cm3_s[i].abs()
            + x.rr_events_cm3_s[i].abs()
            + if i == 1 { x.dr_events_cm3_s.abs() } else { 0.0 };
        photo_bind += chi[i] * x.photo_events_cm3_s[i].abs();
        ci_bind += chi[i] * x.ci_events_cm3_s[i].abs();
        capture_bind += chi[i] * x.rr_events_cm3_s[i].abs();
        photo_heat += abs[i] * p.heat_erg_per_absorber_s[i];
    }
    capture_bind += chi[1] * x.dr_events_cm3_s.abs();
    g[0] = event[0] / nh;
    g[1] = if nhe == 0.0 {
        0.0
    } else {
        (event[1] + event[2]) / nhe
    };
    g[2] = if nhe == 0.0 { 0.0 } else { event[2] / nhe };
    g[3] = event[0];
    g[4] = event[0];
    g[5] = event[1];
    g[6] = event[1] + event[2];
    g[7] = event[2];
    g[8] = event.iter().sum();
    let ci_sink = x
        .ci_thermal_sink_erg_cm3_s
        .iter()
        .map(|v| v.abs())
        .sum::<f64>();
    let rr_sink = x
        .rr_thermal_sink_erg_cm3_s
        .iter()
        .map(|v| v.abs())
        .sum::<f64>();
    let ce_sink = x
        .ce_thermal_sink_erg_cm3_s
        .iter()
        .map(|v| v.abs())
        .sum::<f64>();
    let rad = rr_sink
        + x.dr_thermal_sink_erg_cm3_s.abs()
        + ce_sink
        + x.freefree_thermal_sink_erg_cm3_s.abs();
    let thermal = photo_heat + ci_sink + rad + x.cmb_to_gas_erg_cm3_s.abs();
    let binding = photo_bind + ci_bind + capture_bind;
    let gross_w = (thermal + x.expansion_work_erg_cm3_s.abs()) / nh;
    let eos = state.eos(nh, nhe).map_err(|e| format!("GROSS_EOS {e:?}"))?;
    let particles = nh + nhe + eos.electron_density_cm3;
    g[9] = gross_w;
    g[10] = 2.0 * nh / (3.0 * c.kb_erg_k * particles) * gross_w + t * g[8] / particles;
    let v = fields(x);
    for k in 11..45 {
        g[k] = v[k].abs()
    }
    g[38] = thermal;
    g[39] = binding;
    g[40] = capture_bind + rad;
    g[41] = x.cmb_to_gas_erg_cm3_s.abs();
    g[42] = photo_bind + photo_heat;
    g[43] = x.expansion_work_erg_cm3_s.abs();
    let nuclei_h = x.species_chemical_cm3_s[0] + x.species_chemical_cm3_s[1];
    let nuclei_he =
        x.species_chemical_cm3_s[2] + x.species_chemical_cm3_s[3] + x.species_chemical_cm3_s[4];
    let charge = x.species_chemical_cm3_s[5]
        - (x.species_chemical_cm3_s[1]
            + x.species_chemical_cm3_s[3]
            + 2.0 * x.species_chemical_cm3_s[4]);
    let energy = x.thermal_micro_erg_cm3_s + x.binding_micro_erg_cm3_s + x.escape_erg_cm3_s
        - x.photo_input_erg_cm3_s
        - x.cmb_to_gas_erg_cm3_s;
    for (name, res, scale) in [
        ("h_nuclei", nuclei_h, 2.0 * event[0]),
        ("he_nuclei", nuclei_he, 2.0 * (event[1] + event[2])),
        ("charge", charge, 2.0 * g[8]),
        (
            "micro_energy",
            energy,
            thermal
                + binding
                + capture_bind
                + rad
                + photo_bind
                + photo_heat
                + x.cmb_to_gas_erg_cm3_s.abs(),
        ),
    ] {
        if !res.is_finite() || !scale.is_finite() || res.abs() > 1e-300 + 1e-12 * scale {
            return Err(format!(
                "CONSERVATION_{name} t_bits={} residual={res:e} scale={scale:e}",
                t.to_bits()
            ));
        }
    }
    if g.iter().any(|v| !v.is_finite() || *v < 0.0) {
        return Err(format!("GROSS_NONFINITE t_bits={}", t.to_bits()));
    }
    Ok(g)
}
pub fn compare_rhs_pair(
    a: &IgmPointRhs,
    b: &IgmPointRhs,
    state: &IgmGasState,
    nh: f64,
    nhe: f64,
    t: f64,
    p: IgmPhotoInput,
) -> Result<(), String> {
    let av = fields(a);
    let bv = fields(b);
    let scales = gross_and_conservation(a, state, nh, nhe, t, p)?;
    gross_and_conservation(b, state, nh, nhe, t, p)?;
    if av.len() != 45 || bv.len() != 45 {
        return Err("RHS_FIELD_COUNT".into());
    }
    for k in 0..45 {
        if !av[k].is_finite() || !bv[k].is_finite() {
            return Err(err("rhs_nonfinite", t, k, av[k], bv[k]));
        }
        let bound = 1e-300 + 2e-6 * scales[k];
        if (av[k] - bv[k]).abs() > bound {
            return Err(err("rhs", t, k, av[k], bv[k]));
        }
    }
    Ok(())
}
pub fn compare_rate_bundle(
    a: &rei_microphysics::igm_rates::IgmRates,
    b: &rei_microphysics::igm_rates::IgmRates,
    t: f64,
) -> Result<(), String> {
    let av = columns(a);
    let bv = columns(b);
    for k in 0..15 {
        if !av[k].is_finite()
            || !bv[k].is_finite()
            || (av[k] - bv[k]).abs() > 1e-300 + 1e-6 * av[k].abs()
        {
            return Err(err("pretime_rate", t, k, av[k], bv[k]));
        }
    }
    if mask(a) != mask(b) {
        return Err(err(
            "pretime_rate_mask",
            t,
            15,
            mask(a) as f64,
            mask(b) as f64,
        ));
    }
    for k in 0..3 {
        if a.diagnostics.ci_floor_cm3_s[k].to_bits() != b.diagnostics.ci_floor_cm3_s[k].to_bits() {
            return Err(err(
                "pretime_floor",
                t,
                k,
                a.diagnostics.ci_floor_cm3_s[k],
                b.diagnostics.ci_floor_cm3_s[k],
            ));
        }
        let ac = a.diagnostics.ce_cap_erg[k];
        let bc = b.diagnostics.ce_cap_erg[k];
        if (ac - bc).abs() > 1e-300 + 1e-6 * ac.abs() {
            return Err(err("pretime_cap", t, k, ac, bc));
        }
    }
    for (k, x, y) in [
        (0, a.dr_cooling_erg_cm3_s, b.dr_cooling_erg_cm3_s),
        (
            1,
            a.diagnostics.dr_excluded_erg_cm3_s,
            b.diagnostics.dr_excluded_erg_cm3_s,
        ),
    ] {
        if (x - y).abs() > 1e-300 + 1e-6 * x.abs() {
            return Err(err("pretime_derived", t, k, x, y));
        }
    }
    Ok(())
}
fn rhs(table: &Table, r: &mut Report) -> Result<(), String> {
    for j in 0..257 {
        let t = temperature(j * N / 256);
        for fr in [
            [0.0, 0.0, 0.0],
            [2e-4, 1e-5, 1e-8],
            [0.5, 0.25, 0.25],
            [1.0, 0.0, 1.0],
        ] {
            for nh in [1e-4, 1.0] {
                for nhe in [0.0, 0.08 * nh] {
                    let state = match IgmGasState::from_temperature(fr, nh, nhe, t) {
                        Ok(x) => x,
                        Err(_) => continue,
                    };
                    for photo_on in [false, true] {
                        for tcmb in if photo_on {
                            [2.7255, 100.0].as_slice()
                        } else {
                            [2.7255].as_slice()
                        } {
                            for h in [0.0, 1e-17] {
                                let gamma = if photo_on {
                                    [1e-14, 2e-14, 3e-14]
                                } else {
                                    [0.0; 3]
                                };
                                let p = IgmPhotoInput {
                                    gamma_s: gamma,
                                    heat_erg_per_absorber_s: gamma.map(|v| v * 1e-12),
                                };
                                let x = igm_thermal::igm_point_rhs(&state, nh, nhe, h, *tcmb, p);
                                let y =
                                    igm_point_rhs(&state, nh, nhe, h, *tcmb, p, |q| table.query(q));
                                r.direct += 1;
                                match (x,y){(Ok(a),Ok(b))=>{compare_rhs_pair(&a,&b,&state,nh,nhe,t,p)?;r.rhs_cases+=1},(Err(a),Err(b)) if format!("{a:?}")==format!("{b:?}")=>{},(a,b)=>return Err(format!("RHS_ERROR_MISMATCH t_bits={} reference={a:?} candidate={b:?}",t.to_bits()))}
                            }
                        }
                    }
                }
            }
        }
    }
    Ok(())
}
fn invalid_rhs(table: &Table, r: &mut Report) -> Result<(), String> {
    let (base, nh, nhe, h, photo) = mixed_fixture(10000.0)?;
    let mut cases: Vec<(&str, IgmGasState, f64, f64, f64, IgmPhotoInput)> = Vec::new();
    let mut p = photo;
    p.gamma_s[0] = -1e-14;
    cases.push(("negative_gamma", base, nh, h, 2.7255, p));
    let mut p = photo;
    p.gamma_s[0] = f64::NAN;
    cases.push(("nan_gamma", base, nh, h, 2.7255, p));
    let mut p = photo;
    p.heat_erg_per_absorber_s[0] = -1e-26;
    cases.push(("negative_heat", base, nh, h, 2.7255, p));
    let mut p = photo;
    p.heat_erg_per_absorber_s[0] = f64::NAN;
    cases.push(("nan_heat", base, nh, h, 2.7255, p));
    let mut p = photo;
    p.gamma_s[0] = 0.0;
    cases.push(("heat_without_gamma", base, nh, h, 2.7255, p));
    cases.push(("negative_h", base, nh, -1e-17, 2.7255, photo));
    cases.push(("nan_h", base, nh, f64::NAN, 2.7255, photo));
    cases.push(("zero_tcmb", base, nh, h, 0.0, photo));
    cases.push(("nan_tcmb", base, nh, h, f64::NAN, photo));
    cases.push(("zero_nh", base, 0.0, h, 2.7255, photo));
    let mut bad = base;
    bad.fractions[0] = 1.01;
    cases.push(("forged_h_fraction", bad, nh, h, 2.7255, photo));
    let mut bad = base;
    bad.w_erg_per_h = -base.w_erg_per_h;
    cases.push(("negative_thermal_energy", bad, nh, h, 2.7255, photo));
    cases.push(("negative_h_and_zero_tcmb", base, nh, -1e-17, 0.0, photo));
    if cases.len() != 13 {
        return Err("INVALID_FIXTURE_COUNT".into());
    }
    for (id, state, case_nh, case_h, tcmb, p) in cases {
        let a = igm_thermal::igm_point_rhs(&state, case_nh, nhe, case_h, tcmb, p);
        let b = igm_point_rhs(&state, case_nh, nhe, case_h, tcmb, p, |q| table.query(q));
        match (a, b) {
            (Err(x), Err(y)) if format!("{x:?}") == format!("{y:?}") => {
                r.invalid_rhs_cases += 1;
                r.invalid_rhs_records.push(format!(
                    "{{\"case\":\"{id}\",\"reference\":\"{x:?}\",\"candidate\":\"{y:?}\"}}"
                ));
            }
            (x, y) => {
                return Err(format!(
                    "INVALID_RHS_MISMATCH case={id} reference={x:?} candidate={y:?}"
                ))
            }
        }
    }
    Ok(())
}
pub fn validate(table: &Table, literal_csv: &Path, samples: &[&Path]) -> Result<Report, String> {
    let mut r = Report::default();
    for j in 0..=N {
        check_rates(table, temperature(j), &mut r)?
    }
    for j in 0..N {
        for fraction in [0.25, 0.5, 0.75] {
            let a = &table.nodes[j];
            let b = &table.nodes[j + 1];
            check_rates(
                table,
                ((1.0 - fraction) * a.ln_t + fraction * b.ln_t).exp(),
                &mut r,
            )?
        }
    }
    for &b in &([
        5500.0,
        0.8 * 11605.0,
        118348.0 / 69.07755278982137,
        13179.0 / 69.07755278982137,
        473638.0 / 69.07755278982137,
        470000.0 / 69.07755278982137,
        94000.0 / 69.07755278982137,
    ] as [f64; 7])
    {
        let bits = b.to_bits();
        for t in [f64::from_bits(bits - 1), b, f64::from_bits(bits + 1)] {
            check_rates(table, t, &mut r)?
        }
    }
    for line in std::fs::read_to_string(literal_csv)
        .map_err(|e| e.to_string())?
        .lines()
        .skip(1)
    {
        let parts: Vec<_> = line.split(',').collect();
        let t: f64 = parts[0].parse().map_err(|e| format!("literal parse {e}"))?;
        let a = table.query(t).map_err(|e| format!("literal query {e:?}"))?;
        let c = columns(&a);
        for k in 0..15 {
            let v: f64 = parts[k + 1]
                .parse()
                .map_err(|e| format!("literal field parse {e}"))?;
            if (v - c[k]).abs() > 1e-300 + 1e-6 * v.abs() {
                return Err(err("literal_C", t, k, v, c[k]));
            }
        }
    }
    for t in [
        0.0,
        -1.0,
        0.9999999999999999,
        1e6 + 1.0,
        f64::NAN,
        f64::INFINITY,
        f64::NEG_INFINITY,
    ] {
        let a = igm_rates(t).unwrap_err();
        r.direct += 1;
        let b = table.query(t).unwrap_err();
        if format!("{a:?}") != format!("{b:?}") {
            return Err(format!("DOMAIN_ERROR_MISMATCH {a:?} {b:?}"));
        }
    }
    let mut slope_candidates = std::collections::BTreeSet::new();
    for j in 1..=4097 {
        slope_candidates.insert(((1e6f64).ln() * j as f64 / 4098.0).exp().to_bits());
    }
    for (j, guard) in table.guards.iter().enumerate() {
        if *guard != 0 {
            slope_candidates.insert(table.nodes[j].t.to_bits());
            slope_candidates.insert(table.nodes[j + 1].t.to_bits());
        }
    }
    for bits in slope_candidates {
        r.slope_candidates += 1;
        let t = f64::from_bits(bits);
        let lo = t * (-1e-6f64).exp();
        let hi = t * (1e-6f64).exp();
        if lo < 1.0 || hi > 1e6 {
            r.slope_skipped_domain += 1;
            continue;
        }
        let c = match table
            .nodes
            .binary_search_by(|n| n.t.partial_cmp(&lo).unwrap())
        {
            Ok(k) => k.min(N - 1),
            Err(k) => k - 1,
        };
        let d = match table
            .nodes
            .binary_search_by(|n| n.t.partial_cmp(&hi).unwrap())
        {
            Ok(k) => k.min(N - 1),
            Err(k) => k - 1,
        };
        if (c..=d).any(|k| table.guards[k] != 0) {
            r.slope_skipped_guard += 1;
            continue;
        }
        let a = columns(&igm_rates(lo).map_err(|e| format!("slope {e:?}"))?);
        let b = columns(&igm_rates(hi).map_err(|e| format!("slope {e:?}"))?);
        r.direct += 2;
        let p = columns(&table.query(lo).map_err(|e| format!("slope {e:?}"))?);
        let q = columns(&table.query(hi).map_err(|e| format!("slope {e:?}"))?);
        for k in 0..15 {
            if a[k] == 0.0 && b[k] == 0.0 {
                if p[k].to_bits() != 0 || q[k].to_bits() != 0 {
                    return Err(err("zero_slope", t, k, 0.0, p[k]));
                }
                continue;
            }
            let sa = (b[k].ln() - a[k].ln()) / 2e-6;
            let sb = (q[k].ln() - p[k].ln()) / 2e-6;
            if (sa - sb).abs() > 5e-4 * (1.0 + sa.abs()) {
                return Err(err("slope", t, k, sa, sb));
            }
        }
        r.slopes += 1;
    }
    for path in samples {
        let text = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
        let mut it = text.lines();
        let head: Vec<_> = it.next().ok_or("EMPTY_SAVED")?.split(',').collect();
        let i = head
            .iter()
            .position(|x| *x == "temperature_K")
            .ok_or("NO_T_COLUMN")?;
        let rows: Vec<_> = it.collect();
        for j in 0..128 {
            let idx = j * (rows.len() - 1) / 127;
            let t: f64 = rows[idx]
                .split(',')
                .nth(i)
                .ok_or("MISSING_T")?
                .parse()
                .map_err(|e| format!("sample parse {e}"))?;
            check_rates(table, t, &mut r)?;
            r.saved += 1
        }
    }
    rhs(table, &mut r)?;
    invalid_rhs(table, &mut r)?;
    r.lookups = table.lookup.get() + 7;
    r.fallback = table.fallback.get();
    r.direct += table.direct.get();
    if r.direct > 2_000_000 || r.lookups > 8_000_000 {
        return Err(format!("QUOTA direct={} lookups={}", r.direct, r.lookups));
    }
    Ok(r)
}
