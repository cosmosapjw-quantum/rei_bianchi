use rei_iso_couple_reference::birth_clock::uniform_partition;
fn main() {
    println!("tau,old,births,surviving,absorbed");
    let mut ts = vec![
        0.,
        0.000999999999,
        0.001,
        0.001000000001,
        1.,
        100.,
        1e20,
        1e100,
        1e300,
        f64::from_bits(1),
        800.,
    ];
    for e in -300..=3 {
        ts.push(10f64.powi(e));
    }
    for t in ts {
        for (n, b) in [
            (0., 1.),
            (2., 3.),
            (1e-30, 1.),
            (1., 1e-30),
            (1e300, 0.),
            (0., 1e300),
        ] {
            let p = uniform_partition(n, b, t).unwrap();
            println!(
                "{t:.17e},{n:.17e},{b:.17e},{:.17e},{:.17e}",
                p.surviving, p.absorbed
            );
        }
    }
}
