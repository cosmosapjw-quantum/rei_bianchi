from pathlib import Path
p=Path('rust/rei_microphysics/src/axbi_covariant_driver.rs');s=p.read_text()
def once(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a))
 s=s.replace(a,b,1)
once('use crate::axbi_covariant_transport::{CovariantTransport, PhotonState, PreparedAbsorption};','use crate::axbi_covariant_transport::{CovariantTransport, PhotonState, PreparedAbsorption, HeiiPools};')
once('    pub inactive_hi_split: bool,','    pub inactive_hi_split: bool,\n    /// Opt-in HeII active subcells; primary arrays are below the edge.\n    pub heii_split: bool,')
once('            inactive_hi_split: false,','            inactive_hi_split: false,\n            heii_split:false,')
once('                "inactive_hi_split" => {','                "heii_split" => c.heii_split=match v.trim(){"true"=>true,"false"=>false,_=>return Err(err("AXBI_CONFIG_VALUE"))},\n                "inactive_hi_split" => {')
once('            || (self.inactive_hi_split && self.q_ref != 0.0)','            || (self.heii_split && (self.q_ref!=0. || !self.continuous_birth || !self.nonmonotone_search))\n            || (self.inactive_hi_split && self.q_ref != 0.0)')
once('    pub photon_support_hi: Vec<f64>,','    pub photon_support_hi: Vec<f64>,\n    pub heii_above: Option<PhotonState>,')
once('    birth:Option<Arc<PreparedAbsorption>>,','    birth:Option<Arc<PreparedAbsorption>>,\n    prepared_above:Option<Arc<PreparedAbsorption>>,\n    birth_above:Option<Arc<PreparedAbsorption>>,')
once('/// Immutable inputs shared by leaf residual evaluations.','#[derive(Clone)]\nstruct StageStocks { primary:PhotonState, above:Option<PhotonState> }\n/// Immutable inputs shared by leaf residual evaluations.')
assert s.count('Result<([f64; 4], PhotonState, IgmPointRhs), ForwardError>')==2
s=s.replace('Result<([f64; 4], PhotonState, IgmPointRhs), ForwardError>','Result<([f64; 4], StageStocks, IgmPointRhs), ForwardError>')
once('''        let stocks = absorption.state;
        let photo = absorption.photo;''','''        let mut photo = absorption.photo;
        let above=if let Some(p)=&self.prepared_above{
            let a=if let Some(b)=&self.birth_above{p.evaluate_continuous_birth(b,absorbers,nh,dt)?}
                else{p.evaluate_for_cell_count(self.cells,absorbers,nh,dt)?};
            for k in 0..3{photo.gamma_s[k]+=a.photo.gamma_s[k];photo.heat_erg_per_absorber_s[k]+=a.photo.heat_erg_per_absorber_s[k];}
            Some(a.state)
        }else{None};
        let stocks=StageStocks{primary:absorption.state,above};''')
once('            photon_support_hi: photon_state.support_hi,','            photon_support_hi: photon_state.support_hi,\n            heii_above:if config.heii_split{Some(transport.empty_state())}else{None},')
once('    fn validate_inactive(','    fn validate_heii_mode(&self,s:&DriverState)->Result<(),ForwardError>{\n        if s.heii_above.is_some()!=self.config.heii_split{return Err(err("AXBI_HEII_MODE"))}\n        if let Some(p)=&s.heii_above{self.transport.validate_state(p)?;}\n        Ok(())\n    }\n    fn move_heii_state(&self,s:&mut DriverState,g:&GeometrySnapshot)->Result<(),ForwardError>{\n        self.validate_heii_mode(s)?;\n        if let Some(p)=&s.heii_above{\n            let a=self.transport.move_heii(&HeiiPools{below:self.photon_state(s),above:p.clone()},g)?;\n            Self::set_photon_state(s,a.below);s.heii_above=Some(a.above);\n        }Ok(())\n    }\n    pub fn endpoint_photo(&self,s:&DriverState)->Result<crate::igm_thermal::IgmPhotoInput,ForwardError>{\n        self.validate_heii_mode(s)?;\n        let g=self.background.point_at_scale(s.a)?.geometry()?;let nh=self.n_h0_cm3/s.a.powi(3);\n        if let Some(p)=&s.heii_above{self.transport.heii_endpoint_photo(&HeiiPools{below:self.photon_state(s),above:p.clone()},&g,nh)}else{Ok(self.transport.prepare(&self.photon_state(s),&g)?.evaluate([0.;3],nh,0.)?.photo)}\n    }\n    fn validate_inactive(')
once('''        let (n, u) = self
            .transport
            .inventory(&self.photon_state(state), geometry)?;''','''        self.validate_heii_mode(state)?;
        let (mut n, mut u) = self.transport.inventory(&self.photon_state(state), geometry)?;
        if let Some(p)=&state.heii_above{let (a,b)=self.transport.inventory(p,geometry)?;n+=a;u+=b;}''')
once('''        let mut photons = self.photon_state(state);
        self.transport.add_delta(&mut photons, ray, q, count)?;
        Self::set_photon_state(state, photons);''','''        self.validate_heii_mode(state)?;
        if let Some(p)=&state.heii_above{
            let g=self.background.point_at_scale(state.a)?.geometry()?;
            let mut delta=self.transport.empty_state();self.transport.add_delta(&mut delta,ray,q,count)?;
            let d=self.transport.partition_heii(&delta,&g)?;
            let low=self.transport.merge_heii_states(&self.photon_state(state),&d.below)?;
            let high=self.transport.merge_heii_states(p,&d.above)?;
            Self::set_photon_state(state,low);state.heii_above=Some(high);
        }else{
            let mut photons = self.photon_state(state);
            self.transport.add_delta(&mut photons, ray, q, count)?;
            Self::set_photon_state(state, photons);
        }''')
once('        self.partition_inactive(s, &g1)?;','        self.move_heii_state(s,&g1)?;\n        self.partition_inactive(s, &g1)?;')
# stage births now carry both pools (legacy wrapped)
once('birth:Option<PhotonState>,budget:Option<f64>','birth:Option<StageStocks>,budget:Option<f64>')
once('        self.partition_inactive(&mut old, &geometry)?;','        self.move_heii_state(&mut old,&geometry)?;\n        self.partition_inactive(&mut old, &geometry)?;')
once('''        let birth_number=birth.as_ref().map_or(0.,|p|p.number.iter().sum::<f64>());''','''        let birth_number=birth.as_ref().map_or(0.,|p|p.primary.number.iter().sum::<f64>()+p.above.as_ref().map_or(0.,|a|a.number.iter().sum::<f64>()));
        let prepared_above=old.heii_above.as_ref().map(|p|self.transport.prepare(p,&geometry)).transpose()?.map(Arc::new);
        let birth_above=birth.as_ref().and_then(|p|p.above.as_ref()).map(|p|self.transport.prepare(p,&geometry)).transpose()?.map(Arc::new);''')
once('let birth_u=if budget.is_some(){birth.as_ref().map(|p|p.energy_ref.clone())}else{None};','let birth_u=if budget.is_some(){birth.as_ref().map(|p|p.primary.energy_ref.clone())}else{None};\n        let birth_u_above=if budget.is_some(){birth.as_ref().and_then(|p|p.above.as_ref()).map(|p|p.energy_ref.clone())}else{None};')
s=s.replace('stocks:&PhotonState,rhs:&IgmPointRhs','stocks:&StageStocks,rhs:&IgmPointRhs')
once('''            for (j,(&a,&b)) in old.photon_energy_ref.iter().zip(&stocks.energy_ref).enumerate(){
                let du=(a-b+birth_u.as_ref().map_or(0.,|u|u[j]))*rays[j/ne].scale;
                let y=du-corr;let t=sum+y;corr=(t-sum)-y;sum=t;
            }''','''            for (j,(&a,&b)) in old.photon_energy_ref.iter().zip(&stocks.primary.energy_ref).enumerate(){
                let du=(a-b+birth_u.as_ref().map_or(0.,|u|u[j]))*rays[j/ne].scale;
                let y=du-corr;let t=sum+y;corr=(t-sum)-y;sum=t;
                if let (Some(a),Some(b))=(&old.heii_above,&stocks.above){
                    let du=(a.energy_ref[j]-b.energy_ref[j]+birth_u_above.as_ref().map_or(0.,|u|u[j]))*rays[j/ne].scale;
                    let y=du-corr;let t=sum+y;corr=(t-sum)-y;sum=t;
                }
            }''')
once('let birth=birth.map(|p|self.transport.prepare(&p,&geometry)).transpose()?.map(Arc::new);','let birth=birth.map(|p|self.transport.prepare(&p.primary,&geometry)).transpose()?.map(Arc::new);')
once('            birth,\n        };','            birth,\n            prepared_above,birth_above,\n        };')
once('let nold = old.photons.iter().sum::<f64>()+birth_number;','let nold = old.photons.iter().sum::<f64>()+birth_number+old.heii_above.as_ref().map_or(0.,|p|p.number.iter().sum::<f64>());')
once('let nnew = stocks.number.iter().sum::<f64>();','let nnew = stocks.primary.number.iter().sum::<f64>()+stocks.above.as_ref().map_or(0.,|p|p.number.iter().sum::<f64>());')
once('                Self::set_photon_state(&mut next, stocks);','                Self::set_photon_state(&mut next, stocks.primary);next.heii_above=stocks.above;')
once('''            let mut birth=self.transport.empty_state();
            let emitted=self.transport.inject(&mut birth,&geometry,1./s.a-1.,dt)?;''','''            let (birth,emitted)=if self.config.heii_split{
                let (p,l)=self.transport.inject_heii(&geometry,1./s.a-1.,dt)?;
                (StageStocks{primary:p.below,above:Some(p.above)},l)
            }else{
                let mut p=self.transport.empty_state();let l=self.transport.inject(&mut p,&geometry,1./s.a-1.,dt)?;
                (StageStocks{primary:p,above:None},l)
            };''')
once('        self.inventory_with_geometry(s, &geometry)?;\n        for &n','''        self.inventory_with_geometry(s, &geometry)?;
        // Active support membership is checked at the actual endpoint, not during
        // inventory evaluation across a geometry change.
        if let Some(p)=&s.heii_above{
            let rays=self.transport.ray_geometry(&geometry)?;
            for j in 0..self.transport.cell_count(){
                let scale=rays[j/self.energies.len()].scale;
                let t=54.42;let tol=16.*f64::EPSILON*t;
                if (s.photons[j]>0.&&s.photon_support_hi[j]*scale>t+tol)
                    || (p.number[j]>0.&&p.support_lo[j]*scale<t-tol){return Err(err("AXBI_HEII_ENDPOINT_SUPPORT"))}
            }
        }
        for &n''')
once('        let dn = full\n            .photons','        let mut dn = full\n            .photons')
once('''        let mut du = 0.0;
        let ne = self.energies.len();''','''        self.validate_heii_mode(full)?;self.validate_heii_mode(half)?;
        if let (Some(a),Some(b))=(&full.heii_above,&half.heii_above){
            dn+=a.number.iter().zip(&b.number).map(|(a,b)|(a-b).abs()).sum::<f64>();
        }
        let mut du = 0.0;
        let ne = self.energies.len();''')
once('''                    * ray.scale;
            }
        }
        let r=ErrorComponents''','''                    * ray.scale;
                if let (Some(a),Some(b))=(&full.heii_above,&half.heii_above){du+=(a.energy_ref[j]-b.energy_ref[j]).abs()*ray.scale;}
            }
        }
        let r=ErrorComponents''')
once('''        let a=self.transport.prepare(&self.photon_state(full),&g)?.evaluate([0.;3],nh,0.)?.photo;
        let b=self.transport.prepare(&self.photon_state(half),&g)?.evaluate([0.;3],nh,0.)?.photo;''','''        let a=self.endpoint_photo(full)?;let b=self.endpoint_photo(half)?;''')
once('''        let g=self.background.point_at_scale(half.a)?.geometry()?;
        let p=self.photon_pool_inventory''','''        let p=self.photon_pool_inventory''')
once('let u = (s.photon_energy_ref[j] + s.photon_inactive_energy_ref[j]) * ray.scale;','let u = (s.photon_energy_ref[j] + s.photon_inactive_energy_ref[j]+s.heii_above.as_ref().map_or(0.,|p|p.energy_ref[j])) * ray.scale;')
once('''        let text = format!(
            "AXBI_CHECKPOINT_V4''','''        self.validate_heii_mode(s)?;
        let mut text = format!(
            "AXBI_CHECKPOINT_V4''')
once('''        Ok(text)
    }
    pub fn save_checkpoint''','''        if let Some(p)=&s.heii_above{
            text=text.replacen("AXBI_CHECKPOINT_V4","AXBI_CHECKPOINT_V5",1);
            for v in [&p.number,&p.energy_ref,&p.support_lo,&p.support_hi]{text.push_str(&list(v));text.push('\\n');}
        }
        Ok(text)
    }
    pub fn save_checkpoint''')
once('if lines.len() != 11 || lines[0] != "AXBI_CHECKPOINT_V4" {','if (self.config.heii_split && (lines.len()!=15 || lines[0]!="AXBI_CHECKPOINT_V5")) || (!self.config.heii_split && (lines.len()!=11 || lines[0]!="AXBI_CHECKPOINT_V4")) {')
once('''        let state = DriverState {
            a: v[0],''','''        let heii_above=if self.config.heii_split{Some(PhotonState{number:parse_list(lines[11])?,energy_ref:parse_list(lines[12])?,support_lo:parse_list(lines[13])?,support_hi:parse_list(lines[14])?})}else{None};
        let state = DriverState {
            a: v[0],''')
once('            photon_support_hi,\n            photon_inactive_number,','            photon_support_hi,\n            heii_above,\n            photon_inactive_number,')
# output rates correct, aggregate spectra only (no closure is applied to aggregate)
a=s.index('        let prepared = self.transport.prepare(&self.photon_state(s), &g)?;',s.index('    pub fn output_row('))
b=s.index('        writeln!(',a)
s=s[:a]+'        let gamma=self.endpoint_photo(s)?.gamma_s;\n'+s[b:]
once('''        let rays = self.transport.ray_geometry(&g)?;
        for (k, ray)''','''        let rays = self.transport.ray_geometry(&g)?;
        let primary=self.photon_state(s);
        let diagnostic=if let Some(p)=&s.heii_above{self.transport.merge_heii_states(&primary,p)?}else{primary};
        for (k, ray)''')
# only output_row uses these exact expressions
once('let stock = s.photons[j] + s.photon_inactive_number[j];','let stock = diagnostic.number[j] + s.photon_inactive_number[j];')
once('let mut lo = s.photon_support_lo[j] * ray.scale;','let mut lo = diagnostic.support_lo[j] * ray.scale;')
once('let mut hi = s.photon_support_hi[j] * ray.scale;','let mut hi = diagnostic.support_hi[j] * ray.scale;')
once('lo = if s.photons[j] == 0.0 {','lo = if diagnostic.number[j] == 0.0 {')
once('let energy = (s.photon_energy_ref[j] + s.photon_inactive_energy_ref[j]) * ray.scale;','let energy = (diagnostic.energy_ref[j] + s.photon_inactive_energy_ref[j]) * ray.scale;')
p.write_text(s)
p=Path('rust/rei_microphysics/src/axbi_heii_split.rs');s=p.read_text().replace('    fn merge_heii_states(','    pub(crate) fn merge_heii_states(').replace('// Opt-in spectral owner; the coupled DriverState and checkpoint schema are unchanged.','// Opt-in spectral owner; C2Q uses separate active pools in the coupled driver.');p.write_text(s)
