from pathlib import Path
p=Path('rust/rei_microphysics/src/axbi_covariant_driver.rs');s=p.read_text()
def one(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a))
 s=s.replace(a,b,1)
one('HeiiPools, ActiveBands};','HeiiPools, ActiveBands, FourBands};')
one('    pub hei_split: bool,','    pub hei_split: bool,\n    pub reactive_hi: bool,')
one('            hei_split:false,','            hei_split:false,\n            reactive_hi:false,')
one('                "hei_split" =>','                "reactive_hi" => c.reactive_hi=match v.trim(){"true"=>true,"false"=>false,_=>return Err(err("AXBI_CONFIG_VALUE"))},\n                "hei_split" =>')
one('''            || (self.hei_split && (!self.heii_split || !self.inactive_hi_split))
            || (self.heii_split && (self.q_ref!=0. || !self.continuous_birth || !self.nonmonotone_search))''','''            || (self.reactive_hi && (!self.hei_split || !self.heii_split || self.inactive_hi_split))
            || (self.hei_split && (!self.heii_split || (!self.inactive_hi_split && !self.reactive_hi)))
            || (self.heii_split && ((!self.reactive_hi && self.q_ref!=0.) || !self.continuous_birth || !self.nonmonotone_search))''')
one('    pub hei_middle: Option<PhotonState>,','    pub hei_middle: Option<PhotonState>,\n    pub hi_below: Option<PhotonState>,')
one('''        let transport =
            CovariantTransport::new(&source, reference, config.transport_cells, 13.6, 512.0)?''','''        let qmin=if config.reactive_hi{6.8}else{13.6};
        let transport =
            CovariantTransport::new(&source, reference, config.transport_cells, qmin, 512.0)?''')
one('13.6 * (512.0_f64 / 13.6).powf','qmin * (512.0_f64 / qmin).powf')
one('            hei_middle:if config.hei_split{Some(transport.empty_state())}else{None},','            hei_middle:if config.hei_split{Some(transport.empty_state())}else{None},\n            hi_below:if config.reactive_hi{Some(transport.empty_state())}else{None},')
one('        if let Some(p)=&s.hei_middle{self.transport.validate_state(p)?;}','''        if let Some(p)=&s.hei_middle{self.transport.validate_state(p)?;}
        if s.hi_below.is_some()!=self.config.reactive_hi{return Err(err("AXBI_REACTIVE_MODE"))}
        if let Some(p)=&s.hi_below{self.transport.validate_state(p)?;}''')
one('''        if let (Some(m),Some(h))=(&s.hei_middle,&s.heii_above){
            let a=self.transport.move_bands''','''        if let (Some(b),Some(m),Some(h))=(&s.hi_below,&s.hei_middle,&s.heii_above){
            let a=self.transport.move_four(&FourBands{below:b.clone(),low:self.photon_state(s),middle:m.clone(),high:h.clone()},g)?;
            Self::set_photon_state(s,a.low);s.hi_below=Some(a.below);s.hei_middle=Some(a.middle);s.heii_above=Some(a.high);
        }else if let (Some(m),Some(h))=(&s.hei_middle,&s.heii_above){
            let a=self.transport.move_bands''')
one('''        let pn = state.photon_inactive_number.iter().sum::<f64>();
        let pu = state''','''        let mut pn = state.photon_inactive_number.iter().sum::<f64>();
        let mut pu = state''')
one('        Ok([n, u, f(pn)?, f(pu)?])','''        if let Some(p)=&state.hi_below{let (a,b)=self.transport.inventory(p,geometry)?;pn+=a;pu+=b;}
        Ok([n, u, f(pn)?, f(pu)?])''')
one('''        if let (Some(m),Some(h))=(&state.hei_middle,&state.heii_above){
            let g=self.background.point_at_scale(state.a)?.geometry()?;''','''        if let (Some(b),Some(m),Some(h))=(&state.hi_below,&state.hei_middle,&state.heii_above){
            let g=self.background.point_at_scale(state.a)?.geometry()?;
            let mut delta=self.transport.empty_state();self.transport.add_delta(&mut delta,ray,q,count)?;
            let d=self.transport.partition_four(&delta,&g)?;
            let below=self.transport.merge_heii_states(b,&d.below)?;
            let low=self.transport.merge_heii_states(&self.photon_state(state),&d.low)?;
            let mid=self.transport.merge_heii_states(m,&d.middle)?;
            let high=self.transport.merge_heii_states(h,&d.high)?;
            Self::set_photon_state(state,low);state.hi_below=Some(below);state.hei_middle=Some(mid);state.heii_above=Some(high);
        }else if let (Some(m),Some(h))=(&state.hei_middle,&state.heii_above){
            let g=self.background.point_at_scale(state.a)?.geometry()?;''')
# Source is physically above 13.6 eV; C2R inject_bands exact physical lower edge.
# No absorption or chemistry update of below-HI pool.
one('''        for &n in &s.photons {''','''        if let Some(p)=&s.hi_below{
            let rays=self.transport.ray_geometry(&geometry)?;
            for j in 0..self.transport.cell_count(){
                let scale=rays[j/self.energies.len()].scale;let t=13.6;let tol=16.*f64::EPSILON*t;
                if (p.number[j]>0.&&p.support_hi[j]*scale>t+tol)
                    || (s.photons[j]>0.&&s.photon_support_lo[j]*scale<t-tol){return Err(err("AXBI_HI_REACTIVE_ENDPOINT_SUPPORT"))}
            }
        }
        for &n in &s.photons {''')
one('''        let mut du = 0.0;
        let ne = self.energies.len();''','''        if let (Some(a),Some(b))=(&full.hi_below,&half.hi_below){dn+=a.number.iter().zip(&b.number).map(|(a,b)|(a-b).abs()).sum::<f64>();}
        let mut du = 0.0;
        let ne = self.energies.len();''')
one('if let (Some(a),Some(b))=(&full.hei_middle,&half.hei_middle){du+=(a.energy_ref[j]-b.energy_ref[j]).abs()*ray.scale;}','if let (Some(a),Some(b))=(&full.hei_middle,&half.hei_middle){du+=(a.energy_ref[j]-b.energy_ref[j]).abs()*ray.scale;}\n                if let (Some(a),Some(b))=(&full.hi_below,&half.hi_below){du+=(a.energy_ref[j]-b.energy_ref[j]).abs()*ray.scale;}')
one('s.hei_middle.as_ref().map_or(0.,|p|p.energy_ref[j])) * ray.scale','s.hei_middle.as_ref().map_or(0.,|p|p.energy_ref[j])+s.hi_below.as_ref().map_or(0.,|p|p.energy_ref[j])) * ray.scale')
one('        include_str!("axbi_multithreshold.rs"),','        include_str!("axbi_multithreshold.rs"),\n        include_str!("axbi_reactive_bands.rs"),')
one('''        Ok(text)
    }
    pub fn save_checkpoint''','''        if let Some(p)=&s.hi_below{
            text=text.replacen("AXBI_CHECKPOINT_V6","AXBI_CHECKPOINT_V7",1);
            for v in [&p.number,&p.energy_ref,&p.support_lo,&p.support_hi]{text.push_str(&list(v));text.push('\\n');}
        }
        Ok(text)
    }
    pub fn save_checkpoint''')
one('let (version,len)=if self.config.hei_split{','let (version,len)=if self.config.reactive_hi{("AXBI_CHECKPOINT_V7",23)}else if self.config.hei_split{')
one('''        let state = DriverState {
            a: v[0],''','''        let hi_below=if self.config.reactive_hi{Some(PhotonState{number:parse_list(lines[19])?,energy_ref:parse_list(lines[20])?,support_lo:parse_list(lines[21])?,support_hi:parse_list(lines[22])?})}else{None};
        let state = DriverState {
            a: v[0],''')
one('            heii_above,hei_middle,\n            photon_inactive_number,','            heii_above,hei_middle,hi_below,\n            photon_inactive_number,')
one('        let diagnostic=if let Some(p)=&s.hei_middle{self.transport.merge_heii_states(&diagnostic,p)?}else{diagnostic};','        let diagnostic=if let Some(p)=&s.hei_middle{self.transport.merge_heii_states(&diagnostic,p)?}else{diagnostic};\n        let diagnostic=if let Some(p)=&s.hi_below{self.transport.merge_heii_states(&diagnostic,p)?}else{diagnostic};')
# correct the preexisting misleading generic runner metadata, preserving V4 format in legacy
one('format!("inactive_hi_split={}\\npassive_scope=q0_forward_monotonic_only\\ncheckpoint_version=V4\\ntransport_threads={}\\nparallel_scope=persistent_cell_prepare_and_opt_in_jacobian_columns\\nparallel_jacobian_columns={}\\n", driver.config.inactive_hi_split, driver.config.transport_threads, driver.config.parallel_jacobian_columns)','format!("inactive_hi_split={}\\npassive_scope={}\\ncheckpoint_version={}\\ntransport_threads={}\\nparallel_scope=persistent_cell_prepare_and_opt_in_jacobian_columns\\nparallel_jacobian_columns={}\\n", driver.config.inactive_hi_split, if driver.config.reactive_hi{"reversible_support"}else{"q0_forward_monotonic_only"}, if driver.config.reactive_hi{"V7"}else if driver.config.hei_split{"V6"}else if driver.config.heii_split{"V5"}else{"V4"}, driver.config.transport_threads, driver.config.parallel_jacobian_columns)')
p.write_text(s)
