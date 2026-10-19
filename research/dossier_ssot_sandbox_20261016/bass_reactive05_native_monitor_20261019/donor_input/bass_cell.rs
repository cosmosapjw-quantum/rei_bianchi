//! BASS-INTAKE-01: isolated Hermite-cell geometry/threshold prototype.
//! AUTHORED_UNCOMPILED: current sandbox failed before any native execution.
//! This is NOT installed into source_age, JointCxSplit, or a production solver.
//! Same real-arithmetic Hermite construction as PR159, not bit-equivalent code.
//! Inputs: x=ln(a/a_ref), b dimensionless, H,s,dH/dx in s^-1; photon energy eV.
//! The original BASS provider owns file identity, case selection and clock origin.
//! Whole-cell expansion enables this limited monotone-root path. Contraction
//! returns UnsupportedCell; it is not a claim that contracting models are invalid.
//! Ordinary f64 and a safety cushion are NOT a certified interval calculation.
#![forbid(unsafe_code)]

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error { NonFinite, Domain, UnsupportedCell, RootUnresolved }

#[derive(Clone, Copy, Debug)]
pub struct Node {
    pub x: f64,
    pub b: f64,
    pub h_per_s: f64,
    pub s_per_s: f64,
    pub dh_dln_a_per_s: f64,
}

#[derive(Clone, Copy, Debug)]
struct Cubic([f64; 4]);
impl Cubic {
    fn hermite(y0: f64, y1: f64, d0: f64, d1: f64, width: f64) -> Result<Self, Error> {
        let c = [y0, width * d0, 3.0 * (y1-y0) - width * (2.0*d0+d1),
                 2.0 * (y0-y1) + width * (d0+d1)];
        if !c.iter().all(|x| x.is_finite()) { return Err(Error::NonFinite); }
        Ok(Self(c))
    }
    fn value(self, u: f64) -> f64 {
        ((self.0[3]*u+self.0[2])*u+self.0[1])*u+self.0[0]
    }
    fn dx(self, u: f64, width: f64) -> f64 {
        ((3.0*self.0[3]*u+2.0*self.0[2])*u+self.0[1])/width
    }
}

#[derive(Clone, Copy, Debug)]
pub struct Cell { x0: f64, x1: f64, width: f64, b: Cubic, log_h: Cubic }

#[derive(Clone, Copy, Debug)]
pub struct Geometry {
    pub scale_factors: [f64; 3],
    pub hubble_per_s: [f64; 3],
    pub mean_h_per_s: f64,
    pub signed_s_per_s: f64,
    pub signed_s_over_h: f64,
    pub sigma_magnitude: f64,
    pub b: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct ExpansionCheck {
    pub min_bprime: f64,
    pub max_bprime: f64,
    pub raw_margin: f64,
    pub roundoff_cushion: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct Birth {
    pub x: f64,
    pub b: f64,
    pub energy_ev: f64,
    pub mu: f64,
}
impl Birth {
    fn validate(self) -> Result<(), Error> {
        if ![self.x,self.b,self.energy_ev,self.mu].iter().all(|x| x.is_finite()) {
            return Err(Error::NonFinite);
        }
        if self.energy_ev <= 0.0 || self.mu.abs()>1.0 { return Err(Error::Domain); }
        Ok(())
    }
}

/// A numerical f64 result, not a directed-rounding root enclosure.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Crossing { None, Point(f64), Bracket { left_x: f64, right_x: f64 } }

impl Cell {
    pub fn new(left: Node, right: Node) -> Result<Self, Error> {
        for n in [left,right] {
            if ![n.x,n.b,n.h_per_s,n.s_per_s,n.dh_dln_a_per_s].iter().all(|v| v.is_finite()) {
                return Err(Error::NonFinite);
            }
            if n.h_per_s <= 0.0 { return Err(Error::Domain); }
        }
        let w=right.x-left.x;
        if !w.is_finite() || w<=0.0 { return Err(Error::Domain); }
        Ok(Self { x0:left.x,x1:right.x,width:w,
            b:Cubic::hermite(left.b,right.b,left.s_per_s/left.h_per_s,right.s_per_s/right.h_per_s,w)?,
            log_h:Cubic::hermite(left.h_per_s.ln(),right.h_per_s.ln(),
                left.dh_dln_a_per_s/left.h_per_s,right.dh_dln_a_per_s/right.h_per_s,w)? })
    }
    fn u(self, x: f64) -> Result<f64, Error> {
        if !x.is_finite() { return Err(Error::NonFinite); }
        if x<self.x0 || x>self.x1 { return Err(Error::Domain); }
        Ok((x-self.x0)/self.width)
    }
    fn values(self, x: f64) -> Result<(f64,f64,f64), Error> {
        let u=self.u(x)?;
        let b=self.b.value(u); let r=self.b.dx(u,self.width); let h=self.log_h.value(u).exp();
        if ![b,r,h].iter().all(|v| v.is_finite()) || h<=0.0 { return Err(Error::NonFinite); }
        Ok((b,r,h))
    }
    pub fn geometry(self, a_ref: f64, x: f64) -> Result<Geometry, Error> {
        if !a_ref.is_finite() || a_ref<=0.0 { return Err(Error::Domain); }
        let (b,r,h)=self.values(x)?;
        let aperp=(a_ref.ln()+x-b).exp(); let apar=(a_ref.ln()+x+2.0*b).exp();
        let hp=h*(1.0-r); let hz=h*(1.0+2.0*r); let s=h*r;
        let sigma=3.0_f64.sqrt()*r.abs();
        if ![aperp,apar,hp,hz,s,sigma].iter().all(|v| v.is_finite()) || aperp<=0.0 || apar<=0.0 {
            return Err(Error::NonFinite);
        }
        Ok(Geometry {scale_factors:[aperp,aperp,apar],hubble_per_s:[hp,hp,hz],
            mean_h_per_s:h,signed_s_per_s:s,signed_s_over_h:r,sigma_magnitude:sigma,b})
    }
    /// Test extrema of the complete quadratic b'(x), not just endpoint slopes.
    pub fn expansion(self) -> Result<ExpansionCheck, Error> {
        let q0=self.b.dx(0.0,self.width); let q1=self.b.dx(1.0,self.width);
        let (mut lo,mut hi)=(q0.min(q1),q0.max(q1));
        if self.b.0[3]!=0.0 {
            let uv=-self.b.0[2]/(3.0*self.b.0[3]);
            if uv>0.0 && uv<1.0 {
                let q=self.b.dx(uv,self.width);lo=lo.min(q);hi=hi.max(q);
            }
        }
        let coefficient_scale=(self.b.0[1].abs()+2.0*self.b.0[2].abs()+3.0*self.b.0[3].abs())/self.width;
        let cushion=128.0*f64::EPSILON*(1.0+coefficient_scale);
        let margin=(1.0-hi).min(1.0+2.0*lo);
        if ![lo,hi,cushion,margin].iter().all(|v| v.is_finite()) { return Err(Error::NonFinite); }
        if margin<=cushion { return Err(Error::UnsupportedCell); }
        Ok(ExpansionCheck {min_bprime:lo,max_bprime:hi,raw_margin:margin,roundoff_cushion:cushion})
    }
    /// Source cohort owns birth b and direction; caller must bind them to donor.
    pub fn log_energy_ev(self, birth: Birth, x: f64) -> Result<f64, Error> {
        birth.validate()?;
        if x<birth.x { return Err(Error::Domain); }
        let (b,_,_)=self.values(x)?;let db=b-birth.b;let q=birth.mu*birth.mu;
        let log_sum=if q==0.0 {2.0*db} else if q==1.0 {-4.0*db} else {
            let a=(1.0-q).ln()+2.0*db;let z=q.ln()-4.0*db;let m=a.max(z);
            m+((a-m).exp()+(z-m).exp()).ln()
        };
        let out=birth.energy_ev.ln()-(x-birth.x)+0.5*log_sum;
        if !out.is_finite() { return Err(Error::NonFinite); }
        Ok(out)
    }
    /// Reuse the donor's positive log-H/GL8 clock formula within a single cell.
    /// This is a clock approximation, not an error-certified adaptive quadrature.
    /// Absolute clock origin and accumulation across cells remain donor-owned.
    pub fn delta_proper_s(self, from_x: f64, to_x: f64) -> Result<f64, Error> {
        self.u(from_x)?;self.u(to_x)?;
        if to_x<from_x {return Err(Error::Domain);}
        if to_x==from_x {return Ok(0.0);}
        let pairs=[(0.1834346424956498,0.3626837833783620),
                   (0.5255324099163290,0.3137066458778873),
                   (0.7966664774136267,0.2223810344533745),
                   (0.9602898564975363,0.1012285362903763)];
        let half=(to_x-from_x)*0.5;let mid=from_x+half;let mut out=0.0;
        for (q,w) in pairs {
            let hm=self.values(mid-half*q)?.2;let hp=self.values(mid+half*q)?.2;
            out+=w*half*(1.0/hm+1.0/hp);
        }
        if !out.is_finite() || out<=0.0 {return Err(Error::NonFinite);}
        Ok(out)
    }
    pub fn threshold_crossing(self, birth: Birth, edge_ev: f64, x_tolerance: f64) -> Result<Crossing, Error> {
        birth.validate()?;
        if !edge_ev.is_finite() || edge_ev<=0.0 || !x_tolerance.is_finite() || x_tolerance<=0.0 {
            return Err(Error::Domain);
        }
        // Never conclude 'no crossing' from endpoints of an unqualified cell.
        self.expansion()?;
        let mut lo=self.x0.max(birth.x);let mut hi=self.x1;
        if lo>=hi {return Err(Error::Domain);}
        let edge_log=edge_ev.ln();
        let fl=self.log_energy_ev(birth,lo)?-edge_log;
        let fh=self.log_energy_ev(birth,hi)?-edge_log;
        if fl==0.0 {return Ok(Crossing::Point(lo));}
        if fh==0.0 {return Ok(Crossing::Point(hi));}
        if fl<0.0 || fh>0.0 {return Ok(Crossing::None);}
        for _ in 0..96 {
            if hi-lo<=x_tolerance {return Ok(Crossing::Bracket {left_x:lo,right_x:hi});}
            let mid=lo+0.5*(hi-lo);
            if mid==lo || mid==hi {return Err(Error::RootUnresolved);}
            let fm=self.log_energy_ev(birth,mid)?-edge_log;
            if fm==0.0 {return Ok(Crossing::Point(mid));}
            if fm>0.0 {lo=mid;} else {hi=mid;}
        }
        Err(Error::RootUnresolved)
    }
}
