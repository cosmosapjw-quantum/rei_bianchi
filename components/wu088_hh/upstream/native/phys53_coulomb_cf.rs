//! Standalone Rust 1.99-compatible PHYS53 high-ell central Coulomb CF.
//! This is not the physical noncentral screened scattering DtN.
//! No external crates. Compile: rustc -O native/phys53_coulomb_cf.rs -o phys53_cf
//! Example: ./phys53_cf 21 512 27 1152 24 > high_l_r27.csv
//! No NCP run or Rust compilation is claimed by this source alone.
use std::env;
use std::thread;

#[derive(Clone,Copy,Debug,Default)]
struct C { re: f64, im: f64 }
impl C {
    fn new(re:f64,im:f64)->Self {Self{re,im}}
    fn add(self,b:Self)->Self {Self::new(self.re+b.re,self.im+b.im)}
    fn mul(self,b:Self)->Self {Self::new(self.re*b.re-self.im*b.im,self.re*b.im+self.im*b.re)}
    fn div(self,b:Self)->Self {
        let scale=b.re.abs().max(b.im.abs());
        assert!(scale.is_finite() && scale>0.0);
        let (ar,ai,br,bi)=(self.re/scale,self.im/scale,b.re/scale,b.im/scale);
        let den=br*br+bi*bi;
        Self::new((ar*br+ai*bi)/den,(ai*br-ar*bi)/den)
    }
    fn times(self,s:f64)->Self{ Self::new(self.re*s,self.im*s) }
}
fn coulomb_cf(l:usize,r:f64,depth:usize)->C{
    assert!(r.is_finite() && (20.0..=100.0).contains(&r));
    assert!(depth>=128 && depth<=8192 && l<=4096);
    let k=0.7_f64;
    let eta=-10.0/7.0;
    let rho=k*r;
    let a=C::new(l as f64+1.0,eta);
    let b=C::new(-(l as f64),eta);
    let mut tail=C::default();
    for n in (1..=depth).rev(){
        let x=(n-1) as f64;
        let numer=a.add(C::new(x,0.0)).mul(b.add(C::new(x,0.0)));
        let denom=C::new(2.0*(rho-eta),2.0*(n as f64)).add(tail);
        tail=numer.div(denom);
    }
    C::new(0.0,1.0-eta/rho).add(C::new(0.0,1.0).mul(tail).times(1.0/rho)).times(k)
}
fn scan(first:usize,last:usize,r:f64,depth:usize,workers:usize)->Vec<(usize,C)>{
    assert!(first<=last && workers>0 && workers<=64);
    let n=last-first+1;
    let slice=n.div_ceil(workers);
    let mut chunks=Vec::new();
    thread::scope(|scope|{
        let mut handles=Vec::new();
        for wi in 0..workers{
            let start=first+wi*slice;
            if start>last {break;}
            let end=(start+slice-1).min(last);
            handles.push(scope.spawn(move||{
                (start..=end).map(|l|(l,coulomb_cf(l,r,depth))).collect::<Vec<_>>()
            }));
        }
        for h in handles{chunks.extend(h.join().expect("worker failed"));}
    });
    chunks.sort_by_key(|x|x.0);
    chunks
}
fn main(){
    let v:Vec<String>=env::args().collect();
    if v.len()!=6{
        eprintln!("usage: phys53_cf FIRST_ELL LAST_ELL R_BOHR DEPTH THREADS");
        std::process::exit(2)
    }
    let l0:usize=v[1].parse().expect("first ell");
    let l1:usize=v[2].parse().expect("last ell");
    let r:f64=v[3].parse().expect("radius");
    let depth:usize=v[4].parse().expect("depth");
    let threads:usize=v[5].parse().expect("threads");
    println!("ell,r_Bohr,real_z,imag_f64_noncert");
    for (ell,z) in scan(l0,l1,r,depth,threads){
        println!("{ell},{r:.9},{:.17e},{:.17e}",z.re,z.im);
    }
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]
    fn ell21_original_reference(){
        let z=coulomb_cf(21,27.0,1024);
        assert!((z.re+0.18253880022977345).abs()<1e-12);
        assert!((z.im-0.12712470573077846).abs()<1e-12);
    }
    #[test]
    fn deterministic_parallel(){
        let a=scan(21,64,27.0,1024,1);
        let b=scan(21,64,27.0,1024,8);
        for ((li,zi),(lj,zj)) in a.iter().zip(b.iter()){
            assert_eq!(li,lj);
            assert_eq!(zi.re.to_bits(),zj.re.to_bits());
            assert_eq!(zi.im.to_bits(),zj.im.to_bits());
        }
    }
}