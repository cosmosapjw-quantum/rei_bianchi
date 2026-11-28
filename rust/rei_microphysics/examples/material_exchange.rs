//! Read an explicit proper-cell state and chronological, source-qualified extents on stdin.
use rei_microphysics::{
    igm_state::IgmGasState,
    material_transfer::{Cell, Process, Target, Transfer},
    IsotopeSpecies as S,
};
use std::io::{self, Read};
fn number(s: &str) -> Result<f64, String> {
    s.parse().map_err(|_| format!("invalid number {s}"))
}
fn target(s: &str) -> Result<Target, String> {
    match s {
        "HI" => Ok(Target::H),
        "HeI" => Ok(Target::HeI),
        "HeII" => Ok(Target::HeII),
        _ => Err(format!("unknown target {s}")),
    }
}
fn run(input: &str) -> Result<(), String> {
    let mut lines = input
        .lines()
        .filter(|x| !x.trim().is_empty())
        .map(|x| x.split_whitespace().collect::<Vec<_>>());
    let first = lines.next().ok_or("missing cell")?;
    let ["CELL", scenario, t0, t1, nh, nhe, nd, xh, he1, he2, yd, t, photon, projectile] =
        first.as_slice()
    else {
        return Err("expected CELL scenario start end nh_cm3 nhe_cm3 nd_cm3 xhii xheii xheiii ydii T_K photons_eV_m3 projectiles_eV_m3".into());
    };
    let (nh, nhe) = (number(nh)?, number(nhe)?);
    let gas = IgmGasState::from_temperature(
        [number(xh)?, number(he1)?, number(he2)?],
        nh,
        nhe,
        number(t)?,
    )
    .map_err(|e| e.code())?;
    let mut cell = Cell::from_host(
        scenario,
        number(t0)?,
        gas,
        nh,
        nhe,
        number(nd)?,
        number(yd)?,
    )
    .map_err(|e| e.code())?;
    cell.photon_ev_m3 = number(photon)?;
    cell.projectile_ev_m3 = number(projectile)?;
    let mut transfers = Vec::new();
    for fields in lines {
        let [id, ownership, rest @ ..] = fields.as_slice() else {
            return Err("missing event identity".into());
        };
        let embedded = match *ownership {
            "owned" => true,
            "new" => false,
            _ => return Err("event ownership must be new or owned".into()),
        };
        let event = match rest {
            ["CX", j] => Process::ChargeExchange { net_m3: number(j)? },
            ["PHOT", species, z, e] => Process::Photo {
                target: target(species)?,
                absorbed_m3: number(z)?,
                energy_ev: number(e)?,
            },
            ["ESC", z, e] => Process::EscapingLine {
                number_m3: number(z)?,
                energy_ev: number(e)?,
            },
            ["CR", species, z, w, d] => Process::CosmicRay {
                target: target(species)?,
                births_m3: number(z)?,
                born_kinetic_ev_m3: number(w)?,
                threshold_offset_ev_m3: number(d)?,
            },
            _ => return Err("unknown event or wrong field count".into()),
        };
        transfers.push(Transfer {
            event_id: id,
            already_in_host_rhs: embedded,
            process: event,
        });
    }
    let out = cell
        .advance(scenario, number(t0)?, number(t1)?, &transfers)
        .map_err(|e| e.code())?;
    let initial = cell.total_ev_m3();
    let final_energy = out.total_ev_m3();
    let values = [
        ("time_s", out.proper_s),
        ("T_K", out.temperature_k().map_err(|e| e.code())?),
        ("nHII_m3", out.nuclei.density_m3(S::H1Ionized)),
        ("nDII_m3", out.nuclei.density_m3(S::DIonized)),
        ("nHeII_m3", out.nuclei.density_m3(S::He4SinglyIonized)),
        (
            "electron_thermal_m3",
            out.electron_thermal_m3().map_err(|e| e.code())?,
        ),
        ("electron_fast_m3", out.secondary_electrons_m3),
        ("ionization_ev_m3", out.ionization_ev_m3()),
        ("thermal_ev_m3", out.thermal_ev_m3),
        ("born_kinetic_ev_m3", out.secondary_ev_m3),
        ("threshold_offset_ev_m3", out.threshold_offset_ev_m3),
        ("escaped_ev_m3", out.escaped_ev_m3),
        ("photon_remaining_ev_m3", out.photon_ev_m3),
        ("projectile_remaining_ev_m3", out.projectile_ev_m3),
        ("initial_ev_m3", initial),
        ("final_ev_m3", final_energy),
        ("residual_ev_m3", final_energy - initial),
    ];
    for (name, value) in values {
        println!("{name}\t{value:.17e}");
    }
    Ok(())
}
fn main() {
    let mut input = String::new();
    if let Err(err) = io::stdin()
        .read_to_string(&mut input)
        .map_err(|e| e.to_string())
        .and_then(|_| run(&input))
    {
        eprintln!("{err}");
        std::process::exit(2);
    }
}
