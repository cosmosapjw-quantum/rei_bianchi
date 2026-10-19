from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];C=R/'code/rei_bass_coupled';p=C/'src/bass_optical_birth.rs';s=p.read_text()
s=s.replace('BassOpticalBirthBridge','FixedPacketSplitBridge')
s=s.replace('pub LayerControls,\n);','pub LayerControls,\n    pub Vec<crate::source_age::Cohort>,\n    pub f64,\n    pub usize,\n);')
a=s.index('    pub fn emit_births(');b=s.index('    /// Forward transport',a)
s=s[:a]+'''    /// Return only the immutable pre-generated source births in this interval.
    pub fn emit_births(&self,t0:f64,dt:f64,conf:&NetworkConfig,_gas_mid:&MixtureState)
      -> Result<(Vec<crate::source_age::Cohort>,f64,usize),NetworkError> {
        if !t0.is_finite() || !dt.is_finite() || dt<=0. || conf.photon_source!=SOURCE_ID {return Err(NetworkError::InvalidInput);}
        let births=self.3.iter().filter(|c|c.birth_time_s>=t0 && c.birth_time_s<t0+dt).cloned().collect();
        Ok((births,self.4,self.5))
    }

'''+s[b:]
s=s.replace('use crate::positive_spectral::expand_births;\n','')
s='//! RUN08 generated fixed-source adapter. Only birth scheduling changes;\n//! RUN05 photo/drift/thermal operations retained. See derivation receipt.\n'+s
(C/'src/fixed_packet_split.rs').write_text(s)
ex=(C/'examples/optical_birth_campaign.rs').read_text()
ex=ex.replace('    bass_optical_birth::{BassOpticalBirthBridge, LayerControls},','    bass_optical_birth::{BassOpticalBirthBridge, LayerControls},\n    fixed_packet_split::{FixedPacketSplitBridge,LayerControls as FixedControls},\n    isotope_state::IsotopeNumberState,\n    mixture_eos::MixtureState,')
ex=ex.replace('    let mut state = bridge.initial(full, &conf, p0.time_s).unwrap();','''    let gm=bridge.0.geometry.point_at_time(0.5*(p0.time_s+p1.time_s)).unwrap();
    let r=(p0.a/gm.a).powi(3);let vals=S::ALL.map(|s|full.gas.nuclei.density_m3(s)*r);
    let gas_mid=MixtureState{nuclei:IsotopeNumberState::new(vals).unwrap(),thermal_j_m3:full.gas.thermal_j_m3*r.powf(5./3.)};
    let (mut packet,seed,panels)=bridge.emit_births(p0.time_s,p1.time_s-p0.time_s,&conf,&gas_mid).unwrap();
    packet.sort_by(|a,b|a.birth_time_s.total_cmp(&b.birth_time_s));
    // Independently output source tuple bits to bind every cohort, not just totals.
    if let Ok(path)=std::env::var("RUN08_PACKET_BITS") {
        let mut bits=Vec::new();
        for co in &packet {for f in [co.birth_time_s,co.energy_at_birth_ev,co.direction_at_birth[2],co.n_comoving_m3] {bits.extend_from_slice(&f.to_le_bytes());}}
        std::fs::write(path,bits).unwrap();
    }
    let bridge=FixedPacketSplitBridge(bridge.0,bridge.1,FixedControls{growth,optical_scale,..FixedControls::default()},packet,seed,panels);
    let mut state = bridge.initial(full, &conf, p0.time_s).unwrap();''')
(C/'examples/fixed_packet_campaign.rs').write_text(ex)
(R/'contracts/FIXED_PACKET_DERIVATION.json').write_text(json.dumps({'parent':'src/bass_optical_birth.rs','parent_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'change':'rename wrapper; replace emit_births with immutable interval subset; append immutable packet fields; same photo,drift,full_network steps retained','example':'source packet generated once with initial-gas midpoint dilution and original RUN05 method'},indent=2))
