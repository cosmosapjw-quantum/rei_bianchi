//! Native source-reuse frozen H/He absorption A/B, not the evolving AXBI solver.
//! A: Driver::geometry_map at each half-step with physical-energy-node projection.
//! B: CovariantPhoton::from_local and energy_at with no intermediate projection.
//! Both: identical original reference exponential frozen-gas absorptions at the
//! same geometric midpoint and proper dt, preserving HI/HeI/HeII event and heat.
//! Full native source epochs differ; selected transport source bodies have been
//! byte-audited in RUST_SOURCE_SURFACE_IDENTITY.json.

use rei_microphysics::axbi_driver::{Driver, DriverConfig};
use rei_microphysics::axbi_q_reference::{CovariantPhoton, absorb_frozen_gas};
use rei_microphysics::{CharacteristicRay, HHeModel};
use std::fmt::Write as _;
use std::time::Instant;

const PHOTONS_PER_H: f64 = 1e-10;
const F_HE: f64 = 0.2454 / (4.0 * (1.0 - 0.2454));

#[derive(Clone, Copy, Default)]
struct EventLedger {
    absorbed: [f64; 3],
    binding: f64,
    heating: f64,
    event_balance_residual: f64,
}

impl EventLedger {
    fn add(&mut self, before: f64, p: &rei_microphysics::axbi_q_reference::FrozenAbsorption) {
        let lost = before - p.final_packet.photons_per_h;
        let event_sum: f64 = p.absorbed_per_h.iter().sum();
        self.event_balance_residual += lost - event_sum;
        for j in 0..3 { self.absorbed[j] += p.absorbed_per_h[j]; }
        self.binding += p.binding_ev_per_h;
        self.heating += p.heat_ev_per_h;
    }
    fn total_absorbed(&self) -> f64 { self.absorbed.iter().sum() }
    fn energy_absorbed(&self) -> f64 { self.binding + self.heating }
}

#[derive(Clone, Copy)]
struct Summary {
    q: f64, eta: f64, e_index: usize, nsteps: usize,
    arm: &'static str,
    e0: f64, exact_e_end: f64, final_count: f64, photon_final_u: f64,
    abs: [f64; 3], binding: f64, heating: f64, photon_work: f64,
    boundary_n: f64, boundary_u: f64,
    number_resid: f64, energy_resid: f64,
    event_resid: f64, runtime_ms: f64,
}
impl Summary {
    fn line(&self) -> String {
        let scale = PHOTONS_PER_H;
        format!("{:.6e},{:.6e},{},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.9}",
            self.q, self.eta, self.e_index, self.nsteps, self.arm,
            self.e0, self.exact_e_end, self.final_count/scale,
            self.photon_final_u/scale, self.abs[0]/scale,
            self.abs[1]/scale, self.abs[2]/scale,
            self.binding/scale, self.heating/scale,
            self.photon_work/scale, self.boundary_n/scale,
            self.boundary_u/scale, self.number_resid/scale,
            self.energy_resid/(scale*self.e0), self.event_resid/scale,
            (self.photon_final_u/self.final_count-self.exact_e_end)/self.exact_e_end,
            self.runtime_ms)
    }
}

fn do_case(q: f64, eta: f64, e_index: usize, steps: usize) -> Result<[Summary; 2], String> {
    let start = Instant::now();
    let mut config = DriverConfig::baseline();
    config.q_ref = q;
    config.end_zbar = 19.8;
    config.background_panels = 4096;
    config.energy_subdivisions = 16;
    config.n_mu = 8;
    let (drv, initial) = Driver::new(config).map_err(|e|format!("{e:?}"))?;
    let aref = initial.a;
    let afinal = 1.0/20.8;
    let ne = drv.energies.len();
    if e_index >= ne { return Err("Bad energy index".into()); }
    let E0 = drv.energies[e_index];
    let ray = drv.source.angular_cells.len()/2;
    let mu = drv.source.angular_cells[ray].mu;
    let direction = [(1.0-mu*mu).sqrt(),0.0,mu];
    let gi=drv.background.point_at_scale(aref).unwrap().geometry().unwrap();
    let gf=drv.background.point_at_scale(afinal).unwrap().geometry().unwrap();
    let mut exact = CovariantPhoton::from_local(&gi,E0,direction,PHOTONS_PER_H).unwrap();
    let e_exact_final=exact.energy_at(&gf).unwrap();
    let ray_init = CharacteristicRay::new(1.0,direction,0.0).unwrap();
    let mut state=initial.clone();
    state.photons[ray*ne+e_index]=PHOTONS_PER_H;
    state.ledgers.source_n=PHOTONS_PER_H;
    state.ledgers.source_u=PHOTONS_PER_H*E0;
    let mut bookA=EventLedger::default();
    let mut bookB=EventLedger::default();
    let mut exact_work=0.0_f64;
    let lna=(afinal/aref).ln();
    for j in 1..=steps {
        let aprev=if j==1 {aref} else {aref*(lna*((j-1) as f64)/(steps as f64)).exp()};
        let anext=if j==steps {afinal} else {aref*(lna*(j as f64)/(steps as f64)).exp()};
        let amid=(aprev*anext).sqrt();
        let gprev=drv.background.point_at_scale(aprev).unwrap();
        let gmid=drv.background.point_at_scale(amid).unwrap();
        let gnext=drv.background.point_at_scale(anext).unwrap();
        let dt=gnext.time_s-gprev.time_s;
        if dt<=0.0{return Err("Invalid proper dt".into());}
        // Frozen physical density scaling with original cosmological expansion.
        // Fractions: HI=eta; HeI=eta/2, HeII=eta/2, HeIII=1-eta.
        // Photon trace amount <=1e-10/H ensures the frozen-gas approximation
        // does not exceed the available ion reservoir for eta>=1e-6.
        let nh=drv.n_h0_cm3/amid.powi(3);
        let absorber=[eta*nh,eta*nh*F_HE/2.0,eta*nh*F_HE/2.0];
        let gm=gmid.geometry().unwrap();
        let gpr=gprev.geometry().unwrap();
        let gn=gnext.geometry().unwrap();

        // B: exact collisionless geodesic energy and one frozen-gas collision at midpoint.
        let e_start=exact.energy_at(&gpr).unwrap();
        let e_mid=exact.energy_at(&gm).unwrap();
        let e_end=exact.energy_at(&gn).unwrap();
        let count_before=exact.photons_per_h;
        exact_work+=count_before*(e_start-e_mid);
        let rB=absorb_frozen_gas(&exact,&gm,absorber,dt).map_err(|e|format!("{e:?}"))?;
        bookB.add(count_before,&rB);
        exact=rB.final_packet;
        exact_work+=exact.photons_per_h*(e_mid-e_end);

        // A: original Driver geometry_map projects onto fixed physical energy
        // nodes twice per proper source step, just as a midpoint split does.
        drv.geometry_map(&mut state,amid).map_err(|e|format!("{e:?}"))?;
        let dir_mid=ray_init.pullback(&gi,&gm).unwrap().direction;
        for bin in 0..ne {
            let idx=ray*ne+bin;
            let before=state.photons[idx];
            if before<=0.0{continue;}
            let p=CovariantPhoton::from_local(&gm,drv.energies[bin],dir_mid,before).unwrap();
            let rA=absorb_frozen_gas(&p,&gm,absorber,dt).map_err(|e|format!("{e:?}"))?;
            bookA.add(before,&rA);
            state.photons[idx]=rA.final_packet.photons_per_h;
        }
        drv.geometry_map(&mut state,anext).map_err(|e|format!("{e:?}"))?;
    }
    let countA=state.photons.iter().sum::<f64>();
    let uA=state.photons.iter().enumerate()
        .map(|(k,n)|n*drv.energies[k%ne]).sum::<f64>();
    let num_residA=PHOTONS_PER_H-(countA+bookA.total_absorbed()+state.ledgers.boundary_n);
    let eng_residA=PHOTONS_PER_H*E0-(uA+bookA.energy_absorbed()
       +state.ledgers.photon_work+state.ledgers.boundary_u);
    let nB=exact.photons_per_h;
    let uB=nB*exact.energy_at(&gf).unwrap();
    let num_residB=PHOTONS_PER_H-(nB+bookB.total_absorbed());
    let eng_residB=PHOTONS_PER_H*E0-(uB+bookB.energy_absorbed()+exact_work);
    let tolerance=2e-8;
    for (nm,er,book) in [(num_residA,eng_residA,bookA),
                         (num_residB,eng_residB,bookB)] {
        if nm.abs()/PHOTONS_PER_H>tolerance ||
            er.abs()/(PHOTONS_PER_H*E0)>tolerance ||
            book.event_balance_residual.abs()/PHOTONS_PER_H>tolerance
        {return Err(format!("Photon threshold/energy/number ledger failed: {nm} {er}"));}
        if book.heating < -1e-18 || book.binding < -1e-18 {return Err("Unphysical heat".into());}
    }
    let elapsed=start.elapsed().as_secs_f64()*1000.0;
    Ok([
        Summary{q,eta,e_index,nsteps:steps,arm:"PROJECTED",e0:E0,exact_e_end:e_exact_final,
            final_count:countA,photon_final_u:uA,abs:bookA.absorbed,binding:bookA.binding,
            heating:bookA.heating,photon_work:state.ledgers.photon_work,
            boundary_n:state.ledgers.boundary_n,boundary_u:state.ledgers.boundary_u,
            number_resid:num_residA,energy_resid:eng_residA,event_resid:bookA.event_balance_residual,
            runtime_ms:elapsed},
        Summary{q,eta,e_index,nsteps:steps,arm:"COVARIANT",e0:E0,exact_e_end:e_exact_final,
            final_count:nB,photon_final_u:uB,abs:bookB.absorbed,binding:bookB.binding,
            heating:bookB.heating,photon_work:exact_work,boundary_n:0.0,boundary_u:0.0,
            number_resid:num_residB,energy_resid:eng_residB,event_resid:bookB.event_balance_residual,
            runtime_ms:elapsed},
    ])
}

fn main(){
    let args: Vec<String> = std::env::args().collect();
    let jobs:usize=if args.len()==3 && args[1]=="--jobs" {
        args[2].parse().expect("jobs numeric")
    } else if args.len()==1 {1} else {panic!("usage: source [--jobs 1|2]")};
    if jobs!=1 && jobs!=2{panic!("bounded experimental jobs are 1 or 2");}
    let mut cases=Vec::<(f64,f64,usize,usize)>::new();
    for q in [-0.005_f64,0.0,0.005] {
        for eta in [0.0_f64,1.0e-6,1.0e-5] {
            for idx in [5_usize,20,32,33] {
                for nsteps in [1_usize,32,256]{
                    cases.push((q,eta,idx,nsteps));
                }
            }
        }
    }
    let mut results=Vec::new();
    if jobs==1 {
        for (q,e,idx,n) in cases {results.extend_from_slice(&do_case(q,e,idx,n).unwrap());}
    } else {
        for batch in cases.chunks(2) {
            let mut rows=Vec::<[Summary;2]>::new();
            std::thread::scope(|scope| {
                let handles=batch.iter().map(|&(q,e,idx,n)|
                    scope.spawn(move || do_case(q,e,idx,n))).collect::<Vec<_>>();
                for h in handles {rows.push(h.join().unwrap().unwrap());}
            });
            for v in rows {results.extend_from_slice(&v);}
        }
    }
    let mut out=String::new();
    writeln!(&mut out,"q_ref,eta_neutral,e_index,steps,arm,initial_energy_eV,exact_final_energy_eV,surviving_photons_per_initial,final_photon_energy_eV_per_initial,HI_absorbed_per_initial,HeI_absorbed_per_initial,HeII_absorbed_per_initial,binding_eV_per_initial,heating_eV_per_initial,redshift_work_eV_per_initial,grid_boundary_photons_per_initial,grid_boundary_energy_eV_per_initial,number_residual_per_initial,energy_residual_per_initial_energy,event_residual_per_initial,survivor_mean_energy_relative_error,case_runtime_ms").unwrap();
    for row in &results {writeln!(&mut out,"{}",row.line()).unwrap();}
    print!("{out}");
}
