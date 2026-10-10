use rei_microphysics::{
    cold_conditional_ivp as ivp, cold_stage_composition as cold, AxisymmetricPoint,
};
use std::io::{self, BufRead};
fn main() {
    let mut calls = 0;
    let mut steps = 0;
    let mut trajectories = 0;
    for (id, line) in io::stdin().lock().lines().enumerate() {
        let x: Vec<f64> = line
            .unwrap()
            .split_whitespace()
            .map(|v| v.parse().unwrap())
            .collect();
        assert_eq!(x.len(), 7);
        let y = ivp::initial(x[0], x[3], x[4], x[5], x[2]);
        assert!((ivp::hubble(x[0]) - x[1]).abs() / x[1] <= 3e-12);
        let g = AxisymmetricPoint::new(x[0], 0., ivp::hubble(x[0]), 0.).unwrap();
        let s = ivp::physical(&y).unwrap();
        let z = cold::stage(0., g, &s, x[6]).unwrap();
        calls += 1;
        let pos = cold::stage(1., g, &s, x[6]).unwrap();
        calls += 1;
        assert_eq!(z.derivative, pos.derivative);
        assert!(cold::stage(-1., g, &s, x[6]).is_err());
        calls += 1;
        assert!(cold::stage(f64::NAN, g, &s, x[6]).is_err());
        calls += 1;
        for n in [8, 16, 32] {
            trajectories += 1;
            steps += n;
            let epochs=ivp::integrate(y,x[6],n,false,|tau,y,dy,sources|{calls+=1;println!("{{\"kind\":\"stage\",\"id\":{id},\"n\":{n},\"tau\":{tau:.17e},\"y\":{y:?},\"dy\":{dy:?},\"sources\":{sources:?}}}");}).unwrap();
            println!("{{\"kind\":\"trajectory\",\"id\":{id},\"n\":{n},\"control\":\"physical\",\"epochs\":{epochs:?}}}");
        }
        if id == 0 {
            for free in [true, false] {
                let mut yc = y;
                if !free {
                    yc = ivp::initial(x[0], x[3], x[4], 0., x[2]);
                }
                trajectories += 1;
                steps += 32;
                let epochs=ivp::integrate(yc,x[6],32,free,|tau,y,dy,sources|{calls+=1;println!("{{\"kind\":\"control_stage\",\"free\":{free},\"tau\":{tau:.17e},\"y\":{y:?},\"dy\":{dy:?},\"sources\":{sources:?}}}");}).unwrap();
                println!("{{\"kind\":\"trajectory\",\"id\":0,\"n\":32,\"control\":\"{}\",\"epochs\":{epochs:?}}}",if free {"source_free"}else{"xe0"});
            }
        }
    }
    assert_eq!(trajectories, 14);
    assert_eq!(steps, 288);
    assert!(calls <= 1400);
    println!("{{\"kind\":\"accounting\",\"trajectories\":{trajectories},\"steps\":{steps},\"derivative_attempts\":{calls}}}");
}
