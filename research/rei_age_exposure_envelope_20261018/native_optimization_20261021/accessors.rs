// Task-only APIs appended to the frozen owner module. No new dependency.
static REI_REPAIRS: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
static REI_MAX_REPAIRED_BITS: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
pub fn rei_repair_stats() -> (u64,u64) {
    (REI_REPAIRS.load(std::sync::atomic::Ordering::Relaxed),REI_MAX_REPAIRED_BITS.load(std::sync::atomic::Ordering::Relaxed))
}
fn rei_barycenter(lo:f64,hi:f64,n:f64,u:f64,energy_scale:f64) -> Option<Vec<(f64,f64)>> {
    if !(n.is_finite() && n>0. && n<f64::MIN_POSITIVE && lo.is_finite() && hi.is_finite()
        && lo>=0. && lo<=hi && u.is_finite() && u>=0.) {return None;}
    let q=u/n;
    let clamp=q.clamp(lo,hi);
    for candidate in [q,clamp,clamp.next_down(),clamp.next_up()] {
        if !candidate.is_finite() || candidate<lo || candidate>hi {continue;}
        let nodes=vec![(candidate,n)];
        let count_defect=(sum(nodes.iter().map(|x|x.1))-n).abs();
        let energy_defect=(sum(nodes.iter().map(|x|x.0*x.1))-u).abs();
        if count_defect<=64.0*f64::EPSILON*n && energy_defect<=128.0*f64::EPSILON*energy_scale {return Some(nodes);}
    }
    None
}
impl CovariantTransport {
    pub fn rei_ordered_cohort_evaluate(&self, prepared:Arc<Vec<PreparedAbsorption>>,abs:[f64;3],nh:f64,dt:f64)
        -> Result<Vec<AbsorptionResult>,ForwardError> {
        self.prepare_pool.map_ordered(prepared.len(),move |i|prepared[i].evaluate(abs,nh,dt))
    }
}
pub struct ReiExposure {pub q:f64,pub nodes:usize,pub low:f64,pub high:f64,pub d_min:f64,pub d_max:f64,pub q_lo:f64,pub q_hi:f64,pub s_lo:f64,pub s_hi:f64}
impl PreparedAbsorption {
    pub fn rei_exposure(&self, abs:[f64;3],dt_s:f64) -> Result<ReiExposure,ForwardError> {
        if !abs.iter().all(|&v|nonnegative(v)) || !nonnegative(dt_s) {return Err(bad("REI_EXPOSURE_DOMAIN"));}
        let mut e=ReiExposure {q:0.,nodes:0,low:f64::INFINITY,high:0.,d_min:f64::INFINITY,d_max:1.,q_lo:0.,q_hi:0.,s_lo:0.,s_hi:0.};
        let mut weights=vec![];let model=HHeModel::controlled_fixture();
        for node in &self.nodes {
            if node.number<=0. {continue;}
            let opacity=sum((0..3).map(|j|abs[j]*node.sigma[j]));
            let lambda=model.c_cm_s*opacity;
            let denominator=1.0 + dt_s * model.c_cm_s * opacity;
            if !nonnegative(lambda) || !denominator.is_finite() || denominator<1. {return Err(bad("REI_EXPOSURE_NONFINITE"));}
            weights.push(node.number);e.low=e.low.min(lambda);e.high=e.high.max(lambda);e.nodes+=1;
            e.d_min=e.d_min.min(denominator);e.d_max=e.d_max.max(denominator);
            e.q_lo=(e.q_lo+node.number).next_down().max(0.);e.q_hi=(e.q_hi+node.number).next_up();
            let surviving=node.number/denominator;
            e.s_lo=(e.s_lo+surviving.next_down().max(0.)).next_down().max(0.);
            e.s_hi=(e.s_hi+surviving.next_up()).next_up();
        }
        e.q=sum(weights.into_iter());
        if e.nodes==0 {e.low=0.;e.d_min=1.;}
        if ![e.q,e.q_lo,e.q_hi,e.s_lo,e.s_hi].iter().all(|v|v.is_finite()) {return Err(bad("REI_EXPOSURE_SUM_NONFINITE"));}
        Ok(e)
    }
}
// Public task replay validates the original core quadrature and its unchanged gates.
pub fn rei_cell_replay(lo:f64,hi:f64,n:f64,u:f64,r:f64)->Result<Vec<(f64,f64)>,ForwardError> {
    if !(lo.is_finite() && hi.is_finite() && lo>=0. && hi>lo && n.is_finite() && n>0.
        && u.is_finite() && u>=lo*n && u<=hi*n && r.is_finite() && r>0.) {return Err(bad("REI_REPLAY_DOMAIN"));}
    cell_quadrature(lo,hi,n,u,r,&mut QuadratureDiagnostics::default())
}
pub fn rei_repair_candidate_test(lo:f64,hi:f64,n:f64,u:f64)->bool {rei_barycenter(lo,hi,n,u,u.abs().max(n*(hi-lo))).is_some()}
pub fn rei_synthetic_parallel_control(width:usize)->Result<Vec<u64>,ForwardError> {
    let mut states=Vec::new();
    for i in 0..9 {
        states.push(PreparedAbsorption {template:PhotonState {number:vec![1.],energy_ref:vec![20.],support_lo:vec![15.],support_hi:vec![25.]},nodes:vec![AbsorptionNode {cell:0,q:20.,number:1.+i as f64/10.,sigma:[1e-18,0.,0.],excess_ev:[6.4,0.,0.]}],diagnostics:QuadratureDiagnostics::default()});
    }
    let prepared=Arc::new(states);let pool=OrderedWorkerPool::new(width)?;
    let results=pool.map_ordered(prepared.len(),move |i|prepared[i].evaluate([1e-4,0.,0.],1e-4,1e10))?;
    let mut sum=0f64;let mut out=vec![];
    for r in results {sum+=r.photo.gamma_s[0];out.extend([r.state.number[0].to_bits(),r.state.energy_ref[0].to_bits(),sum.to_bits()]);}
    Ok(out)
}
