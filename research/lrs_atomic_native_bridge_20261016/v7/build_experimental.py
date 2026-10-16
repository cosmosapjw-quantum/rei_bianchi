"""Make an isolated V7 experimental owner crate from an exact PR150 source tree.

Only the destination copy of axbi_driver.rs is changed. This is deliberately a
small mechanical patch with exact-match guards, not a production driver edit.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

EXPECTED = "6ea2b1b4b3875c9163cafc45efe720afded43fc4"


def replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise RuntimeError(f"V7 patch context count {source.count(old)} != 1: {old[:90]!r}")
    return source.replace(old, new, 1)


def main() -> None:
    repo = pathlib.Path(sys.argv[1]).resolve()
    path = repo / "rust/rei_microphysics/src/axbi_driver.rs"
    source = path.read_text()
    before = hashlib.sha256(source.encode()).hexdigest()
    source = replace_once(source,
        "    prepared: Arc<PreparedAbsorption>,\n}\nimpl ResidualContext",
        "    prepared: Arc<PreparedAbsorption>,\n    v7_omit_recomb: bool,\n}\nimpl ResidualContext")
    source = replace_once(source,
        "        let point = AxbiProvider.point(&gas, nh, nhe, 0.0, 2.7255 / self.a, photo)?;\n        let mut residual = [0.0; 4];",
        "        let point = AxbiProvider.point(&gas, nh, nhe, 0.0, 2.7255 / self.a, photo)?;\n        let mut rhs = point.rhs;\n        if self.v7_omit_recomb { v7_strip_recomb(&mut rhs, nh, nhe); }\n        let mut residual = [0.0; 4];")
    source = replace_once(source,
        "dt * point.rhs.fraction_dt[i]", "dt * rhs.fraction_dt[i]")
    source = replace_once(source,
        "dt * point.rhs.w_dt_erg_per_h_s / c.ev_erg", "dt * rhs.w_dt_erg_per_h_s / c.ev_erg")
    source = replace_once(source,
        "Ok((residual, stocks, point.rhs))", "Ok((residual, stocks, rhs))")
    source = replace_once(source,
        "    pub fn chemical_stage(\n        &self,\n        s: &mut DriverState,\n        dt: f64,\n        counter: &mut usize,\n    ) -> Result<(), ForwardError> {\n",
        "    pub fn chemical_stage(\n        &self,\n        s: &mut DriverState,\n        dt: f64,\n        counter: &mut usize,\n    ) -> Result<(), ForwardError> {\n        self.v7_chemical_stage(s, dt, counter, false)\n    }\n    fn v7_chemical_stage(\n        &self,\n        s: &mut DriverState,\n        dt: f64,\n        counter: &mut usize,\n        omit_recomb: bool,\n    ) -> Result<(), ForwardError> {\n")
    source = replace_once(source,
        "            prepared: Arc::new(prepared),\n        };",
        "            prepared: Arc::new(prepared),\n            v7_omit_recomb: omit_recomb,\n        };")
    source = replace_once(source,
        "    /// Controlled fixed-log-scale step for independent geometry and chemistry\n",
        "    pub fn fixed_step_v7(&self, s: &mut DriverState, dln_a: f64) -> Result<(), ForwardError> {\n        if !dln_a.is_finite() || dln_a <= 0.0 || dln_a > 0.005 {\n            return Err(err(\"V7_FIXED_STEP_DOMAIN\"));\n        }\n        if s.accepted >= self.config.max_steps || s.attempts >= self.config.max_attempts {\n            return Err(err(\"AXBI_STEP_CAP\"));\n        }\n        let old = s.clone();\n        let to = old.a * dln_a.exp();\n        let mid = (old.a * to).sqrt();\n        let dt = self.geometry_increment(old.a, to)?.proper_time_s;\n        let mut next = old.clone();\n        let mut counter = s.rhs_evaluations;\n        s.attempts += 1;\n        let result = (|| {\n            self.geometry_map(&mut next, mid)?;\n            self.inject(&mut next, dt)?;\n            self.v7_recomb_stage(&mut next, dt * 0.5)?;\n            self.v7_chemical_stage(&mut next, dt, &mut counter, true)?;\n            self.v7_recomb_stage(&mut next, dt * 0.5)?;\n            self.geometry_map(&mut next, to)?;\n            self.validate(&next, 1e-8)?;\n            let (n0,u0)=self.residuals(&old)?;\n            let (n1,u1)=self.residuals(&next)?;\n            if (n1-n0).abs()>1e-10*next.ledgers.source_n.max(1.0) || (u1-u0).abs()>1e-10*next.ledgers.source_u.max(1.0) {return Err(err(\"V7_STEP_LEDGER\"));}\n            Ok::<(), ForwardError>(())\n        })();\n        s.rhs_evaluations = counter;\n        result?;\n        next.rhs_evaluations = counter;\n        next.accepted = old.accepted + 1;\n        next.attempts = s.attempts;\n        next.next_dln_a = dln_a;\n        *s = next;\n        Ok(())\n    }\n    fn v7_recomb_stage(&self, s: &mut DriverState, dt: f64) -> Result<(), ForwardError> {\n        let nh = self.n_h0_cm3 / s.a.powi(3);\n        let nhe = self.n_he0_cm3 / s.a.powi(3);\n        let c = HHeModel::controlled_fixture();\n        for ordering in [[0_usize,1,2],[2,1,0]] {\n            for j in ordering {\n                let duration = dt * 0.5;\n                let ion = match j { 0 => nh*s.gas.fractions[0], 1 => nhe*s.gas.fractions[1], _ => nhe*s.gas.fractions[2] };\n                let ne = s.gas.eos(nh,nhe)?.electron_density_cm3;\n                if ion == 0.0 || ne == 0.0 { continue; }\n                let w0 = s.gas.w_erg_per_h;\n                let n0 = nh+nhe+ne;\n                let solve = |t: f64| -> Result<(f64,f64,f64),ForwardError> {\n                    if !(10000.0..=24000.0).contains(&t) { return Err(err(\"V7_RATE_DOMAIN\")); }\n                    let rates = crate::igm_rates::igm_rates(t)?;\n                    let alpha = rates.rr_cm3_s[j] + if j==1 {rates.dr_cm3_s} else {0.0};\n                    let cool = rates.rr_cooling_erg_cm3_s[j] + if j==1 {rates.dr_cooling_erg_cm3_s} else {0.0};\n                    if alpha<=0.0 { return Err(err(\"V7_ZERO_ALPHA\")); }\n                    let a = v7_pair_exact(ion, ne, duration*alpha)?;\n                    let q = a*cool/alpha;\n                    if q > nh*w0 || n0-a*0.5 <= 0.0 { return Err(err(\"V7_THERMAL_BOUND\")); }\n                    let predicted = (nh*w0-q*0.5)/(1.5*c.kb_erg_k*(n0-a*0.5));\n                    Ok((a,q,predicted))\n                };\n                let mut lo=10000.0; let mut hi=24000.0;\n                let flo=lo-solve(lo)?.2; let fhi=hi-solve(hi)?.2;\n                if flo*fhi>0.0 { return Err(err(\"V7_MIDPOINT_UNBRACKETED\")); }\n                let mut tm=lo;\n                for _ in 0..75 {\n                    tm=(lo+hi)*0.5;\n                    let fm=tm-solve(tm)?.2;\n                    if fm.abs()<1e-9 {break;}\n                    if fm*flo>0.0 {lo=tm;} else {hi=tm;}\n                }\n                let (a,q,predicted)=solve(tm)?;\n                if (tm-predicted).abs()>2e-7 {return Err(err(\"V7_MIDPOINT_RESIDUAL\"));}\n                let rates=crate::igm_rates::igm_rates(tm)?;\n                let dr_share=if j==1 {rates.dr_cm3_s/(rates.rr_cm3_s[j]+rates.dr_cm3_s)} else {0.0};\n                let mut fractions=s.gas.fractions;\n                if j==0 {fractions[0]-=a/nh;}\n                if j==1 {fractions[1]-=a/nhe;}\n                if j==2 {fractions[2]-=a/nhe; fractions[1]+=a/nhe;}\n                s.gas=IgmGasState::new(fractions,w0-q/nh)?;\n                let tnew=s.gas.eos(nh,nhe)?.temperature_k;\n                if !(10000.0..=24000.0).contains(&tnew) {return Err(err(\"V7_FINAL_RATE_DOMAIN\"));}\n                s.ledgers.rr_events[j]+=a*(1.0-dr_share)/nh;\n                s.ledgers.dr_events+=a*dr_share/nh;\n                s.ledgers.escaped_u+=a*c.threshold_ev[j]/nh+q/(nh*c.ev_erg);\n            }\n        }\n        Ok(())\n    }\n    /// Controlled fixed-log-scale step for independent geometry and chemistry\n")
    source = replace_once(source,
        "    /// Controlled fixed-log-scale step for independent geometry and chemistry\n",
        "    pub fn v7_seed(config: DriverConfig) -> Result<(Self, DriverState), ForwardError> {\n        let (mut driver, mut state) = Self::new(config)?;\n        let nh = driver.n_h0_cm3 / state.a.powi(3);\n        let nhe = driver.n_he0_cm3 / state.a.powi(3);\n        state.gas = IgmGasState::from_temperature([0.075,0.12,0.03],nh,nhe,15000.0)?;\n        driver.initial_energy = driver.total_energy(&state)?;\n        Ok((driver,state))\n    }\n    /// Controlled fixed-log-scale step for independent geometry and chemistry\n")
    # Helpers live in the same module and preserve the untouched baseline API.
    source += '''\nfn v7_pair_exact(a:f64,b:f64,k:f64)->Result<f64,ForwardError>{\n    if !a.is_finite() || !b.is_finite() || !k.is_finite() || a<0.0 || b<0.0 || k<0.0 {return Err(err("V7_PAIR_DOMAIN"));}\n    if a==0.0 || b==0.0 || k==0.0 {return Ok(0.0);}\n    let small=a.min(b); let large=a.max(b); let diff=large-small;\n    let event=if diff==0.0 {let z=small*k; small*z/(1.0+z)}\n        else {let u=-(-diff*k).exp_m1(); small*large*u/(diff+small*u)};\n    Ok(event.max(0.0).min(small))\n}\nfn v7_strip_recomb(rhs:&mut IgmPointRhs,nh:f64,nhe:f64){\n    let rr=rhs.rr_events_cm3_s; let dr=rhs.dr_events_cm3_s;\n    let cool=rhs.rr_thermal_sink_erg_cm3_s.iter().sum::<f64>()+rhs.dr_thermal_sink_erg_cm3_s;\n    let c=HHeModel::controlled_fixture();\n    let bind=(0..3).map(|i| c.threshold_ev[i]*c.ev_erg*rr[i]).sum::<f64>()+c.threshold_ev[1]*c.ev_erg*dr;\n    rhs.fraction_dt[0]+=rr[0]/nh;\n    rhs.species_chemical_cm3_s[0]-=rr[0]; rhs.species_chemical_cm3_s[1]+=rr[0];\n    rhs.species_chemical_cm3_s[2]-=rr[1]+dr; rhs.species_chemical_cm3_s[3]+=rr[1]+dr-rr[2];\n    rhs.species_chemical_cm3_s[4]+=rr[2]; rhs.species_chemical_cm3_s[5]+=rr[0]+rr[1]+dr+rr[2];\n    if nhe>0.0 {rhs.fraction_dt[1]+=(rr[1]+dr-rr[2])/nhe; rhs.fraction_dt[2]+=rr[2]/nhe;}\n    rhs.w_dt_erg_per_h_s+=cool/nh;\n    rhs.thermal_micro_erg_cm3_s+=cool;\n    rhs.binding_micro_erg_cm3_s+=bind;\n    rhs.escape_erg_cm3_s-=bind+cool;\n    rhs.rr_events_cm3_s=[0.0;3]; rhs.dr_events_cm3_s=0.0;\n    rhs.rr_thermal_sink_erg_cm3_s=[0.0;3]; rhs.dr_thermal_sink_erg_cm3_s=0.0;\n}\n'''
    path.write_text(source)
    after = hashlib.sha256(source.encode()).hexdigest()
    print(f"owner={EXPECTED} axbi_driver_before_sha256={before} experimental_sha256={after}")


if __name__ == "__main__":
    main()
