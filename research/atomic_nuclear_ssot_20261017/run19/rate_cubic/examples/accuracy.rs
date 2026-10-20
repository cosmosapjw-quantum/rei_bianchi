mod common;
use common::{HheCubic,source_id};
use rei_rate_cubic::{CubicRateGrid,Error};
use rei_reference::{igm_rates::igm_rates, rate_table::{igm_flat,igm_branch_knots}};
use std::{path::PathBuf,time::Instant};

fn main()->Result<(),Box<dyn std::error::Error>> {
    let dir=std::env::args().nth(1).map(PathBuf::from).ok_or("output directory needed")?;
    std::fs::create_dir_all(&dir)?;
    println!("nodes,build_seconds,heap_bytes,cache_bytes,save_seconds,load_seconds,queries,interpolated,fallback,max_relative,max_absolute,channel,temperature_k");
    for nodes in [16385,32769] {
        let start=Instant::now();let table=HheCubic::new(nodes)?;let build=start.elapsed().as_secs_f64();
        let mut ts:Vec<_>=(0..65537).map(|i|(1e6f64.ln()*(i as f64+0.371)/65537.0).exp()).collect();
        ts.extend([1.0,1e6,10000.0,5500.0,9284.0]);
        for k in igm_branch_knots(){for t in [k.next_down(),k,k.next_up()]{ts.push(t);}}
        // At each actual table cell test a midpoint plus both neighboring f64
        // values around each node. This covers branches/floors/lookup boundaries.
        for i in 0..nodes {let t=table.grid.temperature_at(i).unwrap();
            for q in [t.next_down(),t,t.next_up()]{if (1.0..=1e6).contains(&q){ts.push(q);}}
            if i+1<nodes {ts.push((table.grid.temperature_at(i).unwrap()*table.grid.temperature_at(i+1).unwrap()).sqrt());}}
        let mut max_rel=0.0;let mut max_abs=0.0f64;let mut channel=0;let mut worst_t=0.0;let mut interp=0;
        for &t in &ts {
            if table.grid.sample(t).is_some(){interp+=1;}
            let a=table.rates(t)?;let b=igm_rates(t).map_err(|_|Error::Invalid("source"))?;
            let av=igm_flat(a);let bv=igm_flat(b);
            for j in 0..15 {let abs=(av[j]-bv[j]).abs();max_abs=max_abs.max(abs);
                if bv[j]!=0.0 {let rel=abs/bv[j].abs();if rel>max_rel{max_rel=rel;channel=j;worst_t=t;}assert!(rel<=1e-5,"nodes={nodes} j={j} t={t} rel={rel}");}
                else {assert_eq!(av[j].to_bits(),bv[j].to_bits());}}
            assert_eq!(a.diagnostics.dr_low_branch,b.diagnostics.dr_low_branch);
            assert_eq!(a.diagnostics.ci_floor_cm3_s,b.diagnostics.ci_floor_cm3_s);
            for j in 0..3 {assert_eq!(a.diagnostics.ce_cap_erg[j]==0.0,b.diagnostics.ce_cap_erg[j]==0.0);}
            assert_eq!(a.dr_cooling_erg_cm3_s==0.0,b.dr_cooling_erg_cm3_s==0.0);
        }
        for t in [0.0,-1.0,0.999,1_000_001.0,f64::INFINITY,f64::NAN] {assert!(table.rates(t).is_err());}
        let path=dir.join(format!("hhe_{nodes}.bin"));let s=Instant::now();table.grid.save_new(&path)?;let save=s.elapsed().as_secs_f64();
        let s=Instant::now();let grid=CubicRateGrid::load(&path,source_id())?;let load=s.elapsed().as_secs_f64();let loaded=HheCubic{grid};
        for t in [1.0,42.0,9284.0,9994.35124339563,10000.0,1e6] {assert_eq!(igm_flat(table.rates(t)?),igm_flat(loaded.rates(t)?));}
        println!("{nodes},{build:.9},{},{},{save:.9},{load:.9},{},{interp},{},{max_rel:.17e},{max_abs:.17e},{channel},{worst_t:.17e}",table.grid.storage_bytes(),path.metadata()?.len(),ts.len(),ts.len()-interp);
    }
    Ok(())
}
