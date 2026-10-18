from pathlib import Path
p=Path('rust/rei_microphysics/src/axbi_driver.rs');s=p.read_text()
needle='#[derive(Clone, Debug)]\npub struct Driver {'
insert='''/// Opt-in measurements only; production RHS counters are never debited here.
#[derive(Clone, Debug)]
pub struct ChemicalStageRecord {
    pub comparison: usize,
    pub branch: &'static str,
    pub adaptive_status: &'static str,
    pub a: f64,
    pub dt_s: f64,
    pub old_state: [f64; 4],
    pub state: [f64; 4],
    pub residual: [f64; 4],
    pub jacobian: [[f64; 4]; 4],
    pub added_rhs: usize,
    pub f_he: f64,
    pub k_b_ev_per_k: f64,
}
#[derive(Clone, Debug)]
pub struct ChemicalStageObserver {
    pub records: Vec<ChemicalStageRecord>,
    pub rhs_evaluations: usize,
    pub max_rhs: usize,
    pub max_records: usize,
    pub current_comparison: usize,
    pub current_branch: &'static str,
    pub failure: Option<String>,
}
impl ChemicalStageObserver {
    pub fn new(max_rhs: usize) -> Self {
        Self { records: Vec::new(), rhs_evaluations: 0, max_rhs,
            max_records: 180, current_comparison: 0, current_branch: "DIRECT",
            failure: None }
    }
}
'''
assert needle in s;s=s.replace(needle,insert+needle,1)
needle='''    pub fn chemical_stage(
        &self,
        s: &mut DriverState,
        dt: f64,
        counter: &mut usize,
    ) -> Result<(), ForwardError> {
'''
replacement=needle+'''        self.chemical_stage_observed(s, dt, counter, None)
    }
    fn chemical_stage_observed(
        &self, s: &mut DriverState, dt: f64, counter: &mut usize,
        mut observer: Option<&mut ChemicalStageObserver>,
    ) -> Result<(), ForwardError> {
'''
assert needle in s;s=s.replace(needle,replacement,1)
needle='''                *s = next;
                return Ok(());'''
replacement='''                if let Some(obs) = observer.as_deref_mut() {
                    if obs.records.len() >= obs.max_records {
                        obs.failure = Some("SOURCE011_STAGE_RECORD_CAP".into());
                        return Err(err("SOURCE011_STAGE_RECORD_CAP"));
                    }
                    let before = obs.rhs_evaluations;
                    let accepted_context = context.clone();
                    let result = jacobian_columns(
                        &self.transport.shared_pool(), false, x, residual,
                        &mut obs.rhs_evaluations, obs.max_rhs,
                        move |unknown| accepted_context.evaluate(unknown, dt).map(|v| v.0),
                    );
                    let jacobian = match result {
                        Ok(j) => j,
                        Err(e) => { obs.failure = Some(format!("{:?}", e)); return Err(e); }
                    };
                    obs.records.push(ChemicalStageRecord {
                        comparison: obs.current_comparison, branch: obs.current_branch,
                        adaptive_status: "PENDING_ADAPTIVE_DISPOSITION", a: old.a, dt_s: dt,
                        old_state: [old.gas.fractions[0],old.gas.fractions[1],old.gas.fractions[2],old_w],
                        state: x, residual, jacobian,
                        added_rhs: obs.rhs_evaluations-before,
                        f_he: self.n_he0_cm3/self.n_h0_cm3,
                        k_b_ev_per_k: c.kb_erg_k/c.ev_erg,
                    });
                }
                *s = next;
                return Ok(());'''
assert needle in s;s=s.replace(needle,replacement,1)
needle='''        let mut s = old.clone();
        let mid = (old.a * to).sqrt();'''
replace='''        self.tentative_observed(old, to, counter, None)
    }
    fn tentative_observed(
        &self, old: &DriverState, to: f64, counter: &mut usize,
        observer: Option<&mut ChemicalStageObserver>,
    ) -> Result<DriverState, ForwardError> {
        let mut s = old.clone();
        let mid = (old.a * to).sqrt();'''
assert needle in s;s=s.replace(needle,replace,1);s=s.replace('self.chemical_stage(&mut s, dt, counter)?;','self.chemical_stage_observed(&mut s, dt, counter, observer)?;',1)
needle='''    pub fn adaptive_step(&self, s: &mut DriverState) -> Result<bool, ForwardError> {
'''
replace=needle+'''        self.adaptive_step_inner(s, None)
    }
    pub fn adaptive_step_observed(
        &self, s: &mut DriverState, observer: &mut ChemicalStageObserver,
    ) -> Result<bool, ForwardError> {
        let first = observer.records.len();
        observer.current_comparison = s.comparisons + 1;
        let result = self.adaptive_step_inner(s, Some(observer));
        let status = match &result { Ok(true)=>"ADAPTIVE_ACCEPTED", Ok(false)=>"ADAPTIVE_REJECTED_DISCARDED", Err(_)=>"ADAPTIVE_FAILED_DISCARDED" };
        for record in &mut observer.records[first..] { record.adaptive_status = status; }
        result
    }
    fn adaptive_step_inner(
        &self, s: &mut DriverState, mut observer: Option<&mut ChemicalStageObserver>,
    ) -> Result<bool, ForwardError> {
'''
assert needle in s;s=s.replace(needle,replace,1)
s=s.replace('''            let mut launch = |old: &DriverState, endpoint: f64| {''','''            let mut branch_index = 0usize;
            let mut launch = |old: &DriverState, endpoint: f64| {''',1)
s=s.replace('''                self.tentative(old, endpoint, &mut counter)''','''                if let Some(obs) = observer.as_deref_mut() {
                    obs.current_branch = ["FULL", "FIRST_HALF", "SECOND_HALF"][branch_index];
                }
                branch_index += 1;
                self.tentative_observed(old, endpoint, &mut counter, observer.as_deref_mut())''',1)
needle='''        let id = self.bass_identity().ok_or(err("BASS_CHECKPOINT_MODE"))?;
        let text = fs::read_to_string(path).map_err(|_| err("BASS_CHECKPOINT_IO"))?;
'''
replace='''        let text = fs::read_to_string(path).map_err(|_| err("BASS_CHECKPOINT_IO"))?;
        self.read_bass_checkpoint_envelope(&text, epoch, output)
    }
    fn read_bass_checkpoint_envelope(
        &self, text: &str, epoch: &str, output: &Path,
    ) -> Result<DriverState, ForwardError> {
        let id = self.bass_identity().ok_or(err("BASS_CHECKPOINT_MODE"))?;
'''
assert needle in s;s=s.replace(needle,replace,1)
needle='''    pub fn output_row(
'''
bridge='''    /// Probe-only, hash-pinned SOURCE010 -> observer producer binding bridge.
    /// Ordinary read_bass_checkpoint and fresh-only run policies stay strict.
    pub fn read_source011_probe_checkpoint(
        &self, path: &Path, local_binding: &Path,
    ) -> Result<DriverState, ForwardError> {
        let bytes = fs::read(path).map_err(ioerr)?;
        let hash = sha256_bytes(&bytes)?;
        if hash != "02fbbaa43e77f15ad198aae5b690dfbac7d09d10d6f079a2f3c845bb22f0674a"
            && hash != "a16aaf6059091e450db6460e97d3971cd47a178383e95c5b992a805426ebd243" {
            return Err(err("SOURCE011_PINNED_CHECKPOINT_HASH"));
        }
        let binding = fs::read(local_binding).map_err(ioerr)?;
        if sha256_bytes(&binding)? != "54d8480daafdd0c18e2f0992211536492b58ef28a2488f7e78a6ee00eddb6535" {
            return Err(err("SOURCE011_PINNED_BINDING_HASH"));
        }
        let text = std::str::from_utf8(&bytes).map_err(|_|err("SOURCE011_CHECKPOINT_UTF8"))?;
        let (head, body) = text.split_once("\\nAXBI_CHECKPOINT_V4\\n").ok_or(err("SOURCE011_ENVELOPE"))?;
        let mut lines = head.lines().map(str::to_owned).collect::<Vec<_>>();
        if lines.len()!=11 || lines[4]!="30d164c0d156c71213618dc256c74573241561a72e9853b9d85f8a689183fa50"
            || lines[5]!="15537df0d258496d5ea74258f6efb7233e9afd1a1cabeb58864c6e48fa69aa2e"
            || lines[6]!="source010-half-target-001-SIGNED_MINUS|/root/REI_BASS_SOURCE010_20261016_001/results/SIGNED_MINUS/RUN_BINDING.txt" {
            return Err(err("SOURCE011_ORIGINAL_BINDING"));
        }
        lines[4]=sha256_bytes(compiled_identity().as_bytes())?;
        lines[6]=format!("source010-half-target-001-SIGNED_MINUS|{}",local_binding.display());
        let mapped=format!("{}\\nAXBI_CHECKPOINT_V4\\n{}",lines.join("\\n"),body);
        self.read_bass_checkpoint_envelope(&mapped,"source010-half-target-001-SIGNED_MINUS",local_binding)
    }
    pub fn source011_state_text(&self,s:&DriverState)->Result<String,ForwardError> {
        self.checkpoint_text(s)
    }
'''
assert needle in s;s=s.replace(needle,bridge+needle,1)
s=s.replace('''        include_str!("../../../research/bass_source009_20261016/CONTRACT.json"),''','''        include_str!("../../../research/bass_source009_20261016/CONTRACT.json"),
        include_str!("../examples/bass_nonlinear_stage_probe.rs"),
        include_str!("../../../research/bass_source011_20261016/CONTRACT.json"),''',1)
p.write_text(s)
