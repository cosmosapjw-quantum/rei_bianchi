//! Candidate root data for the independently checked static FT03 map.
use rei_microphysics::{
    ft03_implicit_step, ft03_interval_rhs, Ft03Model, HHeState, Interval, Jet, StepControl,
    FT03_MODEL_ID,
};
use std::fmt::Write;

const RADII: [f64; 7] = [1e-7, 1e-7, 1e-7, 1e-5, 1e-8, 1e-8, 1e-8];
const MANIFEST_SHA: &str = "f4112ac46d520d839fed2070388938c9b0db73a7e16c0d603d519463fca7f9a5";

fn scaled(model: &Ft03Model, state: &HHeState) -> [f64; 7] {
    let nh = model.gas.n_h_cm3;
    [
        state.fractions[0],
        state.fractions[1],
        state.fractions[2],
        state.u_erg_cm3 / (nh * model.gas.ev_erg),
        state.photon_cm3[0] / nh,
        state.photon_cm3[1] / nh,
        state.photon_cm3[2] / nh,
    ]
}
fn down(x: f64) -> f64 {
    if x == 0.0 {
        return -f64::from_bits(1);
    }
    f64::from_bits(if x > 0.0 {
        x.to_bits() - 1
    } else {
        x.to_bits() + 1
    })
}
fn up(x: f64) -> f64 {
    if x == 0.0 {
        return f64::from_bits(1);
    }
    f64::from_bits(if x > 0.0 {
        x.to_bits() + 1
    } else {
        x.to_bits() - 1
    })
}
fn invert(mut a: [[f64; 7]; 7]) -> [[f64; 7]; 7] {
    let mut b = [[0.0; 7]; 7];
    for i in 0..7 {
        b[i][i] = 1.0;
    }
    for k in 0..7 {
        let pivot = (k..7)
            .max_by(|&i, &j| a[i][k].abs().total_cmp(&a[j][k].abs()))
            .unwrap();
        assert!(a[pivot][k].abs() > 1e-300, "singular BE Jacobian");
        a.swap(k, pivot);
        b.swap(k, pivot);
        let p = a[k][k];
        for j in 0..7 {
            a[k][j] /= p;
            b[k][j] /= p;
        }
        for i in 0..7 {
            if i == k {
                continue;
            }
            let factor = a[i][k];
            for j in 0..7 {
                a[i][j] -= factor * a[k][j];
                b[i][j] -= factor * b[k][j];
            }
        }
    }
    b
}
fn num(out: &mut String, x: f64) {
    write!(out, "{x:.17e}").unwrap();
}
fn pair(out: &mut String, x: Interval) {
    out.push('[');
    num(out, x.lo);
    out.push(',');
    num(out, x.hi);
    out.push(']');
}
fn jet(out: &mut String, x: &Jet) {
    out.push_str("{\"value\":");
    pair(out, x.value);
    out.push_str(",\"gradient\":[");
    for i in 0..7 {
        if i > 0 {
            out.push(',');
        }
        pair(out, x.gradient[i]);
    }
    out.push_str("],\"hessian\":[");
    for i in 0..7 {
        if i > 0 {
            out.push(',');
        }
        out.push('[');
        for j in 0..7 {
            if j > 0 {
                out.push(',');
            }
            pair(out, x.hessian[i][j]);
        }
        out.push(']');
    }
    out.push_str("]}");
}
fn site(out: &mut String, model: &Ft03Model, id: &str, dt: f64, state: &HHeState, factor: f64) {
    let center = scaled(model, state);
    let bx: [Interval; 7] = std::array::from_fn(|i| {
        let r = factor * RADII[i];
        Interval::new(down(center[i] - r), up(center[i] + r)).unwrap()
    });
    let rhs = ft03_interval_rhs(model, &bx).expect("FT03 interval box");
    let at_center: [Interval; 7] = center.map(|v| Interval::point(v).unwrap());
    let cj = ft03_interval_rhs(model, &at_center).expect("FT03 center jet");
    let mut a = [[0.0; 7]; 7];
    for i in 0..7 {
        for j in 0..7 {
            let grad = cj[i].gradient[j];
            a[i][j] = if i == j { 1.0 } else { 0.0 } - dt * (grad.lo / 2.0 + grad.hi / 2.0);
        }
    }
    let inv = invert(a);
    write!(out, "{{\"id\":\"{id}\",\"step_s\":").unwrap();
    num(out, dt);
    out.push_str(",\"center\":[");
    for i in 0..7 {
        if i > 0 {
            out.push(',');
        }
        num(out, center[i]);
    }
    out.push_str("],\"box\":[");
    for i in 0..7 {
        if i > 0 {
            out.push(',');
        }
        pair(out, bx[i]);
    }
    out.push_str("],\"preconditioner\":[");
    for i in 0..7 {
        if i > 0 {
            out.push(',');
        }
        out.push('[');
        for j in 0..7 {
            if j > 0 {
                out.push(',');
            }
            num(out, inv[i][j]);
        }
        out.push(']');
    }
    out.push_str("],\"interval_rhs\":[");
    for i in 0..7 {
        if i > 0 {
            out.push(',');
        }
        jet(out, &rhs[i]);
    }
    out.push_str("]}");
}
fn main() {
    let model = Ft03Model::controlled().expect("controlled FT03 model");
    let initial = model.initial_state();
    let control = StepControl {
        residual_tolerance: 1e-13,
        max_iterations: 200,
    };
    let full = ft03_implicit_step(&model, &initial, 1e9, control).expect("full BE center");
    let half1 = ft03_implicit_step(&model, &initial, 5e8, control).expect("half1 BE center");
    let half2 = ft03_implicit_step(&model, &half1.state, 5e8, control).expect("half2 BE center");
    let mut out = String::new();
    write!(out,"{{\"model_id\":\"{FT03_MODEL_ID}\",\"parent_manifest_sha256\":\"{MANIFEST_SHA}\",\"parent_center_bits\":[").unwrap();
    for (i, v) in scaled(&model, &initial).iter().enumerate() {
        if i > 0 {
            out.push(',');
        }
        write!(out, "\"{:016x}\"", v.to_bits()).unwrap();
    }
    out.push_str("],\"sites\":[");
    site(&mut out, &model, "FULL_BE_ENDPOINT", 1e9, &full.state, 1.3);
    out.push(',');
    site(
        &mut out,
        &model,
        "HALF1_BE_ENDPOINT",
        5e8,
        &half1.state,
        1.3,
    );
    out.push(',');
    site(
        &mut out,
        &model,
        "HALF2_BE_ENDPOINT",
        5e8,
        &half2.state,
        1.8,
    );
    out.push_str("]}");
    println!("{out}");
}
