//! Bounded opt-in native chemistry adapter to the pinned VigilODE Radau implementation.
use rei_microphysics::{
    Absorber, AtomicProvider, HHeModel,
    axbi_covariant_transport::{NativeAbsorptionRates, PhotonAttenuation, PhotonState},
    axbi_driver::{
        Driver, DriverConfig, DriverState, NativeClockMode, PhysicalBirthRule, SourceClockConfig,
        SourcePlacement,
    },
    axbi_rates::AxbiProvider,
    igm_state::{IgmGasState, w_erg_per_h_to_ev, w_ev_per_h_to_erg},
    igm_thermal::IgmPointRhs,
};
use rodas5p_core::{CoreError, CoreResult, DenseMatrix, WorkCounters};
use rodas5p_integrators::{OdeProblem, RadauConfig, radau_iia3_tableau, radau_step};
use serde::Serialize;
use std::{
    sync::{
        Arc,
        atomic::{AtomicUsize, Ordering},
    },
    time::Instant,
};
pub type R<T> = Result<T, String>;
fn native<T>(r: Result<T, rei_microphysics::ForwardError>) -> R<T> {
    r.map_err(|e| format!("{e:?}"))
}
fn core(e: String) -> CoreError {
    CoreError::InvalidInput(e)
}
pub fn photon(s: &DriverState) -> PhotonState {
    PhotonState {
        number: s.photons.clone(),
        energy_ref: s.photon_energy_ref.clone(),
        support_lo: s.photon_support_lo.clone(),
        support_hi: s.photon_support_hi.clone(),
    }
}
fn set_photon(s: &mut DriverState, p: PhotonState) {
    s.photons = p.number;
    s.photon_energy_ref = p.energy_ref;
    s.photon_support_lo = p.support_lo;
    s.photon_support_hi = p.support_hi;
}
pub fn initial(seed: bool) -> R<(Driver, DriverState, f64)> {
    let mut c = DriverConfig::baseline();
    c.transport_cells = 8;
    c.n_mu = 8;
    c.transport_threads = 1;
    c.background_panels = 128;
    c.max_rhs = 200000;
    c.max_wall_s = 30.;
    let (mut d, mut s) = native(Driver::new(c))?;
    let nh = d.n_h0_cm3 / s.a.powi(3);
    let nhe = d.n_he0_cm3 / s.a.powi(3);
    s.gas = native(IgmGasState::from_temperature(
        [0.075, 0.12, 0.03],
        nh,
        nhe,
        15000.,
    ))?;
    let g = native(native(d.geometry_point(s.a))?.geometry())?;
    if seed {
        let mut p = d.transport.empty_state();
        let l = native(d.transport.inject(&mut p, &g, 20., 1e16))?;
        set_photon(&mut s, p);
        s.ledgers.source_n = l.added_photons_per_h;
        s.ledgers.source_u = l.added_energy_ev_per_h;
    }
    native(d.set_source_clocks(
        &s,
        SourceClockConfig {
            microphysics: NativeClockMode::AllMid,
            opacity_midpoint: true,
            source: SourcePlacement::Disabled,
            attenuation: PhotonAttenuation::Exponential,
            nonlinear_tolerance: 1e-15,
        },
    ))?;
    let ap = AtomicProvider::reference();
    let abs = [nh * 0.925, nhe * 0.85, nhe * 0.12];
    let mut opacity = 0.;
    for j in 0..3 {
        opacity += abs[j]
            * native(ap.cross_section([Absorber::HI, Absorber::HeI, Absorber::HeII][j], 20.))?;
    }
    Ok((d, s, HHeModel::controlled_fixture().c_cm_s * opacity))
}
#[derive(Clone, Debug, Serialize)]
pub struct CellCoordinate {
    pub cell: usize,
    pub number_index: usize,
    pub offset_index: Option<usize>,
    pub nscale: f64,
    pub lo: f64,
    pub hi: f64,
}
#[derive(Clone, Debug)]
pub struct Coordinates {
    pub cells: Vec<CellCoordinate>,
    pub wscale: f64,
    template: PhotonState,
    pub dimension: usize,
}
impl Coordinates {
    pub fn new(p: &PhotonState, gas: &IgmGasState) -> R<Self> {
        let wscale = native(w_erg_per_h_to_ev(gas.w_erg_per_h))?;
        if !(wscale > 0. && wscale.is_finite()) {
            return Err("positive frozen wscale required".into());
        }
        let mut cells = vec![];
        let mut dimension = 4;
        for k in 0..p.number.len() {
            if p.number[k] == 0. {
                continue;
            }
            let offset_index = if p.support_hi[k] > p.support_lo[k] {
                Some(dimension + 1)
            } else {
                None
            };
            cells.push(CellCoordinate {
                cell: k,
                number_index: dimension,
                offset_index,
                nscale: p.number[k],
                lo: p.support_lo[k],
                hi: p.support_hi[k],
            });
            dimension += if offset_index.is_some() { 2 } else { 1 };
        }
        Ok(Self {
            cells,
            wscale,
            template: p.clone(),
            dimension,
        })
    }
    pub fn encode(&self, p: &PhotonState, g: &IgmGasState) -> R<Vec<f64>> {
        let mut y = vec![0.; self.dimension];
        y[..3].copy_from_slice(&g.fractions);
        y[3] = native(w_erg_per_h_to_ev(g.w_erg_per_h))? / self.wscale;
        for c in &self.cells {
            y[c.number_index] = p.number[c.cell] / c.nscale;
            if let Some(i) = c.offset_index {
                y[i] =
                    (p.energy_ref[c.cell] - c.lo * p.number[c.cell]) / ((c.hi - c.lo) * c.nscale);
            }
        }
        Ok(y)
    }
    pub fn decode(&self, y: &[f64]) -> R<(PhotonState, IgmGasState)> {
        if y.len() != self.dimension || !y.iter().all(|v| v.is_finite()) {
            return Err("coordinate shape/nonfinite".into());
        }
        let g = native(IgmGasState::new(
            [y[0], y[1], y[2]],
            native(w_ev_per_h_to_erg(y[3] * self.wscale))?,
        ))?;
        let mut p = self.template.clone();
        for c in &self.cells {
            let n = y[c.number_index] * c.nscale;
            p.number[c.cell] = n;
            p.energy_ref[c.cell] = if let Some(i) = c.offset_index {
                c.lo.mul_add(n, y[i] * ((c.hi - c.lo) * c.nscale))
            } else {
                c.lo * n
            };
        }
        Ok((p, g))
    }
    pub fn derivative(&self, r: &NativeAbsorptionRates, g: &IgmPointRhs) -> Vec<f64> {
        let mut f = vec![0.; self.dimension];
        f[..3].copy_from_slice(&g.fraction_dt);
        f[3] = g.w_dt_erg_per_h_s / HHeModel::controlled_fixture().ev_erg / self.wscale;
        for c in &self.cells {
            f[c.number_index] = r.number_dt[c.cell] / c.nscale;
            if let Some(i) = c.offset_index {
                f[i] = r.energy_offset_dt[c.cell] / ((c.hi - c.lo) * c.nscale);
            }
        }
        f
    }
    /// Linear part of six physical affine checks: photon N,HII,HeII,HeIII,e,total energy.
    pub fn physical_linear(
        &self,
        v: &[f64],
        ratio: f64,
        ray_scales: &[f64],
        nenergy: usize,
    ) -> [f64; 6] {
        let t = HHeModel::controlled_fixture().threshold_ev;
        let mut n = 0.;
        let mut u = 0.;
        for c in &self.cells {
            let dn = v[c.number_index] * c.nscale;
            let du = c.lo * dn
                + c.offset_index
                    .map_or(0., |i| v[i] * ((c.hi - c.lo) * c.nscale));
            n += dn;
            u += du * ray_scales[c.cell / nenergy];
        }
        [
            n,
            v[0],
            ratio * v[1],
            ratio * v[2],
            v[0] + ratio * (v[1] + 2. * v[2]),
            v[3] * self.wscale + t[0] * v[0] + ratio * (t[1] * v[1] + (t[1] + t[2]) * v[2]) + u,
        ]
    }
}
#[derive(Clone, Debug, Default, Serialize)]
pub struct Events {
    pub p: [f64; 3],
    pub c: [f64; 3],
    pub r: [f64; 3],
    pub d: f64,
    pub photo_binding: f64,
    pub photo_heat: f64,
    pub ce: [f64; 3],
    pub rr: [f64; 3],
    pub dr: f64,
    pub ff: f64,
    pub cmb: f64,
    pub escape: f64,
    pub ci_floor: [f64; 3],
    pub ce_cap: f64,
    pub excluded_dr: f64,
}
impl Events {
    pub fn from_rhs(r: &IgmPointRhs, nh: f64) -> Self {
        let e = 1. / nh;
        let u = e / HHeModel::controlled_fixture().ev_erg;
        let p = r.photo_events_cm3_s.map(|v| v * e);
        let photo_binding = (0..3)
            .map(|j| p[j] * HHeModel::controlled_fixture().threshold_ev[j])
            .sum();
        Self {
            p,
            c: r.ci_events_cm3_s.map(|v| v * e),
            r: r.rr_events_cm3_s.map(|v| v * e),
            d: r.dr_events_cm3_s * e,
            photo_binding,
            photo_heat: r.photo_input_erg_cm3_s * u - photo_binding,
            ce: r.ce_thermal_sink_erg_cm3_s.map(|v| v * u),
            rr: r.rr_thermal_sink_erg_cm3_s.map(|v| v * u),
            dr: r.dr_thermal_sink_erg_cm3_s * u,
            ff: r.freefree_thermal_sink_erg_cm3_s * u,
            cmb: r.cmb_to_gas_erg_cm3_s * u,
            escape: r.escape_erg_cm3_s * u,
            ci_floor: r.ci_floor_events_cm3_s.map(|v| v * e),
            ce_cap: r.ce_cap_cooling_erg_cm3_s.iter().sum::<f64>() * u,
            excluded_dr: r.excluded_dr_cooling_erg_cm3_s * u,
        }
    }
    pub fn add_scaled(&mut self, r: &Self, h: f64) {
        for j in 0..3 {
            self.p[j] += h * r.p[j];
            self.c[j] += h * r.c[j];
            self.r[j] += h * r.r[j];
            self.ce[j] += h * r.ce[j];
            self.rr[j] += h * r.rr[j];
            self.ci_floor[j] += h * r.ci_floor[j];
        }
        self.d += h * r.d;
        self.photo_binding += h * r.photo_binding;
        self.photo_heat += h * r.photo_heat;
        self.dr += h * r.dr;
        self.ff += h * r.ff;
        self.cmb += h * r.cmb;
        self.escape += h * r.escape;
        self.ce_cap += h * r.ce_cap;
        self.excluded_dr += h * r.excluded_dr;
    }
    fn forcing(&self) -> [f64; 6] {
        let net: [f64; 3] = std::array::from_fn(|j| self.p[j] + self.c[j] - self.r[j]);
        [
            -self.p.iter().sum::<f64>(),
            net[0],
            net[1] - self.d - net[2],
            net[2],
            net[0] + net[1] - self.d + net[2],
            self.cmb - self.escape,
        ]
    }
    fn commit(&self, s: &mut DriverState) {
        s.ledgers.absorbed_n += self.p.iter().sum::<f64>();
        for j in 0..3 {
            s.ledgers.photo_events[j] += self.p[j];
            s.ledgers.ci_events[j] += self.c[j];
            s.ledgers.rr_events[j] += self.r[j];
            s.ledgers.ci_floor_events[j] += self.ci_floor[j];
        }
        s.ledgers.dr_events += self.d;
        s.ledgers.escaped_u += self.escape;
        s.ledgers.cmb_input += self.cmb;
        s.ledgers.ce_cap_ev += self.ce_cap;
        s.ledgers.excluded_dr_ev += self.excluded_dr;
    }
}
#[derive(Debug)]
pub struct Budget {
    calls: AtomicUsize,
    pub cap: usize,
    start: Instant,
    pub max_wall_s: f64,
}
impl Budget {
    pub fn new(cap: usize, max_wall_s: f64) -> Arc<Self> {
        Arc::new(Self {
            calls: AtomicUsize::new(0),
            cap,
            start: Instant::now(),
            max_wall_s,
        })
    }
    pub fn calls(&self) -> usize {
        self.calls.load(Ordering::Relaxed)
    }
    fn charge(&self) -> R<()> {
        if self.calls() >= self.cap {
            return Err("NATIVE_RHS_CAP".into());
        }
        if self.start.elapsed().as_secs_f64() > self.max_wall_s {
            return Err("NATIVE_WALL_CAP".into());
        }
        self.calls.fetch_add(1, Ordering::Relaxed);
        Ok(())
    }
}
#[derive(Clone)]
struct Context {
    coordinates: Coordinates,
    transport: rei_microphysics::axbi_covariant_transport::CovariantTransport,
    geometry: rei_microphysics::GeometrySnapshot,
    nh: f64,
    nhe: f64,
    a: f64,
    budget: Arc<Budget>,
}
struct Evaluation {
    f: Vec<f64>,
    events: Events,
    direct: NativeAbsorptionRates,
    gas: IgmGasState,
    point_identity: [f64; 6],
    nodes: usize,
}
#[derive(Debug)]
enum EvaluationError {
    PerturbationDomain(String),
    Fatal(String),
}
impl EvaluationError {
    fn message(self) -> String {
        match self {
            Self::PerturbationDomain(s) => format!("PERTURBATION_DOMAIN: {s}"),
            Self::Fatal(s) => s,
        }
    }
}
fn fd_column(
    base: &[f64],
    plus: Result<Vec<f64>, EvaluationError>,
    minus: Result<Vec<f64>, EvaluationError>,
    eps: f64,
) -> R<Vec<f64>> {
    match (plus, minus) {
        (Ok(p), Ok(m)) => Ok(p.iter().zip(m).map(|(p, m)| (p - m) / (2. * eps)).collect()),
        (Ok(p), Err(EvaluationError::PerturbationDomain(_))) => {
            Ok(p.iter().zip(base).map(|(p, b)| (p - b) / eps).collect())
        }
        (Err(EvaluationError::PerturbationDomain(_)), Ok(m)) => {
            Ok(base.iter().zip(m).map(|(b, m)| (b - m) / eps).collect())
        }
        (Err(EvaluationError::Fatal(e)), _) | (_, Err(EvaluationError::Fatal(e))) => Err(e),
        (Err(p), Err(m)) => Err(format!(
            "FD both directions outside domain: {}; {}",
            p.message(),
            m.message()
        )),
    }
}
impl Context {
    // Only independently established physical inadmissibility permits an FD fallback.
    // Native decoding/arithmetic/reconstruction/provider errors are always fatal.
    fn admissibility(&self, y: &[f64]) -> Result<(), EvaluationError> {
        let domain = |s: &str| EvaluationError::PerturbationDomain(s.into());
        if y.len() != self.coordinates.dimension || !y.iter().all(|v| v.is_finite()) {
            return Err(EvaluationError::Fatal(
                "FD nonfinite or wrong-shaped coordinates".into(),
            ));
        }
        if y[0] < 0. || y[0] > 1. || y[1] < 0. || y[2] < 0. || y[1] + y[2] > 1. {
            return Err(domain("native gas fraction envelope"));
        }
        if y[3] <= 0. {
            return Err(domain("nonpositive thermal energy"));
        }
        for cell in &self.coordinates.cells {
            let n = y[cell.number_index];
            if n <= 0. {
                return Err(domain(
                    "nonpositive occupied photon cell with frozen support",
                ));
            }
            if let Some(i) = cell.offset_index {
                if y[i] < 0. || y[i] > n {
                    return Err(domain("photon energy outside fixed support"));
                }
            }
        }
        let (_, gas) = self.coordinates.decode(y).map_err(EvaluationError::Fatal)?;
        let eos = native(gas.eos(self.nh, self.nhe)).map_err(EvaluationError::Fatal)?;
        if !(1.0..=1e6).contains(&eos.temperature_k) {
            return Err(domain("native rate temperature outside 1..=1e6 K"));
        }
        Ok(())
    }
    fn evaluate_typed(&self, y: &[f64]) -> Result<Evaluation, EvaluationError> {
        self.budget.charge().map_err(EvaluationError::Fatal)?;
        self.admissibility(y)?;
        self.evaluate_native(y)
            .map_err(|e| EvaluationError::Fatal(format!("{e}; scaled_state={y:?}")))
    }
    fn evaluate(&self, y: &[f64]) -> R<Evaluation> {
        self.evaluate_typed(y).map_err(EvaluationError::message)
    }
    fn evaluate_native(&self, y: &[f64]) -> R<Evaluation> {
        let (p, gas) = self.coordinates.decode(y)?;
        native(self.transport.validate_state(&p))?;
        let [x, he2, he3] = gas.fractions;
        let prepared = native(self.transport.prepare(&p, &self.geometry))?;
        let direct = native(prepared.native_rates(
            [
                self.nh * (1. - x),
                self.nhe * (1. - he2 - he3),
                self.nhe * he2,
            ],
            self.nh,
        ))?;
        let rhs =
            native(AxbiProvider.point(&gas, self.nh, self.nhe, 0., 2.7255 / self.a, direct.photo))?
                .rhs;
        let f = self.coordinates.derivative(&direct, &rhs);
        let events = Events::from_rhs(&rhs, self.nh);
        let ray_scales = native(self.transport.ray_geometry(&self.geometry))?
            .iter()
            .map(|r| r.scale)
            .collect::<Vec<_>>();
        let linear = self.coordinates.physical_linear(
            &f,
            self.nhe / self.nh,
            &ray_scales,
            self.transport.n_energy(),
        );
        let forcing = events.forcing();
        let point_identity = std::array::from_fn(|j| linear[j] - forcing[j]);
        Ok(Evaluation {
            f,
            events,
            direct,
            gas,
            point_identity,
            nodes: prepared.node_count(),
        })
    }
    fn jacobian(&self, y: &[f64]) -> R<DenseMatrix> {
        let base = self.evaluate(y)?.f;
        let n = y.len();
        let mut j = DenseMatrix::zeros(n, n);
        for col in 0..n {
            let eps = f64::EPSILON.sqrt() * y[col].abs().max(1.);
            let mut p = y.to_vec();
            let mut m = y.to_vec();
            p[col] += eps;
            m[col] -= eps;
            let fp = self.evaluate_typed(&p).map(|e| e.f);
            // Stop immediately on internal/arithmetic/resource failure.
            if let Err(EvaluationError::Fatal(e)) = &fp {
                return Err(e.clone());
            }
            let fm = self.evaluate_typed(&m).map(|e| e.f);
            let column = fd_column(&base, fp, fm, eps)?;
            for row in 0..n {
                j[(row, col)] = column[row];
            }
        }
        Ok(j)
    }
    fn problem(self: Arc<Self>) -> CoreResult<OdeProblem> {
        let rhs = self.clone();
        let jac = self.clone();
        OdeProblem::new(
            "native-coupled-photon-gas",
            self.coordinates.dimension,
            Arc::new(move |_, y, out| {
                let e = rhs.evaluate(y).map_err(core)?;
                out.copy_from_slice(&e.f);
                Ok(())
            }),
            None,
            Some(Arc::new(move |_, y| jac.jacobian(y).map_err(core))),
            None,
            None,
            true,
            None,
            None,
        )
    }
}
#[derive(Clone, Debug, Serialize)]
pub struct StageRecord {
    pub stage: usize,
    pub weight: f64,
    pub dt_s: f64,
    pub scaled_state: Vec<f64>,
    pub increments: Vec<f64>,
    pub scaled_residual: Vec<f64>,
    pub fractions: [f64; 3],
    pub w_ev: f64,
    pub events_per_h_s: Events,
    pub node_photo_per_h_s: [f64; 3],
    pub node_binding_ev_per_h_s: f64,
    pub node_heat_ev_per_h_s: f64,
    pub point_affine_identity_rate: [f64; 6],
    pub nodes: usize,
}
#[derive(Clone, Debug, Serialize)]
pub struct ChemicalReport {
    pub dt_s: f64,
    pub dimension: usize,
    pub cell_coordinates: Vec<CellCoordinate>,
    pub wscale: f64,
    pub stages: Vec<StageRecord>,
    pub integrated: Events,
    pub max_scaled_stage_residual: f64,
    pub max_scaled_endpoint_closure: f64,
    pub library_wrms: f64,
    pub invariant_defect: [f64; 6],
    pub weighted_physical_stage_residual: [f64; 6],
    pub physical_endpoint_closure: [f64; 6],
    pub weighted_native_point_identity: [f64; 6],
    pub affine_identity_mismatch: [f64; 6],
    pub native_rhs_calls: usize,
    pub work: serde_json::Value,
}
/// Failed candidates preserve physical state and ledgers, while charging attempts/calls.
pub fn chemical_step(
    d: &Driver,
    s: &mut DriverState,
    dt: f64,
    atol: f64,
    budget: Arc<Budget>,
) -> R<ChemicalReport> {
    s.attempts += 1;
    let calls0 = budget.calls();
    let result = (|| {
        if d.config.inactive_hi_split {
            return Err("inactive_hi_split must be false".into());
        }
        if !(dt > 0. && dt.is_finite()) {
            return Err("invalid dt".into());
        }
        let geometry = native(native(d.geometry_point(s.a))?.geometry())?;
        let coordinates = Coordinates::new(&photon(s), &s.gas)?;
        let y = coordinates.encode(&photon(s), &s.gas)?;
        let context = Arc::new(Context {
            coordinates: coordinates.clone(),
            transport: d.transport.clone(),
            geometry,
            nh: d.n_h0_cm3 / s.a.powi(3),
            nhe: d.n_he0_cm3 / s.a.powi(3),
            a: s.a,
            budget: budget.clone(),
        });
        let problem = context.clone().problem().map_err(|e| format!("{e:?}"))?;
        let mut cfg = RadauConfig::default();
        cfg.newton.atol = atol;
        cfg.newton.rtol = 0.;
        let mut work = WorkCounters::default();
        let r = radau_step(&problem, 0., &y, dt, &cfg, &mut work)
            .map_err(|e| format!("radau_step {e:?}; library_work={work:?}"))?;
        if !r.newton.converged {
            return Err("library Newton unconverged".into());
        }
        let (p, gas) = coordinates.decode(&r.y_new)?;
        native(d.transport.validate_state(&p))?;
        native(gas.eos(context.nh, context.nhe))?;
        let (a, b, _) = radau_iia3_tableau();
        let ray_scales = native(d.transport.ray_geometry(&geometry))?
            .iter()
            .map(|r| r.scale)
            .collect::<Vec<_>>();
        let mut integrated = Events::default();
        let mut stages = vec![];
        let mut weighted_residual = vec![0.; y.len()];
        let mut max_scaled_stage_residual = 0.0_f64;
        for i in 0..3 {
            let mut yi = y.clone();
            for j in 0..3 {
                for k in 0..y.len() {
                    yi[k] += a[(i, j)] * r.stage_increments[j][k];
                }
            }
            let e = context.evaluate(&yi)?;
            let residual = (0..y.len())
                .map(|k| r.stage_increments[i][k] - dt * e.f[k])
                .collect::<Vec<_>>();
            for k in 0..y.len() {
                max_scaled_stage_residual = max_scaled_stage_residual.max(residual[k].abs() / atol);
                weighted_residual[k] += b[i] * residual[k];
            }
            integrated.add_scaled(&e.events, dt * b[i]);
            stages.push(StageRecord {
                stage: i,
                weight: b[i],
                dt_s: dt,
                scaled_state: yi,
                increments: r.stage_increments[i].clone(),
                scaled_residual: residual.iter().map(|v| v / atol).collect(),
                fractions: e.gas.fractions,
                w_ev: native(w_erg_per_h_to_ev(e.gas.w_erg_per_h))?,
                events_per_h_s: e.events,
                node_photo_per_h_s: e.direct.absorbed_per_h_s,
                node_binding_ev_per_h_s: e.direct.binding_ev_per_h_s,
                node_heat_ev_per_h_s: e.direct.heat_ev_per_h_s,
                point_affine_identity_rate: e.point_identity,
                nodes: e.nodes,
            });
        }
        let delta = (0..y.len()).map(|k| r.y_new[k] - y[k]).collect::<Vec<_>>();
        let closure = (0..y.len())
            .map(|k| {
                let mut v = r.y_new[k];
                v -= y[k];
                for j in 0..3 {
                    v -= b[j] * r.stage_increments[j][k];
                }
                v
            })
            .collect::<Vec<_>>();
        let max_scaled_endpoint_closure = closure.iter().map(|v| v.abs() / atol).fold(0., f64::max);
        let linear = coordinates.physical_linear(
            &delta,
            context.nhe / context.nh,
            &ray_scales,
            d.transport.n_energy(),
        );
        let forcing = integrated.forcing();
        let invariant_defect = std::array::from_fn(|j| linear[j] - forcing[j]);
        let predicted = coordinates.physical_linear(
            &weighted_residual,
            context.nhe / context.nh,
            &ray_scales,
            d.transport.n_energy(),
        );
        let physical_endpoint_closure = coordinates.physical_linear(
            &closure,
            context.nhe / context.nh,
            &ray_scales,
            d.transport.n_energy(),
        );
        let weighted_native_point_identity = std::array::from_fn(|j| {
            stages
                .iter()
                .map(|stage| dt * stage.weight * stage.point_affine_identity_rate[j])
                .sum::<f64>()
        });
        let affine_identity_mismatch = std::array::from_fn(|j| {
            invariant_defect[j]
                - predicted[j]
                - physical_endpoint_closure[j]
                - weighted_native_point_identity[j]
        });
        let mut next = s.clone();
        next.gas = gas;
        set_photon(&mut next, p);
        integrated.commit(&mut next);
        next.accepted += 1;
        next.max_newton_residual = next.max_newton_residual.max(r.newton.residual_wrms);
        native(d.validate(&next, 1e-8))?;
        let report = ChemicalReport {
            dt_s: dt,
            dimension: y.len(),
            cell_coordinates: coordinates.cells,
            wscale: coordinates.wscale,
            stages,
            integrated,
            max_scaled_stage_residual,
            max_scaled_endpoint_closure,
            library_wrms: r.newton.residual_wrms,
            invariant_defect,
            weighted_physical_stage_residual: predicted,
            physical_endpoint_closure,
            weighted_native_point_identity,
            affine_identity_mismatch,
            native_rhs_calls: budget.calls() - calls0,
            work: serde_json::to_value(&work).map_err(|e| e.to_string())?,
        };
        *s = next;
        Ok(report)
    })();
    s.rhs_evaluations = budget.calls();
    result
}
#[derive(Clone, Debug, Serialize)]
pub struct BirthRecord {
    pub a: f64,
    pub weight_dln_a: f64,
    pub proper_time_weight_s: f64,
    pub added_n: f64,
    pub added_u: f64,
}
#[derive(Clone, Debug, Serialize)]
pub struct SegmentRecord {
    pub begin: f64,
    pub midpoint: f64,
    pub end: f64,
    pub chemical: ChemicalReport,
}
#[derive(Clone, Debug, Serialize)]
pub struct BirthReport {
    pub births: Vec<BirthRecord>,
    pub segments: Vec<SegmentRecord>,
}
/// Exact chronological GL2 outer wrapper. Whole macrostep is a transaction.
pub fn birth_step(
    d: &Driver,
    s: &mut DriverState,
    to: f64,
    rule: PhysicalBirthRule,
    atol: f64,
    budget: Arc<Budget>,
) -> R<BirthReport> {
    let attempt = s.attempts + 1;
    let result = (|| {
        let a0 = s.a;
        let dx = ((to - a0) / a0).ln_1p();
        if !(dx > 0. && dx <= 0.005) {
            return Err("birth step domain".into());
        }
        let mut next = s.clone();
        let mut report = BirthReport {
            births: vec![],
            segments: vec![],
        };
        let mut stops = rule
            .nodes()
            .iter()
            .map(|&(c, w)| (a0 * (c * dx).exp(), Some(w)))
            .collect::<Vec<_>>();
        stops.push((to, None));
        for (end, weight) in stops {
            let begin = next.a;
            if !(end > begin) {
                return Err("unresolved chronological birth".into());
            }
            let midpoint = (begin * end).sqrt();
            let dt =
                ((end - begin) / begin).ln_1p() / native(d.geometry_point(midpoint))?.h_flrw_per_s;
            native(d.geometry_map(&mut next, midpoint))?;
            let chemical = chemical_step(d, &mut next, dt, atol, budget.clone())?;
            native(d.geometry_map(&mut next, end))?;
            report.segments.push(SegmentRecord {
                begin,
                midpoint,
                end,
                chemical,
            });
            if let Some(weight) = weight {
                let proper = dx * weight / native(d.geometry_point(end))?.h_flrw_per_s;
                let mut p = photon(&next);
                let l = if rule.enabled() {
                    let g = native(native(d.geometry_point(end))?.geometry())?;
                    native(d.transport.inject(&mut p, &g, 1. / end - 1., proper))?
                } else {
                    Default::default()
                };
                set_photon(&mut next, p);
                next.ledgers.source_n += l.added_photons_per_h;
                next.ledgers.source_u += l.added_energy_ev_per_h;
                report.births.push(BirthRecord {
                    a: end,
                    weight_dln_a: dx * weight,
                    proper_time_weight_s: proper,
                    added_n: l.added_photons_per_h,
                    added_u: l.added_energy_ev_per_h,
                });
            }
        }
        native(d.validate(&next, 1e-8))?;
        next.accepted = s.accepted + 1;
        next.attempts = attempt;
        next.next_dln_a = dx;
        *s = next;
        Ok(report)
    })();
    s.attempts = attempt;
    s.rhs_evaluations = budget.calls();
    result
}
pub fn state_json(d: &Driver, s: &DriverState) -> R<serde_json::Value> {
    let nh = d.n_h0_cm3 / s.a.powi(3);
    let nhe = d.n_he0_cm3 / s.a.powi(3);
    let eos = native(s.gas.eos(nh, nhe))?;
    let pools = native(d.photon_pool_inventory(s))?;
    Ok(serde_json::json!( {
        "a":s.a,"fractions":s.gas.fractions,"w_ev":native(w_erg_per_h_to_ev(s.gas.w_erg_per_h))?,"temperature_k":eos.temperature_k,
        "electron_per_h":eos.electron_density_cm3/nh,"pools":pools,"number":s.photons,"energy_ref":s.photon_energy_ref,
        "support_lo":s.photon_support_lo,"support_hi":s.photon_support_hi,"ledgers": {
            "source_n":s.ledgers.source_n,"source_u":s.ledgers.source_u,"absorbed_n":s.ledgers.absorbed_n,"escaped_u":s.ledgers.escaped_u,
            "boundary_n":s.ledgers.boundary_n,"boundary_u":s.ledgers.boundary_u,"thermal_work":s.ledgers.thermal_work,"photon_work":s.ledgers.photon_work,
            "cmb_input":s.ledgers.cmb_input,"photo":s.ledgers.photo_events,"ci":s.ledgers.ci_events,"rr":s.ledgers.rr_events,
            "dr":s.ledgers.dr_events,"ci_floor":s.ledgers.ci_floor_events,"ce_cap":s.ledgers.ce_cap_ev,"excluded_dr":s.ledgers.excluded_dr_ev
        }
        ,"accepted":s.accepted,"attempts":s.attempts,"rhs_evaluations":s.rhs_evaluations
    }
    ))
}

#[cfg(test)]
mod classification_regression {
    use super::*;
    #[test]
    fn fd_falls_back_only_for_explicit_perturbation_domain() {
        let base = [2.];
        let good = || Ok(vec![3.]);
        let domain = || {
            Err(EvaluationError::PerturbationDomain(
                "fixed-support envelope".into(),
            ))
        };
        assert_eq!(fd_column(&base, good(), domain(), 0.5).unwrap(), vec![2.]);
        for message in [
            "AXBI_NATIVE_RHS_NONFINITE",
            "AXBI_COVARIANT_QUADRATURE_INTERNAL",
            "IGM_RHS_DOMAIN_OR_ARITHMETIC",
            "NATIVE_RHS_CAP",
        ] {
            let fatal = || Err(EvaluationError::Fatal(message.into()));
            assert_eq!(fd_column(&base, fatal(), good(), 0.5).unwrap_err(), message);
            assert_eq!(fd_column(&base, good(), fatal(), 0.5).unwrap_err(), message);
            assert_eq!(
                fd_column(&base, domain(), fatal(), 0.5).unwrap_err(),
                message
            );
        }
        assert!(fd_column(&base, domain(), domain(), 0.5).is_err());
    }
}
