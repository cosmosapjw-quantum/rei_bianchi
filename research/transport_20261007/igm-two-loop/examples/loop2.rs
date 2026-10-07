use igm_two_loop::{
    observable,
    panel::{Family, Panel},
    tail::LogPositive as LP,
    transport::{self, Sweep},
};
fn rows(kind: &str, family: usize, p: &Panel, q: f64, s0: f64, s1: f64, parts: usize, x: Sweep) {
    for (i, v) in x.owners.as_array().into_iter().enumerate() {
        let (hi, lo) = v.log_parts();
        println!("{kind},{family},{:.17e},{:.17e},{:.17e},{:.17e},{q:.17e},{s0:.17e},{s1:.17e},{:.17e},{parts},{i},{hi:.17e},{lo:.17e},{:.17e},{:.17e},{:.17e},{},{},{:.17e},{:.17e}",p.l,p.r,p.beta,p.ln_n,s1+transport::EC.ln(),x.loss.number,x.loss.energy,x.anchor_relative,x.sites,x.max_panel_rule_sites,v.readout().unwrap().value,x.band_exit_relative);
    }
}
fn main() {
    println!("kind,family,l,r,beta,log_n,q,s0,s1,boundary,parts,owner,log_hi,log_lo,loss_n,loss_e,anchor_relative,sites,max_panel_rule_sites,readout,band_exit_relative");
    let s0 = -13.0_f64.ln();
    for (id, family) in [
        (0, Family::Ordinary),
        (1, Family::RightFront),
        (2, Family::LeftFront),
    ] {
        for beta in [0., 2.] {
            for ln_n in [1e-8_f64.ln(), -750.] {
                let p = Panel {
                    l: s0 + 13.7_f64.ln(),
                    r: s0 + 20.0_f64.ln(),
                    beta,
                    family,
                    ln_n,
                };
                for h in [0., 0.003, 0.008, 0.1, 0.5] {
                    for parts in [1, 8] {
                        rows(
                            "stock",
                            id,
                            &p,
                            0.,
                            s0,
                            s0 + h,
                            parts,
                            transport::sweep_stock(&p, s0, s0 + h, parts).unwrap(),
                        );
                    }
                }
            }
        }
    }
    let d = 13.7_f64.ln() - transport::EC.ln();
    let p = Panel {
        l: 13.7_f64.ln(),
        r: 20_f64.ln(),
        beta: 0.,
        family: Family::Ordinary,
        ln_n: 0.,
    };
    for h in [
        0.,
        d / 2.,
        d,
        d + 0.001,
        d + 0.002,
        d + 0.004,
        0.1,
        0.5,
        0.8,
    ] {
        for parts in [1, 2] {
            rows(
                "source",
                0,
                &p,
                1e-8,
                0.,
                h,
                parts,
                transport::sweep_source(h, 1e-8, 13.7, 20., parts).unwrap(),
            );
        }
    }
    for (id, family) in [
        (0, Family::Ordinary),
        (1, Family::RightFront),
        (2, Family::LeftFront),
    ] {
        let p = Panel {
            l: s0 + 13.7_f64.ln(),
            r: s0 + 20_f64.ln(),
            beta: 2.,
            family,
            ln_n: 1e-8_f64.ln(),
        };
        for parts in [1, 2, 4, 8, 16, 32] {
            let bounds = observable::restricted_bounds(&p, s0, parts).unwrap();
            for (i, v) in [bounds.lower, bounds.upper].into_iter().enumerate() {
                let (hi, lo) = v.log_parts();
                println!("envelope,{id},{:.17e},{:.17e},{:.17e},{:.17e},0,{s0:.17e},{s0:.17e},0,{parts},{i},{hi:.17e},{lo:.17e},0,0,0,0,0,{:.17e},0",p.l,p.r,p.beta,p.ln_n,v.readout().unwrap().value);
            }
        }
    }
    // Explicit sharpness witness in the theory note (reported through native tests).
    let _ = observable::inverse_cubic(LP::from_linear(1.).unwrap(), 1., 4., 2.).unwrap();
}
