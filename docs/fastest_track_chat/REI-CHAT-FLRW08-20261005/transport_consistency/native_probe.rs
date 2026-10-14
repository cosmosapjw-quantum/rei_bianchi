//! Standalone original transport-prefix driver: no full endpoint/source/chemistry.
pub use rei_microphysics::*;
pub use rei_microphysics::coupled_primary;
#[path="../../../../.cuh/fastest-track/REI-CHAT-FLRW08/transport-consistency/outputs/original_transport_prefix.rs"]
mod original_transport_prefix;
use original_transport_prefix::{PairedConfig, paired_initial, energy_nodes, transport_prefix, chosen_ratio};

fn array(a:&[f64])->String {
    format!("[{}]",a.iter().map(|x|format!("{:.17e}",x)).collect::<Vec<_>>().join(","))
}
fn main() {
    let c=PairedConfig{spectral_subdivisions:8,n_mu:8,n_phi:16};
    let e=energy_nodes(&c).unwrap();let n=e.len();
    let mut first=true; print!("{{\"cases\":[");
    for (geometry,h) in [("FLRW",[1e-14;3]),("BI",[1.01e-14,0.99e-14,1e-14])] {
        for t0 in [0.0,5e12] {for dt in [1000.0,6.25e8,1.25e9,2e9] {
            for d in [0usize,17,63,127] {for kind in 0..35usize {
                let mut s=paired_initial(&c).unwrap();s.time_s=t0;
                s.photons.fill(0.0);s.photon_boxes.fill(Interval::point(0.0).unwrap());
                if kind<33 {s.photons[d*n+kind]=if kind==0{0.05}else{1.0};}
                if kind==33 {s.lower_guard_n[d]=0.05;s.lower_guard_u[d]=0.3;}
                if kind==34 {
                    for j in 0..n {s.photons[d*n+j]=0.05*((j+1) as f64)/561.0;}
                    s.lower_guard_n[d]=0.025;s.lower_guard_u[d]=0.125;
                }
                for i in 0..s.photons.len(){s.photon_boxes[i]=Interval::point(s.photons[i]).unwrap();}
                s.lower_guard_n_box[d]=Interval::point(s.lower_guard_n[d]).unwrap();
                s.lower_guard_u_box[d]=Interval::point(s.lower_guard_u[d]).unwrap();
                // Original validate is applied by an appended helper before prefix.
                original_transport_prefix::validate_input(&c,&s,&e).unwrap();
                let (v,gn,gu)=transport_prefix(&c,h,&s,dt,&e).unwrap();
                let r=chosen_ratio(&c,h,t0,dt,d);
                if !first {print!(",")} first=false;
                print!("{{\"geometry\":\"{}\",\"t0\":{:.17e},\"dt\":{:.17e},\"ray\":{},\"kind\":{},\"ratio\":{:.17e},\"photons\":{},\"guard_n\":{:.17e},\"guard_u\":{:.17e}}}",geometry,t0,dt,d,kind,r,array(&v[d*n..(d+1)*n]),gn[d],gu[d]);
            }}
        }}
    }
    println!("]}}");
}
