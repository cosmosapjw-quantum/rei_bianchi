//! Bounded-memory, two-file parallel real AX08 feedback reconstruction.
//! Exact same trapezoid/Kahan prescription as reconstruct_feedback.py.
//! No solver; no source, geometry, or acceptance mutation; stable q cases only.
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::{Path, PathBuf};
use std::thread;
use std::time::Instant;

const G_SI: f64=6.67430e-11;
const C_SI: f64=299792458.0;
const COEFF: f64=8.0*std::f64::consts::PI*G_SI/(3.0*C_SI*C_SI);
const ROWS: usize=312_238;
const HEADER: &str="case_id,time_s,a,H_per_s,effective_radiation_DeltaP_J_m3,ionizing_DeltaP_J_m3,effective_radiation_signed_deltaepsilon_J_m3,extra_energy_J_m3,extra_energy_ratio,total_DeltaP_J_m3";
#[derive(Debug)]
struct Summary {
    case: String,
    rows: usize,
    max_abs_delta_s_over_h: f64,
    endpoint_delta_s_over_h: f64,
    max_extra_energy_ratio: f64,
    endpoint_effective_rad_delta_s_over_h: f64,
    endpoint_ionizing_delta_s_over_h: f64,
    end_a: f64,
    seconds: f64,
}
#[derive(Clone,Copy,Default)]
struct Kahan { sum:f64, correction:f64 }
impl Kahan {
    fn add(&mut self, value:f64) {
        let y=value-self.correction;
        let t=self.sum+y;
        self.correction=(t-self.sum)-y;
        self.sum=t;
    }
}
fn parse(s:&str, context:&str)->Result<f64,String>{
    let x:f64=s.parse().map_err(|_|format!("BAD_NUMBER:{context}"))?;
    if !x.is_finite(){return Err(format!("NONFINITE:{context}"))}
    Ok(x)
}
fn read(path:&Path, case:&str)->Result<Summary,String>{
    let t0=Instant::now();
    let f=File::open(path).map_err(|e|format!("OPEN:{case}:{e}"))?;
    let mut reader=BufReader::with_capacity(1024*1024,f);
    let mut line=String::with_capacity(1024);
    reader.read_line(&mut line).map_err(|e|e.to_string())?;
    if line.trim_end_matches(&['\r','\n'][..])!=HEADER {return Err("HEADER_DRIFT".into())}
    let mut before:Option<(f64,f64,[f64;2])>=None;
    let mut accum=[Kahan::default();2];
    let mut rows=0;
    let mut max_s=0.0_f64;
    let mut max_extra=0.0_f64;
    let mut end=(0.,0.,[0.,0.],0.);
    loop {
        line.clear();
        if reader.read_line(&mut line).map_err(|e|e.to_string())?==0 {break}
        let mut it=line.trim_end_matches(&['\r','\n'][..]).split(',');
        if it.next()!=Some(case){return Err(format!("CASE_MISMATCH:{case}:row{rows}"))}
        let t=parse(it.next().ok_or("MISSING_TIME")?,"time")?;
        let a=parse(it.next().ok_or("MISSING_A")?,"a")?;
        let h=parse(it.next().ok_or("MISSING_H")?,"H")?;
        let p0=parse(it.next().ok_or("MISSING_P0")?,"p0")?;
        let p1=parse(it.next().ok_or("MISSING_P1")?,"p1")?;
        let _delta_eps=it.next().ok_or("MISSING_DEPS")?;
        let _extra_energy=it.next().ok_or("MISSING_EEXTRA")?;
        let extra=parse(it.next().ok_or("MISSING_EXTRA_RATIO")?,"extra")?;
        let pt=parse(it.next().ok_or("MISSING_TOTAL_P")?,"total")?;
        if it.next().is_some() || a<=0. || h<=0. {return Err("CSV_FIELD_OR_DOMAIN".into())}
        if (p0+p1-pt).abs()>1e-25_f64.max(1e-12*pt.abs()) {return Err("PRESSURE_LEDGER".into())}
        if let Some((old_t,old_a,old_p))=before {
            if t<=old_t || a<=old_a{return Err("CLOCK_NOT_MONOTONE".into())}
            for j in 0..2 {
                accum[j].add(0.5*(old_a.powi(3)*old_p[j]+a.powi(3)*[p0,p1][j])*(t-old_t));
            }
        } else if t.abs()>1e-4 || (a-1./21.).abs()>1e-16{return Err("INITIAL_CLOCK_DRIFT".into())}
        let co=[accum[0].sum*COEFF/(a.powi(3)*h),accum[1].sum*COEFF/(a.powi(3)*h)];
        let sum=co[0]+co[1];
        max_s=max_s.max(sum.abs());
        max_extra=max_extra.max(extra.abs());
        end=(a,sum,co,extra);
        before=Some((t,a,[p0,p1]));
        rows+=1;
    }
    if rows!=ROWS || end.0!=0.2 {return Err(format!("MISSING_REPRESENTED_INTERVAL:{case}:{rows}"))}
    Ok(Summary{
        case:case.into(),rows,
        max_abs_delta_s_over_h:max_s,endpoint_delta_s_over_h:end.1,
        max_extra_energy_ratio:max_extra,
        endpoint_effective_rad_delta_s_over_h:end.2[0],
        endpoint_ionizing_delta_s_over_h:end.2[1],
        end_a:end.0,seconds:t0.elapsed().as_secs_f64()
    })
}
fn print_row(s:&Summary){
    println!("{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.6}",
       s.case,s.rows,s.max_abs_delta_s_over_h,s.endpoint_delta_s_over_h,
       s.max_extra_energy_ratio,s.endpoint_effective_rad_delta_s_over_h,
       s.endpoint_ionizing_delta_s_over_h,s.end_a,s.seconds);
}
fn main()->Result<(),String>{
    let mut args=std::env::args().skip(1);
    let root=PathBuf::from(args.next().ok_or("Usage: axbi_feedback_fast ROOT [--serial]")?);
    let serial=matches!(args.next().as_deref(),Some("--serial"));
    let paths=[
       ("ZERO",root.join("research/axbi_goal_20261014/runs/flrw/32d11e733155/ZERO_composed_001/feedback.csv")),
       ("SHEAR_MINUS",root.join("research/axbi_goal_20261014/runs/paired/32d11e733155/SHEAR_MINUS_composed_001/feedback.csv"))
    ];
    println!("case,rows,max_abs_delta_s_over_H,endpoint_delta_s_over_H,max_extra_energy_ratio,endpoint_effective_rad_delta_s_over_H,endpoint_ionizing_delta_s_over_H,end_a,wall_seconds");
    if serial{
        for (case,path) in paths {print_row(&read(&path,case)?)}
    }else{
        let results=thread::scope(|scope|{
            let a=scope.spawn(||read(&paths[0].1,paths[0].0));
            let b=scope.spawn(||read(&paths[1].1,paths[1].0));
            let r0=a.join().map_err(|_|"PANIC_READING_ZERO".to_string())??;
            let r1=b.join().map_err(|_|"PANIC_READING_HALF_PLUS".to_string())??;
            Ok::<_,String>([r0,r1])
        })?;
        for r in &results {print_row(r)}
    }
    Ok(())
}
