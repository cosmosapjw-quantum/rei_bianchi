//! Complete fixed-run control matrix. No post-hoc edits or new source spectrum.
//! Usage: output.csv Xend max_N cells [nonlinear_tolerance]
use rei_microphysics::{
    axbi_covariant_transport::PhotonAttenuation,
    axbi_driver::{Driver,DriverConfig,NativeClockMode,SourceClockConfig,SourcePlacement,
        PhysicalBirthRule,BirthMicroSegment,BirthStepReport,BirthSample},
    igm_state::IgmGasState,
};
use std::{fs::File,io::{Write,BufWriter},time::Instant};
fn main()->Result<(),String>{
    let args:Vec<String>=std::env::args().collect();
    if args.len()<5||args.len()>6{return Err("usage output.csv Xend max_N cells [nonlinear_tolerance]".into());}
    let xend:f64=args[2].parse().map_err(|_|"Xend")?;
    let max_n:usize=args[3].parse().map_err(|_|"maxN")?;
    let cells:usize=args[4].parse().map_err(|_|"cells")?;
    let tol:f64=if args.len()==6{args[5].parse().map_err(|_|"tol")?}else{1e-13};
    if !xend.is_finite()||xend<=0.||xend>0.002||!(8..=2048).contains(&max_n)||!max_n.is_power_of_two()||!(8..=512).contains(&cells){return Err("run domain".into());}
    let mut w=BufWriter::new(File::create(&args[1]).map_err(|e|e.to_string())?);
    let mut births=BufWriter::new(File::create(format!("{}.births.csv",args[1])).map_err(|e|e.to_string())?);
    writeln!(w,"mode,cells,N,step,X,Xend,T_K,HII,HeII,HeIII,electrons_per_H,photons_per_H,source_N,source_U,photo_HI,photo_HeI,photo_HeII,CI_HI,CI_HeI,CI_HeII,RR_HII,RR_HeII,RR_HeIII,DR_HeII,photo_binding_eV_H,photo_heat_eV_H,CE_HI_eV_H,CE_HeI_eV_H,CE_HeII_eV_H,RR_HII_eV_H,RR_HeII_eV_H,RR_HeIII_eV_H,DR_HeII_eV_H,FF_eV_H,CMB_eV_H,thermal_work_eV_H,photon_work_eV_H,escape_eV_H,boundary_U_eV_H,energy_residual_eV_H,photon_residual_H,max_newton_residual,rhs_calls,microsegments,wall_s").map_err(|e|e.to_string())?;
    writeln!(births,"mode,N,step,birth,a,weight_dln_a,proper_time_weight_s,added_N,added_U").map_err(|e|e.to_string())?;
    for mode in ["be_control","common_combined","physical_midpoint","physical_gl2","source_off","source_off_midpoint","source_off_gl2"] {
        let mut n=8;
        while n<=max_n {
            let mut cfg=DriverConfig::baseline();cfg.transport_cells=cells;cfg.transport_threads=1;cfg.background_panels=128;
            let (mut d,mut s)=Driver::new(cfg).map_err(|e|format!("init {e:?}"))?;
            s.gas=IgmGasState::from_temperature([0.075,0.12,0.03],d.n_h0_cm3/s.a.powi(3),d.n_he0_cm3/s.a.powi(3),15000.).map_err(|e|format!("gas {e:?}"))?;
            let mut opt=SourceClockConfig{microphysics:NativeClockMode::AllMid,opacity_midpoint:true,
                attenuation:PhotonAttenuation::Exponential,source:SourcePlacement::Disabled,nonlinear_tolerance:tol};
            let rule=match mode {
                "be_control"=>{opt.microphysics=NativeClockMode::OwnerBe;opt.opacity_midpoint=false;
                    opt.attenuation=PhotonAttenuation::BackwardEuler;opt.source=SourcePlacement::Before;None},
                "common_combined"=>{opt.source=SourcePlacement::SymmetricHalves;None},
                "physical_midpoint"=>Some(PhysicalBirthRule::Midpoint),
                "physical_gl2"=>Some(PhysicalBirthRule::Gauss2),
                "source_off_midpoint"=>Some(PhysicalBirthRule::DisabledMidpoint),
                "source_off_gl2"=>Some(PhysicalBirthRule::DisabledGauss2),
                "source_off"=>None,
                _=>unreachable!(),
            };
            d.set_source_clocks(&s,opt).map_err(|e|format!("config {e:?}"))?;
            let a0=s.a;let dx=xend/n as f64;let clock=Instant::now();
            let (mut photo_binding,mut photo_heat,mut ff,mut microsegments)=(0.,0.,0.,0usize);
            let mut ce=[0.;3];let mut rr=[0.;4];
            for step in 1..=n {
                let before=s.clone();
                let report:BirthStepReport=if let Some(rule)=rule {
                    d.fixed_step_physical_birth(&mut s,dx,rule).map_err(|e|format!("mode={mode} N={n} step={step} {e:?}"))?
                }else{
                    d.fixed_step(&mut s,dx).map_err(|e|format!("mode={mode} N={n} step={step} {e:?}"))?;
                    let rhs=d.last_clock_rhs().map_err(|e|format!("rhs {e:?}"))?.ok_or("no diagnostic")?;
                    let segment=BirthMicroSegment::from_rhs(&d,before.a,s.a,rhs).map_err(|e|format!("segment {e:?}"))?;
                    let mut samples=Vec::new();
                    if opt.source!=SourcePlacement::Disabled {
                        let count=if opt.source==SourcePlacement::SymmetricHalves{2}else{1};
                        for _ in 0..count {samples.push(BirthSample{a:segment.a_mid,weight_dln_a:dx/count as f64,
                            proper_time_weight_s:segment.dt_s/count as f64,
                            added_photons_per_h:(s.ledgers.source_n-before.ledgers.source_n)/count as f64,
                            added_energy_ev_per_h:(s.ledgers.source_u-before.ledgers.source_u)/count as f64});}
                    }
                    BirthStepReport{births:samples,segments:vec![segment]}
                };
                for r in &report.segments {
                    photo_binding+=r.photo_binding_ev_per_h;photo_heat+=r.photo_heat_ev_per_h;
                    for j in 0..3 {ce[j]+=r.ce_cooling_ev_per_h[j];}
                    for j in 0..4 {rr[j]+=r.rrdr_cooling_ev_per_h[j];}
                    ff+=r.ff_cooling_ev_per_h;microsegments+=1;
                }
                for (i,b) in report.births.iter().enumerate(){
                    writeln!(births,"{mode},{n},{step},{i},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",b.a,b.weight_dln_a,b.proper_time_weight_s,b.added_photons_per_h,b.added_energy_ev_per_h).map_err(|e|e.to_string())?;
                }
                let nh=d.n_h0_cm3/s.a.powi(3);let nhe=d.n_he0_cm3/s.a.powi(3);
                let eos=s.gas.eos(nh,nhe).map_err(|e|format!("eos {e:?}"))?;
                let (nr,er)=d.residuals(&s).map_err(|e|format!("ledger {e:?}"))?;
                let mut values=vec![(s.a/a0).ln(),xend,eos.temperature_k,s.gas.fractions[0],s.gas.fractions[1],s.gas.fractions[2],
                    eos.electron_density_cm3/nh,s.photons.iter().chain(s.photon_inactive_number.iter()).sum(),s.ledgers.source_n,s.ledgers.source_u];
                values.extend(s.ledgers.photo_events);values.extend(s.ledgers.ci_events);values.extend(s.ledgers.rr_events);
                values.push(s.ledgers.dr_events);values.extend([photo_binding,photo_heat]);values.extend(ce);values.extend(rr);
                values.extend([ff,s.ledgers.cmb_input,s.ledgers.thermal_work,s.ledgers.photon_work,s.ledgers.escaped_u,s.ledgers.boundary_u,
                    er,nr,s.max_newton_residual,s.rhs_evaluations as f64,microsegments as f64,clock.elapsed().as_secs_f64()]);
                if !values.iter().all(|x|x.is_finite()){return Err("nonfinite output".into());}
                write!(w,"{mode},{cells},{n},{step}").map_err(|e|e.to_string())?;
                for v in values {write!(w,",{v:.17e}").map_err(|e|e.to_string())?;}
                writeln!(w).map_err(|e|e.to_string())?;
            }
            w.flush().map_err(|e|e.to_string())?;births.flush().map_err(|e|e.to_string())?;
            eprintln!("COMPLETE mode={mode} N={n} cells={cells} Xend={xend} microsegments={microsegments} wall={:.6}",clock.elapsed().as_secs_f64());
            n*=2;
        }
    }
    Ok(())
}
