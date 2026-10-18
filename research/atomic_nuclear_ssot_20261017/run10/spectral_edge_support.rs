//! RUN10 candidate: photon-count anchored, positive two-node spectral rules.
//! SOURCE_WRITTEN_NOT_COMPILED: ChatGPT sandbox unavailable in this turn.
//! No parent owner, native solver, input packet or default behavior is modified.
//! All energies and kT are eV. Fractions refer to the whole native source.
//! Caller must independently establish monotonically nonincreasing ray energy.
//! An endpoint ratio <= 1 alone is NOT a monotonicity certificate.
#![forbid(unsafe_code)]

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Error { Input, UnresolvedBand, MomentDomain, MomentConvergence }
#[derive(Debug, Clone, Copy)]
pub struct Cell {
    pub lower_ev: f64,
    pub upper_ev: f64,
    pub owner_mean_ev: f64,
    pub photon_fraction: f64,
}
#[derive(Debug, Clone, Copy)]
pub struct Node {
    pub energy_ev: f64,
    pub photon_fraction: f64,
    pub panel_lower_ev: f64,
    pub panel_upper_ev: f64,
}
#[derive(Debug, Clone)]
pub struct Rule {
    pub nodes: Vec<Node>,
    pub photon_fraction_residual: f64,
    pub continuous_mean_ev: f64,
    pub mean_residual_ev: f64,
    pub continuous_minus_owner_mean_ev: f64,
}

/// Birth thresholds and their terminal preimages. Exact duplicate cuts only.
/// active_edges must be max(binding threshold, cross-section fit threshold).
/// The mathematical scope is a positive, achromatic, monotone redshift path.
pub fn monotone_swept_cuts(
    lo: f64, hi: f64, ratio_end: f64, active_edges: &[f64],
) -> Result<Vec<f64>, Error> {
    if !lo.is_finite() || !hi.is_finite() || lo <= 0.0 || hi <= lo
        || !ratio_end.is_finite() || ratio_end <= 0.0 || ratio_end > 1.0
        || active_edges.iter().any(|e| !e.is_finite() || *e <= 0.0) {
        return Err(Error::Input);
    }
    let mut cuts = vec![lo, hi];
    for &edge in active_edges {
        if lo < edge && edge < hi { cuts.push(edge); }
        // Avoid overflow: a preimage at or beyond hi is outside this cell.
        if edge < hi * ratio_end {
            let preimage = edge / ratio_end;
            if lo < preimage && preimage < hi { cuts.push(preimage); }
        }
    }
    cuts.sort_by(f64::total_cmp);
    cuts.dedup();
    Ok(cuts)
}

/// Raw moments in local z=(E-mid)/half on [-1,1], including dE.
/// The shape is the existing E^2/expm1(E/kT); no new atomic rate is introduced.
fn simpson_moments(lo: f64, hi: f64, kt: f64, n: usize) -> Result<[f64;4], Error> {
    let mid = 0.5 * (lo + hi);
    let half = 0.5 * (hi - lo);
    if !(lo < mid && mid < hi) { return Err(Error::UnresolvedBand); }
    let mut out = [0.0;4];
    let mut correction = [0.0;4];
    for i in 0..=n {
        let z = -1.0 + 2.0 * i as f64 / n as f64;
        let energy = mid + half * z;
        let denominator = (energy / kt).exp_m1();
        if !denominator.is_finite() || denominator <= 0.0 { return Err(Error::MomentDomain); }
        let simpson = if i == 0 || i == n { 1.0 } else if i % 2 == 0 { 2.0 } else { 4.0 };
        let factor = (2.0 * half / (3.0 * n as f64)) * simpson * energy * energy / denominator;
        let mut power = 1.0;
        for k in 0..4 {
            let value = factor * power - correction[k];
            let next = out[k] + value;
            correction[k] = (next - out[k]) - value;
            out[k] = next;
            power *= z;
        }
    }
    if out.iter().any(|x| !x.is_finite()) || out[0] <= 0.0 { return Err(Error::MomentDomain); }
    Ok(out)
}

/// Successive Simpson rules test local moments against the positive zeroth moment.
/// This stopping criterion is a diagnostic, NOT a rigorous quadrature enclosure.
pub fn blackbody_moments(lo: f64, hi: f64, kt: f64) -> Result<[f64;4], Error> {
    if !lo.is_finite() || !hi.is_finite() || !kt.is_finite()
        || lo <= 0.0 || hi <= lo || kt <= 0.0 { return Err(Error::Input); }
    let mut previous = simpson_moments(lo, hi, kt, 32)?;
    for n in [64,128,256,512,1024,2048,4096] {
        let current = simpson_moments(lo, hi, kt, n)?;
        let change = (0..4).map(|k| (current[k]-previous[k]).abs()).fold(0.0_f64,f64::max);
        if change <= 5e-13 * current[0] { return Ok(current); }
        previous = current;
    }
    Err(Error::MomentConvergence)
}

/// Positive two-node Gauss-Christoffel rule from local moments M0..M3.
/// Returns (z, conditional weight); conditional weights sum to one mathematically.
pub fn gauss2_local(m: [f64;4]) -> Result<[(f64,f64);2],Error> {
    if m.iter().any(|x| !x.is_finite()) || m[0] <= 0.0 { return Err(Error::MomentDomain); }
    let mu = m[1]/m[0];
    let second = m[2]/m[0];
    let variance = second-mu*mu;
    if !variance.is_finite() || variance <= 0.0 { return Err(Error::MomentDomain); }
    let third = m[3]/m[0]-3.0*mu*second+2.0*mu*mu*mu;
    let alpha = third/variance;
    let radius = (alpha*alpha+4.0*variance).sqrt();
    let zm = mu+0.5*(alpha-radius);
    let zp = mu+0.5*(alpha+radius);
    let wm = (zp-mu)/(zp-zm);
    let wp = (mu-zm)/(zp-zm);
    if !(-1.0 < zm && zm < zp && zp < 1.0 && wm > 0.0 && wp > 0.0)
        || !wm.is_finite() || !wp.is_finite() { return Err(Error::MomentDomain); }
    Ok([(zm,wm),(zp,wp)])
}

/// Replace only one source cell; the caller keeps all other cells byte-for-byte.
/// f_child = f_owner * integral_child(shape)/integral_cell(shape).
/// This defines the conditional source measure, not a post-evolution repair.
/// The continuous mean and the stored Simpson32 owner mean are reported separately.
/// Do not suppress the reported residuals or claim exact binary64 conservation.
pub fn refine_cell(
    cell: Cell, ratio_end: f64, active_edges: &[f64], subdivisions: usize, kt_ev: f64,
) -> Result<Rule,Error> {
    if !cell.photon_fraction.is_finite() || cell.photon_fraction <= 0.0
        || !cell.owner_mean_ev.is_finite()
        || !(cell.lower_ev < cell.owner_mean_ev && cell.owner_mean_ev < cell.upper_ev)
        || !(1..=64).contains(&subdivisions) { return Err(Error::Input); }
    let cuts = monotone_swept_cuts(cell.lower_ev,cell.upper_ev,ratio_end,active_edges)?;
    let full = blackbody_moments(cell.lower_ev,cell.upper_ev,kt_ev)?;
    let continuous_mean = 0.5*(cell.lower_ev+cell.upper_ev)
        +0.5*(cell.upper_ev-cell.lower_ev)*full[1]/full[0];
    let mut nodes = Vec::with_capacity(2*(cuts.len()-1)*subdivisions);
    for pair in cuts.windows(2) {
        for j in 0..subdivisions {
            let a = if j == 0 {pair[0]} else {pair[0]+(pair[1]-pair[0])*j as f64/subdivisions as f64};
            let b = if j+1 == subdivisions {pair[1]} else {pair[0]+(pair[1]-pair[0])*(j+1) as f64/subdivisions as f64};
            let m = blackbody_moments(a,b,kt_ev)?;
            for (z,w) in gauss2_local(m)? {
                let energy = 0.5*(a+b)+0.5*(b-a)*z;
                let fraction = cell.photon_fraction*(m[0]/full[0])*w;
                if !(a < energy && energy < b) { return Err(Error::UnresolvedBand); }
                if !fraction.is_finite() || fraction <= 0.0 { return Err(Error::MomentDomain); }
                nodes.push(Node {energy_ev:energy,photon_fraction:fraction,panel_lower_ev:a,panel_upper_ev:b});
            }
        }
    }
    let count:f64 = nodes.iter().map(|p|p.photon_fraction).sum();
    let energy:f64 = nodes.iter().map(|p|p.photon_fraction*p.energy_ev).sum();
    Ok(Rule {
        photon_fraction_residual:count-cell.photon_fraction,
        continuous_mean_ev:continuous_mean,
        mean_residual_ev:energy/cell.photon_fraction-continuous_mean,
        continuous_minus_owner_mean_ev:continuous_mean-cell.owner_mean_ev,
        nodes,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture()->Cell {Cell{lower_ev:13.6,upper_ev:13.6*(24.59_f64/13.6).powf(1.0/16.0),owner_mean_ev:13.854295937824058,photon_fraction:0.1}}
    fn kt()->f64 {1.380649e-16/1.602176634e-12*50000.0}
    const D:f64=13.602134599702;
    #[test] fn swept_edges_are_sorted() {
        let c=fixture(); let e=monotone_swept_cuts(c.lower_ev,c.upper_ev,(-0.0004_f64).exp(),&[13.6,D]).unwrap();
        assert_eq!(e.len(),5); assert!(e.windows(2).all(|p|p[0]<p[1]));
    }
    #[test] fn static_path_has_only_birth_edges() {
        let c=fixture();assert_eq!(monotone_swept_cuts(c.lower_ev,c.upper_ev,1.0,&[13.6,D,D]).unwrap().len(),3);
    }
    #[test] fn invalid_endpoint_ratio_rejected() {
        for eta in [0.0,-1.0,1.001,f64::NAN] {assert_eq!(monotone_swept_cuts(13.6,14.2,eta,&[D]),Err(Error::Input));}
    }
    #[test] fn uniform_rule_reproduces_four_moments() {
        let q=gauss2_local([2.0,0.0,2.0/3.0,0.0]).unwrap();
        for k in 0_i32..4 {let v:f64=q.iter().map(|(z,w)|w*z.powi(k)).sum();let target=if k%2==0 {1.0/(k+1)as f64}else{0.0};assert!((v-target).abs()<1e-14);}
    }
    #[test] fn first_cell_count_energy_and_positivity() {
        let c=fixture();let r=refine_cell(c,(-0.0004_f64).exp(),&[13.6,D],1,kt()).unwrap();
        assert_eq!(r.nodes.len(),8);assert!(r.nodes.iter().all(|p|p.photon_fraction>0.0));
        assert!(r.photon_fraction_residual.abs()<1e-11*c.photon_fraction);
        assert!(r.mean_residual_ev.abs()<1e-10);
        assert!(r.continuous_minus_owner_mean_ev.abs()<1e-10);
    }
    #[test] fn deuterium_crossing_band_is_represented() {
        let eta=(-0.0004_f64).exp();let c=fixture();let r=refine_cell(c,eta,&[13.6,D],1,kt()).unwrap();
        let crossing:f64=r.nodes.iter().filter(|p|D<p.energy_ev&&p.energy_ev<D/eta).map(|p|p.photon_fraction).sum();
        assert!((crossing/c.photon_fraction-0.010871289873784619).abs()<5e-11);
    }
}
