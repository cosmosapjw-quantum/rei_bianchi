//! Analytic O(L) solve of the ORIGINAL full shifted HH Jacobian, not a preconditioner.
//! Uses the block order (f,g), A/B, z. J is frozen at one accepted/rejected base state.
use num_complex::Complex64 as C;
use rodas5p_core::{CoreError,CoreResult};
use wu088_hh_phys69_vigilode::{K,Q_SCALE,TARGET_A,TARGET_B,get,put};
use crate::kernel::finite;

pub struct FrozenJacobian {
    n:usize, valid:bool,
    f:Vec<C>, q:Vec<f64>, ca:Vec<f64>, cb:Vec<f64>,
    za:Vec<C>, zb:Vec<C>, zf:Vec<C>,
}
impl FrozenJacobian {
    pub fn new(n:usize)->Self { Self{n,valid:false,f:vec![C::default();n],q:vec![0.0;n],ca:vec![0.0;n],cb:vec![0.0;n],za:vec![C::default();n],zb:vec![C::default();n],zf:vec![C::default();n]} }
    pub fn workspace_bytes(&self)->usize { (self.f.capacity()+self.za.capacity()+self.zb.capacity()+self.zf.capacity())*16+(self.q.capacity()+self.ca.capacity()+self.cb.capacity())*8 }
    pub fn invalidate(&mut self) { self.valid=false; }
    pub(crate) fn prepare(&mut self,r:f64,y:&[f64],a:&[f64],b:&[f64])->CoreResult<()> {
        self.valid=false;
        if self.n<=TARGET_A || y.len()!=2*(4*self.n+1) || a.len()!=self.n || b.len()!=self.n {
            return Err(CoreError::Dimension("frozen HH Jacobian shape".into()));
        }
        for j in 0..self.n {
            let f=get(y,j); let ar=get(y,2*self.n+j)/f; let br=get(y,3*self.n+j)/f;
            self.f[j]=f; self.q[j]=K*K+2.0/r-(j*(j+1)) as f64/(r*r);
            self.ca[j]=Q_SCALE*a[j]; self.cb[j]=Q_SCALE*b[j];
            self.za[j]=br/f; self.zb[j]=ar/f; self.zf[j]=-2.0*ar*br/f;
        }
        if self.f.iter().chain(&self.za).chain(&self.zb).chain(&self.zf).any(|z|!z.re.is_finite() || !z.im.is_finite())
            || self.q.iter().chain(&self.ca).chain(&self.cb).any(|x|!x.is_finite()) {
            return Err(CoreError::NonFinite("frozen HH Jacobian coefficients".into()));
        }
        self.valid=true; Ok(())
    }
    pub fn min_denominator(&self,s:f64)->CoreResult<f64> {
        if !self.valid || !s.is_finite() {return Err(CoreError::InvalidInput("invalid frozen state/shift".into()));}
        let mut minimum=f64::INFINITY;
        for &q in &self.q { let d=1.0+s*s*q;
            if !d.is_finite() || d<=0.0 { return Err(CoreError::LinearSolve("nonpositive shifted oscillator denominator".into())); }
            minimum=minimum.min(d);
        } Ok(minimum)
    }
    pub fn apply(&self,v:&[f64],out:&mut[f64])->CoreResult<()> {
        let n=self.n;
        if !self.valid || v.len()!=2*(4*n+1) || out.len()!=v.len() {return Err(CoreError::Dimension("frozen JVP shape/state".into()));}
        finite(v)?;
        let fa=self.f[TARGET_A]; let fb=self.f[TARGET_B];
        let va=get(v,TARGET_A); let vb=get(v,TARGET_B); let mut dz=C::default();
        for j in 0..n {
            let df=get(v,j);
            put(out,j,-get(v,n+j)); put(out,n+j,df*self.q[j]);
            put(out,2*n+j,(va*self.f[j]+fa*df)*self.ca[j]);
            put(out,3*n+j,(vb*self.f[j]+fb*df)*self.cb[j]);
            dz+=self.za[j]*get(v,2*n+j)+self.zb[j]*get(v,3*n+j)+self.zf[j]*df;
        }
        put(out,4*n,dz); finite(out)
    }
    /// Returns an observed normwise backward residual. It is not an interval enclosure.
    /// Caller supplies scratch so all eight stage solves allocate zero heap storage.
    pub fn solve(&self,s:f64,rhs:&[f64],out:&mut[f64],scratch:&mut[f64])->CoreResult<f64> {
        let n=self.n;
        if rhs.len()!=2*(4*n+1) || out.len()!=rhs.len() || scratch.len()!=rhs.len() {return Err(CoreError::Dimension("shifted HH solve shape".into()));}
        finite(rhs)?; self.min_denominator(s)?;
        for j in 0..n {
            let bf=get(rhs,j); let bg=get(rhs,n+j);
            let xf=(bf-s*bg)/(1.0+s*s*self.q[j]);
            put(out,j,xf); put(out,n+j,bg+s*self.q[j]*xf);
        }
        let fa=self.f[TARGET_A]; let fb=self.f[TARGET_B];
        let xa=get(out,TARGET_A); let xb=get(out,TARGET_B); let mut dz=C::default();
        for j in 0..n {
            let df=get(out,j);
            let a=get(rhs,2*n+j)+s*((xa*self.f[j]+fa*df)*self.ca[j]);
            let b=get(rhs,3*n+j)+s*((xb*self.f[j]+fb*df)*self.cb[j]);
            put(out,2*n+j,a); put(out,3*n+j,b);
            dz+=self.za[j]*a+self.zb[j]*b+self.zf[j]*df;
        }
        put(out,4*n,get(rhs,4*n)+s*dz); finite(out)?;
        self.apply(out,scratch)?;
        let mut numerator=0.0_f64; let mut denom=0.0_f64;
        for ((&x,&jx),&b) in out.iter().zip(scratch.iter()).zip(rhs) {
            numerator=numerator.max((x-s*jx-b).abs());
            denom=denom.max(x.abs()+s.abs()*jx.abs()+b.abs());
        }
        if !denom.is_finite() || !numerator.is_finite() {
            return Err(CoreError::NonFinite("shifted residual norm overflow".into()));
        }
        let residual=if denom==0.0 {0.0} else {numerator/denom};
        if !residual.is_finite() || residual>512.0*f64::EPSILON {return Err(CoreError::LinearSolve(format!("HH shifted residual {residual:e}")));}
        Ok(residual)
    }
}
