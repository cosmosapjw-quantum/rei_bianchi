mod native_owner;
use native_owner::*;
use rei_microphysics::{
    axbi_covariant_transport::PhotonState,
    axbi_driver::{Driver, DriverConfig},
    axbi_rates::AxbiProvider,
    igm_state::{w_erg_per_h_to_ev, w_ev_per_h_to_erg, IgmGasState},
    igm_thermal::IgmPhotoInput,
    HHeModel,
};
use std::{
    fs,
    io::{self, BufRead},
    path::Path,
};
fn driver(q: f64) -> Result<(Driver, Accepted), Box<dyn std::error::Error>> {
    let mut cfg = DriverConfig::baseline();
    cfg.q_ref = q;
    cfg.n_mu = 8;
    cfg.energy_subdivisions = 8;
    cfg.transport_cells = 16;
    cfg.background_panels = 256;
    cfg.inactive_hi_split = false;
    cfg.transport_threads = 1;
    cfg.parallel_jacobian_columns = false;
    let (d, mut s) = Driver::new(cfg)?;
    s.gas = IgmGasState::from_temperature(
        [0.01, 0.01, 0.001],
        d.n_h0_cm3 / s.a.powi(3),
        d.n_he0_cm3 / s.a.powi(3),
        8000.,
    )?;
    Ok((d, empty(s)))
}
struct Setup {
    d: Driver,
    s0: Accepted,
    births: Vec<f64>,
    templates: Vec<PhotonState>,
    encoded: Vec<Vec<f64>>,
}
fn encode(p: &PhotonState) -> Result<Vec<f64>, Box<dyn std::error::Error>> {
    let n = p.number.len();
    let mut v = vec![0.; 2 * n];
    for k in 0..n {
        let number = p.number[k];
        if number == 0. {
            continue;
        }
        let lo = p.support_lo[k];
        let hi = p.support_hi[k];
        if hi == lo {
            v[k] = number.ln();
        } else {
            let l = (-lo).mul_add(number, p.energy_ref[k]);
            let r = hi.mul_add(number, -p.energy_ref[k]);
            if l <= 0. || r <= 0. {
                return Err("initial nonpositive slack".into());
            }
            v[k] = l.ln();
            v[n + k] = r.ln();
        }
    }
    Ok(v)
}
fn setup(q: f64) -> Result<Setup, Box<dyn std::error::Error>> {
    let (d, s0) = driver(q)?;
    let x0 = s0.gas_owner.a.ln();
    let width = 0.002;
    let mut births = vec![];
    let mut templates = vec![];
    let mut encoded = vec![];
    for i in 0..8 {
        let x = x0 + width * (i as f64 + 0.5) / 8.;
        let a = x.exp();
        let g = d.geometry_point(a)?.geometry()?;
        let h = d.geometry_point(a)?.h_per_s;
        let mut p = d.transport.empty_state();
        d.transport
            .inject(&mut p, &g, 1. / a - 1., width / 8. / h)?;
        births.push(x);
        encoded.push(encode(&p)?);
        templates.push(p);
    }
    Ok(Setup {
        d,
        s0,
        births,
        templates,
        encoded,
    })
}
fn gas_encoded(s: &Accepted) -> Result<Vec<f64>, Box<dyn std::error::Error>> {
    let g = s.gas_owner.gas;
    let [x, y, z] = g.fractions;
    let neutral = 1. - y - z;
    Ok(vec![
        (x / (1. - x)).ln(),
        (y / neutral).ln(),
        (z / neutral).ln(),
        w_erg_per_h_to_ev(g.w_erg_per_h)?.ln(),
    ])
}
fn gas_decode(z: &[f64]) -> Result<IgmGasState, Box<dyn std::error::Error>> {
    let x = if z[0] >= 0. {
        1. / (1. + (-z[0]).exp())
    } else {
        let e = z[0].exp();
        e / (1. + e)
    };
    let max = z[1].max(z[2]).max(0.);
    let n = (-max).exp();
    let y = (z[1] - max).exp();
    let zz = (z[2] - max).exp();
    let norm = n + y + zz;
    Ok(IgmGasState::new(
        [x, y / norm, zz / norm],
        w_ev_per_h_to_erg(z[3].exp())?,
    )?)
}
fn decode(
    template: &PhotonState,
    z: &[f64],
) -> Result<(PhotonState, Vec<f64>, Vec<f64>), Box<dyn std::error::Error>> {
    let n = template.number.len();
    let mut p = template.clone();
    let mut first = vec![0.; n];
    let mut second = vec![0.; n];
    for k in 0..n {
        if template.number[k] == 0. {
            continue;
        }
        let lo = template.support_lo[k];
        let hi = template.support_hi[k];
        let l = z[k].exp();
        if !l.is_finite() || l == 0. {
            return Err("positive coordinate underflow or nonfinite".into());
        }
        first[k] = l;
        if hi == lo {
            p.number[k] = l;
            p.energy_ref[k] = lo * l;
        } else {
            let r = z[n + k].exp();
            if !r.is_finite() || r == 0. {
                return Err("positive coordinate underflow or nonfinite".into());
            }
            second[k] = r;
            p.number[k] = (l + r) / (hi - lo);
            p.energy_ref[k] = if l <= r {
                lo.mul_add(p.number[k], l)
            } else {
                hi.mul_add(p.number[k], -r)
            };
        }
        if p.energy_ref[k] < lo * p.number[k] || p.energy_ref[k] > hi * p.number[k] {
            return Err(format!("strict reconstructed support domain at cell{k}:lo={lo},hi={hi},N={},U={},L={l},R={}",p.number[k],p.energy_ref[k],second[k]).into());
        }
    }
    Ok((p, first, second))
}
/// Normalized shape is passed to native prepare. Log amplitude is retained
/// even when the physical linear population is below binary64 range.
fn normalized_decode(
    template: &PhotonState,
    z: &[f64],
) -> Result<(PhotonState, Vec<f64>, Vec<f64>, Vec<f64>), Box<dyn std::error::Error>> {
    let n = template.number.len();
    let mut p = template.clone();
    let mut l = vec![0.; n];
    let mut r = vec![0.; n];
    let mut logn = vec![f64::NEG_INFINITY; n];
    for k in 0..n {
        if template.number[k] == 0. {
            continue;
        }
        let lo = template.support_lo[k];
        let hi = template.support_hi[k];
        if hi == lo {
            p.number[k] = 1.;
            p.energy_ref[k] = lo;
            l[k] = 1.;
            logn[k] = z[k];
        } else {
            let m = z[k].max(z[n + k]);
            logn[k] = m + ((z[k] - m).exp() + (z[n + k] - m).exp()).ln() - (hi - lo).ln();
            l[k] = (z[k] - logn[k]).exp();
            r[k] = (z[n + k] - logn[k]).exp();
            if l[k] <= 0. || r[k] <= 0. || !logn[k].is_finite() {
                return Err("normalized shape ratio underflow or nonfinite".into());
            }
            p.number[k] = 1.;
            p.energy_ref[k] = if l[k] <= r[k] { lo + l[k] } else { hi - r[k] };
        }
        if p.energy_ref[k] < lo || p.energy_ref[k] > hi {
            return Err("normalized strict support domain".into());
        }
    }
    Ok((p, l, r, logn))
}
// Extra coordinates: escape,CMB,photon work,thermal work,photo[3],RR[3],CI[3],DR.
const EXTRA: usize = 14;
fn evaluate(
    s: &Setup,
    active: usize,
    x: f64,
    z: &[f64],
) -> Result<Vec<f64>, Box<dyn std::error::Error>> {
    let a = x.exp();
    let point = s.d.geometry_point(a)?;
    let g = point.geometry()?;
    let h = point.h_per_s;
    let gas = gas_decode(z)?;
    let nh = s.d.n_h0_cm3 / a.powi(3);
    let nhe = s.d.n_he0_cm3 / a.powi(3);
    let [f, y, zz] = gas.fractions;
    let ab = [nh * (1. - f), nhe * (1. - y - zz), nhe * y];
    let cells = s.d.transport.cell_count();
    let mut photo = IgmPhotoInput::default();
    let mut moments = vec![0.; 2 * cells * 8];
    let rays = s.d.transport.ray_geometry(&g)?;
    let mut work = 0.;
    for i in 0..active {
        let off = 4 + 2 * cells * i;
        let (p, l, r, logn) = normalized_decode(&s.templates[i], &z[off..off + 2 * cells])?;
        let prep = s.d.transport.prepare(&p, &g)?;
        let (dm, pp) = prep.research_positive_log_rhs(ab, nh, &l, &r, &logn)?;
        for k in 0..3 {
            photo.gamma_s[k] += pp.gamma_s[k];
            photo.heat_erg_per_absorber_s[k] += pp.heat_erg_per_absorber_s[k];
        }
        for j in 0..dm.len() {
            moments[2 * cells * i + j] = dm[j] / h;
        }
        for k in 0..cells {
            let ray = &rays[k / s.d.transport.n_energy()];
            let directional_h =
                g.hubble_per_s[0] * (1. - ray.mu * ray.mu) + g.hubble_per_s[2] * ray.mu * ray.mu;
            if p.number[k] > 0. {
                work += (logn[k] + (p.energy_ref[k] * ray.scale).ln()).exp() * directional_h / h;
            }
        }
    }
    let rhs = AxbiProvider.point(&gas, nh, nhe, h, 2.7255 / a, photo)?.rhs;
    let neutral = 1. - y - zz;
    let dneutral = -rhs.fraction_dt[1] - rhs.fraction_dt[2];
    let w = w_erg_per_h_to_ev(gas.w_erg_per_h)?;
    let ev = HHeModel::controlled_fixture().ev_erg;
    let mut out = vec![
        rhs.fraction_dt[0] / (f * (1. - f) * h),
        (rhs.fraction_dt[1] / y - dneutral / neutral) / h,
        (rhs.fraction_dt[2] / zz - dneutral / neutral) / h,
        rhs.w_dt_erg_per_h_s / (ev * w * h),
    ];
    out.extend(moments);
    out.extend([
        rhs.escape_erg_cm3_s / (nh * ev * h),
        rhs.cmb_to_gas_erg_cm3_s / (nh * ev * h),
        work,
        rhs.expansion_work_erg_cm3_s / (nh * ev * h),
    ]);
    out.extend(rhs.photo_events_cm3_s.map(|r| r / (nh * h)));
    out.extend(rhs.rr_events_cm3_s.map(|r| r / (nh * h)));
    out.extend(rhs.ci_events_cm3_s.map(|r| r / (nh * h)));
    out.push(rhs.dr_events_cm3_s / (nh * h));
    if out.iter().any(|r| !r.is_finite()) {
        return Err("nonfinite transformed RHS".into());
    }
    Ok(out)
}
fn physical(
    s: &Setup,
    active: usize,
    x: f64,
    z: &[f64],
) -> Result<String, Box<dyn std::error::Error>> {
    let gas = gas_decode(z)?;
    let g = s.d.geometry_point(x.exp())?.geometry()?;
    let cells = s.d.transport.cell_count();
    let rays = s.d.transport.ray_geometry(&g)?;
    let mut flat = vec![
        gas.fractions[0],
        gas.fractions[1],
        gas.fractions[2],
        w_erg_per_h_to_ev(gas.w_erg_per_h)?,
    ];
    let mut cohort = vec![];
    let mut totaln = 0.;
    let mut totalu = 0.;
    let mut quad = 0.;
    let mut log_population = vec![];
    let mut underflow = 0usize;
    let mut positive_lanes = 0usize;
    for i in 0..8 {
        let mut ns = vec![0.; cells];
        let mut us = vec![0.; cells];
        let mut logs = vec![];
        let mut n = 0.;
        let mut u = 0.;
        if i < active {
            let (p, _, _, logn) = normalized_decode(
                &s.templates[i],
                &z[4 + 2 * cells * i..4 + 2 * cells * (i + 1)],
            )?;
            for k in 0..cells {
                if p.number[k] == 0. {
                    logs.push(None);
                    continue;
                }
                positive_lanes += 1;
                logs.push(Some(logn[k]));
                ns[k] = logn[k].exp();
                us[k] = (logn[k] + p.energy_ref[k].ln()).exp();
                if ns[k] == 0. {
                    underflow += 1;
                }
                let ray = &rays[k / s.d.transport.n_energy()];
                let physical_u = (logn[k] + (p.energy_ref[k] * ray.scale).ln()).exp();
                n += ns[k];
                u += physical_u;
                quad += physical_u * (ray.mu * ray.mu - 1. / 3.);
            }
        } else {
            logs = vec![None; cells];
        }
        flat.extend(&ns);
        flat.extend(&us);
        cohort.push([n, u]);
        totaln += n;
        totalu += u;
        log_population.push(logs);
    }
    let log_json = log_population
        .iter()
        .map(|v| {
            format!(
                "[{}]",
                v.iter()
                    .map(|o| o.map(|x| x.to_string()).unwrap_or("null".to_string()))
                    .collect::<Vec<_>>()
                    .join(",")
            )
        })
        .collect::<Vec<_>>()
        .join(",");
    let extras = &z[4 + 2 * cells * 8..];
    // Every rounded-to-zero positive linear population is retained above in logN.
    // Underflow contributes at most one smallest binary64 subnormal per lane to
    // displayed linear N; this is an output rounding bound, not structural deletion.
    Ok(format!("{{\"flat\":{:?},\"cohorts\":{:?},\"N\":{totaln},\"U\":{totalu},\"quadrupole_U_mu2_minus_third\":{quad},\"ledgers\":{:?},\"log_population\":[{log_json}],\"positive_lanes\":{positive_lanes},\"linear_N_underflow_lanes\":{underflow},\"linear_N_underflow_absolute_bound\":{:e}}}",flat,cohort,extras,underflow as f64*f64::from_bits(1)))
}
fn diagnose(
    s: &Setup,
    active: usize,
    x: f64,
    z: &[f64],
) -> Result<String, Box<dyn std::error::Error>> {
    let g = s.d.geometry_point(x.exp())?.geometry()?;
    let cells = s.d.transport.cell_count();
    for i in 0..active {
        let (p, l, r) = decode(
            &s.templates[i],
            &z[4 + 2 * cells * i..4 + 2 * cells * (i + 1)],
        )?;
        s.d.transport.validate_state(&p)?;
        for k in 0..cells {
            if p.number[k] == 0. {
                continue;
            }
            let mut single = s.d.transport.empty_state();
            single.number[k] = p.number[k];
            single.energy_ref[k] = p.energy_ref[k];
            single.support_lo[k] = p.support_lo[k];
            single.support_hi[k] = p.support_hi[k];
            if let Err(e) = s.d.transport.prepare(&single, &g) {
                return Ok(format!("{{\"strict_native_state_valid\":true,\"cohort\":{i},\"cell\":{k},\"N\":{},\"U\":{},\"lo\":{},\"hi\":{},\"L\":{},\"R\":{},\"native_error\":\"{e:?}\"}}",p.number[k],p.energy_ref[k],p.support_lo[k],p.support_hi[k],l[k],r[k]));
            }
        }
    }
    Ok("all native prepare cells valid".to_string())
}
fn normalized_diagnose(
    s: &Setup,
    active: usize,
    x: f64,
    z: &[f64],
) -> Result<String, Box<dyn std::error::Error>> {
    let g = s.d.geometry_point(x.exp())?.geometry()?;
    let cells = s.d.transport.cell_count();
    let mut reports = vec![];
    for i in 0..active {
        let (p, _, _) = decode(
            &s.templates[i],
            &z[4 + 2 * cells * i..4 + 2 * cells * (i + 1)],
        )?;
        for k in 0..cells {
            if p.number[k] == 0. {
                continue;
            }
            let mut single = s.d.transport.empty_state();
            single.number[k] = p.number[k];
            single.energy_ref[k] = p.energy_ref[k];
            single.support_lo[k] = p.support_lo[k];
            single.support_hi[k] = p.support_hi[k];
            if s.d.transport.prepare(&single, &g).is_err() {
                let amplitude = p.number[k];
                single.number[k] = 1.;
                single.energy_ref[k] = p.energy_ref[k] / amplitude;
                let prep = s.d.transport.prepare(&single, &g)?;
                let evaluated = prep.evaluate([1., 1., 1.], 1., 0.)?;
                let scales = evaluated
                    .photo
                    .gamma_s
                    .into_iter()
                    .chain(evaluated.photo.heat_erg_per_absorber_s)
                    .map(|v| v * amplitude)
                    .collect::<Vec<_>>();
                reports.push(format!("{{\"cohort\":{i},\"cell\":{k},\"amplitude\":{amplitude:e},\"lo\":{},\"hi\":{},\"mean\":{},\"normalized_count\":{},\"normalized_reference_energy\":{},\"node_count\":{},\"max_count_relative_defect\":{},\"max_energy_relative_defect\":{},\"scaled_photo_finite\":{},\"scaled_photo\":{:?}}}",single.support_lo[k],single.support_hi[k],single.energy_ref[k],evaluated.state.number[k],evaluated.state.energy_ref[k],prep.node_count(),prep.diagnostics.max_count_relative_defect,prep.diagnostics.max_energy_relative_defect,scales.iter().all(|v|v.is_finite()),scales));
            }
        }
    }
    Ok(format!("[{}]", reports.join(",")))
}
fn server(q: f64) -> Result<(), Box<dyn std::error::Error>> {
    let s = setup(q)?;
    let x0 = s.s0.gas_owner.a.ln();
    let initial = gas_encoded(&s.s0)?;
    let cells = s.d.transport.cell_count();
    let injections = s
        .templates
        .iter()
        .map(|p| {
            let mut v = p.number.clone();
            v.extend(&p.energy_ref);
            v
        })
        .collect::<Vec<_>>();
    let active_indices = s
        .templates
        .iter()
        .enumerate()
        .map(|(i, p)| {
            let mut v = vec![];
            for k in 0..cells {
                if p.number[k] > 0. {
                    v.push(4 + 2 * cells * i + k);
                    if p.support_hi[k] > p.support_lo[k] {
                        v.push(4 + 2 * cells * i + cells + k);
                    }
                }
            }
            v
        })
        .collect::<Vec<_>>();
    let source_inventory = s
        .templates
        .iter()
        .enumerate()
        .map(|(i, p)| {
            let g = s.d.geometry_point(s.births[i].exp())?.geometry()?;
            let (n, u) = s.d.transport.inventory(p, &g)?;
            Ok([n, u])
        })
        .collect::<Result<Vec<_>, rei_microphysics::ForwardError>>()?;
    println!("{{\"x0\":{x0},\"x1\":{},\"births\":{:?},\"initial\":{:?},\"encoded_births\":{:?},\"physical_births\":{:?},\"cells\":{cells},\"extra\":{EXTRA},\"initial_physical\":{:?},\"active_indices\":{:?},\"source_inventory\":{:?},\"he_h\":{},\"binding_ev\":{:?}}}",x0+0.002,s.births,initial,s.encoded,injections,vec![s.s0.gas_owner.gas.fractions[0],s.s0.gas_owner.gas.fractions[1],s.s0.gas_owner.gas.fractions[2],w_erg_per_h_to_ev(s.s0.gas_owner.gas.w_erg_per_h)?],active_indices,source_inventory,s.d.n_he0_cm3/s.d.n_h0_cm3,HHeModel::controlled_fixture().threshold_ev);
    for line in io::stdin().lock().lines() {
        let line = line?;
        let mut iter = line.split_whitespace();
        let mode = iter.next().ok_or("missing mode")?;
        let active = iter.next().ok_or("missing active")?.parse::<usize>()?;
        let x = iter.next().ok_or("missing x")?.parse::<f64>()?;
        let z = iter.map(str::parse::<f64>).collect::<Result<Vec<_>, _>>()?;
        let result = match mode {
            "R" => evaluate(&s, active, x, &z).map(|v| {
                v.iter()
                    .map(|r| format!("{r:.17e}"))
                    .collect::<Vec<_>>()
                    .join(" ")
            }),
            "P" => physical(&s, active, x, &z),
            "D" => diagnose(&s, active, x, &z),
            "S" => normalized_diagnose(&s, active, x, &z),
            "OLD" => {
                let mut result = Ok("OLD_ACCEPTED".to_string());
                for (i, t) in s.templates.iter().enumerate() {
                    let mut p = t.clone();
                    p.number = z[4 + 2 * cells * i..4 + 2 * cells * i + cells].to_vec();
                    p.energy_ref = z[4 + 2 * cells * i + cells..4 + 2 * cells * (i + 1)].to_vec();
                    for k in 0..cells {
                        if p.number[k] == 0. {
                            p.support_lo[k] = 0.;
                            p.support_hi[k] = 0.;
                        }
                    }
                    if let Err(e) = s.d.transport.validate_state(&p) {
                        result = Err(e.into());
                        break;
                    }
                }
                result
            }
            _ => Err("invalid mode".into()),
        };
        match result {
            Ok(v) => println!("{v}"),
            Err(e) => println!("ERR {e:?}"),
        };
    }
    Ok(())
}
fn native(q: f64, out: &Path) -> Result<(), Box<dyn std::error::Error>> {
    let s = setup(q)?;
    fs::create_dir_all(out)?;
    for level in [1, 2, 4, 8] {
        let to = (s.s0.gas_owner.a.ln() + 0.002).exp();
        let mesh = common_mesh(s.s0.gas_owner.a, to, &[8], level);
        let a = trial_on_mesh(&s.d, &s.s0, to, 8, &mesh, &mut 0)?;
        let mut f = vec![
            a.gas_owner.gas.fractions[0],
            a.gas_owner.gas.fractions[1],
            a.gas_owner.gas.fractions[2],
            w_erg_per_h_to_ev(a.gas_owner.gas.w_erg_per_h)?,
        ];
        for c in &a.cohorts {
            f.extend(&c.surviving.number);
            f.extend(&c.surviving.energy_ref);
        }
        fs::write(
            out.join(format!("native_q{q}_level{level}.json")),
            format!("{{\"flat\":{:?}}}", f),
        )?;
    }
    Ok(())
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = std::env::args().collect::<Vec<_>>();
    let q = args[2].parse()?;
    match args[1].as_str() {
        "server" => server(q),
        "native" => native(q, Path::new(&args[3])),
        _ => Err("mode".into()),
    }
}
