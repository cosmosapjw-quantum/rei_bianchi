//! Research-only native moving threshold with prescribed gas and exact source birth.
use rei_microphysics::axbi_covariant_driver::{compiled_identity, Driver, DriverConfig};
use rei_microphysics::HHeModel;
use std::{
    fs,
    io::{BufWriter, Write},
    path::Path,
    time::Instant,
};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let v = std::env::args().skip(1).collect::<Vec<_>>();
    if v.len() != 5 {
        return Err("usage config q split|full schedule.csv output_dir".into());
    }
    let mut c = DriverConfig::read(&fs::read_to_string(&v[0])?)?;
    c.transport_cells = v[1].parse()?;
    c.energy_budget_ev_per_h = 0.;
    if c.q_ref != 0. {
        return Err("only FLRW prescribed gas campaign".into());
    }
    let split = match v[2].as_str() {
        "split" => true,
        "full" => false,
        _ => return Err("mode".into()),
    };
    let (d, _) = Driver::new(c)?;
    let tr = &d.transport;
    let raw = fs::read_to_string(&v[3])?;
    let out = Path::new(&v[4]);
    fs::create_dir(out)?;
    fs::write(out.join("source_identity.txt"), compiled_identity())?;
    fs::write(out.join("schedule.csv"), raw.as_bytes())?;
    let mut file = BufWriter::new(fs::File::create(out.join("history.csv"))?);
    writeln!(file,"step,a,z,source_N,source_U,absorbed_HI,absorbed_HeI,absorbed_HeII,absorbed_binding,absorbed_heat,absorbed_U,redshift_work,N,U,N_defect,E_defect,Gamma_HI,Gamma_HeI,Gamma_HeII,heat_HI,heat_HeI,heat_HeII,above_N")?;
    let ev = HHeModel::controlled_fixture().ev_erg;
    let mut p = tr.empty_state();
    let mut pools = tr.empty_heii();
    let mut source = [0.; 2];
    let mut ab = [0.; 3];
    let (mut binding, mut heat, mut work) = (0., 0., 0.);
    let mut before = 1. / 21.;
    let start = Instant::now();
    let mut steps = 0;
    for (index, line) in raw.lines().skip(1).enumerate() {
        let x: Vec<f64> = line.split(',').map(str::parse).collect::<Result<_, _>>()?;
        if x.len() != 9 {
            return Err("schedule shape".into());
        }
        let (a, m, b) = (x[0], x[1], x[2]);
        if a != before || a >= m || m >= b {
            return Err("schedule order".into());
        }
        let gp = d.background.point_at_scale(a)?.geometry()?;
        let gm = d.background.point_at_scale(m)?.geometry()?;
        let gn = d.background.point_at_scale(b)?.geometry()?;
        let nh = d.n_h0_cm3 / m.powi(3);
        let nhe = d.n_he0_cm3 / m.powi(3);
        let abs = [nh * (1. - x[3]), nhe * (1. - x[4] - x[5]), nhe * x[4]];
        let dt = d.background.interval_increment(a, b)?.proper_time_s;
        let old = if split {
            tr.heii_inventory(&pools, &gp)?
        } else {
            tr.inventory(&p, &gp)?
        };
        let mid_old = if split {
            pools = tr.move_heii(&pools, &gm)?;
            tr.heii_inventory(&pools, &gm)?
        } else {
            tr.inventory(&p, &gm)?
        };
        work += old.1 - mid_old.1;
        let emitted;
        let absorbed;
        let bnd;
        let ht;
        let mid_new;
        if split {
            let (birth, l) = tr.inject_heii(&gm, 1. / m - 1., dt)?;
            let r = tr.advance_heii(&pools, &birth, &gm, abs, nh, dt)?;
            emitted = l;
            absorbed = r.absorbed_per_h;
            bnd = r.binding_ev_per_h;
            ht = r.heat_ev_per_h;
            pools = r.state;
            mid_new = tr.heii_inventory(&pools, &gm)?;
            pools = tr.move_heii(&pools, &gn)?;
        } else {
            let mut birth = tr.empty_state();
            emitted = tr.inject(&mut birth, &gm, 1. / m - 1., dt)?;
            let r = tr.prepare(&p, &gm)?.evaluate_continuous_birth(
                &tr.prepare(&birth, &gm)?,
                abs,
                nh,
                dt,
            )?;
            absorbed = r.absorbed_per_h;
            bnd = r.binding_ev_per_h;
            ht = r.heat_ev_per_h;
            p = r.state;
            mid_new = tr.inventory(&p, &gm)?;
        }
        source[0] += emitted.added_photons_per_h;
        source[1] += emitted.added_energy_ev_per_h;
        for k in 0..3 {
            ab[k] += absorbed[k]
        }
        binding += bnd;
        heat += ht;
        let inv = if split {
            tr.heii_inventory(&pools, &gn)?
        } else {
            tr.inventory(&p, &gn)?
        };
        work += mid_new.1 - inv.1;
        let ndef = inv.0 + ab.iter().sum::<f64>() - source[0];
        let edef = inv.1 + binding + heat + work - source[1];
        if ndef.abs() > 1e-10 * source[0].max(1.) || edef.abs() > 1e-10 * source[1].max(1.) {
            return Err("photon ledger".into());
        }
        let nhend = d.n_h0_cm3 / b.powi(3);
        let r = if split {
            tr.heii_endpoint_photo(&pools, &gn, nhend)?
        } else {
            tr.prepare(&p, &gn)?.evaluate([0.; 3], nhend, 0.)?.photo
        };
        let an = if split {
            pools.above.number.iter().sum::<f64>()
        } else {
            tr.partition_heii(&p, &gn)?.above.number.iter().sum::<f64>()
        };
        let data = [
            b,
            1. / b - 1.,
            source[0],
            source[1],
            ab[0],
            ab[1],
            ab[2],
            binding,
            heat,
            binding + heat,
            work,
            inv.0,
            inv.1,
            ndef,
            edef,
            r.gamma_s[0],
            r.gamma_s[1],
            r.gamma_s[2],
            r.heat_erg_per_absorber_s[0] / ev,
            r.heat_erg_per_absorber_s[1] / ev,
            r.heat_erg_per_absorber_s[2] / ev,
            an,
        ];
        write!(file, "{}", index + 1)?;
        for y in data {
            if !y.is_finite() {
                return Err("nonfinite".into());
            }
            write!(file, ",{y:.17e}")?
        }
        writeln!(file)?;
        before = b;
        steps = index + 1;
    }
    file.flush()?;
    if before != 0.2 {
        return Err("missing endpoint".into());
    }
    fs::write(
        out.join("RETURN.txt"),
        format!(
            "status=COMPLETE_PRESCRIBED_GAS\nq={}\nmode={}\nsteps={}\nwall_s={}\n",
            v[1],
            v[2],
            steps,
            start.elapsed().as_secs_f64()
        ),
    )?;
    println!(
        "COMPLETE {} q={} steps={} (ledger in history.csv)",
        v[2], v[1], steps
    );
    Ok(())
}
