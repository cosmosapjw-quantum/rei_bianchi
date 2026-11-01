use rei_f08_characteristic_owner::{
    energy_after, qhat, CharacteristicPhoton, FIRST_DT_S, H, INITIAL_PHOTONS_PER_H, LOWER_NODE_EV,
    SOURCE_EV,
};
fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("direction,qx,qy,qz,energy_exact_ev,old_hat_lower_photons_per_h,subphysical_energy");
    let nd = 128;
    for d in 0..nd {
        let q = qhat(8, 16, d)?;
        let p = CharacteristicPhoton {
            birth_ev: SOURCE_EV,
            photons_per_h: INITIAL_PHOTONS_PER_H / nd as f64,
            q,
        };
        let energy = energy_after(p, H, FIRST_DT_S)?;
        if !(LOWER_NODE_EV < energy && energy < SOURCE_EV) {
            return Err("first-step energy outside original native interval".into());
        }
        let old_hat = p.photons_per_h * (SOURCE_EV - energy) / (SOURCE_EV - LOWER_NODE_EV);
        println!(
            "{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{}",
            d,
            q[0],
            q[1],
            q[2],
            energy,
            old_hat,
            energy < LOWER_NODE_EV
        );
    }
    Ok(())
}
