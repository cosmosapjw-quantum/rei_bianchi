//! Deterministic independent Rust sweep of positive exponential cell cuts.
//! Research-only reference, no production Rust source mutation.
//! Compiled with Rust >= 1.75; no external crates or atomic data assumptions.
use std::env;
use std::time::Instant;
use std::thread;
#[derive(Default, Clone, Copy)]
struct Outcome {
    count: u64,
    failures: u64,
    max_n_rel: f64,
    max_u_rel: f64,
    max_roundtrip: f64,
    checksum: f64,
}
fn mean(t: f64) -> f64 {
    if t < 0.0 { return 1.0-mean(-t); }
    if t==0.0 {return 0.5;}
    if t<0.01 {return 0.5+t/12.0-t.powi(3)/720.0+t.powi(5)/30240.0-t.powi(7)/1209600.0;}
    if t>700.0 {return 1.0-1.0/t;}
    1.0-1.0/t+1.0/t.exp_m1()
}
fn tail(t: f64,r:f64)->f64 {
    if r<=0.0{return 1.0;}if r>=1.0{return 0.0;}
    if t==0.0{return 1.0-r;}
    if t>0.0 {return -(-t*(1.0-r)).exp_m1() / -(-t).exp_m1();}
    (t*r).exp() * (-(t*(1.0-r)).exp_m1()) / -(t).exp_m1()
}
fn head(t:f64,r:f64)->f64 {
    if r<=0.0{return 0.0;}if r>=1.0{return 1.0;}
    if t==0.0{return r;}
    if t>0.0 {
        return (-t*(1.0-r)).exp() * (-(-t*r).exp_m1()) / -(-t).exp_m1();
    }
    -(t*r).exp_m1()/-(t).exp_m1()
}
fn split(n:f64,lo:f64,hi:f64,t:f64,cut:f64)->(f64,f64,f64,f64) {
    let u=n*(lo+(hi-lo)*mean(t));
    if cut<=lo{return (n,0.0,u,0.0);}
    if cut>hi{return (0.0,n,0.0,u);}
    let r=(cut-lo)/(hi-lo);
    let ta=tail(t,r);let he=head(t,r);
    let (na,np,ua,up)=if ta<=he {
        let na=n*ta;
        let np=n-na;
        let ua=if na>0.0{na*(cut+(hi-cut)*mean(t*(1.0-r)))}else{0.0};
        (na,np,ua,u-ua)
    } else {
        let np=n*he;
        let na=n-np;
        let up=if np>0.0{np*(lo+(cut-lo)*mean(t*r))}else{0.0};
        (na,np,u-up,up)
    };
    (na,np,ua,up)
}
fn uniform(i:u64,lane:u64)->f64 {
    let mut x=i.wrapping_mul(0x9e3779b97f4a7c15)
       .wrapping_add(lane.wrapping_mul(0xbf58476d1ce4e5b9));
    x=(x^(x>>30)).wrapping_mul(0xbf58476d1ce4e5b9);
    x=(x^(x>>27)).wrapping_mul(0x94d049bb133111eb);
    ((x^(x>>31))>>11) as f64 / 9007199254740992.0
}
fn work(lo_i:u64,hi_i:u64)->Outcome {
    let mut out=Outcome::default();
    for i in lo_i..hi_i {
        let lo=0.1+uniform(i,1)*20.0;
        let hi=lo+0.1+uniform(i,2)*60.0;
        let t=(uniform(i,3)*2.0-1.0)*30.0;
        let n=0.0001+uniform(i,4)*5.0;
        let r=uniform(i,5)*1.1-0.05;
        let cut=lo+(hi-lo)*r;
        let (na,np,ua,up)=split(n,lo,hi,t,cut);
        let u=n*(lo+(hi-lo)*mean(t));
        let en=((na+np)-n).abs()/n;
        let eu=((ua+up)-u).abs()/u.max(1e-100);
        let a_min=if na>0.0 {na*lo.max(cut)} else {0.0};
        let a_max=na*hi;
        let p_min=np*lo;
        let p_max=np*hi.min(cut);
        let good=na>=0.0&&np>=0.0&&ua>=0.0&&up>=0.0
             &&en<=2e-13&&eu<=2e-13
             &&ua+1e-12*u.max(1.0)>=a_min
             &&ua<=a_max+1e-12*u.max(1.0)
             &&up+1e-12*u.max(1.0)>=p_min
             &&up<=p_max+1e-12*u.max(1.0);
        if !good {
            out.failures+=1;
            if out.failures<=5 {
                eprintln!("BAD i={} t={} r={} lo={} hi={} cut={} n={} u={} an={} pn={} au={} pu={} amin={} amax={} pmin={} pmax={} en={} eu={}",i,t,r,lo,hi,cut,n,u,na,np,ua,up,a_min,a_max,p_min,p_max,en,eu);
            }
        }
        // Reverse geometry to an identical reference cutoff: source-free
        // immutable parent must return exactly the original projection.
        let resplit=split(n,lo,hi,t,cut);
        let round=(resplit.0-na).abs()+(resplit.1-np).abs()
                 +(resplit.2-ua).abs()+(resplit.3-up).abs();
        out.max_roundtrip=out.max_roundtrip.max(round);
        out.max_n_rel=out.max_n_rel.max(en);
        out.max_u_rel=out.max_u_rel.max(eu);
        out.checksum += (na*0.1+ua*0.01+n*0.001).sin();
        out.count+=1;
    }
    out
}
fn main(){
    let args:Vec<String>=env::args().collect();
    let cases=args.get(1).and_then(|v|v.parse::<u64>().ok()).unwrap_or(1_000_000);
    let threads=args.get(2).and_then(|v|v.parse::<usize>().ok()).unwrap_or(1).max(1);
    let wall=Instant::now();
    let mut handles=Vec::new();
    for t in 0..threads {
        let start=(cases as u128*t as u128/threads as u128) as u64;
        let end=(cases as u128*(t+1) as u128/threads as u128) as u64;
        handles.push(thread::spawn(move||work(start,end)));
    }
    let mut out=Outcome::default();
    for h in handles {
        let r=h.join().expect("worker panicked");
        out.count+=r.count;
        out.failures+=r.failures;
        out.max_n_rel=out.max_n_rel.max(r.max_n_rel);
        out.max_u_rel=out.max_u_rel.max(r.max_u_rel);
        out.max_roundtrip=out.max_roundtrip.max(r.max_roundtrip);
        out.checksum+=r.checksum;
    }
    println!("{{\"schema\":\"rei.signed_cut.ncp_sweep.v1\",\"cases\":{},\"threads\":{},\"failures\":{},\"max_n_rel\":{:.17e},\"max_u_rel\":{:.17e},\"max_roundtrip_abs\":{:.17e},\"checksum\":{:.17e},\"wall_s\":{:.6}}}",
      out.count,threads,out.failures,out.max_n_rel,out.max_u_rel,out.max_roundtrip,out.checksum,wall.elapsed().as_secs_f64());
    if out.failures!=0 || out.count!=cases {std::process::exit(1);}
}
