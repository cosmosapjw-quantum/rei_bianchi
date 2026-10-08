use crate::{
    err, material, nonnegative, positive, product,
    v2::{self, Owners},
    Fallible,
};
use rei_microphysics::{
    igm_background::FlrwPoint, igm_config::HistoryConfig, igm_photo::packet_opacity,
    verner_cutoff_ev, Absorber, AtomicProvider, HHeModel,
};
pub const SPECIES: [Absorber; 3] = [Absorber::HI, Absorber::HeI, Absorber::HeII];
#[derive(Clone, Debug)]
pub struct Grid {
    pub nodes: Vec<(f64, f64)>,
    pub intervals: usize,
    pub base: usize,
    pub order: usize,
}
impl Grid {
    pub fn new(cfg: &HistoryConfig, base: usize, order: usize) -> Fallible<Self> {
        if ![128, 256, 512].contains(&base) || ![2, 4].contains(&order) {
            return Err("undeclared quadrature".into());
        }
        let s0 = cfg.start;
        let s1 = s0 + cfg.max_dln_a;
        let lo = s0 + cfg.source.energy_min_ev.ln();
        let hi = s1 + cfg.source.energy_max_ev.ln();
        let mut cuts = (0..=base)
            .map(|i| lo + (hi - lo) * i as f64 / base as f64)
            .collect::<Vec<_>>();
        let energies = [
            cfg.source.energy_min_ev,
            cfg.source.energy_max_ev,
            verner_cutoff_ev(SPECIES[0]),
            verner_cutoff_ev(SPECIES[1]),
            verner_cutoff_ev(SPECIES[2]),
        ];
        // Union of all prescribed phase-segment and endpoint-control time grids.
        for i in 0..=24 {
            let s = time_at(cfg, i, 24);
            for e in energies {
                let eta = s + e.ln();
                if eta > lo && eta < hi {
                    cuts.push(eta)
                }
            }
        }
        cuts.sort_by(f64::total_cmp);
        cuts.dedup();
        let intervals = cuts.len() - 1;
        let mut nodes = Vec::new();
        for ab in cuts.windows(2) {
            for (eta, w) in positive_rule(ab[0], ab[1], order) {
                if !(eta > ab[0] && eta < ab[1]) {
                    return Err(format!("unresolved quadrature cell {:?}", ab));
                }
                positive(w)?;
                nodes.push((eta, w));
            }
        }
        if nodes.len() > 4096 {
            return Err("live sample cap".into());
        }
        Ok(Self {
            nodes,
            intervals,
            base,
            order,
        })
    }
}
#[derive(Clone, Debug)]
pub struct Radiation {
    pub density: crate::diagnostics::Density,
    pub owners: Owners,
    pub min_heat: f64,
}
pub fn characteristic(
    cfg: &HistoryConfig,
    p: FlrwPoint,
    y: [f64; 4],
    eta: f64,
    s0: f64,
    s1: f64,
    f: f64,
) -> Fallible<Owners> {
    characteristic_staged(cfg, eta, s0, s1, f, |_| Ok((y, p)))
}
/// The same affine stage function is used by the physical path and mathematical controls.
pub fn affine(y0: [f64; 4], y1: [f64; 4], theta: f64) -> [f64; 4] {
    std::array::from_fn(|i| y0[i] + theta * (y1[i] - y0[i]))
}
pub fn characteristic_path(
    cfg: &HistoryConfig,
    y0: [f64; 4],
    y1: [f64; 4],
    eta: f64,
    s0: f64,
    s1: f64,
    f: f64,
) -> Fallible<Owners> {
    characteristic_staged(cfg, eta, s0, s1, f, |m| {
        let theta = (m - s0) / (s1 - s0);
        if !(theta > 0. && theta < 1.) {
            return Err("unresolved affine stage".into());
        }
        let p = cfg.background.at_ln_a(m).map_err(err)?;
        let y = affine(y0, y1, theta);
        material::rhs(y, p)?;
        crate::diagnostics::stage(2, y, p)?;
        Ok((y, p))
    })
}
fn characteristic_staged<F: FnMut(f64) -> Fallible<([f64; 4], FlrwPoint)>>(
    cfg: &HistoryConfig,
    eta: f64,
    s0: f64,
    s1: f64,
    f: f64,
    mut stage: F,
) -> Fallible<Owners> {
    if !f.is_finite() || f < 0.0 {
        return Err("invalid transported stock".into());
    }
    if s1 <= s0 {
        return Err("invalid temporal cell".into());
    }
    let source_start = eta - cfg.source.energy_max_ev.ln();
    let source_stop = eta - cfg.source.energy_min_ev.ln();
    let tau = eta - verner_cutoff_ev(SPECIES[0]).ln();
    if tau <= s0 {
        if f != 0.0 {
            return Err("unsupported initial outflow stock".into());
        }
        return Ok(Owners::default());
    }
    let end = s1.min(tau);
    let mut events = vec![source_start, source_stop];
    for a in SPECIES {
        events.push(eta - verner_cutoff_ev(a).ln())
    }
    let cuts = v2::topology(s0, end, &events);
    let mut stock = f;
    let mut last_u: Option<f64> = None;
    let mut last_pair = None;
    let mut sum = Owners::default();
    for ab in cuts.windows(2) {
        let (a, b) = (ab[0], ab[1]);
        let mid = (a + b) * 0.5;
        if !(mid > a && mid < b) {
            return Err(format!(
                "unresolved temporal geometry eta={eta:.17e},a={a:.17e},b={b:.17e}"
            ));
        }
        let (y, p) = stage(mid)?;
        let g = material::gas(y)?;
        let e = positive((eta - mid).exp())?;
        let opacity = packet_opacity(&g, e, p.n_h_cm3, p.n_he_cm3).map_err(err)?;
        let rates = std::array::from_fn(|i| opacity[i] / p.hubble_per_s);
        let q = if mid >= source_start && mid < source_stop {
            positive(
                cfg.source.photons_per_h_per_s
                    / ((1.0 / cfg.source.energy_min_ev - 1.0 / cfg.source.energy_max_ev)
                        * e
                        * p.hubble_per_s),
            )?
        } else {
            0.0
        };
        let (energy_start, _) = crate::event_anchor::start_energy(eta, a, b)?;
        if let Some(previous_u) = last_u {
            let begin = v2::EPS * energy_start * stock;
            if (previous_u - begin).abs() > 2e-12 * previous_u.abs().max(begin.abs()) {
                return Err("cross-segment energy discontinuity".into());
            }
        }
        let mut o = v2::kernel(stock, q, rates, b - a, energy_start).map_err(|e| {
            format!(
                "kernel {e}; eta={eta:.17e},a={a:.17e},b={b:.17e},Eend={:.17e}",
                (eta - a).exp() * (-(b - a)).exp()
            )
        })?;
        crate::record::segment(eta, a, b, y, p, stock, q, rates, energy_start, o)?;
        // Inspect authoritative final state before stripping stock from cumulative owners.
        let mut check = Owners::default();
        v2::try_add_scaled(&mut check, o, 1.0).map_err(|e| {
            format!(
                "segment owner admission {e}; eta={eta:.17e},a={a:.17e},b={b:.17e},N={:.17e},U={:.17e},lnN={:?},lnU={:?}",
                o.n, o.u, o.ln_n, o.ln_u
            )
        })?;
        let ledger = v2::owner_ledger(o).map_err(err)?;
        for i in 0..3 {
            material::photoheat_owner(
                o.an[i],
                o.be[i],
                HHeModel::controlled_fixture().threshold_ev[i],
                ledger.heat[i],
            )
            .map_err(|e| {
                format!(
                    "segment photoheat {e}; species={i},eta={eta:.17e},a={a:.17e},b={b:.17e},A={:.17e},B={:.17e}",
                    o.an[i], o.be[i]
                )
            })?;
        }
        stock = o.n;
        last_u = Some(o.u);
        last_pair = Some((
            ledger.terms[0],
            ledger.terms[1],
            [ledger.occurrence[0], ledger.occurrence[1]],
            [ledger.coefficient[0], ledger.coefficient[1]],
        ));
        o.n = 0.0;
        o.u = 0.0;
        v2::replace_owner_components(&mut o,&[0,1]).map_err(err)?;
        o.ln_n = None;
        o.ln_u = None;
        v2::try_add_scaled(&mut sum, o, 1.0).map_err(err)?;
    }
    if tau <= s1 {
        sum.outn = stock;
        sum.oute = product(
            product(
                HHeModel::controlled_fixture().ev_erg,
                verner_cutoff_ev(SPECIES[0]),
            )?,
            stock,
        )?;
    } else {
        let mut ledger = v2::owner_ledger(sum).map_err(err)?;
        sum.n = stock;
        sum.u = last_u.unwrap_or(0.0);
        crate::diagnostics::continuity(sum.u, v2::EPS * (eta - s1).exp() * stock)?;
        if stock > 0.0 {
            let (number, energy, occurrence, coefficient) =
                last_pair.ok_or("missing canonical transported pair")?;
            ledger.terms[0] = number;
            ledger.terms[1] = energy;
            ledger.occurrence[0] = occurrence[0];
            ledger.occurrence[1] = occurrence[1];
            ledger.coefficient[0] = coefficient[0];
            ledger.coefficient[1] = coefficient[1];
            sum.canonical = Some(ledger);
            sum.ln_n = Some(number.value.log());
            sum.ln_u = Some(energy.value.log())
        }
    }
    if tau <= s1 {
        v2::replace_owner_components(&mut sum, &[0, 1, 5, 6]).map_err(err)?;
    } else {
        v2::replace_owner_components(&mut sum, &[5, 6]).map_err(err)?;
    }
    if eta >= s1 + cfg.source.energy_max_ev.ln() && sum.n != 0.0 {
        return Err("nonzero at/beyond causal source front".into());
    }
    Ok(sum)
}
pub fn transaction(
    cfg: &HistoryConfig,
    grid: &Grid,
    p: FlrwPoint,
    y: [f64; 4],
    s0: f64,
    s1: f64,
    old: &crate::diagnostics::Density,
) -> Fallible<Radiation> {
    if old.len() != grid.nodes.len() {
        return Err("grid/state length mismatch".into());
    }
    material::rhs(y, p)?;
    let mut owners = Owners::default();
    let mut density = Vec::with_capacity(old.len());
    let mut canonical_density = Vec::with_capacity(old.len());
    let mut min_heat = f64::INFINITY;
    for (j, &(eta, w)) in grid.nodes.iter().enumerate() {
        let o = characteristic(cfg, p, y, eta, s0, s1, old[j])?;
        density.push(o.n);
        let ledger = v2::owner_ledger(o).map_err(err)?;
        canonical_density.push(crate::diagnostics::PhotonNode {
            number: ledger.terms[0],
            energy: ledger.terms[1],
        });
        v2::try_add_scaled(&mut owners, o, w).map_err(err)?;
        for i in 0..3 {
            min_heat = min_heat.min(o.be[i] - v2::EPS * v2::CHI[i] * o.an[i]);
        }
    }
    Ok(Radiation {
        density: crate::diagnostics::Density::from_parts(density, canonical_density).map_err(err)?,
        owners,
        min_heat,
    })
}
/// Private all-owner transaction with actual segment-centered physical staging.
pub fn transaction_path(
    cfg: &HistoryConfig,
    grid: &Grid,
    y0: [f64; 4],
    y1: [f64; 4],
    s0: f64,
    s1: f64,
    old: &crate::diagnostics::Density,
) -> Fallible<Radiation> {
    if old.len() != grid.nodes.len() {
        return Err("grid/state length mismatch".into());
    }
    let mut owners = Owners::default();
    let mut density = Vec::with_capacity(old.len());
    let mut canonical_density = Vec::with_capacity(old.len());
    let mut min_heat = f64::INFINITY;
    for (j, &(eta, w)) in grid.nodes.iter().enumerate() {
        crate::record::node(j, w);
        let o = characteristic_path(cfg, y0, y1, eta, s0, s1, old[j])?;
        crate::record::node_output(j, o)?;
        density.push(o.n);
        let ledger = v2::owner_ledger(o).map_err(err)?;
        canonical_density.push(crate::diagnostics::PhotonNode {
            number: ledger.terms[0],
            energy: ledger.terms[1],
        });
        v2::try_add_scaled(&mut owners, o, w).map_err(err)?;
        for i in 0..3 {
            min_heat = min_heat.min(o.be[i] - v2::EPS * v2::CHI[i] * o.an[i]);
        }
    }
    Ok(Radiation {
        density: crate::diagnostics::Density::from_parts(density, canonical_density).map_err(err)?,
        owners,
        min_heat,
    })
}
pub fn inventory(grid: &Grid, _s: f64, density: &crate::diagnostics::Density) -> Fallible<[f64; 2]> {
    use canonical::Tracked;
    let mut n = Tracked::empty();
    let mut e = Tracked::empty();
    for (&(_, w), node) in grid.nodes.iter().zip(density.canonical()) {
        n = n.add(node.number.scale(w).map_err(err)?).map_err(err)?;
        e = e.add(node.energy.scale(w).map_err(err)?).map_err(err)?;
    }
    Ok([nonnegative(n.readout().map_err(err)?.0)?, nonnegative(e.readout().map_err(err)?.0)?])
}
pub static LAST_GAMMA_BOUND:std::sync::Mutex<[f64;3]>=std::sync::Mutex::new([0.;3]);
pub fn gamma(grid:&Grid,s:f64,density:&crate::diagnostics::Density,p:FlrwPoint)->Fallible<[f64;3]>{
 use canonical::{Tracked,Wide};let c=HHeModel::controlled_fixture();let mut out=[Tracked::empty();3];
 for (&(eta,w),node) in grid.nodes.iter().zip(density.canonical()){for i in 0..3{let sigma=AtomicProvider::reference().cross_section(SPECIES[i],(eta-s).exp()).map_err(err)?;
 let mut t=node.number;for factor in [c.c_cm_s,p.n_h_cm3,sigma,w]{t=t.scale(factor).map_err(err)?;if !t.value.is_empty(){t.loss=t.loss.upper_add(Wide::from_parts(1.,t.value.exponent()-51).map_err(err)?).map_err(err)?;}}
 let old=out[i];out[i]=old.add(t).map_err(err)?;if !old.value.is_empty()&&!t.value.is_empty(){out[i].loss=out[i].loss.upper_add(Wide::from_parts(1.,out[i].value.exponent()-51).map_err(err)?).map_err(err)?;}}}
 let mut values=[0.;3];let mut bounds=[0.;3];for i in 0..3{let(v,b)=out[i].readout().map_err(err)?;values[i]=v;bounds[i]=b.bound_readout().map_err(err)?;if bounds[i]>1e-22+1e-3*v.abs(){return Err("GAMMA_REPRESENTATION_ORIGINAL_ALLOWANCE".into())}}
 *LAST_GAMMA_BOUND.lock().map_err(err)?=bounds;Ok(values)
}

/// Canonical common time lattice: all prescribed denominators divide 24.
pub fn time_at(cfg: &HistoryConfig, k: usize, n: usize) -> f64 {
    assert!(n > 0 && (24 % n == 0 || [48, 96, 192].contains(&n)));
    let lattice = if n <= 24 {
        (k * (24 / n)) as f64
    } else {
        k as f64 / (n / 24) as f64
    };
    cfg.start + cfg.max_dln_a * lattice / 24.0
}
/// Explicit positive Gauss4, independently formed from closed-form nodes/weights.
fn positive_rule(a: f64, b: f64, order: usize) -> Vec<(f64, f64)> {
    let h = (b - a) * 0.5;
    let nodes = if order == 2 {
        vec![(-1. / 3f64.sqrt(), 1.), (1. / 3f64.sqrt(), 1.)]
    } else {
        let d = (6f64 / 5.).sqrt();
        let inner = ((3. - 2. * d) / 7.).sqrt();
        let outer = ((3. + 2. * d) / 7.).sqrt();
        let wi = (18. + 30f64.sqrt()) / 36.;
        let wo = (18. - 30f64.sqrt()) / 36.;
        vec![(-outer, wo), (-inner, wi), (inner, wi), (outer, wo)]
    };
    nodes
        .into_iter()
        .map(|(x, w)| (a + h * (1. + x), h * w))
        .collect()
}
