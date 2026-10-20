//! Recovery R1 fixture wrapper over exact BR05 inputs and unchanged owners.
//! Previous wrapper bytes are missing; this implementation requires fresh checks.
use crate::{Error, Result};
use rei_iso_couple_reference::{
    HHeModel,
    ap_midpoint::{ApMidpointBridge, BirthMode},
    axbi_sources::{AxbiSource, SOURCE_ID},
    bass_reactive::{BindingBridge, BoundSourceAgeBridge, GeometryChoice},
    bianchi_i::GeometrySnapshot,
    deuterium_atomic::DAtomicProvider,
    donor::BassSourceIdentity,
    full_network::NetworkConfig,
    isotope_state::{IsotopeNumberState, IsotopeSpecies},
    midpoint_coupled::Centering,
    mixture_eos::MixtureState,
    positive_spectral::{SpectralMode, expand_births},
    qualified_table::QualifiedTable,
    reflection_pool::PoolLimits,
    retarded_transport::RetardedControls,
    source_age::Cohort,
};
use std::{collections::BTreeMap, fs, io::Write, path::Path};

type CsvRow = BTreeMap<String, String>;
fn rows(path: &Path) -> Result<Vec<CsvRow>> {
    let text = fs::read_to_string(path)?;
    let mut lines = text.lines();
    let header: Vec<_> = lines
        .next()
        .ok_or(Error::InvalidInput("empty_fixture_csv"))?
        .split(',')
        .collect();
    let mut out = Vec::new();
    for line in lines {
        let fields: Vec<_> = line.split(',').collect();
        if fields.len() != header.len() {
            return Err(Error::InvalidInput("fixture_csv_width"));
        }
        out.push(
            header
                .iter()
                .zip(fields)
                .map(|(a, b)| (a.to_string(), b.to_string()))
                .collect(),
        );
    }
    Ok(out)
}
fn number(row: &CsvRow, key: &str) -> Result<f64> {
    let x = row
        .get(key)
        .ok_or(Error::InvalidInput("fixture_csv_field"))?
        .parse::<f64>()
        .map_err(|_| Error::InvalidInput("fixture_csv_number"))?;
    if !x.is_finite() {
        return Err(Error::InvalidInput("fixture_nonfinite"));
    }
    Ok(x)
}
fn index(row: &CsvRow, key: &str) -> Result<usize> {
    row.get(key)
        .ok_or(Error::InvalidInput("fixture_csv_field"))?
        .parse()
        .map_err(|_| Error::InvalidInput("fixture_csv_index"))
}
fn source_bits(source: &AxbiSource) -> Vec<u64> {
    let mut result = vec![
        source.spectral_cells.len() as u64,
        source.angular_cells.len() as u64,
    ];
    for cell in &source.spectral_cells {
        result.extend(
            [
                cell.lower_ev,
                cell.upper_ev,
                cell.energy_ev,
                cell.photon_fraction,
            ]
            .map(f64::to_bits),
        );
    }
    for cell in &source.angular_cells {
        result.extend([cell.mu, cell.count_fraction].map(f64::to_bits));
    }
    result
}

pub struct NativeFixture {
    pub case: String,
    pub bridge: ApMidpointBridge,
    pub conf: NetworkConfig,
    pub rate_gas: MixtureState,
    pub t0: f64,
    pub tm: f64,
    pub t1: f64,
    pub recorded_mid_volume: f64,
    pub recorded_mid_geometry: GeometrySnapshot,
    pub source_midpoint_amplitude: f64,
    pub thresholds_ev: [f64; 4],
    original_templates: Vec<Cohort>,
    locked_source: Vec<u64>,
}
impl NativeFixture {
    pub fn load(root: &Path, case: &str) -> Result<Self> {
        if !["SIGNED_MINUS", "SIGNED_PLUS"].contains(&case) {
            return Err(Error::InvalidInput("fixture_case"));
        }
        let steps = rows(&root.join("inputs/STEP1_STEPS.csv"))?;
        if steps.len() != 1 || index(&steps[0], "step")? != 1 {
            return Err(Error::InvalidInput("fixture_step1_only"));
        }
        let row = &steps[0];
        let (t0, tm, t1) = (
            number(row, "t0_s")?,
            number(row, "tm_s")?,
            number(row, "t1_s")?,
        );
        if t0 != 0.0 || tm != 2.5e11 || t1 != 5e11 {
            return Err(Error::InvalidInput("fixture_locked_clock"));
        }
        let recorded_mid_geometry = GeometrySnapshot::new(
            [
                number(row, "mid_a1")?,
                number(row, "mid_a2")?,
                number(row, "mid_a3")?,
            ],
            [
                number(row, "mid_H1_per_s")?,
                number(row, "mid_H2_per_s")?,
                number(row, "mid_H3_per_s")?,
            ],
        )?;
        let recorded_mid_volume = number(row, "mid_volume")?;
        if recorded_mid_volume.to_bits() != recorded_mid_geometry.volume_factor()?.to_bits() {
            return Err(Error::InvalidInput("fixture_mid_volume"));
        }
        let mut densities = [0.0; 13];
        for sp in IsotopeSpecies::ALL {
            densities[sp as usize] = number(row, &format!("rate_{sp:?}_m3"))?;
        }
        let rate_gas = MixtureState {
            nuclei: IsotopeNumberState::new(densities)
                .map_err(|_| Error::InvalidInput("fixture_rate_gas"))?,
            thermal_j_m3: number(row, "rate_thermal_j_m3")?,
        };
        rate_gas.eos()?;
        let donor = root.join("parent/donor_input/donor");
        let geometry = GeometryChoice::table(
            QualifiedTable::load(
                &donor.join("background_968rows_f9f0bfd3.csv"),
                &donor.join("manifest_968_ccf05824.json"),
                BassSourceIdentity {
                    producer_commit: "3c39bbbf46b6663e7c40277e194fd0ef48118472".into(),
                    source_csv_sha256:
                        "5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133".into(),
                    source_manifest_sha256:
                        "98eddf4673780f0bbca711b373a3e0746cfafc8190674c8d2d6c4de658dc3eed".into(),
                    case: case.into(),
                    grid_points: 121,
                },
            )?,
            8192,
        )?;
        let source = AxbiSource::new(1900.0 / (21_f64.powi(3) * 1e6), 0.2, 16, 8)?;
        let locked_source = source_bits(&source);
        let hhe = HHeModel::controlled_fixture().threshold_ev;
        let deuterium = DAtomicProvider::new(hhe[0], hhe[0] + 0.0037, "MANUFACTURED_D_H_DELTA_CHI")
            .map_err(|_| Error::InvalidInput("fixture_deuterium_owner"))?;
        let mut conf = NetworkConfig::source_bound(deuterium, SOURCE_ID);
        conf.cx_controls.rtol = 1e-12;
        conf.cx_controls.atol_normalized = 1e-14;
        conf.cx_controls.max_attempts = 20000;
        conf.cx_controls.max_rate_calls = 2500000;
        let bridge = ApMidpointBridge::from_original(
            BindingBridge(
                BoundSourceAgeBridge::new(source, geometry)?,
                RetardedControls::new(2, 4, SpectralMode::OriginalCellMean)?,
                PoolLimits::default(),
                Centering::JointCxSplit,
            ),
            BirthMode::Fitted { refinement: 8 },
        );
        let mut fixture = Self {
            case: case.into(),
            bridge,
            conf,
            rate_gas,
            t0,
            tm,
            t1,
            recorded_mid_volume,
            recorded_mid_geometry,
            source_midpoint_amplitude: 0.0,
            thresholds_ev: [hhe[0], hhe[1], hhe[2], deuterium.chi_d_ev()],
            original_templates: Vec::new(),
            locked_source,
        };
        fixture.source_midpoint_amplitude = fixture.emission_amplitude(&recorded_mid_geometry)?;
        let template_rows = rows(&root.join("inputs/STEP1_TEMPLATES.csv"))?;
        if template_rows.len() != 384 {
            return Err(Error::InvalidInput("fixture_384_templates"));
        }
        let midpoint = fixture.bridge.0.geometry.snapshot(tm)?;
        if case == "SIGNED_MINUS" && midpoint != recorded_mid_geometry {
            return Err(Error::InvalidInput("fixture_owner_mid_geometry"));
        }
        for (id, row) in template_rows.iter().enumerate() {
            if index(row, "step")? != 1 || index(row, "template_id")? != id {
                return Err(Error::InvalidInput("fixture_template_identity"));
            }
            let spectral_index = index(row, "spectral_index")?;
            let angular_index = index(row, "angular_index")?;
            // The locked native source enumerates every spectral/angle pair
            // once, with the angular label varying fastest. A duplicate valid
            // row must not silently replace another native source population.
            if spectral_index != id / 8 || angular_index != id % 8 {
                return Err(Error::InvalidInput("fixture_source_label_completeness"));
            }
            let energy_at_birth_ev = number(row, "energy_ev")?;
            let n_comoving_m3 = number(row, "midpoint_rate_com3_s")?;
            let cell = fixture
                .bridge
                .0
                .source
                .spectral_cells
                .get(spectral_index)
                .ok_or(Error::InvalidInput("fixture_spectral_index"))?;
            let angle = fixture
                .bridge
                .0
                .source
                .angular_cells
                .get(angular_index)
                .ok_or(Error::InvalidInput("fixture_angular_index"))?;
            let expected_rate =
                fixture.source_midpoint_amplitude * cell.photon_fraction * angle.count_fraction;
            let direction_at_birth = [
                number(row, "raw_birth_direction1")?,
                number(row, "raw_birth_direction2")?,
                number(row, "raw_birth_direction3")?,
            ];
            let expected_direction = [(1.0 - angle.mu * angle.mu).sqrt(), 0.0, angle.mu];
            if energy_at_birth_ev.to_bits() != cell.energy_ev.to_bits()
                || n_comoving_m3.to_bits() != expected_rate.to_bits()
                || direction_at_birth.map(f64::to_bits) != expected_direction.map(f64::to_bits)
                || n_comoving_m3 <= 0.0
            {
                return Err(Error::InvalidInput("fixture_native_source_mismatch"));
            }
            fixture.original_templates.push(Cohort {
                birth_time_s: tm,
                birth_geometry: midpoint,
                energy_at_birth_ev,
                direction_at_birth,
                n_comoving_m3,
                spectral_index,
                angular_index,
            });
        }
        fixture.validate_source()?;
        Ok(fixture)
    }

    pub fn validate_source(&self) -> Result<()> {
        if source_bits(&self.bridge.0.source) != self.locked_source {
            return Err(Error::InvalidInput("source_owner_cells"));
        }
        Ok(())
    }
    pub fn emission_amplitude(&self, geometry: &GeometrySnapshot) -> Result<f64> {
        let volume = geometry.volume_factor()?;
        let z = 1.0 / volume.cbrt() - 1.0;
        let amplitude = self.bridge.0.source.at_redshift(z)?.proper_photons_cm3_s * 1e6 * volume;
        if !amplitude.is_finite() || amplitude <= 0.0 {
            return Err(Error::InvalidInput("source_amplitude"));
        }
        Ok(amplitude)
    }
    pub fn templates(&self, split: bool) -> Result<Vec<Cohort>> {
        self.validate_source()?;
        Ok(expand_births(
            &self.bridge.0.source,
            &self.original_templates,
            self.thresholds_ev[3],
            if split {
                SpectralMode::SplitPositiveGauss3
            } else {
                SpectralMode::OriginalCellMean
            },
        )?)
    }
    pub fn rates(&self, energy_ev: f64, volume: f64) -> Result<[f64; 4]> {
        if !volume.is_finite() || volume <= 0.0 {
            return Err(Error::InvalidInput("rate_volume"));
        }
        let rates = self
            .bridge
            .opacity_channels(energy_ev, &self.rate_gas, &self.conf)?;
        let scaled = rates.map(|x| x * (self.recorded_mid_volume / volume));
        if scaled.iter().any(|x| !x.is_finite() || *x < 0.0) {
            return Err(Error::InvalidInput("scaled_opacity"));
        }
        Ok(scaled)
    }

    pub fn export(&self, directory: &Path) -> Result<()> {
        fs::create_dir_all(directory)?;
        let mut file = fs::File::create(directory.join("FIXTURE.csv"))?;
        write!(
            file,
            "case,t0_s,tm_s,t1_s,recorded_mid_volume,source_midpoint_amplitude,rate_temperature_K,chi_HI_ev,chi_HeI_ev,chi_HeII_ev,chi_DI_ev"
        )?;
        for sp in IsotopeSpecies::ALL {
            write!(file, ",rate_{sp:?}_m3")?;
        }
        writeln!(file)?;
        write!(
            file,
            "{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
            self.case,
            self.t0,
            self.tm,
            self.t1,
            self.recorded_mid_volume,
            self.source_midpoint_amplitude,
            self.rate_gas.eos()?.temperature_k,
            self.thresholds_ev[0],
            self.thresholds_ev[1],
            self.thresholds_ev[2],
            self.thresholds_ev[3]
        )?;
        for sp in IsotopeSpecies::ALL {
            write!(file, ",{:.17e}", self.rate_gas.nuclei.density_m3(sp))?;
        }
        writeln!(file)?;
        let mut file = fs::File::create(directory.join("TEMPLATES.csv"))?;
        writeln!(
            file,
            "template,spectral,angular,energy_ev,midpoint_rate_com3_s,raw_n1,raw_n2,raw_n3,n1,n2,n3,k_HI_per_s,k_HeI_per_s,k_HeII_per_s,k_DI_per_s,tau"
        )?;
        for (id, co) in self.original_templates.iter().enumerate() {
            let ray = co.ray_at(&co.birth_geometry)?;
            let k =
                self.bridge
                    .opacity_channels(co.energy_at_birth_ev, &self.rate_gas, &self.conf)?;
            writeln!(
                file,
                "{id},{},{},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                co.spectral_index,
                co.angular_index,
                co.energy_at_birth_ev,
                co.n_comoving_m3,
                co.direction_at_birth[0],
                co.direction_at_birth[1],
                co.direction_at_birth[2],
                ray.direction[0],
                ray.direction[1],
                ray.direction[2],
                k[0],
                k[1],
                k[2],
                k[3],
                k.iter().sum::<f64>() * (self.t1 - self.t0)
            )?;
        }
        let mut file = fs::File::create(directory.join("GEOMETRY_PROBES.csv"))?;
        writeln!(file, "u,time_s,a1,a2,a3,H1_per_s,H2_per_s,H3_per_s,volume")?;
        for i in 0..=64 {
            let u = i as f64 / 64.0;
            let t = self.t0 + (self.t1 - self.t0) * u;
            let g = self.bridge.0.geometry.snapshot(t)?;
            writeln!(
                file,
                "{u:.17e},{t:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e},{:.17e}",
                g.scale_factors[0],
                g.scale_factors[1],
                g.scale_factors[2],
                g.hubble_per_s[0],
                g.hubble_per_s[1],
                g.hubble_per_s[2],
                g.volume_factor()?
            )?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};

    #[test]
    fn duplicate_valid_native_source_row_is_rejected() {
        let source_root = Path::new(env!("CARGO_MANIFEST_DIR")).join("..");
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let temporary = std::env::temp_dir().join(format!(
            "br06_r1_duplicate_source_{}_{}",
            std::process::id(),
            stamp
        ));
        fs::create_dir_all(temporary.join("inputs")).unwrap();
        let donor = "parent/donor_input/donor";
        fs::create_dir_all(temporary.join(donor)).unwrap();
        for name in [
            "background_968rows_f9f0bfd3.csv",
            "manifest_968_ccf05824.json",
        ] {
            fs::copy(
                source_root.join(donor).join(name),
                temporary.join(donor).join(name),
            )
            .unwrap();
        }
        fs::copy(
            source_root.join("inputs/STEP1_STEPS.csv"),
            temporary.join("inputs/STEP1_STEPS.csv"),
        )
        .unwrap();
        let text = fs::read_to_string(source_root.join("inputs/STEP1_TEMPLATES.csv")).unwrap();
        let mut lines: Vec<_> = text.lines().map(String::from).collect();
        let id_column = lines[0]
            .split(',')
            .position(|name| name == "template_id")
            .unwrap();
        // Row one is otherwise an entirely valid copy of native row zero.
        // Its sequential id is retained, so per-row checks alone admit it.
        let mut duplicate: Vec<_> = lines[1].split(',').map(String::from).collect();
        duplicate[id_column] = "1".into();
        lines[2] = duplicate.join(",");
        fs::write(
            temporary.join("inputs/STEP1_TEMPLATES.csv"),
            lines.join("\n") + "\n",
        )
        .unwrap();
        let admitted = NativeFixture::load(&temporary, "SIGNED_MINUS");
        fs::remove_dir_all(&temporary).unwrap();
        assert!(matches!(
            admitted,
            Err(Error::InvalidInput("fixture_source_label_completeness"))
        ));
    }
}
