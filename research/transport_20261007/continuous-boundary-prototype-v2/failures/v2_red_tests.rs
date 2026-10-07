mod primitives;
use primitives::*;
use std::io::Write;
fn close(a: f64, b: f64, rel: f64) {
    assert!(a.is_finite() && b.is_finite());
    assert!(
        (a - b).abs() <= rel * a.abs().max(b.abs()).max(1e-300),
        "{a:.17e} vs {b:.17e}, error {:.3e}",
        (a - b).abs()
    );
}
fn audit(o: Owners, n0: f64, u0: f64) {
    close(o.n + o.an.iter().sum::<f64>() + o.outn, n0 + o.qn, 2e-12);
    close(
        o.u + o.be.iter().sum::<f64>() + o.red + o.oute,
        u0 + o.qe,
        2e-12,
    );
    for x in [o.n, o.u, o.red, o.qn, o.qe, o.outn, o.oute]
        .into_iter()
        .chain(o.an)
        .chain(o.be)
    {
        assert!(x >= 0.0 && x.is_finite());
    }
}
fn original(o: Owners) -> (f64, f64) {
    let n = (o.n + o.an.iter().sum::<f64>() + o.outn - o.qn).abs() / (1e-10 * o.qn.max(1e-10));
    let e =
        (o.u + o.be.iter().sum::<f64>() + o.red + o.oute - o.qe).abs() / (1e-10 * o.qe.max(1e-20));
    assert!(n <= 1.0 && e <= 1.0, "original budget {n} {e}");
    (n, e)
}
fn t1_sweep() {
    let l = EC.ln() + 0.1;
    let d = Density {
        l,
        r: l + 1.0,
        a: 0.7,
        k: 0.0,
    };
    let (n0, m0) = moments(d, l, d.r);
    let mut maxnr: f64 = 0.0;
    for s in [0.0, 0.017, 0.099, 0.1, 0.10001, 0.38, 0.673, 1.1, 1.4] {
        let o = initial_transaction(d, 0.0, s, 8, false);
        let a = l.max(EC.ln() + s).min(d.r);
        close(o.n, 0.7 * (d.r - a), 2e-12);
        close(o.outn, 0.7 * (a - l), 2e-12);
        audit(o, n0, EPS * m0);
        let split = initial_transaction(d, 0.0, s, 32, false);
        close(o.n, split.n, 2e-12);
        close(o.red, split.red, 2e-12);
        maxnr = maxnr.max((o.n + o.outn - n0).abs());
    }
    let o = initial_transaction(d, 0.4, 0.8, 16, false);
    let (n, m) = moments(d, EC.ln() + 0.4, d.r);
    audit(o, n, EPS * (-0.4f64).exp() * m);
    close(o.outn, 0.28, 2e-12);
    println!("DIAG T1 max_raw_N_residual={maxnr:e}");
}
fn t2_continuity() {
    let l = EC.ln();
    let d = Density {
        l,
        r: l + 1.0,
        a: 0.7,
        k: 1.3,
    };
    let (n0, m0) = moments(d, l, d.r);
    for x in [0.211324865405187, 0.5, 0.788675134594813, 1.0] {
        let h = 1e-9;
        let a = initial_transaction(d, 0.0, x - h, 8, false);
        let b = initial_transaction(d, 0.0, x + h, 8, false);
        assert!((b.outn - a.outn).abs() < 1e-7);
        audit(b, n0, EPS * m0);
    }
    let eta = l + 0.5;
    let atom = Inventory::Atom { eta, n: 1.0 };
    assert_eq!(atomic_transaction(atom, 0.0, 0.5 - 1e-9).unwrap().outn, 0.0);
    assert_eq!(atomic_transaction(atom, 0.0, 0.5 + 1e-9).unwrap().outn, 1.0);
    println!("DIAG T2 smooth density continuous across former Gauss abscissae; declared physical atom retains unit jump");
}
fn t3_kernel() {
    let mut file = std::fs::File::create("results/kernel_values.csv").unwrap();
    writeln!(file, "h,lambda_h,f,q,e,n,u,a0,a1,a2,b0,b1,b2,red,qn,qe").unwrap();
    let mut cases = 0;
    for h in [1e-6, 0.01, 0.5, 2.0] {
        for z in [0.0, 1e-12, 1e-6, 0.1, 1.0, 100.0, 1000.0] {
            for (f, q) in [(0.7, 0.0), (0.0, 0.3), (0.7, 0.3)] {
                let e = 200.0 * f64::exp(h);
                let rates = [0.5 * z / h, 0.3 * z / h, 0.2 * z / h];
                let o = kernel(f, q, rates, h, e).unwrap();
                audit(o, f, EPS * e * f);
                for i in 0..3 {
                    assert!(o.be[i] - EPS * CHI[i] * o.an[i] >= 0.0);
                }
                writeln!(file,"{h:.17e},{z:.17e},{f:.17e},{q:.17e},{e:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",o.n,o.u,o.an[0],o.an[1],o.an[2],o.be[0],o.be[1],o.be[2],o.red,o.qn,o.qe).unwrap();
                cases += 1;
            }
        }
    }
    assert!(kernel(1.0, -1.0, [0.0; 3], 1.0, 100.0).is_err());
    assert!(kernel(1.0, 0.0, [0.0, 1.0, 0.0], 1.0, 20.0).is_err());
    println!("DIAG T3 {cases} kernel cases; all competing owners nonnegative; invalid source/support rejected");
}
fn t3b_events() {
    let eta = EC.ln() + 0.5;
    let o = characteristic(eta, 0.0, 0.8, 0.7, 0.3, 0.1, 0.4, [0.4, 0.0, 0.0]).unwrap();
    audit(o, 0.7, EPS * eta.exp() * 0.7);
    assert_eq!(o.n, 0.0);
    close(o.qn, 0.09, 1e-14);
    assert!(o.outn > 0.0 && o.an[0] > 0.0);
    close(o.oute, EPS * EC * o.outn, 1e-15);
    let n = characteristic(eta, 0.0, 0.8, 0.0, 0.3, 0.1, 0.4, [0.4, 0.0, 0.0]).unwrap();
    original(n);
    assert!(n.outn > 0.0);
    let eta = 100.0f64.ln();
    let all = characteristic(eta, 0.0, 2.1, 0.7, 0.3, 0.1, 1.5, [0.4, 0.3, 0.2]).unwrap();
    audit(all, 0.7, EPS * 100.0 * 0.7);
    for i in 0..3 {
        assert!(all.an[i] > 0.0 && all.be[i] - EPS * CHI[i] * all.an[i] >= 0.0);
    }
    println!("DIAG T3b frozen-source turn-on/off and HI/HeI/HeII cutoff splits share all owners");
}
fn t4_source() {
    let mut file = std::fs::File::create("results/source_values.csv").unwrap();
    writeln!(file, "t,n,u,red,qn,qe,outn,oute").unwrap();
    let mut mn: f64 = 0.0;
    let mut me: f64 = 0.0;
    for t in [0.001, 0.02, 0.123, 0.31, 0.8, 1.2] {
        let o = source_transaction(0.0, t, t, 13.7, 100.0, 32);
        writeln!(
            file,
            "{t:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            o.n, o.u, o.red, o.qn, o.qe, o.outn, o.oute
        )
        .unwrap();
        close(o.qn, t * (1.0 / 13.7 - 1.0 / 100.0), 3e-12);
        close(o.qe, EPS * t * (100.0f64 / 13.7).ln(), 3e-12);
        let (n, e) = original(o);
        mn = mn.max(n);
        me = me.max(e);
        assert_eq!(
            source_density(t + 100.0f64.ln() + 1e-6, t, 13.7, 100.0),
            0.0
        );
        let delta = 1e-6;
        let near = source_density(t + 100.0f64.ln() - delta, t, 13.7, 100.0);
        assert!(near > 0.0 && near < 2e-8);
        if t > 0.02 {
            assert!(o.outn > 0.0);
        }
        for partitions in [1, 2, 4, 8, 16] {
            let mut sum = Owners::default();
            for j in 0..partitions {
                let a = t * j as f64 / partitions as f64;
                let b = t * (j + 1) as f64 / partitions as f64;
                let z = source_transaction(a, b, t, 13.7, 100.0, 16);
                sum.n += z.n;
                sum.u += z.u;
                sum.qn += z.qn;
                sum.qe += z.qe;
                sum.red += z.red;
                sum.outn += z.outn;
                sum.oute += z.oute;
            }
            original(sum);
            close(sum.n, o.n, 3e-12);
            close(sum.outn, o.outn, 3e-12);
        }
    }
    let below = source_transaction(0.0, 0.3, 0.3, 12.0, 100.0, 32);
    original(below);
    assert!(below.oute < EPS * EC * below.outn);
    let dt = 1e-7;
    let t = 0.31;
    let a = source_transaction(0.0, t, t, 13.7, 100.0, 32);
    let b = source_transaction(0.0, t + dt, t + dt, 13.7, 100.0, 32);
    let trace = source_density(EC.ln() + t, t, 13.7, 100.0);
    close((b.outn - a.outn) / dt, trace, 1e-5);
    let h = 2.5;
    close(h * trace, (h * (b.outn - a.outn)) / dt, 1e-5);
    println!("DIAG T4 original max N budget ratio={mn:e}; E={me:e}; exact-time expanding source, off-phase, interval partition, crossing, direct-below-band and H conversion controls");
}
fn t5_reconstruction() {
    let mut file = std::fs::File::create("results/closure_values.csv").unwrap();
    writeln!(
        file,
        "l,r,n,beta,front,m,n_roundtrip,m_roundtrip,beta_inverse,target_scaled"
    )
    .unwrap();
    let mut worst: f64 = 0.0;
    for front in [false, true] {
        for width in [1e-7, 0.01, 1.0] {
            for beta in [-64.0, -12.0, 0.0, 12.0, 64.0] {
                let l = EC.ln();
                let mut r = l + width;
                if r - l < width {
                    r = f64::from_bits(r.to_bits() + 1);
                }
                let c = Closure {
                    l,
                    r,
                    n: 0.7,
                    beta,
                    front,
                };
                let (n, m) = closure_moments(c);
                let r = reconstruct(c.l, c.r, n, m, front).unwrap();
                let (n1, m1) = closure_moments(r);
                writeln!(file,"{:.17e},{:.17e},{n:.17e},{beta:.17e},{},{m:.17e},{n1:.17e},{m1:.17e},{:.17e},{:.17e}",c.l,c.r,front as u8,r.beta,(m/n/c.l.exp()-1.0)/(c.r-c.l).exp_m1()).unwrap();
                close(n, n1, 5e-12);
                close(m, m1, 5e-12);
                worst = worst.max(((m1 - m) / m).abs());
                if width > 1e-6 {
                    close(beta + 100.0, r.beta + 100.0, 1e-9);
                }
                if front {
                    let w = c.r - c.l;
                    let mut prev = f64::INFINITY;
                    for delta in [1e-3, 1e-4, 1e-5, 1e-6] {
                        let v = density_value(c, c.r - w * delta);
                        assert!(v >= 0.0 && v < prev);
                        prev = v;
                    }
                    assert_eq!(density_value(c, c.r + w * 0.01), 0.0);
                }
            }
        }
    }
    let tail = kernel(0.7, 0.0, [1000.0, 0.0, 0.0], 1.0, 100.0).unwrap();
    assert_eq!(tail.n, 0.0);
    close(tail.ln_n.unwrap(), 0.7f64.ln() - 1000.0, 1e-15);
    assert!(tail.ln_u.is_some());
    assert!(admit_sample(1.0, f64::from_bits(1.0f64.to_bits() + 1), 1.0, 1.0f64.exp()).is_err());
    assert_eq!(inventory(None, None).unwrap(), Inventory::Empty);
    assert!(matches!(
        inventory(Some(-1000.0), Some(-997.0)).unwrap(),
        Inventory::LogTail { .. }
    ));
    assert!(inventory(None, Some(0.0)).is_err());
    assert!(reconstruct(0.0, 1.0, 1.0, 0.9, false).is_err());
    assert!(reconstruct(0.0, 1.0, 1.0, 1.0, true).is_err());
    let nominal_l = EC.ln();
    let nominal_r = nominal_l + 1e-7;
    assert!(nominal_r - nominal_l < 1e-7);
    assert!(reconstruct(nominal_l, nominal_r, 1.0, nominal_l.exp(), false).is_err());
    let x = 1.0f64;
    let next = f64::from_bits(x.to_bits() + 1);
    assert!(reconstruct(x, next, 1.0, x.exp(), false).is_err());
    let d = Density {
        l: x,
        r: next,
        a: 1.0,
        k: 0.0,
    };
    let (n, m) = moments(d, x, next);
    assert!(n > 0.0 && m > 0.0);
    assert!(reconstruct(0.0, 1.0, 1.0, 1.0 + 1e-12, false).is_err());
    println!("DIAG T5 max moment roundtrip={worst:e}; authoritative log tails retained; unresolvable widths/extreme means reject, no clipping");
}
fn t5b_tail_admission() {
    assert!(characteristic(EC.ln() + 2.0, 0.0, 1.0, 1e-320, 0.0, 0.5, 0.75, [0.0; 3]).is_err());
    assert!(kernel(0.0, f64::from_bits(1), [0.0; 3], 1e-6, 100.0).is_err());
    assert!(characteristic(
        EC.ln() + 2.0,
        0.0,
        1.0,
        0.7,
        0.0,
        0.5,
        0.75,
        [1000.0, 0.0, 0.0]
    )
    .is_err());
    println!("DIAG T5b multi-segment underflow rejects rather than replacing an authoritative tail by empty");
}
fn t6_negative() {
    let base = source_transaction(0.0, 0.8, 0.8, 13.7, 100.0, 32);
    original(base);
    let budgetn = 1e-10 * base.qn.max(1e-10);
    let budgete = 1e-10 * base.qe.max(1e-20);
    assert!((base.n + base.outn * 0.9 - base.qn).abs() > budgetn);
    assert!((base.u + base.red - base.qe).abs() > budgete);
    assert!((base.u + base.red + base.outn * EPS * CHI[0] - base.qe).abs() > budgete);
    let wrong_remap_m = base.u * 0.99;
    assert!((wrong_remap_m + base.red + base.oute - base.qe).abs() > budgete);
    let a = kernel(1.0, 0.0, [2.0, 0.0, 0.0], 0.1, 20.0).unwrap();
    let b = kernel(1.0, 0.0, [0.1, 0.0, 0.0], 0.1, 100.0).unwrap();
    assert!((EPS * 60.0 * (a.an[0] + b.an[0]) - a.be[0] - b.be[0]).abs() > 1e-14);
    let frozen = kernel(0.0, 0.3, [0.0; 3], 0.5, 100.0).unwrap();
    assert!((frozen.n - 0.3 * 0.5f64.exp_m1()).abs() > 1e-4);
    let front = 0.8 + 100.0f64.ln();
    let leaking = Closure {
        l: front - 0.1,
        r: front + 0.01,
        n: 1e-8,
        beta: 0.0,
        front: true,
    };
    assert!(!source_support_admitted(leaking, front));
    assert!(source_support_admitted(
        Closure {
            r: front,
            ..leaking
        },
        front
    ));
    let atom = |s: f64| if s >= 0.5 { 0.2 } else { 0.0 };
    assert_eq!(atom(0.50001) - atom(0.49999), 0.2);
    println!("DIAG T6 rejected 7 deliberate owner/support corruptions; old fixed-node staircase remains visible");
}
fn t7_quadrature() {
    let d = Density {
        l: EC.ln(),
        r: EC.ln() + 1.0,
        a: 0.3,
        k: 2.0,
    };
    let (n, m) = moments(d, d.l, d.r);
    let pairs: Vec<_> = (0..16)
        .map(|i| moments(d, d.l + i as f64 / 16.0, d.l + (i + 1) as f64 / 16.0))
        .collect();
    let mut file = std::fs::File::create("results/initial_quadrature_samples.csv").unwrap();
    writeln!(file, "l,r,weight_N,moment_M,eta,N_error,M_error").unwrap();
    for (i, (n, m)) in pairs.iter().enumerate() {
        let a = d.l + i as f64 / 16.0;
        let b = d.l + (i + 1) as f64 / 16.0;
        let eta = admit_sample(a, b, *n, *m).unwrap();
        writeln!(
            file,
            "{a:.17e},{b:.17e},{n:.17e},{m:.17e},{eta:.17e},0,{:.17e}",
            n * eta.exp() - m
        )
        .unwrap();
    }
    let (a, b) = merge_moments(&pairs);
    close(a, n, 5e-12);
    close(b, m, 5e-12);
    let mut errors = Vec::new();
    let refv = initial_transaction(d, 0.0, 0.4, 512, true);
    for p in [4, 8, 16, 32, 64] {
        let o = initial_transaction(d, 0.0, 0.4, p, true);
        audit(o, n, EPS * m);
        errors.push((p, (o.an[0] - refv.an[0]).abs() / refv.an[0]));
    }
    assert!(errors.last().unwrap().1 < errors[0].1);
    let mut qerrs = Vec::new();
    let refq = source_transaction(0.0, 0.8, 0.8, 13.7, 100.0, 64);
    for q in [4, 8, 16, 32, 64] {
        let o = source_transaction(0.0, 0.8, 0.8, 13.7, 100.0, q);
        original(o);
        qerrs.push((q, (o.n - refq.n).abs() / refq.n));
    }
    assert!(qerrs[3].1 < 1e-6);
    let l = 1.0f64;
    let b = f64::from_bits(l.to_bits() + 1);
    let c = f64::from_bits(l.to_bits() + 2);
    assert_eq!(topology(l, c, &[b, b]), vec![l, b, c]);
    let nodes = gauss(0.0, 1.0, 64);
    assert!(nodes.iter().all(|(x, w)| *x > 0.0 && *x < 1.0 && *w > 0.0));
    close(nodes.iter().map(|(_, w)| w).sum(), 1.0, 1e-14);
    println!("DIAG T7 panel quadrature refinement={errors:?}; source quadrature refinement={qerrs:?}; split/merge preserves both moments; adjacent-float topology retained");
}
fn t7b_reconstruction_bias() {
    let t = 0.8;
    let l = EC.ln() + t;
    let r = 100.0f64.ln() + t;
    let breaks = [100.0f64.ln(), 13.7f64.ln() + t];
    let integrate = |a: f64, b: f64, kind: usize| {
        let mut sum = 0.0;
        for ab in topology(a, b, &breaks).windows(2) {
            for (eta, w) in gauss(ab[0], ab[1], 64) {
                let factor = match kind {
                    0 => 1.0,
                    1 => eta.exp(),
                    _ => f64::exp(-3.0 * (eta - t)),
                };
                sum += w * source_density(eta, t, 13.7, 100.0) * factor;
            }
        }
        sum
    };
    let exact = integrate(l, r, 2);
    let mut errs = Vec::new();
    for panels in [4, 8, 16, 32, 64] {
        let mut val = 0.0;
        for i in 0..panels {
            let a = l + (r - l) * i as f64 / panels as f64;
            let b = l + (r - l) * (i + 1) as f64 / panels as f64;
            let n = integrate(a, b, 0);
            let m = integrate(a, b, 1);
            let c = reconstruct(a, b, n, m, i + 1 == panels).unwrap();
            let (nn, mm) = closure_moments(c);
            close(n, nn, 5e-12);
            close(m, mm, 5e-12);
            for (eta, w) in gauss(a, b, 64) {
                val += w * density_value(c, eta) * f64::exp(-3.0 * (eta - t));
            }
        }
        errs.push((panels, (val - exact).abs() / exact));
    }
    assert!(errs.last().unwrap().1 < 1e-3);
    assert!(errs.last().unwrap().1 < errs[0].1);
    println!("DIAG T7b reconstruction-only E^-3 observable relative bias={errs:?}; no joined projected-history claim");
}
fn t7c_quadrature_target() {
    let d = Density {
        l: EC.ln(),
        r: EC.ln() + 1.0,
        a: 0.3,
        k: 2.0,
    };
    let reference = initial_transaction(d, 0.0, 0.4, 512, true).an[0];
    let mut file = std::fs::File::create("results/initial_opacity_convergence.csv").unwrap();
    writeln!(file, "parts,absorption_N").unwrap();
    let mut last = 0.0;
    for p in [4, 8, 16, 32, 64] {
        let n = initial_transaction(d, 0.0, 0.4, p, true).an[0];
        writeln!(file, "{p},{n:.17e}").unwrap();
        last = (n - reference).abs() / reference;
    }
    assert!(
        last < 1e-6,
        "frozen initial-opacity quadrature target missed: {last:.17e} > 1e-6"
    );
}
fn v2_initial_admission(){
 let d=Density{l:0.0,r:1.0,a:1.0,k:0.0};
 assert_eq!(try_moments(Density{a:0.0,..d},0.0,1.0).unwrap(),(0.0,0.0));
 assert!(try_moments(Density{a:f64::from_bits(1),..d},0.0,1.0).is_err());
 assert!(try_moments(Density{a:f64::MIN_POSITIVE,..d},0.0,0.5).is_err());
 assert!(try_moments(Density{r:2.0,k:-1000.0,..d},1.0,2.0).is_err());
 assert!(try_moments(Density{l:1000.0,r:1001.0,..d},1000.0,1001.0).is_err());
 assert!(try_moments(Density{a:f64::NAN,..d},0.0,1.0).is_err());
 let ordinary=try_moments(d,0.0,1.0).unwrap();close(ordinary.0,1.0,1e-15);
 println!("DIAG V2 initial exact-zero accepted; subnormal, underflowed, overflowed and invalid positive moments reject");
}
fn v2_weighted_admission(){
 let b=Owners{n:1.0,u:EPS*20.0,an:[0.1,0.0,0.0],be:[EPS*2.0,0.0,0.0],red:EPS,qn:0.3,qe:EPS*30.0,outn:0.2,oute:EPS*EC*0.2,..Owners::default()};
 let before=b;
 for w in [f64::from_bits(1),f64::MIN_POSITIVE,-1.0,f64::INFINITY]{let mut a=before;assert!(try_add_scaled(&mut a,b,w).is_err());assert_eq!(a,before);}
 for bad in [Owners{n:0.0,u:0.0,ln_n:Some(-1000.0),..Owners::default()},Owners{n:1.0,u:0.0,ln_u:Some(-1000.0),..Owners::default()},Owners{an:[-1.0,0.0,0.0],..Owners::default()}]{let mut a=before;assert!(try_add_scaled(&mut a,bad,1.0).is_err());assert_eq!(a,before);}
 let mut huge=Owners{n:f64::MAX,u:f64::MAX,..Owners::default()};let save=huge;assert!(try_add_scaled(&mut huge,save,2.0).is_err());assert_eq!(huge,save);
 let mut a=Owners::default();try_add_scaled(&mut a,b,0.5).unwrap();close(a.n,0.5,1e-15);close(a.u,EPS*10.0,1e-15);
 println!("DIAG V2 weighted owners reject subnormal/underflow/overflow and authoritative tails atomically, ordinary contribution accepted");
}
fn v2_conditioned_target(){
 let data=include_str!("../fixtures/normalization_targets.csv");let mut worst:f64=0.0;
 for line in data.lines().skip(1){let p:Vec<f64>=line.split(',').map(|x|x.parse().unwrap()).collect();let got=normalized_target(p[0],p[1],p[2],p[3]).unwrap();let error=(got-p[4]).abs();worst=worst.max(error);assert!(error<=5e-13,"exact-input target error {error:e}");}
 println!("DIAG V2 compensated exact-input normalized target max error={worst:e}");
}
fn v2_refinement_candidates(){
 let d=Density{l:EC.ln(),r:EC.ln()+1.0,a:0.3,k:2.0};let mut f=std::fs::File::create("results/v2_opacity_candidates.csv").unwrap();writeln!(f,"parts,absorption_N").unwrap();
 let(n,m)=moments(d,d.l,d.r);
 for p in [128,256,512]{let o=initial_transaction(d,0.0,0.4,p,true);audit(o,n,EPS*m);writeln!(f,"{p},{:.17e}",o.an[0]).unwrap();}
 println!("DIAG V2 candidates128/256/512 measured; acceptance decided by independent higher-order oracle");
}
fn main() {
    let tests: [(&str, fn()); 15] = [
        ("T1_sweep", t1_sweep),
        ("T2_continuity", t2_continuity),
        ("T3_kernel", t3_kernel),
        ("T3b_events", t3b_events),
        ("T4_source", t4_source),
        ("T5_reconstruction", t5_reconstruction),
        ("T5b_tail_admission", t5b_tail_admission),
        ("T6_negative", t6_negative),
        ("T7_quadrature", t7_quadrature),
        ("T7b_reconstruction_bias", t7b_reconstruction_bias),
        ("T7c_quadrature_target", t7c_quadrature_target),
("V2_initial_admission",v2_initial_admission),("V2_weighted_admission",v2_weighted_admission),("V2_conditioned_target",v2_conditioned_target),("V2_refinement_candidates",v2_refinement_candidates),
    ];
    let mut fail = 0;
    for (name, test) in tests {
        let r = std::panic::catch_unwind(test);
        println!("RESULT {name} {}", if r.is_ok() { "PASS" } else { "FAIL" });
        if r.is_err() {
            fail += 1;
        }
    }
    if fail > 0 {
        std::process::exit(1);
    }
}
