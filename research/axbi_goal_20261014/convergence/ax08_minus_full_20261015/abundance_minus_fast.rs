// Actual AX08 full-source streaming abundance/charge audit.
// std-only Rust, no solver; handles all 312238*6 records, O(1) memory.
// SHA-pinned source protection is the caller's responsibility.
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::time::Instant;
use std::env;
fn readcols(line: &str, n: usize) -> Result<Vec<&str>, String> {
    let cols:Vec<_>=line.trim_end().split(',').collect();
    if cols.len()!=n {return Err(format!("COLS_{n}_GOT_{}",cols.len()))}
    Ok(cols)
}
fn num(col:&str)->Result<f64,String>{
    let x:f64=col.trim().parse().map_err(|_|format!("BAD_NUMERIC_{col}"))?;
    if !x.is_finite(){return Err("NONFINITE_PHYSICAL_NUMBER".into())}
    Ok(x)
}
fn m(v:&mut f64,x:f64){if x>*v{*v=x}}
fn go(args:Vec<String>)->Result<(),String>{
    if args.len()!=4 {return Err("usage abundance_audit_fast CASE HISTORY.csv ABUNDANCES.csv".into())}
    let case=&args[1];
    if case!="SHEAR_MINUS" {return Err("CASE_NOT_COMPLETED_MINUS".into())}
    let start=Instant::now();
    let mut history=BufReader::with_capacity(1<<20,File::open(&args[2]).map_err(|e|e.to_string())?);
    let mut abundance=BufReader::with_capacity(1<<20,File::open(&args[3]).map_err(|e|e.to_string())?);
    let mut s=String::new();let mut a=String::new();
    history.read_line(&mut s).map_err(|e|e.to_string())?;
    abundance.read_line(&mut a).map_err(|e|e.to_string())?;
    let hh=readcols(&s,25)?;let aa=readcols(&a,14)?;
    for (j,k) in [
        (0,"case_id"),(3,"time_s"),(4,"a"),(9,"x_HII"),(10,"x_HeII"),(11,"x_HeIII"),
        (12,"nH_proper_cm3"),(13,"ne_proper_cm3"),(14,"temperature_K"),
        (23,"x_HI"),(24,"x_HeI")] {
        if hh[j]!=k{return Err(format!("HISTORY_COLUMN_{j}_EXPECTED_{k}"))}
    }
    for (j,k) in [(0,"run_id"),(1,"time_s"),(3,"Tgas_K"),(5,"species_id"),
       (6,"A"),(9,"nproper"),(10,"element_fraction"),(11,"Ybaryon"),(12,"electron_xe")]{
        if aa[j]!=k{return Err(format!("ABUNDANCE_COLUMN_{j}_EXPECTED_{k}"))}
    }
    let species=["H_I","H_II","He_I","He_II","He_III","electron"];
    let nuclei=[1.,1.,4.,4.,4.,0.];
    let mut maxima=[0f64;9];
    let mut nehe_initial=0f64;
    let mut prev_t=-1f64;let mut prev_a=0f64;let mut rows=0usize;
    loop{
        s.clear();
        let count=history.read_line(&mut s).map_err(|e|e.to_string())?;
        if count==0{break;}
        let h=readcols(&s,25)?;
        if h[0]!=case{return Err(format!("HISTORY_CASE_{rows}"))}
        let t=num(h[3])?;let scale=num(h[4])?;
        let hion=[num(h[23])?,num(h[9])?,num(h[24])?,num(h[10])?,num(h[11])?];
        let n_h=num(h[12])?;let ne_hist=num(h[13])?;let temp=num(h[14])?;
        if t<=prev_t||scale<=prev_a||n_h<=0. {return Err("BAD_HISTORY_CLOCK_SCALE".into())}
        prev_t=t;prev_a=scale;
        let mut n=[0f64;6];
        let mut frac=[0f64;5];let mut baryon=[0f64;5];let mut electron_fraction=0f64;
        for k in 0..6{
            a.clear();if abundance.read_line(&mut a).map_err(|e|e.to_string())?==0 {
                return Err(format!("MISSING_ABUNDANCE_AT_{rows}_{k}"))}
            let r=readcols(&a,14)?;
            if r[0]!=case||r[5]!=species[k]||num(r[6])?!=nuclei[k]{
                return Err(format!("SPECIES_ID_OR_A_AT_{rows}_{k}"))}
            if num(r[1])?!=t{return Err(format!("SPECIES_CLOCK_{rows}_{k}"))}
            m(&mut maxima[7],(num(r[3])?-temp).abs());
            n[k]=num(r[9])?;
            if n[k]<0. {return Err(format!("NEGATIVE_SPECIES_{rows}_{k}"))}
            if k<5{
                frac[k]=num(r[10])?;
                baryon[k]=num(r[11])?;
            }else {electron_fraction=num(r[12])?;}
        }
        let h_total=n[0]+n[1];let he_total=n[2]+n[3]+n[4];
        let e=n[1]+n[3]+2.*n[4];
        if h_total<=0.||he_total<=0. {return Err("ZERO_NUCLEUS_SOURCE".into())}
        let ratio=he_total/h_total;if rows==0{nehe_initial=ratio}
        m(&mut maxima[0],(n[0]/h_total-frac[0]).abs()+
                             (n[1]/h_total-frac[1]).abs()+
                             (n[2]/he_total-frac[2]).abs()+
                             (n[3]/he_total-frac[3]).abs()+
                             (n[4]/he_total-frac[4]).abs());
        for k in 0..5 {m(&mut maxima[1],(frac[k]-hion[k]).abs());}
        m(&mut maxima[2],((e-n[5])/n_h).abs());
        m(&mut maxima[3],(n[5]/n_h-electron_fraction).abs());
        m(&mut maxima[4],((h_total-n_h)/n_h).abs());
        m(&mut maxima[5],(ratio-nehe_initial).abs());
        m(&mut maxima[6],(baryon[0]+baryon[1]+4.*(baryon[2]+baryon[3]+baryon[4])-1.).abs());
        m(&mut maxima[8],((e-ne_hist)/n_h).abs());
        rows+=1;
    }
    a.clear();if abundance.read_line(&mut a).map_err(|e|e.to_string())?>0 {return Err("EXTRA_ABUNDANCES".into())}
    if rows!=312238 {return Err(format!("WRONG_FULL_ROWS_{rows}"))}
    if maxima.iter().any(|x|!x.is_finite()||*x>5e-9) {return Err(format!("CENSUS_MISMATCH_{maxima:?}"))}
    println!("{{\"schema\":\"rei.axbi.rust_abundance_census.v1\",\"case\":\"{}\",\"history_rows\":{},\"ion_rows\":{},\"seconds\":{:.9},\"helium_per_hydrogen_initial\":{:.17e},\"max_abs_residuals\":[{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}],\"all_pass\":true,\"source_ivp_reexecuted\":false}}",
      case,rows,6*rows,start.elapsed().as_secs_f64(),nehe_initial,
      maxima[0],maxima[1],maxima[2],maxima[3],maxima[4],maxima[5],maxima[6],maxima[7],maxima[8]);
    Ok(())
}
fn main(){
    if let Err(e)=go(env::args().collect()){
        eprintln!("AX08_CENSUS_FAIL:{e}");std::process::exit(2)
    }
}
