//! Independent binary64 reference for the finite original HH second Born term.
//!
//! Fixed atomic B=27, T=65, k=7/10, m=0, targets ell=21,20.  All internal
//! j=0..L are retained.  H/H(B) and d_r H/H(B) at T are external Arb-derived
//! seeds; the angular quadrature, complex arithmetic, and backward RK4 path
//! below are independent.  This is a diagnostic, not interval certification.
use std::env;
use std::fs;
use std::ops::{Add, Div, Mul, Neg, Sub};
use std::time::Instant;

const B: f64 = 27.0;
const T: f64 = 65.0;
const K: f64 = 0.7;
const SHIFT: f64 = 0.7;
const TARGET_A: usize = 21;
const TARGET_B: usize = 20;
const ANGULAR_NODES: usize = 96;

#[derive(Clone, Copy, Debug, Default)]
struct C { re: f64, im: f64 }
impl C {
    fn new(re: f64, im: f64) -> Self { Self { re, im } }
    fn real(re: f64) -> Self { Self { re, im: 0.0 } }
    fn abs(self) -> f64 { self.re.hypot(self.im) }
    fn finite(self) -> bool { self.re.is_finite() && self.im.is_finite() }
}
impl Add for C { type Output = Self;
    fn add(self, rhs: Self) -> Self { Self::new(self.re+rhs.re,self.im+rhs.im) } }
impl Sub for C { type Output = Self;
    fn sub(self, rhs: Self) -> Self { Self::new(self.re-rhs.re,self.im-rhs.im) } }
impl Neg for C { type Output = Self;
    fn neg(self) -> Self { Self::new(-self.re,-self.im) } }
impl Mul for C { type Output = Self;
    fn mul(self, rhs: Self) -> Self {
        Self::new(self.re*rhs.re-self.im*rhs.im,self.re*rhs.im+self.im*rhs.re)
    }
}
impl Mul<f64> for C { type Output = Self;
    fn mul(self, rhs: f64) -> Self { Self::new(self.re*rhs,self.im*rhs) } }
impl Div for C { type Output = Self;
    fn div(self, rhs: Self) -> Self {
        let norm = rhs.re*rhs.re+rhs.im*rhs.im;
        Self::new((self.re*rhs.re+self.im*rhs.im)/norm,
                  (self.im*rhs.re-self.re*rhs.im)/norm)
    }
}

fn legendre_pair(n: usize, x: f64) -> (f64,f64) {
    if n==0 { return (1.0,0.0); }
    let (mut pm,mut pp)=(1.0,x);
    for j in 2..=n {
        let next=((2*j-1) as f64*x*pp-(j-1) as f64*pm)/j as f64;
        pm=pp; pp=next;
    }
    (pp,pm)
}

fn gauss_legendre(n: usize) -> (Vec<f64>,Vec<f64>) {
    assert!(n>=2);
    let (mut nodes,mut weights)=(vec![0.0;n],vec![0.0;n]);
    for i in 0..n.div_ceil(2) {
        let mut x=(std::f64::consts::PI*(i as f64+0.75)/(n as f64+0.5)).cos();
        for _ in 0..40 {
            let (pn,pnm)=legendre_pair(n,x);
            let derivative=n as f64*(x*pn-pnm)/(x*x-1.0);
            let next=x-pn/derivative;
            if next==x || (next-x).abs()<2.0*f64::EPSILON { x=next; break; }
            x=next;
        }
        let (pn,pnm)=legendre_pair(n,x);
        let derivative=n as f64*(x*pn-pnm)/(x*x-1.0);
        let weight=2.0/((1.0-x*x)*derivative*derivative);
        nodes[i]=-x; nodes[n-1-i]=x;
        weights[i]=weight; weights[n-1-i]=weight;
    }
    (nodes,weights)
}

struct Angular {
    nodes: Vec<f64>, weights: Vec<f64>, basis: Vec<Vec<f64>>, channels: usize,
}
impl Angular {
    fn new(lmax: usize, q: usize) -> Self {
        let (nodes,weights)=gauss_legendre(q);
        let mut basis=Vec::with_capacity(q);
        for &mu in &nodes {
            let mut p=vec![1.0;lmax+1];
            if lmax>0 { p[1]=mu; }
            for l in 2..=lmax {
                p[l]=((2*l-1) as f64*mu*p[l-1]-(l-1) as f64*p[l-2])/l as f64;
            }
            for (l,value) in p.iter_mut().enumerate() { *value*=((2*l+1) as f64/2.0).sqrt(); }
            basis.push(p);
        }
        Self { nodes,weights,basis,channels:lmax+1 }
    }
    fn element(&self, r:f64, left:usize, right:usize) -> f64 {
        let mut value=0.0;
        for q in 0..self.nodes.len() {
            let d=(r*r+SHIFT*SHIFT-2.0*r*SHIFT*self.nodes[q]).sqrt();
            let potential=2.0*(1.0+1.0/d)*(-2.0*d).exp();
            value+=self.weights[q]*self.basis[q][left]*self.basis[q][right]*potential;
        }
        value
    }
    fn target_rows(&self, r:f64) -> (Vec<f64>,Vec<f64>) {
        let (mut a,mut b)=(vec![0.0;self.channels],vec![0.0;self.channels]);
        for q in 0..self.nodes.len() {
            let d=(r*r+SHIFT*SHIFT-2.0*r*SHIFT*self.nodes[q]).sqrt();
            let potential=2.0*(1.0+1.0/d)*(-2.0*d).exp()*self.weights[q];
            let left=potential*self.basis[q][TARGET_A];
            let right=potential*self.basis[q][TARGET_B];
            for j in 0..self.channels {
                a[j]+=left*self.basis[q][j];
                b[j]+=right*self.basis[q][j];
            }
        }
        (a,b)
    }
}

fn rhs(r:f64, y:&[C], out:&mut [C], angular:&Angular) {
    let n=angular.channels;
    let (va,vb)=angular.target_rows(r);
    let (fa,fb)=(y[TARGET_A],y[TARGET_B]);
    let mut second=C::default();
    for j in 0..n {
        let q=K*K+2.0/r-(j*(j+1)) as f64/(r*r);
        out[j]=y[n+j];
        out[n+j]=y[j]*(-q);
        out[2*n+j]=fa*y[j]*(-va[j]);
        out[3*n+j]=fb*y[j]*(-vb[j]);
        // The complex bilinear product is intentional; no conjugation.
        second=second+y[2*n+j]*y[3*n+j]/(y[j]*y[j]);
    }
    out[4*n]=-second;
}

struct Rk4Workspace { k1:Vec<C>,k2:Vec<C>,k3:Vec<C>,k4:Vec<C>,temp:Vec<C> }
impl Rk4Workspace {
    fn new(size:usize) -> Self {
        Self { k1:vec![C::default();size],k2:vec![C::default();size],
               k3:vec![C::default();size],k4:vec![C::default();size],temp:vec![C::default();size] }
    }
    fn step<F:FnMut(f64,&[C],&mut[C])>(&mut self,r:f64,h:f64,y:&mut[C],mut f:F) {
        f(r,y,&mut self.k1);
        for i in 0..y.len() { self.temp[i]=y[i]+self.k1[i]*(h/2.0); }
        f(r+h/2.0,&self.temp,&mut self.k2);
        for i in 0..y.len() { self.temp[i]=y[i]+self.k2[i]*(h/2.0); }
        f(r+h/2.0,&self.temp,&mut self.k3);
        for i in 0..y.len() { self.temp[i]=y[i]+self.k3[i]*h; }
        f(r+h,&self.temp,&mut self.k4);
        for i in 0..y.len() {
            y[i]=y[i]+(self.k1[i]+self.k2[i]*2.0+self.k3[i]*2.0+self.k4[i])*(h/6.0);
        }
    }
}

fn manufactured_constant_potential(steps:usize) -> (f64,f64) {
    let (v,interval)=(0.15,1.25);
    let mut y=vec![C::default();3];
    let mut rk=Rk4Workspace::new(3);
    let h=-interval/steps as f64;
    for step in 0..steps {
        let r=interval+step as f64*h;
        rk.step(r,h,&mut y,|_,state,out| {
            out[0]=C::real(-v); out[1]=C::real(-v); out[2]=-(state[0]*state[1]);
        });
    }
    (y[2].re,v*v*interval*interval*interval/3.0)
}

fn read_seed(path:&str) -> Result<Vec<(C,C)>,String> {
    let input=fs::read_to_string(path).map_err(|e|e.to_string())?;
    let mut result=Vec::new();
    for line in input.lines().filter(|line|!line.trim().is_empty() && !line.starts_with('#')) {
        let fields:Vec<&str>=line.split_whitespace().collect();
        if fields.len()!=5 { return Err("seed requires ell, ReF, ImF, ReG, ImG".into()); }
        let ell=fields[0].parse::<usize>().map_err(|e|e.to_string())?;
        if ell!=result.len() || ell>64 { return Err("seed channels must be consecutive 0..L<=64".into()); }
        let values:Result<Vec<f64>,_>=fields[1..].iter().map(|value|value.parse::<f64>()).collect();
        let values=values.map_err(|e|e.to_string())?;
        if values.iter().any(|value|!value.is_finite()) { return Err("nonfinite seed".into()); }
        let pair=(C::new(values[0],values[1]),C::new(values[2],values[3]));
        if pair.0.abs()==0.0 { return Err("zero seed denominator".into()); }
        result.push(pair);
    }
    if result.len()<=TARGET_A { return Err("the seed must include target ell21".into()); }
    Ok(result)
}

fn run(steps:usize, seed_path:&str) -> Result<(),String> {
    if steps==0 || steps>1_000_000 { return Err("steps must lie in 1..1000000".into()); }
    let seed=read_seed(seed_path)?;
    let n=seed.len();
    let angular=Angular::new(n-1,ANGULAR_NODES);
    let mut y=vec![C::default();4*n+1];
    for (j,(f,g)) in seed.into_iter().enumerate() { y[j]=f;y[n+j]=g; }
    let mut rk=Rk4Workspace::new(y.len());
    let h=(B-T)/steps as f64;
    let clock=Instant::now();
    for step in 0..steps {
        // Compute each coordinate from its integer index; avoid accumulated r drift.
        let r=T+(B-T)*(step as f64/steps as f64);
        rk.step(r,h,&mut y,|r,state,out|rhs(r,state,out,&angular));
        if y.iter().any(|value|!value.finite()) { return Err(format!("nonfinite state at step {step}")); }
    }
    let elapsed=clock.elapsed().as_secs_f64();
    let d2=y[4*n];
    let mut drift=0.0_f64;
    for f in &y[..n] { drift=drift.max((*f-C::real(1.0)).abs()); }
    let (manufactured,expected)=manufactured_constant_potential(16);
    let manufactured_error=(manufactured-expected).abs();
    let d1a=y[2*n+TARGET_B];
    let d1b=y[3*n+TARGET_A];
    println!(concat!("{{\n",
        "  \"status\": \"COMPLETED_BINARY64_REFERENCE_NOT_CERTIFICATE\",\n",
        "  \"L\": {}, \"m\": 0, \"target\": [21,20],\n",
        "  \"B\": 27, \"T\": 65, \"k\": \"7/10\",\n",
        "  \"steps\": {}, \"step_size\": {:.17e}, \"angular_nodes\": 96,\n",
        "  \"d2\": {{\"real\": {:.17e}, \"imag\": {:.17e}}},\n",
        "  \"d1_q21_20\": {{\"real\": {:.17e}, \"imag\": {:.17e}}},\n",
        "  \"d1_q20_21\": {{\"real\": {:.17e}, \"imag\": {:.17e}}},\n",
        "  \"normalization_drift_max_abs_F_B_minus_1\": {:.17e},\n",
        "  \"manufactured_d2\": {:.17e}, \"manufactured_expected\": {:.17e},\n",
        "  \"manufactured_absolute_error\": {:.17e},\n",
        "  \"integration_elapsed_seconds\": {:.9}, \"HH_R10\": \"OFF\"\n",
        "}}"),n-1,steps,h,d2.re,d2.im,d1a.re,d1a.im,d1b.re,d1b.im,drift,
        manufactured,expected,manufactured_error,elapsed);
    Ok(())
}

fn main() {
    let args:Vec<String>=env::args().collect();
    if args.len()!=3 { eprintln!("usage: phys68_rust_reference STEPS SEED_TEXT"); std::process::exit(2); }
    let steps=match args[1].parse::<usize>() { Ok(n)=>n,Err(e)=>{eprintln!("{e}");std::process::exit(2)} };
    if let Err(error)=run(steps,&args[2]) { eprintln!("{error}");std::process::exit(1); }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn complex_bilinear_product_and_division() {
        let (a,b)=(C::new(2.0,3.0),C::new(5.0,-7.0));
        let product=a*b;
        assert_eq!(product.re,31.0); assert_eq!(product.im,1.0);
        assert!(((product/b)-a).abs()<1e-15);
        assert_eq!((C::new(0.0,1.0)*C::new(0.0,1.0)).re,-1.0);
    }
    #[test]
    fn gaussian_moments_and_normalized_basis() {
        let angular=Angular::new(28,96);
        for degree in [0_i32,2,4,20,56,100,190] {
            let sum:f64=angular.nodes.iter().zip(&angular.weights).map(|(x,w)|w*x.powi(degree)).sum();
            assert!((sum-2.0/(degree as f64+1.0)).abs()<2e-14);
        }
        for left in [0,20,21,28] {
            for right in [0,20,21,28] {
                let sum:f64=(0..96).map(|q|angular.weights[q]*angular.basis[q][left]*angular.basis[q][right]).sum();
                let expected=if left==right {1.0} else {0.0};
                assert!((sum-expected).abs()<1e-13);
            }
        }
    }
    #[test]
    fn original_potential_matches_closed_form_v00() {
        let angular=Angular::new(28,96);
        for r in [27.0,39.0] {
            let low=r-SHIFT;let high=r+SHIFT;
            let exact=((low/2.0+0.75)*(-2.0*low).exp()-(high/2.0+0.75)*(-2.0*high).exp())/(r*SHIFT);
            assert!((angular.element(r,0,0)/exact-1.0).abs()<2e-13);
        }
    }
    #[test]
    fn backward_rk4_manufactured_second_born_sign_and_factor() {
        for steps in [1,2,16] {
            let (value,expected)=manufactured_constant_potential(steps);
            assert!(value>0.0);
            assert!((value-expected).abs()<3e-17);
        }
    }
    #[test]
    fn free_outgoing_ode_refines_at_fourth_order() {
        fn solve(steps:usize)->C {
            let mut state=vec![C::real(1.0),C::new(0.0,K)];
            let mut rk=Rk4Workspace::new(2);
            let h=1.0/steps as f64;
            for step in 0..steps { rk.step(step as f64*h,h,&mut state,|_,y,out| {
                out[0]=y[1];out[1]=y[0]*(-K*K);
            }); }
            state[0]
        }
        let exact=C::new(K.cos(),K.sin());
        let coarse=(solve(8)-exact).abs();let fine=(solve(16)-exact).abs();
        assert!(coarse/fine>15.0 && coarse/fine<17.0);
    }
}
