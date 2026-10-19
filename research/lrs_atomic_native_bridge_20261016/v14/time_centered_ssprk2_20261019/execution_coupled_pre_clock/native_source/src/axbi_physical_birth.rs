//! V14 fixed-run adapter: chronological source birth, original V13 transport/gas.
//! This file is a CHILD module of axbi_driver, not a standalone alternative RHS.
//! All accepted physical updates use the existing native tentative, inject and
//! validate functions. Actual test/compile admission lives in execution receipts.
use super::{err,Driver,DriverState,ForwardError,HHeModel,IgmPointRhs,SourcePlacement};

#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum PhysicalBirthRule { Midpoint, Gauss2, DisabledMidpoint, DisabledGauss2 }
impl PhysicalBirthRule {
    /// (fractional log-a time, positive fractional quadrature weight).
    pub fn nodes(self) -> Vec<(f64,f64)> {
        match self {
            Self::Midpoint|Self::DisabledMidpoint => vec![(0.5,1.0)],
            Self::Gauss2|Self::DisabledGauss2 => {
                let c=0.5*(1.0-1.0/3.0_f64.sqrt());
                vec![(c,0.5),(1.0-c,0.5)]
            }
        }
    }
    pub fn enabled(self)->bool {matches!(self,Self::Midpoint|Self::Gauss2)}
}
#[derive(Clone,Debug)]
pub struct BirthSample {
    pub a:f64,
    pub weight_dln_a:f64,
    pub proper_time_weight_s:f64,
    pub added_photons_per_h:f64,
    pub added_energy_ev_per_h:f64,
}
#[derive(Clone,Debug)]
pub struct BirthMicroSegment {
    pub a_begin:f64,pub a_mid:f64,pub a_end:f64,pub dt_s:f64,pub n_h_cm3:f64,
    pub photo_events_per_h:[f64;3],pub ci_events_per_h:[f64;3],
    pub rr_events_per_h:[f64;3],pub dr_events_per_h:f64,
    pub photo_binding_ev_per_h:f64,pub photo_heat_ev_per_h:f64,
    pub ce_cooling_ev_per_h:[f64;3],pub rrdr_cooling_ev_per_h:[f64;4],
    pub ff_cooling_ev_per_h:f64,pub cmb_input_ev_per_h:f64,
    pub escaped_ev_per_h:f64,
}
impl BirthMicroSegment {
    /// Integrate THIS segment's rate. Never use a final RHS with a macro dt.
    pub fn from_rhs(d:&Driver,begin:f64,end:f64,r:IgmPointRhs)->Result<Self,ForwardError> {
        let mid=(begin*end).sqrt();
        let h=d.geometry_point(mid)?.h_flrw_per_s;
        let dt=(end/begin).ln()/h;
        let nh=d.n_h0_cm3/mid.powi(3);
        let c=HHeModel::controlled_fixture();
        let events=dt/nh;let energy=events/c.ev_erg;
        if !events.is_finite()||events<=0.||!energy.is_finite(){return Err(err("V14_SEGMENT_SCALE"));}
        let ph=r.photo_events_cm3_s.map(|v|v*events);
        let binding=(0..3).map(|i|ph[i]*c.threshold_ev[i]).sum::<f64>();
        let rr=r.rr_thermal_sink_erg_cm3_s.map(|v|v*energy);
        Ok(Self{a_begin:begin,a_mid:mid,a_end:end,dt_s:dt,n_h_cm3:nh,
            photo_events_per_h:ph,ci_events_per_h:r.ci_events_cm3_s.map(|v|v*events),
            rr_events_per_h:r.rr_events_cm3_s.map(|v|v*events),dr_events_per_h:r.dr_events_cm3_s*events,
            photo_binding_ev_per_h:binding,
            photo_heat_ev_per_h:r.photo_input_erg_cm3_s*energy-binding,
            ce_cooling_ev_per_h:r.ce_thermal_sink_erg_cm3_s.map(|v|v*energy),
            rrdr_cooling_ev_per_h:[rr[0],rr[1],rr[2],r.dr_thermal_sink_erg_cm3_s*energy],
            ff_cooling_ev_per_h:r.freefree_thermal_sink_erg_cm3_s*energy,
            cmb_input_ev_per_h:r.cmb_to_gas_erg_cm3_s*energy,
            escaped_ev_per_h:r.escape_erg_cm3_s*energy})
    }
}
#[derive(Clone,Debug,Default)]
pub struct BirthStepReport {
    pub births:Vec<BirthSample>,
    pub segments:Vec<BirthMicroSegment>,
}
impl Driver {
    /// Fixed macrostep with actual birth geometry; no changes to adaptive path.
    ///
    /// Set SourceClockConfig.source=Disabled before calling. This prevents the
    /// inner original tentative from injecting any additional photons. Existing
    /// original rate, EOS, opacity/attenuation and gas-clock settings are used.
    /// Native substeps evolve all already-born photons; no new photon is evolved
    /// before its actual injection. Nonlinear/stiff/threshold convergence still
    /// requires actual native evidence; GL2 is not a full-solver p=4 assertion.
    pub fn fixed_step_physical_birth(&self,s:&mut DriverState,dln_a:f64,
                                    rule:PhysicalBirthRule)->Result<BirthStepReport,ForwardError> {
        if !dln_a.is_finite()||dln_a<=0.||dln_a>0.005 {
            return Err(err("V14_FIXED_STEP_DOMAIN"));
        }
        if !self.source_clocks.is_some_and(|v|v.source==SourcePlacement::Disabled) {
            return Err(err("V14_REQUIRES_DISABLED_INNER_SOURCE"));
        }
        if s.accepted>=self.config.max_steps||s.attempts>=self.config.max_attempts {
            return Err(err("AXBI_STEP_CAP"));
        }
        let saved_rhs=self.last_clock_rhs()?;
        let mut counter=s.rhs_evaluations;
        s.attempts+=1;
        let result=(||->Result<(DriverState,BirthStepReport),ForwardError>{
            let mut next=s.clone();
            let mut report=BirthStepReport::default();
            let a0=s.a;let final_a=a0*dln_a.exp();
            for (fraction,weight) in rule.nodes() {
                let birth_a=a0*(fraction*dln_a).exp();
                if birth_a<=next.a||birth_a>=final_a {return Err(err("V14_UNRESOLVED_BIRTH_CLOCK"));}
                let before=next.a;
                next=self.tentative(&next,birth_a,&mut counter)?;
                let rhs=self.last_clock_rhs()?.ok_or(err("V14_MISSING_SEGMENT_RHS"))?;
                report.segments.push(BirthMicroSegment::from_rhs(self,before,birth_a,rhs)?);
                let hubble=self.geometry_point(birth_a)?.h_flrw_per_s;
                let physical_weight=dln_a*weight/hubble;
                if !physical_weight.is_finite()||physical_weight<=0. {return Err(err("V14_SOURCE_WEIGHT"));}
                let n0=next.ledgers.source_n;let u0=next.ledgers.source_u;
                if rule.enabled(){self.inject(&mut next,physical_weight)?;}
                report.births.push(BirthSample{a:birth_a,weight_dln_a:dln_a*weight,
                    proper_time_weight_s:physical_weight,
                    added_photons_per_h:next.ledgers.source_n-n0,
                    added_energy_ev_per_h:next.ledgers.source_u-u0});
            }
            let before=next.a;
            next=self.tentative(&next,final_a,&mut counter)?;
            let rhs=self.last_clock_rhs()?.ok_or(err("V14_MISSING_SEGMENT_RHS"))?;
            report.segments.push(BirthMicroSegment::from_rhs(self,before,final_a,rhs)?);
            self.validate(&next,1e-8)?;
            let (n0,e0)=self.residuals(s)?;let (n1,e1)=self.residuals(&next)?;
            if (n1-n0).abs()>1e-10*next.ledgers.source_n.max(1.) ||
               (e1-e0).abs()>1e-10*next.ledgers.source_u.max(1.) {
                return Err(err("V14_MACRO_LEDGER"));
            }
            Ok((next,report))
        })();
        // Even a failed macrostep consumes attempted RHS budget. Physical state
        // and diagnostic are not committed until ALL substeps and injections pass.
        s.rhs_evaluations=counter;
        match result {
            Ok((mut next,report))=>{
                next.rhs_evaluations=counter;next.attempts=s.attempts;
                next.accepted=s.accepted+1;next.next_dln_a=dln_a;*s=next;Ok(report)
            }
            Err(e)=>{
                *self.last_clock_rhs.lock().map_err(|_|err("AXBI_CLOCK_POISONED"))?=saved_rhs;
                Err(e)
            }
        }
    }
}
