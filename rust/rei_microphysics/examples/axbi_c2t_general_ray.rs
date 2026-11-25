use rei_microphysics::general_ray::canonical_ray;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let raw = std::fs::read_to_string(std::env::args().nth(1).ok_or("input")?)?;
    println!("case,id,u,energy_scale,nx,ny,nz,jacobian");
    for line in raw.lines().skip(1) {
        let v: Vec<_> = line.split(',').collect();
        if v.len() != 24 {
            return Err("shape".into());
        }
        let f = v[2..]
            .iter()
            .map(|s| s.parse::<f64>())
            .collect::<Result<Vec<_>, _>>()?;
        let c0 = std::array::from_fn(|i| std::array::from_fn(|j| f[4 + 3 * i + j]));
        let c1 = std::array::from_fn(|i| std::array::from_fn(|j| f[13 + 3 * i + j]));
        let p = canonical_ray(c0, c1, [f[1], f[2], f[3]])?;
        println!(
            "{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            v[0],
            v[1],
            f[0],
            p.energy_scale,
            p.direction[0],
            p.direction[1],
            p.direction[2],
            p.jacobian
        );
    }
    Ok(())
}
