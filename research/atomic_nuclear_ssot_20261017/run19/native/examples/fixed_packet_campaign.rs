#[path = "common/mod.rs"]
mod common;
use rei_iso_couple_reference::{
    bass_optical_birth::{BassOpticalBirthBridge, LayerControls},
    bass_source_bridge::BassSourceBridge,
    fixed_packet_split::{FixedPacketSplitBridge, LayerControls as FixedControls},
    isotope_state::IsotopeNumberState,
    isotope_state::IsotopeSpecies as S,
    mixture_eos::MixtureState,
    positive_spectral::SpectralMode,
    retarded_transport::RetardedControls,
};
fn main() {
    let args: Vec<_> = std::env::args().collect();
    let case = args.get(1).map_or("SIGNED_MINUS", |s| s.as_str());
    let steps: usize = args.get(2).map_or("2", |s| s.as_str()).parse().unwrap();
    let grid: usize = args.get(3).map_or("121", |s| s.as_str()).parse().unwrap();
    let split = args.get(4).is_some_and(|s| s == "split");
    let event = args.get(5).is_none_or(|s| s != "off");
    let slices: usize = args.get(6).map_or("2", |s| s.as_str()).parse().unwrap();
    let birth: usize = args.get(7).map_or("4", |s| s.as_str()).parse().unwrap();
    assert!((1..=64).contains(&steps));
    let g = common::load(case, grid);
    let p0 = g.point_at_x(0.7).unwrap();
    let p1 = g.point_at_x(0.7004).unwrap();
    let (full, conf, source) = common::fixture(&g, 0.7);
    let b0 = full.gas.nuclei.moments().unwrap().baryon_density_m3 * p0.a.powi(3);
    let spectrum = if split {
        SpectralMode::SplitPositiveGauss3
    } else {
        SpectralMode::OriginalCellMean
    };
    let ctl = RetardedControls::new(birth, slices, spectrum).unwrap();
    let ctl = if event {
        ctl.with_threshold_events()
    } else {
        ctl
    };
    let growth: f64 = args.get(8).map_or("2.0", |s| s.as_str()).parse().unwrap();
    let optical_scale: f64 = args.get(9).map_or("1.0", |s| s.as_str()).parse().unwrap();
    let bridge = BassOpticalBirthBridge(
        BassSourceBridge::new(source, g, 2.7255).unwrap(),
        ctl,
        LayerControls {
            growth,
            optical_scale,
            ..LayerControls::default()
        },
    );
    let gm = bridge
        .0
        .geometry
        .point_at_time(0.5 * (p0.time_s + p1.time_s))
        .unwrap();
    let r = (p0.a / gm.a).powi(3);
    let vals = S::ALL.map(|s| full.gas.nuclei.density_m3(s) * r);
    let gas_mid = MixtureState {
        nuclei: IsotopeNumberState::new(vals).unwrap(),
        thermal_j_m3: full.gas.thermal_j_m3 * r.powf(5. / 3.),
    };
    let (mut packet, seed, panels) = bridge
        .emit_births(p0.time_s, p1.time_s - p0.time_s, &conf, &gas_mid)
        .unwrap();
    packet.sort_by(|a, b| a.birth_time_s.total_cmp(&b.birth_time_s));
    // Independently output source tuple bits to bind every cohort, not just totals.
    if let Ok(path) = std::env::var("RUN08_PACKET_BITS") {
        let mut bits = Vec::new();
        for co in &packet {
            for f in [
                co.birth_time_s,
                co.energy_at_birth_ev,
                co.direction_at_birth[2],
                co.n_comoving_m3,
            ] {
                bits.extend_from_slice(&f.to_le_bytes());
            }
        }
        std::fs::write(path, bits).unwrap();
    }
    let bridge = FixedPacketSplitBridge(
        bridge.0,
        bridge.1,
        FixedControls {
            growth,
            optical_scale,
            ..FixedControls::default()
        },
        packet,
        seed,
        panels,
    );
    let mut state = bridge.initial(full, &conf, p0.time_s).unwrap();
    let mut emax = 0.0_f64;
    let mut bmax = 0.0_f64;
    let mut photo = [0.0; 4];
    let mut ci = 0.;
    let mut rr = 0.;
    let mut cx = 0.;
    let mut cuts = 0;
    let mut ff = 0.;
    let mut cmb = 0.;
    let mut work_gap = 0.0_f64;
    let mut tau_max = 0.0_f64;
    let mut panels_max = 0_usize;
    for i in 0..steps {
        let goal = if i + 1 == steps {
            p1.time_s
        } else {
            p0.time_s + (p1.time_s - p0.time_s) * (i + 1) as f64 / steps as f64
        };
        let dt = goal - state.time_s;
        let gm = bridge
            .0
            .geometry
            .point_at_time(state.time_s + dt * 0.5)
            .unwrap();
        let vm = gm.a.powi(3);
        let (out, d) = bridge
            .advance_with_diagnostics(&state, &conf, dt)
            .unwrap_or_else(|e| panic!("{case} n={steps} step={i} dt={dt} error={e:?}"));
        tau_max = tau_max.max(d.tau_seed);
        panels_max = panels_max.max(d.panels);
        let d = d.retarded;
        emax = emax.max(out.global_energy_relative_error);
        cuts += d.provider_threshold_cuts;
        for (x, y) in photo.iter_mut().zip(out.chemistry_budget.photo_events_m3) {
            *x += y * vm;
        }
        ci += out.chemistry_budget.ci_events_m3.iter().sum::<f64>() * vm;
        rr += out.chemistry_budget.rr_events_m3.iter().sum::<f64>() * vm;
        cx += out.chemistry_budget.cx_signed_m3 * vm;
        ff += out.chemistry_budget.freefree_integrated_j_m3 * vm;
        cmb += out.chemistry_budget.cmb_change_j_m3 * vm;
        work_gap =
            work_gap.max((d.photon_work_ledger_j_com3 - d.photon_work_independent_j_com3).abs());
        state = out.state;
        let a = bridge.0.geometry.point_at_time(state.time_s).unwrap().a;
        let bb = state.full.gas.nuclei.moments().unwrap().baryon_density_m3 * a.powi(3);
        bmax = bmax.max((bb / b0 - 1.).abs());
    }
    let nn = state.full.gas.nuclei;
    let nh = nn.density_m3(S::H1Neutral) + nn.density_m3(S::H1Ionized);
    let nd = nn.density_m3(S::DNeutral) + nn.density_m3(S::DIonized);
    let surv = state.cohorts.iter().map(|c| c.n_comoving_m3).sum::<f64>();
    let pres = (surv + state.photon_absorbed_count_com3 - state.source_injected_count_com3).abs()
        / state.source_injected_count_com3;
    println!(
        "case,grid,steps,spectrum,event,slices,birth,dt_total_s,T_k,x_hii,x_dii,ne_m3,born_com3,survivor_com3,absorbed_com3,HI_com3,HeI_com3,HeII_com3,DI_com3,CI_com3,RR_com3,CX_com3,FF_J_com3,CMB_J_com3,photon_res,baryon_res,energy_step_res,cuts,cohorts,work_gap_J_com3,growth,tau_seed_max,panels_max"
    );
    println!(
        "{case},{grid},{steps},{spectrum:?},{event},{slices},{birth},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{cuts},{},{:.17e},{growth},{tau_max:.17e},{panels_max}",
        p1.time_s - p0.time_s,
        state.full.gas.eos().unwrap().temperature_k,
        nn.density_m3(S::H1Ionized) / nh,
        nn.density_m3(S::DIonized) / nd,
        nn.moments().unwrap().neutral_free_electron_density_m3,
        state.source_injected_count_com3,
        surv,
        state.photon_absorbed_count_com3,
        photo[0],
        photo[1],
        photo[2],
        photo[3],
        ci,
        rr,
        cx,
        ff,
        cmb,
        pres,
        bmax,
        emax,
        state.cohorts.len(),
        work_gap
    );
}
