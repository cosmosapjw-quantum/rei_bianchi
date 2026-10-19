//! Explicit opt-in gas-midpoint / native moment SSPRK(2,2) coupling.
//! SourceClockConfig.attenuation is intentionally ignored ONLY by these named
//! SSPRK APIs. Gas midpoint coupling is not a coupled SSP positivity theorem.
use super::*;
use crate::axbi_covariant_transport::Ssprk2AbsorptionReport;
#[derive(Clone,Debug)]
pub struct SsprkChemicalReport {pub rhs:IgmPointRhs,pub transport:Ssprk2AbsorptionReport}
#[derive(Clone,Debug,Default)]
pub struct SsprkStageDiagnostics {
 pub max_tau_stage1:f64,pub max_tau_stage2:f64,
 pub nodes_stage1:usize,pub nodes_stage2:usize,
 pub quad_count_stage1:f64,pub quad_count_stage2:f64,
 pub quad_energy_stage1:f64,pub quad_energy_stage2:f64,
}
impl SsprkStageDiagnostics {
 pub fn include(&mut self,r:&Ssprk2AbsorptionReport) {
  self.max_tau_stage1=self.max_tau_stage1.max(r.max_tau_stage1);self.max_tau_stage2=self.max_tau_stage2.max(r.max_tau_stage2);
  self.nodes_stage1+=r.nodes_stage1;self.nodes_stage2+=r.nodes_stage2;
  self.quad_count_stage1=self.quad_count_stage1.max(r.diagnostics_stage1.max_count_relative_defect);self.quad_count_stage2=self.quad_count_stage2.max(r.diagnostics_stage2.max_count_relative_defect);
  self.quad_energy_stage1=self.quad_energy_stage1.max(r.diagnostics_stage1.max_energy_relative_defect);self.quad_energy_stage2=self.quad_energy_stage2.max(r.diagnostics_stage2.max_energy_relative_defect);
 }
}
#[derive(Clone,Debug)]
pub struct SsprkBirthStepReport {pub birth:BirthStepReport,pub stages:SsprkStageDiagnostics}
#[derive(Clone)]
struct SsprkContext {gas:IgmGasState,a:f64,nh:f64,nhe:f64,geometry:GeometrySnapshot,initial:PhotonState,transport:CovariantTransport}
impl SsprkContext {
 fn evaluate(&self,unknown:[f64;4],dt:f64)->Result<([f64;4],Ssprk2AbsorptionReport,IgmPointRhs),ForwardError>{
  let gas=IgmGasState::new([unknown[0],unknown[1],unknown[2]],w_ev_per_h_to_erg(unknown[3])?)?;
  let mid=IgmGasState::new(std::array::from_fn(|j|0.5*(self.gas.fractions[j]+gas.fractions[j])),0.5*(self.gas.w_erg_per_h+gas.w_erg_per_h))?;
  let [x,y,z]=mid.fractions;
  let transport=self.transport.absorb_ssprk2(&self.initial,&self.geometry,[self.nh*(1.-x),self.nhe*(1.-y-z),self.nhe*y],self.nh,dt)?;
  let micro=AxbiProvider.point(&mid,self.nh,self.nhe,0.,2.7255/self.a,IgmPhotoInput::default())?.rhs;
  let rhs=add_absorption_rhs(micro,&transport.absorption,&mid,self.nh,self.nhe,dt)?;
  let mut residual=[0.;4];for j in 0..3{residual[j]=unknown[j]-self.gas.fractions[j]-dt*rhs.fraction_dt[j];}
  residual[3]=unknown[3]-w_erg_per_h_to_ev(self.gas.w_erg_per_h)?-dt*rhs.w_dt_erg_per_h_s/HHeModel::controlled_fixture().ev_erg;
  for &v in &residual{f(v)?;}Ok((residual,transport,rhs))
 }
}
impl Driver {
 fn guard_ssprk2(&self)->Result<(),ForwardError>{
  if self.config.parallel_jacobian_columns || !self.source_clocks.is_some_and(|c|c.microphysics==NativeClockMode::AllMid && c.opacity_midpoint && c.source==SourcePlacement::Disabled) {return Err(err("AXBI_SSP_CLOCK_PRECONDITION"));}Ok(())
 }
 /// New fixed-geometry chemistry stage; explicit SSPRK photons supersede the
 /// scalar attenuation selector only in this named API. Counter includes all
 /// residual/Jacobian/line-search work, even on failure; state/RHS commit once.
 pub fn chemical_stage_ssprk2(&self,s:&mut DriverState,dt:f64,counter:&mut usize)->Result<SsprkChemicalReport,ForwardError>{
  self.guard_ssprk2()?;if !dt.is_finite()||dt<=0.{return Err(err("AXBI_STAGE_DT"));}
  let geometry=self.geometry_point(s.a)?.geometry()?;let mut old=s.clone();self.partition_inactive(&mut old,&geometry)?;
  let context=SsprkContext{gas:old.gas,a:old.a,nh:self.n_h0_cm3/old.a.powi(3),nhe:self.n_he0_cm3/old.a.powi(3),geometry,initial:self.photon_state(&old),transport:self.transport.clone()};
  let old_w=w_erg_per_h_to_ev(old.gas.w_erg_per_h)?;let mut x=[old.gas.fractions[0],old.gas.fractions[1],old.gas.fractions[2],old_w];
  for _ in 0..50 {
   if *counter>=self.config.max_rhs{return Err(err("AXBI_RHS_CAP"));}*counter+=1;
   let(residual,transport,rhs)=context.evaluate(x,dt)?;
   let norm=self.norm(residual,old_w,x[3]);
   if norm<=self.source_clocks.unwrap().nonlinear_tolerance {
                let nh = self.n_h0_cm3 / old.a.powi(3);
                let c = HHeModel::controlled_fixture();
                let nold = old.photons.iter().sum::<f64>();
                let nnew = transport.absorption.state.number.iter().sum::<f64>();
                let events = rhs.photo_events_cm3_s.map(|e| e * dt / nh);
                let event_total = events.iter().sum::<f64>();
                if (nold - nnew - event_total).abs() > 1e-10 * old.ledgers.source_n.max(1.0) {
                    return Err(err("AXBI_ABSORPTION_LEDGER"));
                }
                let mut next = old.clone();
                next.gas = IgmGasState::new([x[0], x[1], x[2]], w_ev_per_h_to_erg(x[3])?)?;
                Self::set_photon_state(&mut next, transport.absorption.state.clone());
                next.ledgers.absorbed_n += event_total;
                for k in 0..3 {
                    next.ledgers.photo_events[k] += events[k];
                    next.ledgers.rr_events[k] += rhs.rr_events_cm3_s[k] * dt / nh;
                    next.ledgers.ci_events[k] += rhs.ci_events_cm3_s[k] * dt / nh;
                    next.ledgers.ci_floor_events[k] += rhs.ci_floor_events_cm3_s[k] * dt / nh;
                }
                next.ledgers.dr_events += rhs.dr_events_cm3_s * dt / nh;
                next.ledgers.ce_cap_ev +=
                    rhs.ce_cap_cooling_erg_cm3_s.iter().sum::<f64>() * dt / (nh * c.ev_erg);
                next.ledgers.excluded_dr_ev +=
                    rhs.excluded_dr_cooling_erg_cm3_s * dt / (nh * c.ev_erg);
                next.ledgers.escaped_u += rhs.escape_erg_cm3_s * dt / (nh * c.ev_erg);
                next.ledgers.cmb_input += rhs.cmb_to_gas_erg_cm3_s * dt / (nh * c.ev_erg);
                next.max_newton_residual = next.max_newton_residual.max(norm);
                *self
                    .last_clock_rhs
                    .lock()
                    .map_err(|_| err("AXBI_CLOCK_POISONED"))? =
                    if self.clock_mode.is_some() || self.source_clocks.is_some() {
                        Some(rhs)
                    } else {
                        None
                    };
                *s = next;
                return Ok(SsprkChemicalReport{rhs,transport});
            }
   let columns_context=context.clone();
   let jac=jacobian_columns(&self.transport.shared_pool(),false,x,residual,counter,self.config.max_rhs,move |u|columns_context.evaluate(u,dt).map(|v|v.0))?;
   let direction=solve4(jac,residual.map(|r|-r))?;let mut alpha=1.;let mut accepted=None;
   for _ in 0..40 {
    let trial=std::array::from_fn(|j|x[j]+alpha*direction[j]);
    if *counter>=self.config.max_rhs{return Err(err("AXBI_RHS_CAP"));}*counter+=1;
    if let Ok((r,_,_))=context.evaluate(trial,dt){if self.norm(r,old_w,trial[3])<norm{accepted=Some(trial);break;}}
    alpha*=0.5;
   }
   x=accepted.ok_or(err("AXBI_NEWTON_LINESEARCH"))?;
  }Err(err("AXBI_NEWTON_ITERATIONS"))
 }
 fn tentative_ssprk2(&self,old:&DriverState,to:f64,counter:&mut usize)->Result<(DriverState,SsprkChemicalReport),ForwardError>{
  if !to.is_finite()||to<=old.a{return Err(err("AXBI_SSP_FORWARD_TIME"));}
  let mut s=old.clone();let mid=(old.a*to).sqrt();let dt=(to/old.a).ln()/self.geometry_point(mid)?.h_flrw_per_s;
  self.geometry_map(&mut s,mid)?;let report=self.chemical_stage_ssprk2(&mut s,dt,counter)?;self.geometry_map(&mut s,to)?;self.validate(&s,1e-8)?;
  let(n0,u0)=self.residuals(old)?;let(n1,u1)=self.residuals(&s)?;
  if (n1-n0).abs()>1e-10*s.ledgers.source_n.max(1.)||(u1-u0).abs()>1e-10*s.ledgers.source_u.max(1.){return Err(err("AXBI_STEP_LEDGER"));}Ok((s,report))
 }
 pub fn fixed_step_physical_birth_ssprk2(&self,s:&mut DriverState,dln_a:f64,rule:PhysicalBirthRule)->Result<SsprkBirthStepReport,ForwardError>{
  self.guard_ssprk2()?;
  if !dln_a.is_finite()||dln_a<=0.||dln_a>0.005{return Err(err("V15_FIXED_STEP_DOMAIN"));}
  if s.accepted>=self.config.max_steps||s.attempts>=self.config.max_attempts{return Err(err("AXBI_STEP_CAP"));}
  let saved_rhs=self.last_clock_rhs()?;let mut counter=s.rhs_evaluations;s.attempts+=1;
  let result=(||->Result<(DriverState,SsprkBirthStepReport),ForwardError>{
   let mut next=s.clone();let mut birth=BirthStepReport::default();let mut stages=SsprkStageDiagnostics::default();
   let a0=s.a;let final_a=a0*dln_a.exp();
   for(fraction,weight)in rule.nodes(){
    let birth_a=a0*(fraction*dln_a).exp();if birth_a<=next.a||birth_a>=final_a{return Err(err("V14_UNRESOLVED_BIRTH_CLOCK"));}
    let before=next.a;let(new,r)=self.tentative_ssprk2(&next,birth_a,&mut counter)?;next=new;
    birth.segments.push(BirthMicroSegment::from_rhs(self,before,birth_a,r.rhs)?);stages.include(&r.transport);
    let physical_weight=dln_a*weight/self.geometry_point(birth_a)?.h_flrw_per_s;
    if !physical_weight.is_finite()||physical_weight<=0.{return Err(err("V14_SOURCE_WEIGHT"));}
    let n0=next.ledgers.source_n;let u0=next.ledgers.source_u;if rule.enabled(){self.inject(&mut next,physical_weight)?;}
    birth.births.push(BirthSample{a:birth_a,weight_dln_a:dln_a*weight,proper_time_weight_s:physical_weight,added_photons_per_h:next.ledgers.source_n-n0,added_energy_ev_per_h:next.ledgers.source_u-u0});
   }
   let before=next.a;let(new,r)=self.tentative_ssprk2(&next,final_a,&mut counter)?;next=new;
   birth.segments.push(BirthMicroSegment::from_rhs(self,before,final_a,r.rhs)?);stages.include(&r.transport);self.validate(&next,1e-8)?;
   let(n0,e0)=self.residuals(s)?;let(n1,e1)=self.residuals(&next)?;
   if(n1-n0).abs()>1e-10*next.ledgers.source_n.max(1.)||(e1-e0).abs()>1e-10*next.ledgers.source_u.max(1.){return Err(err("V14_MACRO_LEDGER"));}
   Ok((next,SsprkBirthStepReport{birth,stages}))
  })();s.rhs_evaluations=counter;
  match result{Ok((mut next,report))=>{next.rhs_evaluations=counter;next.attempts=s.attempts;next.accepted=s.accepted+1;next.next_dln_a=dln_a;*s=next;Ok(report)},Err(e)=>{*self.last_clock_rhs.lock().map_err(|_|err("AXBI_CLOCK_POISONED"))?=saved_rhs;Err(e)}}
 }
}
