use rei_microphysics::spectral_ff::SpectralFf;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = std::env::args().skip(1).collect::<Vec<_>>();
    let n: usize = args[1].parse()?;
    let xmin: f64 = args[2].parse()?;
    let absolute = args[3] == "absolute";
    let mut s = SpectralFf::new(xmin, 60., n)?;
    let mut work = 0.;
    let mut net = 0.;
    let mut thin = 0.;
    let mut abs = 0.;
    let mut emission = 0.;
    let mut peak_tau = 0_f64;
    let mut peak_thick = 0usize;
    let mut endbb = 0.;
    println!("a,net,thin,emission,planck_abs,work,U,peak_tau,peak_thick,ratio");
    for l in std::fs::read_to_string(&args[0])?.lines().skip(1) {
        let v = l
            .split(',')
            .map(str::parse::<f64>)
            .collect::<Result<Vec<_>, _>>()?;
        let [a, t, tc, f, b, bb0, bbmid, bb1]: [f64; 8] =
            v.try_into().map_err(|_| "stage shape")?;
        let old = s.energy(bb0)?;
        let q = s.advance(t, tc, f, b, bbmid, absolute)?;
        let u = s.energy(bb1)?;
        work += old + q.net - u;
        net += q.net;
        thin += q.thin_net;
        abs += q.planck_abs;
        emission += q.emission;
        peak_tau = peak_tau.max(q.max_tau);
        peak_thick = peak_thick.max(q.thick_cells);
        endbb = bb1;
        println!("{a:.17e},{net:.17e},{thin:.17e},{emission:.17e},{abs:.17e},{work:.17e},{u:.17e},{peak_tau:.17e},{peak_thick},{:.17e}",q.absolute_ratio);
    }
    let mut out = String::from("x,delta\n");
    for (x, d) in s.x.iter().zip(s.delta.iter()) {
        out += &format!("{x:.17e},{d:.17e}\n");
    }
    std::fs::write(&args[4], out)?;
    eprintln!("final_energy={:.17e}", s.energy(endbb)?);
    Ok(())
}
