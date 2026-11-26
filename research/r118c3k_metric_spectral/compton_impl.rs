// C3J isolated shadow only. Number weights x^3 dl match this native FF grid.
impl SpectralFf {
    fn c3j_sweep(&mut self, theta:f64, dt:f64, parity:usize, bb:f64)->Result<f64,ForwardError>{
        let mut energy=0.;
        for i in (parity..self.x.len()-1).step_by(2){
            let j=i+1;let xi=self.x[i];let xj=self.x[j];let dx=xj-xi;
            let ci=xi.powi(3)*self.dl;let cj=xj.powi(3)*self.dl;
            let fi0=pl(xi);let fj0=pl(xj);let u=self.delta[i];let v=self.delta[j];
            let fi=fi0+u;let fj=fj0+v;
            if fi<0.||fj<0.||!fi.is_finite()||!fj.is_finite(){return Err(bad())}
            let dd=dx/theta;let q=(-dd).exp();let b=-(-dd).exp_m1();let g=(xi*xj).powi(2)*dd/(dx*b);
            let j0=-g*fi0*(1.+fj0)*(-dx).exp()*(dx*(1.-1./theta)).exp_m1();
            let flux=j0+g*((1.+b*fi0)*v+(-q+b*fj0)*u+b*u*v);
            let m=ci*fi+cj*fj;let aa=g*b/(ci*cj);
            let bbcoef=g*(-(1.+b*fi)/cj+(-q+b*fj)/ci);
            let bt=g*(-1./cj-q/ci+b*m/(ci*cj));let cc=g*m/cj;
            let disc=(bt*bt+4.*aa*cc).sqrt();let z=-(-disc*dt).exp_m1();
            let den=disc*(2.-z)-bbcoef*z;
            if !den.is_finite()||den<=0.{return Err(bad())}
            let mut transfer=2.*flux*z/den;
            let lo=-ci*fi;let hi=cj*fj;let tol=64.*f64::EPSILON*m;
            if !transfer.is_finite()||transfer<lo-tol||transfer>hi+tol{return Err(bad())}
            transfer=transfer.max(lo).min(hi);
            self.delta[i]+=transfer/ci;self.delta[j]-=transfer/cj;
            energy-=bb*15./std::f64::consts::PI.powi(4)*dx*transfer;
        }
        Ok(energy)
    }
    pub fn advance_compton(&mut self,theta:f64,clock:f64,bb:f64)->Result<f64,ForwardError>{
        if theta<=0.||clock<0.||bb<=0.||![theta,clock,bb].iter().all(|v|v.is_finite()){return Err(bad())}
        // Trial only: if a later sweep fails leave receiver byte-identical.
        let mut trial=self.clone();
        let mut q=trial.c3j_sweep(theta,clock/2.,0,bb)?;
        q+=trial.c3j_sweep(theta,clock,1,bb)?;
        q+=trial.c3j_sweep(theta,clock/2.,0,bb)?;
        if trial.delta.iter().zip(&trial.x).any(|(v,x)|!v.is_finite()||v+pl(*x)<0.){return Err(bad())}
        *self=trial;Ok(q)
    }
    pub fn c3j_number(&self)->f64{
        self.x.iter().zip(&self.delta).map(|(x,d)|x.powi(3)*self.dl*d).sum()
    }
}
#[cfg(test)]
mod c3j_checks {
    use super::*;
    #[test]
    fn equilibrium_and_conservation(){
        let mut s=SpectralFf::new(1e-10,60.,1024).unwrap();
        assert_eq!(s.advance_compton(1.,1e-8,1e7).unwrap(),0.);
        assert!(s.distortion().iter().all(|x|*x==0.));
        let q=s.advance_compton(0.3,1e-8,1e7).unwrap();
        assert!(q<0.);assert!((s.energy(1e7).unwrap()-q).abs()<1e-13*q.abs());
        assert!(s.c3j_number().abs()<1e-21);
        let d=s.distortion().to_vec();assert!(s.advance_compton(-1.,1e-8,1e7).is_err());assert_eq!(d,s.distortion());
    }
}
