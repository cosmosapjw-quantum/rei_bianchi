use rei_microphysics::{
    axbi_covariant_driver::{Driver, DriverConfig},
    general_angular::{Coframe, GeneralAngular},
};
fn metric(v: &[f64]) -> Coframe {
    std::array::from_fn(|i| std::array::from_fn(|j| v[1] * v[8 + 3 * i + j]))
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let data = std::fs::read_to_string(&args[0])?
        .lines()
        .skip(1)
        .map(|l| {
            l.split(',')
                .map(str::parse::<f64>)
                .collect::<Result<Vec<_>, _>>()
        })
        .collect::<Result<Vec<_>, _>>()?;
    let mut history = vec![];
    for i in 0..=128 {
        let k = i * (data.len() - 1) / 128;
        history.push(metric(&data[k]));
    }
    let cfg = DriverConfig::read(&std::fs::read_to_string(&args[1])?)?;
    let (d, _) = Driver::new(cfg)?;
    let mut lrs = vec![];
    for i in 0..=128 {
        let a = if i == 128 {
            0.2
        } else {
            (1. / 21.) * (21_f64 / 5.).powf(i as f64 / 128.)
        };
        let b = d.background.point_at_scale(a)?.b;
        lrs.push([
            [a * (-b).exp(), 0., 0.],
            [0., a * (-b).exp(), 0.],
            [0., 0., a * (2. * b).exp()],
        ]);
    }
    println!("case,mode,nmu,nphi,max_area_error,max_dipole,max_stf_pressure");
    for (name, h) in [("actual_bass", history), ("strong_lrs", lrs)] {
        for (mode, center) in [
            ("plain", h[0]),
            (
                "balanced",
                if name == "strong_lrs" {
                    let a = 1. / 21.;
                    let b = d.background.point_at_scale(0.2)?.b / 2.;
                    [
                        [a * (-b).exp(), 0., 0.],
                        [0., a * (-b).exp(), 0.],
                        [0., 0., a * (2. * b).exp()],
                    ]
                } else {
                    h[64]
                },
            ),
        ] {
            for n in [8, 16, 32] {
                let g = GeneralAngular::new(h[0], center, n, n * 2)?;
                let mut ar = 0_f64;
                let mut dp = 0_f64;
                let mut pp = 0_f64;
                for &c in &h {
                    let s = g.source_at(c)?;
                    ar = ar.max((s.raw_area - 1.).abs());
                    dp = dp.max(s.dipole.iter().map(|x| x * x).sum::<f64>().sqrt());
                    let mut p = 0.;
                    for i in 0..3 {
                        for j in 0..3 {
                            p += (s.pressure[i][j] - if i == j { 1. / 3. } else { 0. }).powi(2);
                        }
                    }
                    pp = pp.max(p.sqrt());
                }
                println!("{name},{mode},{n},{},{ar:.17e},{dp:.17e},{pp:.17e}", n * 2);
            }
        }
    }
    Ok(())
}
