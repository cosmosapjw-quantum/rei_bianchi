use std::{
    fs::{self, File},
    io::{BufWriter, Write},
    time::Instant,
};
const EC: f64 = 13.6;
const G8: [(f64, f64); 8] = [
    (-0.9602898564975363, 0.1012285362903763),
    (-0.7966664774136267, 0.2223810344533745),
    (-0.5255324099163290, 0.3137066458778873),
    (-0.1834346424956498, 0.3626837833783620),
    (0.1834346424956498, 0.3626837833783620),
    (0.5255324099163290, 0.3137066458778873),
    (0.7966664774136267, 0.2223810344533745),
    (0.9602898564975363, 0.1012285362903763),
];
const G16: [(f64, f64); 16] = [
    (-0.9894009349916499, 0.0271524594117541),
    (-0.9445750230732326, 0.0622535239386479),
    (-0.8656312023878318, 0.0951585116824928),
    (-0.7554044083550030, 0.1246289712555339),
    (-0.6178762444026438, 0.1495959888165767),
    (-0.4580167776572274, 0.1691565193950025),
    (-0.2816035507792589, 0.1826034150449236),
    (-0.0950125098376374, 0.1894506104550685),
    (0.0950125098376374, 0.1894506104550685),
    (0.2816035507792589, 0.1826034150449236),
    (0.4580167776572274, 0.1691565193950025),
    (0.6178762444026438, 0.1495959888165767),
    (0.7554044083550030, 0.1246289712555339),
    (0.8656312023878318, 0.0951585116824928),
    (0.9445750230732326, 0.0622535239386479),
    (0.9894009349916499, 0.0271524594117541),
];
#[derive(Clone, Copy, Debug)]
struct Cell {
    l: f64,
    r: f64,
    a: f64,
    b: f64,
}
fn moments(c: Cell) -> (f64, f64) {
    let d = c.r - c.l;
    let n = d * c.a;
    (n, (c.l + c.r) * 0.5 * n + d * d * c.b / 6.)
}
fn dg_rhs(c: Cell, fl: f64, fr: f64) -> (f64, f64) {
    let d = c.r - c.l;
    (
        -(fr - fl) / d,
        -3. * (fr + fl) / d - 6. * moments(c).1 / (d * d),
    )
}
fn limit(c: &mut Cell) -> Result<f64, String> {
    if c.a < 0. {
        return Err(format!("negative mean: {:?}", c));
    }
    let old = c.b;
    if c.a - c.b.abs() < 0. {
        c.b = c.b.signum() * c.a;
    } // Algebraically b*=a/|b|, no density floor.
    Ok((c.r - c.l).powi(2) * (c.b - old) / 6.)
}
fn panel(l: f64, r: f64, a: f64, s: f64) -> (f64, f64, f64, f64, f64) {
    let cut = s.max(l).min(r);
    let n = a * (r - cut);
    let no = a * (cut - l);
    let u = EC * (-s).exp() * a * cut.exp() * (r - cut).exp_m1();
    let eo = EC * no;
    let w = EC * a * (l.exp() * (cut - l).exp_m1() - (cut - l))
        + EC * a * (-(-s).exp_m1()) * cut.exp() * (r - cut).exp_m1();
    (n, u, no, eo, w)
}
fn node(x: f64, m: f64, s: f64) -> (f64, f64, f64, f64, f64) {
    let age = s.min(x);
    let work = m * EC * x.exp() * (-(-age).exp_m1());
    if x > s {
        (m, m * EC * (x - age).exp(), 0., 0., work)
    } else {
        (0., 0., m, EC * m, work)
    }
}
fn fluxes(c: &[Cell]) -> Vec<f64> {
    let mut f = Vec::with_capacity(c.len() + 1);
    for x in c {
        f.push(-x.l * (x.a - x.b));
    }
    f.push(0.);
    f
}
fn totals(c: &[Cell]) -> (f64, f64) {
    c.iter()
        .map(|x| moments(*x))
        .fold((0., 0.), |a, b| (a.0 + b.0, a.1 + b.1))
}
struct State {
    cells: Vec<Cell>,
    no: f64,
    eo: f64,
    w: f64,
    du: f64,
    abs_du: f64,
    lim_count: usize,
    min_raw: f64,
    steps: usize,
}
impl State {
    fn new(cells: Vec<Cell>) -> Self {
        Self {
            cells,
            no: 0.,
            eo: 0.,
            w: 0.,
            du: 0.,
            abs_du: 0.,
            lim_count: 0,
            min_raw: 0.,
            steps: 0,
        }
    }
}
fn step(st: &mut State, dt: f64, dg: bool, limited: bool) -> Result<(), String> {
    let f0 = fluxes(&st.cells);
    let u0 = totals(&st.cells).1;
    let mut stage = Vec::with_capacity(st.cells.len());
    let mut du1 = 0.;
    let mut adu1 = 0.;
    for (i, c) in st.cells.iter().enumerate() {
        let (da, db) = if dg {
            dg_rhs(*c, f0[i], f0[i + 1])
        } else {
            (-(f0[i + 1] - f0[i]) / (c.r - c.l), 0.)
        };
        let mut q = Cell {
            a: c.a + dt * da,
            b: c.b + dt * db,
            ..*c
        };
        st.min_raw = st.min_raw.min(q.a - q.b.abs());
        if limited {
            let old = q.b;
            let du = limit(&mut q)?;
            du1 += du;
            adu1 += du.abs();
            if q.b != old {
                st.lim_count += 1;
            }
        }
        stage.push(q);
    }
    let f1 = fluxes(&stage);
    let u1 = totals(&stage).1;
    let mut du2 = 0.;
    let mut adu2 = 0.;
    for (i, c) in st.cells.iter_mut().enumerate() {
        let (da, db) = if dg {
            dg_rhs(stage[i], f1[i], f1[i + 1])
        } else {
            (-(f1[i + 1] - f1[i]) / (c.r - c.l), 0.)
        };
        let mut q = Cell {
            a: 0.5 * c.a + 0.5 * (stage[i].a + dt * da),
            b: 0.5 * c.b + 0.5 * (stage[i].b + dt * db),
            ..*c
        };
        st.min_raw = st.min_raw.min(q.a - q.b.abs());
        if limited {
            let old = q.b;
            let du = limit(&mut q)?;
            du2 += du;
            adu2 += du.abs();
            if q.b != old {
                st.lim_count += 1;
            }
        }
        *c = q;
    }
    let out = -0.5 * dt * (f0[0] + f1[0]);
    st.no += out;
    st.eo += st.cells[0].l * out;
    st.w += 0.5 * dt * (u0 + u1);
    st.du += 0.5 * du1 + du2;
    st.abs_du += 0.5 * adu1 + adu2;
    st.steps += 1;
    Ok(())
}
fn bump(x: f64, c: f64) -> f64 {
    let z = (x - 0.65) / 0.25;
    if z.abs() >= 1. {
        0.
    } else {
        c * (-1. / (1. - z * z)).exp()
    }
}
fn integrate<F: Fn(f64) -> f64>(l: f64, r: f64, rule: &[(f64, f64)], f: F) -> f64 {
    if r <= l {
        return 0.;
    }
    let d = (r - l) * 0.5;
    let m = (r + l) * 0.5;
    rule.iter().map(|(q, w)| d * w * f(m + d * q)).sum()
}
#[derive(Clone)]
struct Init {
    cells: Vec<Cell>,
    panels: Vec<(f64, f64, f64)>,
    nodes: Vec<(f64, f64)>,
    zeros: usize,
    zero_n_bound: f64,
}
fn initial(n: usize, c: f64) -> Init {
    let l = (100. / EC).ln();
    let dx = l / n as f64;
    let mut out = Init {
        cells: vec![],
        panels: vec![],
        nodes: vec![],
        zeros: 0,
        zero_n_bound: 0.,
    };
    for i in 0..n {
        let xl = i as f64 * dx;
        let xr = (i + 1) as f64 * dx;
        let el = EC * xl.exp();
        let er = EC * xr.exp();
        let mut nn = 0.;
        let mut uu = 0.;
        for (q, w) in G8 {
            let x = (xl + xr) * 0.5 + 0.5 * dx * q;
            let gg = bump(x, c);
            let geom = 0.5 * dx * w;
            if gg == 0. && (x > 0.4 && x < 0.9) {
                out.zeros += 1;
                out.zero_n_bound += geom * c * (-700f64).exp();
            }
            let ww = geom * gg;
            out.nodes.push((x, ww));
            nn += ww;
            uu += EC * x.exp() * ww;
        }
        out.cells.push(Cell {
            l: el,
            r: er,
            a: nn / (er - el),
            b: 6. * (uu - 0.5 * (el + er) * nn) / (er - el).powi(2),
        });
        out.panels.push((xl, xr, nn / dx));
    }
    out
}
fn cell_mass(c: Cell, l: f64, r: f64) -> f64 {
    if r <= l {
        return 0.;
    }
    let mid = 0.5 * (c.l + c.r);
    c.a * (r - l) + c.b * ((r - mid).powi(2) - (l - mid).powi(2)) / (c.r - c.l)
}
fn negative_mass(c: Cell) -> f64 {
    let hl = c.a - c.b;
    let hr = c.a + c.b;
    let d = c.r - c.l;
    if hl >= 0. && hr >= 0. {
        0.
    } else if hl <= 0. && hr <= 0. {
        -d * c.a
    } else {
        0.5 * d * hl.min(hr).powi(2) / (hr - hl).abs()
    }
}
fn density_shape(cs: &[Cell], s: f64, c: f64, rule: &[(f64, f64)]) -> f64 {
    cs.iter()
        .map(|cell| {
            let mid = 0.5 * (cell.l + cell.r);
            integrate(cell.l, cell.r, rule, |e| {
                let h = cell.a + cell.b * 2. * (e - mid) / (cell.r - cell.l);
                (h - bump((e / EC).ln() + s, c) / e).abs()
            })
        })
        .sum()
}
fn panel_shape(ps: &[(f64, f64, f64)], s: f64, c: f64, rule: &[(f64, f64)]) -> f64 {
    ps.iter()
        .map(|(l, r, a)| {
            integrate((l - s).max(0.), (r - s).max(0.), rule, |x| {
                (a - bump(x + s, c)).abs()
            })
        })
        .sum()
}
fn write_row(
    w: &mut BufWriter<File>,
    method: &str,
    n: usize,
    cfl: f64,
    s: f64,
    v: (f64, f64, f64, f64, f64),
    n0: f64,
    u0_pre: f64,
    u0_post: f64,
    initial_du: f64,
    du: f64,
    abs_du: f64,
    min: f64,
    neg: f64,
    l1_8: f64,
    l1_16: f64,
    bins: [f64; 32],
    steps: usize,
    lim_count: usize,
    min_raw: f64,
    init_count: usize,
    zero_count: usize,
    zero_bound: f64,
    secs: f64,
) {
    let (nn, u, no, eo, work) = v;
    let stock_min = if method == "stock" { min } else { f64::NAN };
    let min = if method == "stock" { f64::NAN } else { min };
    write!(w,"{method},{n},{cfl:.17e},{s:.17e},{nn:.17e},{u:.17e},{no:.17e},{eo:.17e},{work:.17e},{n0:.17e},{u0_pre:.17e},{u0_post:.17e},{initial_du:.17e},{du:.17e},{abs_du:.17e},{:.17e},{:.17e},{:.17e},{min:.17e},{neg:.17e},{l1_8:.17e},{l1_16:.17e},{steps},{lim_count},{min_raw:.17e},{init_count},{zero_count},{zero_bound:.17e},{secs:.9e}",(nn+no-n0)/n0,(u+eo+work-u0_post)/u0_post,(u+eo+work-u0_pre)/u0_pre).unwrap();
    write!(w, ",{:.17e}", stock_min).unwrap();
    for b in bins {
        write!(w, ",{b:.17e}").unwrap();
    }
    writeln!(w).unwrap();
    w.flush().unwrap();
}
fn cases(c: f64, outdir: &str) -> Result<(), String> {
    fs::create_dir_all(outdir).map_err(|e| e.to_string())?;
    let epochs: [f64; 9] = [0., 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.];
    let l = (100. / EC).ln();
    let mut w = BufWriter::new(File::create(format!("{outdir}/results.csv")).unwrap());
    write!(w,"method,n,cfl,s,N,U,Nout,Eout,W,N0,U0_pre,U0_post,initial_du,stage_du,stage_abs_du,Nres,Eres_post,Eres_pre,min_density,negative_mass,L1_GL8,L1_GL16,steps,lim_count,min_raw_stage,initial_limit_count,zero_nodes,zero_N_bound,case_seconds,stock_min_weight").unwrap();
    for j in 0..32 {
        write!(w, ",bin{j}").unwrap();
    }
    writeln!(w).unwrap();
    for n in [32, 64, 128, 256] {
        for method in ["stock", "partial"] {
            let clock = Instant::now();
            let init = initial(n, c);
            let n0 = init.nodes.iter().map(|x| x.1).sum();
            let u0 = if method == "stock" {
                init.nodes.iter().map(|(x, m)| EC * x.exp() * m).sum()
            } else {
                init.panels
                    .iter()
                    .map(|(a, b, m)| panel(*a, *b, *m, 0.).1)
                    .sum()
            };
            for s in epochs {
                let mut v = (0., 0., 0., 0., 0.);
                let mut bins = [0.; 32];
                let (l18, l116, min) = if method == "stock" {
                    for (x, m) in &init.nodes {
                        let q = node(*x, *m, s);
                        v.0 += q.0;
                        v.1 += q.1;
                        v.2 += q.2;
                        v.3 += q.3;
                        v.4 += q.4;
                        if *x > s {
                            let j = ((x - s) / l * 32.).floor() as usize;
                            if j < 32 {
                                bins[j] += m;
                            }
                        }
                    }
                    (
                        f64::NAN,
                        f64::NAN,
                        init.nodes.iter().map(|x| x.1).fold(f64::INFINITY, f64::min),
                    )
                } else {
                    for (a, b, m) in &init.panels {
                        let q = panel(*a, *b, *m, s);
                        v.0 += q.0;
                        v.1 += q.1;
                        v.2 += q.2;
                        v.3 += q.3;
                        v.4 += q.4;
                        for (j, bin) in bins.iter_mut().enumerate() {
                            let lo = (j as f64 * l / 32. + s).max(*a);
                            let hi = ((j + 1) as f64 * l / 32. + s).min(*b);
                            *bin += m * (hi - lo).max(0.);
                        }
                    }
                    (
                        panel_shape(&init.panels, s, c, &G8),
                        panel_shape(&init.panels, s, c, &G16),
                        0.,
                    )
                };
                write_row(
                    &mut w,
                    method,
                    n,
                    0.,
                    s,
                    v,
                    n0,
                    u0,
                    u0,
                    0.,
                    0.,
                    0.,
                    min,
                    0.,
                    l18,
                    l116,
                    bins,
                    0,
                    0,
                    0.,
                    0,
                    init.zeros,
                    init.zero_n_bound,
                    clock.elapsed().as_secs_f64(),
                );
            }
            println!("completed {method} n={n}");
        }
    }
    for method in ["fv", "dg", "dg_limited"] {
        for (n, cfl) in [
            (32, 0.075),
            (64, 0.075),
            (128, 0.075),
            (256, 0.075),
            (128, 0.15),
            (128, 0.0375),
        ] {
            let clock = Instant::now();
            let init = initial(n, c);
            let mut cells = init.cells.clone();
            if method == "fv" {
                for cell in &mut cells {
                    cell.b = 0.;
                }
            }
            let (n0, u0_pre) = totals(&cells);
            let mut idu = 0.;
            let mut icount = 0;
            if method == "dg_limited" {
                for cell in &mut cells {
                    let old = cell.b;
                    idu += limit(cell)?;
                    if old != cell.b {
                        icount += 1;
                    }
                }
            }
            let u0_post = totals(&cells).1;
            let zero_count = init.zeros;
            let zero_bound = init.zero_n_bound;
            drop(init);
            let mut st = State::new(cells);
            let max_dt = cfl
                * st.cells
                    .iter()
                    .map(|x| (x.r - x.l) / x.r)
                    .fold(f64::INFINITY, f64::min);
            let mut prev = 0.;
            for s in epochs {
                let k = ((s - prev) / max_dt).ceil() as usize;
                if k > 0 {
                    let dt = (s - prev) / k as f64;
                    for _ in 0..k {
                        step(&mut st, dt, method != "fv", method == "dg_limited")?;
                    }
                }
                prev = s;
                let (nn, u) = totals(&st.cells);
                let min = st
                    .cells
                    .iter()
                    .map(|x| x.a - x.b.abs())
                    .fold(f64::INFINITY, f64::min);
                let neg = st.cells.iter().map(|x| negative_mass(*x)).sum();
                let mut bins = [0.; 32];
                for (j, bin) in bins.iter_mut().enumerate() {
                    let el = EC * (j as f64 * l / 32.).exp();
                    let er = EC * ((j + 1) as f64 * l / 32.).exp();
                    for cell in &st.cells {
                        *bin += cell_mass(*cell, el.max(cell.l), er.min(cell.r));
                    }
                }
                write_row(
                    &mut w,
                    method,
                    n,
                    cfl,
                    s,
                    (nn, u, st.no, st.eo, st.w),
                    n0,
                    u0_pre,
                    u0_post,
                    idu,
                    st.du,
                    st.abs_du,
                    min,
                    neg,
                    density_shape(&st.cells, s, c, &G8),
                    density_shape(&st.cells, s, c, &G16),
                    bins,
                    st.steps,
                    st.lim_count,
                    st.min_raw,
                    icount,
                    zero_count,
                    zero_bound,
                    clock.elapsed().as_secs_f64(),
                );
            }
            println!("completed {method} n={n} cfl={cfl} steps={}", st.steps);
        }
    }
    Ok(())
}
include!("tests.rs");
fn main() {
    let a: Vec<String> = std::env::args().collect();
    if a.len() != 3 {
        panic!("usage: bench NORMALIZATION OUTPUT_DIR");
    }
    cases(a[1].parse().unwrap(), &a[2]).unwrap();
}
