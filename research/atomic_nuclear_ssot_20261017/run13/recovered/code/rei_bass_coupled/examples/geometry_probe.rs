#[path = "common/mod.rs"]
mod common;
fn main() {
    println!(
        "case,grid,x,time_s,a,b,h_per_s,s_per_s,x_roundtrip,slope_min,slope_max,hamiltonian,raychaudhuri"
    );
    for case in [
        "COLD_FLRW",
        "WARM_ISOTROPIC",
        "MASSIVE_A_PLUS",
        "MASSIVE_A_MINUS",
        "MASS3_A_PLUS",
        "MASS300_A_PLUS",
        "SIGNED_PLUS",
        "SIGNED_MINUS",
    ] {
        for grid in [121, 241] {
            let g = common::load(case, grid);
            for x in [0., 1e-8, 0.0004, 0.051, 0.7, 1., 1.4, g.x_max()] {
                let p = g.point_at_x(x).unwrap();
                println!(
                    "{case},{grid},{x:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                    p.time_s,
                    p.a,
                    p.b,
                    p.h,
                    p.s,
                    g.x_at_time(p.time_s).unwrap(),
                    g.slope_min,
                    g.slope_max,
                    g.hamiltonian_max,
                    g.raychaudhuri_max
                );
            }
        }
    }
}
