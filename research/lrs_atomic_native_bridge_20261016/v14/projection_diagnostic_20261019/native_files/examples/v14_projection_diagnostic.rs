//! Additive frozen-gas reconstruction diagnostic; no order assertions or solver edits.
use rei_microphysics::{
    axbi_covariant_transport::{CovariantTransport, PhotonAttenuation, PhotonState, QuadratureDiagnostics},
    axbi_driver::{Driver, DriverConfig}, Absorber, AtomicProvider, GeometrySnapshot, HHeModel,
};
use std::{fs::File, io::{BufWriter, Write}, time::Instant};
type Res<T> = Result<T, String>;
#[derive(Clone)]
struct Outcome {
    state: PhotonState, n: f64, u: f64, events: [f64; 3], binding: f64, heat: f64,
    residual_n: f64, residual_u: f64, min_n: f64, min_slack: f64,
    nodes_total: usize, nodes_min: usize, nodes_max: usize, q: QuadratureDiagnostics,
}
fn run(core: &CovariantTransport, initial: &PhotonState, geo: &GeometrySnapshot,
       absorbers: [f64; 3], nh: f64, dt: f64, m: usize) -> Res<Outcome> {
    let (n0,u0)=core.inventory(initial,geo).map_err(|e|format!("initial inventory {e:?}"))?;
    let mut o=Outcome { state:initial.clone(), n:n0, u:u0, events:[0.;3], binding:0.,heat:0.,
        residual_n:0.,residual_u:0.,min_n:f64::INFINITY,min_slack:f64::INFINITY,
        nodes_total:0,nodes_min:usize::MAX,nodes_max:0,q:QuadratureDiagnostics::default() };
    for step in 0..m {
        let p=core.prepare(&o.state,geo).map_err(|e|format!("prepare step={step}/{m} {e:?}"))?;
        let nc=p.node_count();o.nodes_total+=nc;o.nodes_min=o.nodes_min.min(nc);o.nodes_max=o.nodes_max.max(nc);
        o.q.max_count_relative_defect=o.q.max_count_relative_defect.max(p.diagnostics.max_count_relative_defect);
        o.q.max_energy_relative_defect=o.q.max_energy_relative_defect.max(p.diagnostics.max_energy_relative_defect);
        o.q.max_asymptotic_mean_defect_ev=o.q.max_asymptotic_mean_defect_ev.max(p.diagnostics.max_asymptotic_mean_defect_ev);
        o.q.omitted_tail_number_bound_per_h+=p.diagnostics.omitted_tail_number_bound_per_h;
        o.q.omitted_tail_energy_bound_ev_per_h+=p.diagnostics.omitted_tail_energy_bound_ev_per_h;
        o.q.omitted_tail_endpoint_moment_bound_ev_per_h+=p.diagnostics.omitted_tail_endpoint_moment_bound_ev_per_h;
        let r=p.evaluate_with_rule(absorbers,nh,dt,PhotonAttenuation::Exponential)
            .map_err(|e|format!("evaluate step={step}/{m} {e:?}"))?;
        for j in 0..3 {o.events[j]+=r.absorbed_per_h[j];}
        o.binding+=r.binding_ev_per_h;o.heat+=r.heat_ev_per_h;o.state=r.state;
        // Native public validation checks support invariants without changing them.
        core.validate_state(&o.state).map_err(|e|format!("validate step={step}/{m} {e:?}"))?;
        for k in 0..o.state.number.len() {
            let n=o.state.number[k];let u=o.state.energy_ref[k];let lo=o.state.support_lo[k];let hi=o.state.support_hi[k];
            o.min_n=o.min_n.min(n);
            if n>0. {
                let denom=u.abs().max((hi*n).abs()).max(f64::MIN_POSITIVE);
                let slack=(u-lo*n).min(hi*n-u)/denom;
                o.min_slack=o.min_slack.min(slack);
            }
        }
    }
    (o.n,o.u)=core.inventory(&o.state,geo).map_err(|e|format!("final inventory {e:?}"))?;
    o.residual_n=n0-o.n-o.events.iter().sum::<f64>();
    o.residual_u=u0-o.u-o.binding-o.heat;
    if !metrics(&o).iter().all(|x|x.is_finite()) { return Err("nonfinite outcome".into()); }
    Ok(o)
}
fn metrics(o:&Outcome)->Vec<f64>{
    let mut v=vec![o.n,o.u];v.extend(o.events);v.extend([o.binding,o.heat,o.residual_n,o.residual_u,
        o.min_n,o.min_slack,o.nodes_total as f64,o.nodes_min as f64,o.nodes_max as f64,
        o.q.max_count_relative_defect,o.q.max_energy_relative_defect,
        o.q.omitted_tail_number_bound_per_h,o.q.omitted_tail_energy_bound_ev_per_h,
        o.q.omitted_tail_endpoint_moment_bound_ev_per_h,o.q.max_asymptotic_mean_defect_ev]);v
}
const FIELDS:&str="N,U,photo_HI,photo_HeI,photo_HeII,binding,heat,residual_N,residual_U,min_number,min_support_slack_normalized,nodes_total,nodes_min,nodes_max,quad_max_count_relative_defect,quad_max_energy_relative_defect,quad_tail_N_bound_sum,quad_tail_U_bound_sum,quad_tail_endpoint_moment_bound_sum,quad_max_asymptotic_mean_defect_eV";
#[allow(clippy::too_many_arguments)]
fn row(w:&mut BufWriter<File>,cw:&mut BufWriter<File>,kind:&str,cells:usize,spectrum:&str,
       theta:f64,m:usize,dt:f64,kref:f64,n0:f64,u0:f64,base:&Outcome,o:&Outcome)->Res<()> {
    let dn:Vec<f64>=o.state.number.iter().zip(&base.state.number).map(|(a,b)|a-b).collect();
    let du:Vec<f64>=o.state.energy_ref.iter().zip(&base.state.energy_ref).map(|(a,b)|a-b).collect();
    let l1n=dn.iter().map(|x|x.abs()).sum::<f64>();let l1u=du.iter().map(|x|x.abs()).sum::<f64>();
    let mut v=vec![theta,m as f64,dt,kref,n0,u0];v.extend(metrics(base));v.extend(metrics(o));
    v.extend([l1n,l1u,l1n/n0,l1u/u0,o.n-base.n,o.u-base.u]);
    for j in 0..3 {v.push(o.events[j]-base.events[j]);}
    v.extend([o.binding-base.binding,o.heat-base.heat]);
    if !v.iter().all(|x|x.is_finite()) {return Err("nonfinite row".into());}
    write!(w,"{kind},{cells},{spectrum}").map_err(|e|e.to_string())?;
    for x in v {write!(w,",{x:.17e}").map_err(|e|e.to_string())?;}writeln!(w).map_err(|e|e.to_string())?;
    for k in 0..dn.len() {
        writeln!(cw,"{kind},{cells},{spectrum},{theta:.17e},{m},{k},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            base.state.number[k],o.state.number[k],dn[k],base.state.energy_ref[k],o.state.energy_ref[k],du[k]).map_err(|e|e.to_string())?;
    }
    w.flush().map_err(|e|e.to_string())?;cw.flush().map_err(|e|e.to_string())?;
    Ok(())
}
fn main()->Res<()> {
    let args:Vec<String>=std::env::args().collect();if args.len()!=2{return Err("usage: v14_projection_diagnostic output.csv".into());}
    let clock=Instant::now();
    let mut w=BufWriter::new(File::create(&args[1]).map_err(|e|e.to_string())?);
    let mut cw=BufWriter::new(File::create(format!("{}.cells.csv",args[1])).map_err(|e|e.to_string())?);
    write!(w,"kind,cells,spectrum,theta,m,dt_s,k_ref_s_inv,initial_N,initial_U").map_err(|e|e.to_string())?;
    for prefix in ["base","result"] {for field in FIELDS.split(','){write!(w,",{prefix}_{field}").map_err(|e|e.to_string())?;}}
    writeln!(w,",cell_N_L1,cell_U_ref_L1,cell_N_L1_normalized,cell_U_ref_L1_normalized,delta_N_signed,delta_U_signed,delta_photo_HI,delta_photo_HeI,delta_photo_HeII,delta_binding,delta_heat").map_err(|e|e.to_string())?;
    writeln!(cw,"kind,cells,spectrum,theta,m,cell,base_N,result_N,delta_N,base_U_ref,result_U_ref,delta_U_ref").map_err(|e|e.to_string())?;
    for cells in [8,16,32,64] {
        let mut cfg=DriverConfig::baseline();cfg.transport_cells=cells;cfg.transport_threads=1;cfg.background_panels=128;
        let (d,_)=Driver::new(cfg).map_err(|e|format!("driver cells={cells} {e:?}"))?;
        let a=1.0_f64/21.0;let geo=d.geometry_point(a).and_then(|p|p.geometry()).map_err(|e|format!("geometry {e:?}"))?;
        let nh=d.n_h0_cm3/a.powi(3);let nhe=d.n_he0_cm3/a.powi(3);
        let absorbers=[nh*(1.-0.075),nhe*(1.-0.12-0.03),nhe*0.12];
        let ap=AtomicProvider::reference();let species=[Absorber::HI,Absorber::HeI,Absorber::HeII];
        let mut opacity=0.;for j in 0..3 {opacity+=absorbers[j]*ap.cross_section(species[j],20.).map_err(|e|format!("cross_section {e:?}"))?;}
        let kref=HHeModel::controlled_fixture().c_cm_s*opacity;
        if !kref.is_finite()||kref<=0. {return Err("invalid k_ref".into());}
        let core=&d.transport;let mut broad=core.empty_state();
        core.inject(&mut broad,&geo,20.,1e10).map_err(|e|format!("inject {e:?}"))?;
        let broad_n=core.inventory(&broad,&geo).map_err(|e|format!("inventory {e:?}"))?.0;
        let mut delta=core.empty_state();core.add_delta(&mut delta,0,60.,broad_n).map_err(|e|format!("delta {e:?}"))?;
        for (spectrum,initial) in [("md14_broad",broad),("delta60",delta)] {
            let (n0,u0)=core.inventory(&initial,&geo).map_err(|e|format!("inventory {e:?}"))?;
            for theta in [0.8,0.4,0.2,0.1,0.05,0.025] {
                let dt=theta/kref;
                let full=run(core,&initial,&geo,absorbers,nh,dt,1).map_err(|e|format!("pair full cells={cells} {spectrum} theta={theta} {e}"))?;
                let halves=run(core,&initial,&geo,absorbers,nh,dt/2.,2).map_err(|e|format!("pair halves cells={cells} {spectrum} theta={theta} {e}"))?;
                row(&mut w,&mut cw,"pair",cells,spectrum,theta,2,dt,kref,n0,u0,&full,&halves)?;
            }
            if cells==16 {
                let full=run(core,&initial,&geo,absorbers,nh,1./kref,1)?;
                for m in [1,2,4,8,16,32,64] {
                    let dt=1./(kref*m as f64);let o=run(core,&initial,&geo,absorbers,nh,dt,m)
                        .map_err(|e|format!("history {spectrum} m={m} {e}"))?;
                    row(&mut w,&mut cw,"history",cells,spectrum,1.,m,dt,kref,n0,u0,&full,&o)?;
                }
            }
            eprintln!("COMPLETE cells={cells} spectrum={spectrum} wall_s={:.6}",clock.elapsed().as_secs_f64());
        }
    }
    eprintln!("COMPLETE diagnostic wall_s={:.6}",clock.elapsed().as_secs_f64());Ok(())
}
