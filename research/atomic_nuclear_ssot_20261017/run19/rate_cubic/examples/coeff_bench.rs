mod common;
use common::HheCubic;
use rei_rate_cubic::{CubicRateGrid,Error,weighted_channels};
use rei_reference::{igm_rates::igm_rates,rate_table::{IgmRateTable,igm_flat}};
use std::{hint::black_box,time::Instant};

// A retained witness makes it possible to inspect exactly this safe Rust kernel
// in LLVM IR/assembly. It neither enables fast-math nor assumes a SIMD width.
#[inline(never)]
pub fn vectorization_witness(a:&[f64;16],b:&[f64;16],c:&[f64;16],d:&[f64;16],w:[f64;4])->[f64;16]{
    weighted_channels(a,b,c,d,w)
}
fn main()->Result<(),Box<dyn std::error::Error>>{
    let probe=std::env::args().any(|x|x=="--probe");let n=if probe{512}else{32768};let reps=if probe{1}else{5};
    let a=[1.0;16];black_box(vectorization_witness(black_box(&a),&a,&a,&a,black_box([-0.0625,0.5625,0.5625,-0.0625])));
    let start=Instant::now();let linear=IgmRateTable::build_default().unwrap();eprintln!("loglinear_build_seconds={:.9}",start.elapsed().as_secs_f64());
    let start=Instant::now();let cubic=HheCubic::new(32769)?;eprintln!("cubic_build_seconds={:.9}",start.elapsed().as_secs_f64());
    println!("pattern,n,workers,repeat,backend,ns_per_query,checksum");
    for pattern in ["ordered_logT","random_logT","local_10000K"] {
        let mut seed=0x13a7c0ffeed12345u64;
        let ts:Vec<_>=(0..n).map(|i|{
            let z=if pattern=="ordered_logT" {(i as f64+0.314)/(n as f64)}else{seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;(seed>>11)as f64/(1u64<<53)as f64};
            if pattern=="local_10000K"{10000.0*(0.98+0.04*z)}else{(1e6f64.ln()*z).exp()}
        }).collect();
        for workers in [1,2,4] {for repeat in 0..reps {for backend in ["direct","loglinear","cubic"] {
            // The same caller-owned array, worker counts, inputs, and coefficients.
            // Thread construction/join is included; table creation is excluded.
            let mut out=vec![[0.0;15];n];let start=Instant::now();
            CubicRateGrid::<16>::batch_into(black_box(&ts),&mut out,workers,|t| {
                let r=match backend {"direct"=>igm_rates(t).map_err(|_|Error::Invalid("direct"))?,
                    "loglinear"=>linear.rates(t).map_err(|_|Error::Invalid("loglinear"))?,_=>cubic.rates(t)?};
                Ok(igm_flat(r))
            })?;
            black_box(&out);let elapsed=start.elapsed().as_secs_f64()*1e9/(n as f64);
            let checksum=out.iter().map(|r|r[0]+r[3]+r[14]).sum::<f64>();
            println!("{pattern},{n},{workers},{repeat},{backend},{elapsed:.9},{checksum:.17e}");
        }}}
    }
    Ok(())
}
