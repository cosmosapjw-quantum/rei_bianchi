use rei_rate_cubic::{CubicRateGrid, Sample, Error, centered_weights};
use sha2::{Digest, Sha256};

fn model(t: f64) -> Result<Sample<4>, Error> {
    let x=t.ln(); Ok(Sample { values:[2.0+x+x*x+x*x*x, t.powf(-0.7), 0.0, 1e-20], tag:7 })
}
fn grid() -> CubicRateGrid<4> {
    CubicRateGrid::build(1.0,100.0,1025,[17;32],model,|_,_|false,|j,_,_|j==2).unwrap()
}
#[test]
fn exact_polynomial_zero_and_fallback_contract() {
    let g=grid();
    for i in 1..4096 {
        let t=(0.01+4.58*i as f64/4096.0).exp();
        let a=g.sample(t).unwrap(); let b=model(t).unwrap();
        assert!((a.values[0]-b.values[0]).abs()<1e-12);
        assert!(((a.values[1]-b.values[1])/b.values[1]).abs()<1e-10);
        assert_eq!(a.values[2].to_bits(),0.0f64.to_bits()); assert_eq!(a.tag,7);
    }
    for t in [f64::NAN,-1.0,0.0,0.99,1.0,100.0,101.0,f64::INFINITY] { assert!(g.sample(t).is_none()); }
}
#[test]
fn complete_support_guard_and_uncertified_zero() {
    let g=CubicRateGrid::build(1.0,100.0,1025,[0;32],model,|a,b|a<=10.0&&b>=10.0,|j,_,_|j==2).unwrap();
    for t in [9.999,10.0,10.001] { assert!(g.sample(t).is_none()); }
    let g=CubicRateGrid::build(1.0,100.0,33,[0;32],model,|_,_|false,|_,_,_|false).unwrap();
    assert_eq!(g.blocked_cells(),32);
}
#[test]
fn weights_reproduce_degree_three_and_conditioning() {
    for i in 0..=1024 { let t=i as f64/1024.0; let w=centered_weights(t);
        for p in 0..4 { let y=w.iter().zip([-1.0f64,0.0,1.0,2.0]).map(|(w,x)|w*x.powi(p)).sum::<f64>();
            assert!((y-t.powi(p)).abs()<1e-15); }
        assert!((w.iter().map(|x|x.abs()).sum::<f64>()-(1.0+t*(1.0-t))).abs()<1e-15);
    }
}
#[test]
fn ordered_inplace_batch_and_errors() {
    let g=grid(); let ts:Vec<_>=(0..4096).map(|i|(0.01+4.58*i as f64/4096.0).exp()).collect();
    let mut reference=vec![[0.0;4];ts.len()];
    CubicRateGrid::<4>::batch_into(&ts,&mut reference,1,|t|Ok(g.sample(t).unwrap().values)).unwrap();
    for workers in [2,4] {let mut out=vec![[0.0;4];ts.len()];
        CubicRateGrid::<4>::batch_into(&ts,&mut out,workers,|t|Ok(g.sample(t).unwrap().values)).unwrap(); assert_eq!(reference,out);}
    assert!(CubicRateGrid::<4>::batch_into(&ts,&mut reference,0,|_|Ok([0.0;4])).is_err());
    assert!(CubicRateGrid::<4>::batch_into(&ts,&mut reference[..3],1,|_|Ok([0.0;4])).is_err());
}
#[test]
fn cache_roundtrip_source_and_corruption() {
    let g=grid(); let dir=std::env::temp_dir().join(format!("rei-cubic-test-{}",std::process::id()));
    std::fs::create_dir(&dir).unwrap(); let path=dir.join("table.bin"); g.save_new(&path).unwrap();
    assert!(g.save_new(&path).is_err());
    let loaded=CubicRateGrid::<4>::load(&path,[17;32]).unwrap();
    for t in [1.01,2.345,10.0,98.0] { assert_eq!(g.sample(t).unwrap().values,loaded.sample(t).unwrap().values); }
    assert!(CubicRateGrid::<4>::load(&path,[18;32]).is_err());
    let raw=std::fs::read(&path).unwrap();
    for k in [0,20,56,88,raw.len()-1] {let mut b=raw.clone();b[k]^=1;let p=dir.join(format!("bad-{k}")); std::fs::write(&p,&b).unwrap(); assert!(CubicRateGrid::<4>::load(&p,[17;32]).is_err());}
    // A recomputed digest does not excuse an invalid boundary mask.
    let mut b=raw.clone(); let first_flag=88+1025*(4*8+1); b[first_flag..first_flag+4].copy_from_slice(&0u32.to_le_bytes());
    let n=b.len(); let digest=Sha256::digest(&b[..n-32]);b[n-32..].copy_from_slice(&digest);
    let p=dir.join("bad-boundary");std::fs::write(&p,b).unwrap();assert!(CubicRateGrid::<4>::load(&p,[17;32]).is_err());
    std::fs::remove_dir_all(dir).unwrap();
}
