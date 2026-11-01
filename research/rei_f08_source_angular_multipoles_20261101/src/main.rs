//! Source-locked REI F08 donor angular moments. No new ionization IVP or CMB sky.
use std::collections::BTreeMap;
use std::io::{self, BufRead};

const N_MU: usize = 8;
const N_PHI: usize = 16;
const N_RAYS: usize = N_MU * N_PHI;
const DT_S: f64 = 625_000_000.0;
const FIELDS: [&str; 4] = [
    "HI_photoionization_rate",
    "HI_photoelectron_heat_rate",
    "HI_cumulative_absorption",
    "HI_cumulative_photoelectron_heat",
];
const UNITS: [&str; 4] = [
    "events_per_H_per_s",
    "eV_per_H_per_s",
    "photons_per_H",
    "eV_per_H",
];

#[derive(Clone, Debug)]
struct Ray {
    direction: usize,
    t_s: f64,
    q: [f64; 3],
    values: [f64; 4],
}

fn original_qhat(d: usize) -> [f64; 3] {
    let mu = -1.0 + 2.0 * ((d / N_PHI) as f64 + 0.5) / N_MU as f64;
    let phi = 2.0 * std::f64::consts::PI * ((d % N_PHI) as f64 + 0.5) / N_PHI as f64;
    let r = (1.0 - mu * mu).sqrt();
    let q = [r * phi.cos(), r * phi.sin(), mu];
    let norm = q[0].hypot(q[1]).hypot(q[2]);
    q.map(|x| x / norm)
}

fn q2(q: [f64; 3]) -> [f64; 6] {
    [q[0]*q[0], q[1]*q[1], q[2]*q[2], q[0]*q[1], q[0]*q[2], q[1]*q[2]]
}

fn parse_input<R: BufRead>(input: R) -> Result<BTreeMap<(String,u32),Vec<Ray>>,String> {
    let mut lines = input.lines();
    let header = lines.next().ok_or("empty original source")?.map_err(|e| e.to_string())?;
    if !header.starts_with("branch,source_original_tick,proper_time_s,direction_id,q_x,q_y,q_z,") {
        return Err("original source header does not match F08 angle event schema".into());
    }
    let mut groups = BTreeMap::<(String,u32),Vec<Ray>>::new();
    for (i,line) in lines.enumerate() {
        let s = line.map_err(|e|e.to_string())?;
        if s.trim().is_empty() {continue;}
        let c: Vec<&str> = s.split(',').collect();
        if c.len()!=15 {return Err(format!("source CSV row {} has {} columns",i+2,c.len()));}
        let branch=c[0];
        if branch!="S0_BI" && branch!="S0_FLRW" {return Err(format!("unknown branch {}",branch));}
        let u32p=|idx:usize| c[idx].parse::<u32>().map_err(|e|format!("row {} field {}: {}",i+2,idx,e));
        let f64p=|idx:usize| c[idx].parse::<f64>().map_err(|e|format!("row {} field {}: {}",i+2,idx,e));
        let tick=u32p(1)?;
        let t_s=f64p(2)?;
        let direction=u32p(3)? as usize;
        let q=[f64p(4)?,f64p(5)?,f64p(6)?];
        let values=[f64p(10)?,f64p(11)?,f64p(12)?,f64p(13)?];
        if tick==0 || tick>16_000 || !t_s.is_finite() || (t_s - tick as f64*DT_S).abs()>0.01
            || direction>=N_RAYS || q.iter().any(|v|!v.is_finite())
            || values.iter().any(|v|!v.is_finite()||*v<0.0) {
            return Err(format!("source row {} failed finite physics/domain check",i+2));
        }
        let refq=original_qhat(direction);
        if (0..3).any(|k|(q[k]-refq[k]).abs()>5e-12) {
            return Err(format!("source row {} direction differs from original qhat",i+2));
        }
        groups.entry((branch.to_string(),tick)).or_default().push(Ray{direction,t_s,q,values});
    }
    Ok(groups)
}

fn validate_original(groups: &BTreeMap<(String,u32),Vec<Ray>>) -> Result<(),String> {
    if groups.len()!=30 {return Err(format!("expected 30 source groups; observed {}",groups.len()));}
    let mut branch_counts=[0usize;2];
    for ((branch,tick),rays) in groups {
        branch_counts[if branch=="S0_BI"{0}else{1}]+=1;
        if rays.len()!=N_RAYS {return Err(format!("{} tick {} has {} rays",branch,tick,rays.len()));}
        let mut ids=[false;N_RAYS];
        for ray in rays {
            if ids[ray.direction] {return Err(format!("duplicate {} tick {} ray {}",branch,tick,ray.direction));}
            ids[ray.direction]=true;
            if (ray.t_s-*tick as f64*DT_S).abs()>0.01 {return Err("time mismatch".into());}
        }
        if ids.iter().any(|v|!*v){return Err("missing source direction".into());}
    }
    if branch_counts!=[15,15] {return Err(format!("incorrect source branch groups {:?}",branch_counts));}
    Ok(())
}

fn moment(rays:&[Ray], field:usize)->Result<(f64,[f64;6]),String>{
    let n=rays.len();
    if n==0{return Err("empty angle group".into());}
    let mut mean=[0.0;6];
    for r in rays {
        let b=q2(r.q);
        for j in 0..6 {mean[j]+=b[j];}
    }
    for j in 0..6 {mean[j]/=n as f64;}
    let mut sum=0.0;
    let mut raw=[0.0;6];
    for r in rays {
        let x=r.values[field];
        sum+=x;
        let b=q2(r.q);
        for j in 0..6 {raw[j]+=x*(b[j]-mean[j]);}
    }
    if !sum.is_finite() || sum<=0.0 {return Err("nonpositive physical source total".into());}
    for j in 0..6{raw[j]/=sum;}
    Ok((sum,raw))
}

fn run()->Result<(),String>{
    let input=io::stdin().lock();
    let groups=parse_input(input)?;
    validate_original(&groups)?;
    println!("branch,original_tick,proper_time_s,quantity,units,source_total,q_xx,q_yy,q_zz,q_xy,q_xz,q_yz,q_xx_minus_yy");
    for ((branch,tick),rays) in &groups {
        for field in 0..4 {
            let (total,q)=moment(rays,field)?;
            let tr=q[0]+q[1]+q[2];
            if tr.abs()>2e-12 {return Err(format!("trace error {} tick {} field {}",branch,tick,field));}
            if branch=="S0_FLRW" && q.iter().any(|v|v.abs()>2e-11) {
                return Err(format!("spurious FLRW quadrupole tick {} field {}",tick,field));
            }
            println!("{},{},{:.17e},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                branch,tick,rays[0].t_s,FIELDS[field],UNITS[field],total,
                q[0],q[1],q[2],q[3],q[4],q[5],q[0]-q[1]);
        }
    }
    Ok(())
}

fn main() {
    if let Err(message)=run() {
        eprintln!("REI F08 source analysis failed: {}",message);
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn synthetic(field:fn([f64;3])->f64)->Vec<Ray>{
        (0..N_RAYS).map(|d|{
            let q=original_qhat(d);
            Ray{direction:d,t_s:DT_S,q,values:[field(q);4]}
        }).collect()
    }
    #[test]
    fn actual_8x16_grid_centering_and_kappa(){
        let rays=synthetic(|_|1.0);
        let z=rays.iter().map(|r|r.q[2]*r.q[2]).sum::<f64>()/128.0;
        let x=rays.iter().map(|r|r.q[0]*r.q[0]).sum::<f64>()/128.0;
        let y=rays.iter().map(|r|r.q[1]*r.q[1]).sum::<f64>()/128.0;
        let k=rays.iter().map(|r|(r.q[0]*r.q[0]-r.q[1]*r.q[1]).powi(2)).sum::<f64>()/128.0;
        assert!((z-0.328125).abs()<2e-15);
        assert!((x-0.3359375).abs()<2e-15);
        assert!((y-0.3359375).abs()<2e-15);
        assert!((k-2185.0/8192.0).abs()<2e-15);
    }
    #[test]
    fn no_false_isotropic_quadrupole(){
        let rays=synthetic(|_|1.0);
        let (_,q)=moment(&rays,0).unwrap();
        assert!(q.iter().all(|v|v.abs()<1e-14));
    }
    #[test]
    fn first_order_energy_slope_signs(){
        let sdt=1.0e-16*DT_S;
        for slope in [-2.6887263918990483,132.1997293204128] {
            let rays=synthetic(|q|1.0-sdt*slope*(q[0]*q[0]-q[1]*q[1]));
            let (_,m)=moment(&rays,0).unwrap();
            let expected=-sdt*(2185.0/8192.0)*slope;
            assert!(((m[0]-m[1])-expected).abs()<2e-14);
        }
    }
}
