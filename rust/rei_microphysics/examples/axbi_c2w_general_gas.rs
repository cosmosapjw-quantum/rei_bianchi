use rei_microphysics::{
    axbi_covariant_driver::{compiled_identity, Driver, DriverConfig},
    general_history::{GeneralHistory, HistoryPoint},
};
use std::{
    fs,
    io::{BufWriter, Write},
    path::Path,
    time::Instant,
};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let p = std::env::args().skip(1).collect::<Vec<_>>();
    let data = fs::read_to_string(&p[0])?
        .lines()
        .skip(1)
        .map(|l| {
            l.split(',')
                .map(str::parse::<f64>)
                .collect::<Result<Vec<_>, _>>()
        })
        .collect::<Result<Vec<_>, _>>()?;
    let h = GeneralHistory::new(
        data.iter()
            .map(|v| HistoryPoint {
                a: v[1],
                h: v[2],
                f: std::array::from_fn(|i| std::array::from_fn(|j| v[8 + 3 * i + j])),
            })
            .collect(),
        p[2].parse()?,
        p[3].parse()?,
    )?;
    let config = DriverConfig::read(&fs::read_to_string(&p[1])?)?;
    let (d, mut s) = Driver::new_general(config, h)?;
    let out = Path::new(&p[4]);
    fs::create_dir(out)?;
    fs::write(out.join("source_identity.txt"), compiled_identity())?;
    fs::write(out.join("config.cfg"), fs::read(&p[1])?)?;
    let mut w = BufWriter::new(fs::File::create(out.join("history.csv"))?);
    writeln!(w,"accepted,a,z,h,time_s,xHII,xHeII,xHeIII,T,ne,J0,Pxx,Pyy,Pzz,Pxy,Pxz,Pyz,Fx,Fy,Fz,Ndef,Edef,source_N,source_U,thermal_work,photon_work,escaped_U,cmb_input,local_error")?;
    let a0 = s.a;
    let mut t = 0.;
    let begin = Instant::now();
    let cap: f64 = p[5].parse()?;
    let end = 1. / (1. + d.config.end_zbar);
    let mut status = "COMPLETE";
    loop {
        let h = d.transport.general_history().unwrap();
        let q = h.point(s.a)?;
        let m = d.general_moments(&s)?;
        let e = s
            .gas
            .eos(d.n_h0_cm3 / s.a.powi(3), d.n_he0_cm3 / s.a.powi(3))?;
        let (nd, ed) = d.residuals(&s)?;
        let f = s.gas.fractions;
        let l = &s.ledgers;
        writeln!(w,"{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",s.accepted,s.a,1./s.a-1.,q.h,t,f[0],f[1],f[2],e.temperature_k,e.electron_density_cm3,m.energy,m.pressure[0][0],m.pressure[1][1],m.pressure[2][2],m.pressure[0][1],m.pressure[0][2],m.pressure[1][2],m.flux[0],m.flux[1],m.flux[2],nd,ed,l.source_n,l.source_u,l.thermal_work,l.photon_work,l.escaped_u,l.cmb_input,s.last_error)?;
        if s.a >= end {
            break;
        }
        if begin.elapsed().as_secs_f64() > cap {
            status = "WALL_CAP";
            break;
        }
        let old = s.a;
        loop {
            match d.adaptive_step(&mut s) {
                Ok(true) => break,
                Ok(false) => {}
                Err(e) => {
                    if s.consecutive_rejects >= 30 || s.next_dln_a < 1e-10 {
                        return Err(format!("{e:?}").into());
                    }
                }
            }
            if s.consecutive_rejects >= 30 || s.next_dln_a < 1e-10 {
                return Err("REJECT_CAP".into());
            }
        }
        t += d.transport.general_history().unwrap().dt(old, s.a)?;
    }
    w.flush()?;
    d.validate(&s, 1e-8)?;
    // A diagnostic terminal stock dump; deliberately not a resumable checkpoint.
    let mut stock = BufWriter::new(fs::File::create(out.join("stocks.csv"))?);
    writeln!(stock, "ray,cell,band,N,Uref,lo,hi")?;
    let ne = d.energies.len();
    for (b, n, u, l, r) in [
        (
            0,
            &s.hi_below.as_ref().unwrap().number,
            &s.hi_below.as_ref().unwrap().energy_ref,
            &s.hi_below.as_ref().unwrap().support_lo,
            &s.hi_below.as_ref().unwrap().support_hi,
        ),
        (
            1,
            &s.photons,
            &s.photon_energy_ref,
            &s.photon_support_lo,
            &s.photon_support_hi,
        ),
        (
            2,
            &s.hei_middle.as_ref().unwrap().number,
            &s.hei_middle.as_ref().unwrap().energy_ref,
            &s.hei_middle.as_ref().unwrap().support_lo,
            &s.hei_middle.as_ref().unwrap().support_hi,
        ),
        (
            3,
            &s.heii_above.as_ref().unwrap().number,
            &s.heii_above.as_ref().unwrap().energy_ref,
            &s.heii_above.as_ref().unwrap().support_lo,
            &s.heii_above.as_ref().unwrap().support_hi,
        ),
    ] {
        for k in 0..n.len() {
            writeln!(
                stock,
                "{},{},{b},{:.17e},{:.17e},{:.17e},{:.17e}",
                k / ne,
                k % ne,
                n[k],
                u[k],
                l[k],
                r[k]
            )?;
        }
    }
    stock.flush()?;
    let mut rays = BufWriter::new(fs::File::create(out.join("rays.csv"))?);
    writeln!(rays, "ray,scale,nx,ny,nz,weight")?;
    let (r, n) = d.transport.general_history().unwrap().rays(s.a)?;
    for i in 0..r.len() {
        writeln!(
            rays,
            "{i},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            r[i].scale, n[i][0], n[i][1], n[i][2], r[i].angular_weight
        )?;
    }
    rays.flush()?;
    fs::write(
        out.join("RETURN.txt"),
        format!(
            "status={status}\ninitial_a={a0:.17e}\na={:.17e}\naccepted={}\nwall_s={:.6}\n",
            s.a,
            s.accepted,
            begin.elapsed().as_secs_f64()
        ),
    )?;
    println!("{status} z={} accepted={}", 1. / s.a - 1., s.accepted);
    Ok(())
}
