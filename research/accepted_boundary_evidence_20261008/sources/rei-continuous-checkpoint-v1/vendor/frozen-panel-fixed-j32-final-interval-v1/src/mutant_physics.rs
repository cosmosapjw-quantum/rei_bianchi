//! Frozen material, evolving-background characteristic adapter. MODEL_UNRESOLVED.
//! No provider, gas state, accepted primitive, or physical support is modified.
use super::*;
use rei_microphysics::{
    igm_background::FlrwPoint,
    igm_config::{parse_config, HistoryConfig},
    igm_photo::packet_opacity,
    igm_state::IgmGasState,
    igm_thermal::igm_point_rhs,
    verner_cutoff_ev, Absorber, AtomicProvider, HHeModel,
};
const SPECIES: [Absorber; 3] = [Absorber::HI, Absorber::HeI, Absorber::HeII];
pub struct Frame {
    pub cfg: HistoryConfig,
    pub gas: IgmGasState,
    pub times: [f64; 17],
    pub mesh: Vec<f64>,
}
impl Frame {
    pub fn new(bulk: usize) -> R<Self> {
        if bulk != 64 && bulk != 128 { return Err("only B64/B128 are admitted".into()); }
        let cfg = parse_config(include_str!("../../long-flrw/configs/igm_manufactured_z12_to10.cfg")).map_err(err)?;
        if cfg.max_dln_a.to_bits() != 0.0002f64.to_bits()
            || cfg.fractions != [2e-4, 0., 0.]
            || cfg.temperature_k != 30.
            || cfg.source.photons_per_h_per_s != 1e-15
            || cfg.source.energy_min_ev != 13.7 || cfg.source.energy_max_ev != 100.
        { return Err("manufactured fixture changed".into()); }
        count("config_parses", 1);
        let p = cfg.background.at_ln_a(cfg.start).map_err(err)?;
        count("background_calls", 1);
        let gas = IgmGasState::from_temperature(cfg.fractions, p.n_h_cm3, p.n_he_cm3, cfg.temperature_k).map_err(err)?;
        // Construct once. Every later stage borrows this identical material state.
        let times = std::array::from_fn(|j| cfg.start + cfg.max_dln_a * (j as f64 / 4.));
        let l = cfg.start + cfg.source.energy_min_ev.ln();
        let r = times[16] + cfg.source.energy_max_ev.ln();
        let grid: [f64; 129] = std::array::from_fn(|i| l + (r-l) * i as f64 / 128.);
        let mut mesh = Vec::with_capacity(214);
        for i in (0..=128).step_by(128 / bulk) { mesh.push(grid[i]); }
        let energies = [cfg.source.energy_min_ev, cfg.source.energy_max_ev,
            verner_cutoff_ev(SPECIES[0]), verner_cutoff_ev(SPECIES[1]), verner_cutoff_ev(SPECIES[2])];
        for s in times { for e in energies { let edge = s + e.ln(); if edge > l && edge < r { mesh.push(edge); } } }
        record_vec("physics.mesh.pre_dedup", &mesh);
        mesh.sort_by(f64::total_cmp);
        mesh.dedup_by(|a,b| *a == *b);
        record_vec("physics.mesh", &mesh);
        if mesh.len()-1 > 256 { return Err("persistent panel cap".into()); }
        let frame = Self { cfg, gas, times, mesh };
        frame.admit_stage(frame.times[0])?;
        Ok(frame)
    }

    fn energies(&self) -> [f64; 5] {
        [self.cfg.source.energy_min_ev, self.cfg.source.energy_max_ev,
         verner_cutoff_ev(SPECIES[0]), verner_cutoff_ev(SPECIES[1]), verner_cutoff_ev(SPECIES[2])]
    }
    fn admit_stage(&self, s: f64) -> R<FlrwPoint> {
        let p = self.cfg.background.at_ln_a(s).map_err(err)?;
        count("background_calls", 1);
        self.gas.eos(p.n_h_cm3, p.n_he_cm3).map_err(err)?;
        count("eos_calls", 1);
        igm_point_rhs(&self.gas, p.n_h_cm3, p.n_he_cm3, p.hubble_per_s, p.tcmb_k, Default::default()).map_err(err)?;
        count("zero_photo_rhs_calls", 1);
        Ok(p)
    }

    /// Replay at most four bases, with only the retained lattice's temporal cuts.
    /// Endpoint stock replaces its predecessor; only eleven flow owners accumulate.
    pub fn replay(&self, eta: f64, base_start: usize, base_end: usize, m: usize,
                  initial: Tracked, source_on: bool) -> R<Owners> {
        if !eta.is_finite() || base_start >= base_end || base_end > 4 || ![1,2,4].contains(&m) {
            return Err("unsupported replay descriptor".into());
        }
        let _sites = SiteGuard::new(22)?;
        let s0 = self.times[4*base_start];
        let s1 = self.times[4*base_end];
        let tau = eta - verner_cutoff_ev(SPECIES[0]).ln();
        if tau <= s0 {
            if !initial.value.is_empty() || !initial.loss.is_empty() { return Err("unsupported initial outflow stock".into()); }
            return Ok(Owners::empty());
        }
        let end = s1.min(tau);
        let mut cuts = Vec::with_capacity(22);
        cuts.push(s0); cuts.push(end);
        for j in (4*base_start..=4*base_end).step_by(4/m) {
            let s = self.times[j]; if s > s0 && s < end { cuts.push(s); }
        }
        for e in self.energies() { let t = eta-e.ln(); if t > s0 && t < end { cuts.push(t); } }
        record_vec("physics.events.pre_dedup", &cuts);
        cuts.sort_by(f64::total_cmp); cuts.dedup_by(|a,b| *a == *b);
        record_vec("physics.events", &cuts);
        let mut increments = Vec::with_capacity(21);
        record_vec("physics.segment_owners", &increments);
        let source_start = eta-self.cfg.source.energy_max_ev.ln();
        let source_stop = eta-self.cfg.source.energy_min_ev.ln();
        let mut stock = initial;
        let mut last_u: Option<Tracked> = None;
        for ab in cuts.windows(2) {
            let (a,b) = (ab[0],ab[1]); let h = b-a;
            if h < 1e-12 || h > 2. { return Err(format!("unsupported positive segment eta={:016x} a={:016x} b={:016x} h={:016x}", eta.to_bits(), a.to_bits(), b.to_bits(), h.to_bits())); }
            let mid = (a+b)*0.5;
            if !(mid > a && mid < b) { return Err("unresolved segment midpoint".into()); }
            let p = self.admit_stage(mid)?;
            let e = (eta-mid).exp();
            let opacity = packet_opacity(&self.gas, e, p.n_h_cm3, p.n_he_cm3).map_err(err)?;
            count("opacity_calls", 1);
            let rates = std::array::from_fn(|i| opacity[i]/p.hubble_per_s);
            let q = if source_on && mid >= source_start && mid < source_stop {
                self.cfg.source.photons_per_h_per_s / ((1./self.cfg.source.energy_min_ev - 1./self.cfg.source.energy_max_ev)*e*p.hubble_per_s)
            } else { 0. };
            let q = Tracked::from_f64(q).map_err(err)?;
            let (energy_start, _) = start_energy(eta,a,b)?;
            if let Some(previous) = last_u {
                let beginning = stock.scale(energy_start).map_err(err)?.scale(EPS).map_err(err)?;
                let (lo,hi) = if previous.value.le(beginning.value) { (previous.value,beginning.value) } else { (beginning.value,previous.value) };
                if rel(lo,hi)?.abs() > 2e-12 {
                    return Err(format!("cross-segment carried energy discontinuity eta={:016x} a={:016x} b={:016x}",eta.to_bits(),a.to_bits(),b.to_bits()));
                }
            }
            count("characteristic_segments", 1);
            let mut o = segment(stock, q, rates, h, energy_start).map_err(|e| format!("{e}; eta={:016x} a={:016x} b={:016x} E={:016x}",eta.to_bits(),a.to_bits(),b.to_bits(),energy_start.to_bits()))?;
            if !o.a[2].value.is_empty() || !o.b[2].value.is_empty() || !o.outn.value.is_empty() || !o.oute.value.is_empty() {
                return Err("fixture exact-zero species/outflow invariant".into());
            }
            stock = o.n; last_u = Some(o.u);
            o.n = Tracked::empty(); o.u = Tracked::empty();
            increments.push(o);
            record_vec("physics.segment_owners", &increments);
        }
        record_vec("physics.segment_owners", &increments);
        if end != s1 && (!stock.value.is_empty() || !stock.loss.is_empty()) { return Err("physical cutoff export is outside this frozen window".into()); }
        let mut out = sum_owners(&increments)?;
        out.n = stock;
        out.u = last_u.unwrap_or(Tracked::empty());
        Ok(out)
    }

    /// Per-density direct Gamma (s^-1) and instantaneous heat (erg/H/s).
    /// Gamma never divides an absorption owner by a vanishing neutral fraction.
    pub fn diagnostic_rates(&self, eta: f64, s: f64) -> R<[f64;4]> {
        if !eta.is_finite() || !s.is_finite() { return Err("invalid endpoint diagnostic".into()); }
        let p = self.admit_stage(s)?;
        let e = (eta-s).exp();
        if !(13.6..=1e4).contains(&e) { return Err("endpoint energy outside primitive domain".into()); }
        let opacity = packet_opacity(&self.gas,e,p.n_h_cm3,p.n_he_cm3).map_err(err)?;
        count("opacity_calls", 1);
        let c = HHeModel::controlled_fixture();
        let mut out = [0.;4];
        for i in 0..3 {
            let sigma = AtomicProvider::reference().cross_section(SPECIES[i], e).map_err(err)?;
            count("cross_section_calls", 1);
            out[i] = c.c_cm_s*p.n_h_cm3*sigma;
            if sigma > 0. { out[3] += opacity[i]*EPS*(e-c.threshold_ev[i]); }
        }
        if !out.into_iter().all(|v| v.is_finite() && v >= 0.) { return Err("invalid direct physical rate".into()); }
        Ok(out)
    }

    /// Independent continuous-density control on the very same immutable closure.
    /// One base transition; m selects temporal staging and order is 16 or 32.
    pub fn stock_density_control(&self, panel: &Panel, base: usize, m: usize, order: usize) -> R<Owners> {
        if base >= 4 || ![1,2,4].contains(&m) || ![16,32].contains(&order) {
            return Err("unsupported continuous-density control".into());
        }
        let _sites = SiteGuard::new(order+64)?;
        // Include every stored historical transformed edge, not a P+10 estimate.
        let mut cuts = Vec::with_capacity(87);
        cuts.push(panel.l); cuts.push(panel.r);
        for s in self.times { for e in self.energies() { let edge = s+e.ln(); if edge > panel.l && edge < panel.r { cuts.push(edge); } } }
        record_vec("physics.stock_cuts.pre_dedup", &cuts);
        cuts.sort_by(f64::total_cmp); cuts.dedup_by(|a,b| *a == *b);
        record_vec("physics.stock_cuts", &cuts);
        let mut pieces = Vec::with_capacity(cuts.len()-1);
        record_vec("physics.stock_piece_totals", &pieces);
        for ab in cuts.windows(2) {
            let nodes = v2::gauss(ab[0],ab[1],order);
            record_vec("physics.stock_nodes", &nodes);
            count("quadrature_sites_created", nodes.len());
            let mut values = Vec::with_capacity(order);
            record_vec("physics.stock_site_owners", &values);
            for (eta, weight) in nodes {
                if !(eta > ab[0] && eta < ab[1] && weight > 0.) { return Err("unresolved positive stock node".into()); }
                let density = panel.density(eta)?;
                let coefficient = Tracked::exact(density).scale(1.).map_err(err)?;
                let o = self.replay(eta,base,base+1,m,Tracked::from_f64(1.).map_err(err)?,false)?;
                values.push(o.weighted(coefficient).map_err(err)?);
                record_vec("physics.stock_site_owners", &values);
            }
            record_vec("physics.stock_site_owners", &values);
            pieces.push(sum_owners(&values)?);
            record_vec("physics.stock_piece_totals", &pieces);
            count("quadrature_sites_retired", order);
        }
        record_vec("physics.stock_piece_totals", &pieces);
        sum_owners(&pieces)
    }
}
