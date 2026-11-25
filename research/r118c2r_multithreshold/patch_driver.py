from pathlib import Path
p=Path('rust/rei_microphysics/src/axbi_heii_split.rs')
s=p.read_text()
a='''    pub fn partition_heii(
        &self,
        p: &PhotonState,
        g: &GeometrySnapshot,
    ) -> Result<HeiiPools, ForwardError> {
        self.validate_state(p)?;'''
b='''    pub fn partition_heii(
        &self,
        p: &PhotonState,
        g: &GeometrySnapshot,
    ) -> Result<HeiiPools, ForwardError> {
        self.partition_edge(p,g,2)
    }
    pub(crate) fn partition_edge(&self,p:&PhotonState,g:&GeometrySnapshot,edge:usize)->Result<HeiiPools,ForwardError>{
        if edge>=FIT_THRESHOLDS_EV.len(){return Err(bad("AXBI_EDGE_DOMAIN"))}
        self.validate_state(p)?;'''
assert s.count(a)==1;s=s.replace(a,b)
a='let t = FIT_THRESHOLDS_EV[2];';assert s.count(a)==2;s=s.replace(a,'let t = FIT_THRESHOLDS_EV[edge];',1)
p.write_text(s)
p=Path('rust/rei_microphysics/src/axbi_multithreshold.rs')
p.write_text('''// Included in covariant_transport; same atomic fit edges and quadrature owner.
#[derive(Clone, Debug, PartialEq)]
pub struct ActiveBands {
    pub low:PhotonState,
    pub middle:PhotonState,
    pub high:PhotonState,
}
impl CovariantTransport {
    pub fn empty_bands(&self)->ActiveBands{ActiveBands{low:self.empty_state(),middle:self.empty_state(),high:self.empty_state()}}
    pub fn partition_bands(&self,p:&PhotonState,g:&GeometrySnapshot)->Result<ActiveBands,ForwardError>{
        let a=self.partition_heii(p,g)?;
        let b=self.partition_edge(&a.below,g,1)?;
        Ok(ActiveBands{low:b.below,middle:b.above,high:a.above})
    }
    pub fn move_bands(&self,p:&ActiveBands,g:&GeometrySnapshot)->Result<ActiveBands,ForwardError>{
        let mut out=self.empty_bands();
        for s in [&p.low,&p.middle,&p.high]{
            let a=self.partition_bands(s,g)?;
            out.low=self.merge_heii_states(&out.low,&a.low)?;
            out.middle=self.merge_heii_states(&out.middle,&a.middle)?;
            out.high=self.merge_heii_states(&out.high,&a.high)?;
        }
        Ok(out)
    }
    pub fn inject_bands(&self,g:&GeometrySnapshot,z:f64,dt:f64)->Result<(ActiveBands,SourceLedger),ForwardError>{
        if !nonnegative(dt){return Err(bad("AXBI_BANDS_SOURCE_DT"))}
        let amount=self.source.at_redshift(z)?.per_h_s*dt;
        if !nonnegative(amount){return Err(bad("AXBI_BANDS_SOURCE_AMOUNT"))}
        let rays=self.ray_geometry(g)?;let mut p=self.empty_bands();let mut l=SourceLedger::default();
        for (j,r) in rays.iter().enumerate(){
            for (s,c) in self.source.spectral_cells.iter().enumerate(){
                if c.lower_ev/r.scale<self.edges[0]||c.upper_ev/r.scale>*self.edges.last().unwrap(){return Err(bad("AXBI_COVARIANT_SOURCE_OUTSIDE_GRID"))}
                let amp=amount*r.angular_weight*c.photon_fraction/self.source_norms[s];
                if amp==0.{continue}
                for i in 0..self.n_energy(){
                    let lo=c.lower_ev.max(self.edges[i]*r.scale);let hi=c.upper_ev.min(self.edges[i+1]*r.scale);
                    if hi<=lo{continue}
                    let t=FIT_THRESHOLDS_EV[1];let u=FIT_THRESHOLDS_EV[2];
                    for (lower,upper,target) in [(lo,hi.min(t),&mut p.low),(lo.max(t),hi.min(u),&mut p.middle),(lo.max(u),hi,&mut p.high)]{
                        if upper<=lower{continue}
                        let (n,en)=source_moments(lower,upper);let n=amp*n;let en=amp*en;
                        let qlo=if lower==self.edges[i]*r.scale{self.edges[i]}else{lower/r.scale};
                        let qhi=if upper==self.edges[i+1]*r.scale{self.edges[i+1]}else{upper/r.scale};
                        add_support(target,j*self.n_energy()+i,n,en/r.scale,qlo,qhi);
                        l.added_photons_per_h+=n;l.added_energy_ev_per_h+=en;
                    }
                }
            }
        }
        for a in [&p.low,&p.middle,&p.high]{self.validate_state(a)?}
        Ok((p,l))
    }
}
''')
p=Path('rust/rei_microphysics/src/axbi_covariant_transport.rs')
p.write_text(p.read_text()+'\ninclude!("axbi_multithreshold.rs");\n')
p=Path('rust/rei_microphysics/src/axbi_covariant_driver.rs');s=p.read_text()
def one(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a))
 s=s.replace(a,b,1)
one('PreparedAbsorption, HeiiPools};','PreparedAbsorption, HeiiPools, ActiveBands};')
one('    pub heii_split: bool,','    pub heii_split: bool,\n    pub hei_split: bool,')
one('            heii_split:false,','            heii_split:false,\n            hei_split:false,')
one('                "heii_split" =>','                "hei_split" => c.hei_split=match v.trim(){"true"=>true,"false"=>false,_=>return Err(err("AXBI_CONFIG_VALUE"))},\n                "heii_split" =>')
one('            || (self.heii_split &&','            || (self.hei_split && (!self.heii_split || !self.inactive_hi_split))\n            || (self.heii_split &&')
one('    pub heii_above: Option<PhotonState>,','    pub heii_above: Option<PhotonState>,\n    pub hei_middle: Option<PhotonState>,')
one('struct StageStocks { primary:PhotonState, above:Option<PhotonState> }','struct StageStocks { primary:PhotonState, above:Option<PhotonState>, middle:Option<PhotonState> }')
one('    birth_above:Option<Arc<PreparedAbsorption>>,','    birth_above:Option<Arc<PreparedAbsorption>>,\n    prepared_middle:Option<Arc<PreparedAbsorption>>,\n    birth_middle:Option<Arc<PreparedAbsorption>>,')
one('        let stocks=StageStocks{primary:absorption.state,above};','''        let middle=if let Some(p)=&self.prepared_middle{
            let a=if let Some(b)=&self.birth_middle{p.evaluate_continuous_birth(b,absorbers,nh,dt)?}
                else{p.evaluate_for_cell_count(self.cells,absorbers,nh,dt)?};
            for k in 0..3{photo.gamma_s[k]+=a.photo.gamma_s[k];photo.heat_erg_per_absorber_s[k]+=a.photo.heat_erg_per_absorber_s[k];}
            Some(a.state)
        }else{None};
        let stocks=StageStocks{primary:absorption.state,above,middle};''')
one('            heii_above:if config.heii_split{Some(transport.empty_state())}else{None},','            heii_above:if config.heii_split{Some(transport.empty_state())}else{None},\n            hei_middle:if config.hei_split{Some(transport.empty_state())}else{None},')
one('        if let Some(p)=&s.heii_above{self.transport.validate_state(p)?;}','''        if let Some(p)=&s.heii_above{self.transport.validate_state(p)?;}
        if s.hei_middle.is_some()!=self.config.hei_split{return Err(err("AXBI_HEI_MODE"))}
        if let Some(p)=&s.hei_middle{self.transport.validate_state(p)?;}''')
one('''        if let Some(p)=&s.heii_above{
            let a=self.transport.move_heii''','''        if let (Some(m),Some(h))=(&s.hei_middle,&s.heii_above){
            let a=self.transport.move_bands(&ActiveBands{low:self.photon_state(s),middle:m.clone(),high:h.clone()},g)?;
            Self::set_photon_state(s,a.low);s.hei_middle=Some(a.middle);s.heii_above=Some(a.high);
        }else if let Some(p)=&s.heii_above{
            let a=self.transport.move_heii''')
one('''        if let Some(p)=&s.heii_above{self.transport.heii_endpoint_photo(&HeiiPools{below:self.photon_state(s),above:p.clone()},&g,nh)}else{Ok(self.transport.prepare(&self.photon_state(s),&g)?.evaluate([0.;3],nh,0.)?.photo)}''','''        let mut photo=if let Some(p)=&s.heii_above{self.transport.heii_endpoint_photo(&HeiiPools{below:self.photon_state(s),above:p.clone()},&g,nh)?}else{self.transport.prepare(&self.photon_state(s),&g)?.evaluate([0.;3],nh,0.)?.photo};
        if let Some(p)=&s.hei_middle{let a=self.transport.prepare(p,&g)?.evaluate([0.;3],nh,0.)?.photo;for k in 0..3{photo.gamma_s[k]+=a.gamma_s[k];photo.heat_erg_per_absorber_s[k]+=a.heat_erg_per_absorber_s[k];}}
        Ok(photo)''')
one('        if let Some(p)=&state.heii_above{let (a,b)=self.transport.inventory(p,geometry)?;n+=a;u+=b;}','        if let Some(p)=&state.heii_above{let (a,b)=self.transport.inventory(p,geometry)?;n+=a;u+=b;}\n        if let Some(p)=&state.hei_middle{let (a,b)=self.transport.inventory(p,geometry)?;n+=a;u+=b;}')
one('''        if let Some(p)=&state.heii_above{
            let g=self.background.point_at_scale(state.a)?.geometry()?;''','''        if let (Some(m),Some(h))=(&state.hei_middle,&state.heii_above){
            let g=self.background.point_at_scale(state.a)?.geometry()?;
            let mut delta=self.transport.empty_state();self.transport.add_delta(&mut delta,ray,q,count)?;
            let d=self.transport.partition_bands(&delta,&g)?;
            let low=self.transport.merge_heii_states(&self.photon_state(state),&d.low)?;
            let mid=self.transport.merge_heii_states(m,&d.middle)?;
            let high=self.transport.merge_heii_states(h,&d.high)?;
            Self::set_photon_state(state,low);state.hei_middle=Some(mid);state.heii_above=Some(high);
        }else if let Some(p)=&state.heii_above{
            let g=self.background.point_at_scale(state.a)?.geometry()?;''')
one('p.above.as_ref().map_or(0.,|a|a.number.iter().sum::<f64>()));','p.above.as_ref().map_or(0.,|a|a.number.iter().sum::<f64>())+p.middle.as_ref().map_or(0.,|a|a.number.iter().sum::<f64>()));')
one('        let birth_above=birth.as_ref().and_then(|p|p.above.as_ref()).map(|p|self.transport.prepare(p,&geometry)).transpose()?.map(Arc::new);','''        let birth_above=birth.as_ref().and_then(|p|p.above.as_ref()).map(|p|self.transport.prepare(p,&geometry)).transpose()?.map(Arc::new);
        let prepared_middle=old.hei_middle.as_ref().map(|p|self.transport.prepare(p,&geometry)).transpose()?.map(Arc::new);
        let birth_middle=birth.as_ref().and_then(|p|p.middle.as_ref()).map(|p|self.transport.prepare(p,&geometry)).transpose()?.map(Arc::new);''')
one('        let birth_u_above=if budget.is_some(){birth.as_ref().and_then(|p|p.above.as_ref()).map(|p|p.energy_ref.clone())}else{None};','''        let birth_u_above=if budget.is_some(){birth.as_ref().and_then(|p|p.above.as_ref()).map(|p|p.energy_ref.clone())}else{None};
        let birth_u_middle=if budget.is_some(){birth.as_ref().and_then(|p|p.middle.as_ref()).map(|p|p.energy_ref.clone())}else{None};''')
one('''                    let du=(a.energy_ref[j]-b.energy_ref[j]+birth_u_above.as_ref().map_or(0.,|u|u[j]))*rays[j/ne].scale;
                    let y=du-corr;let t=sum+y;corr=(t-sum)-y;sum=t;
                }''','''                    let du=(a.energy_ref[j]-b.energy_ref[j]+birth_u_above.as_ref().map_or(0.,|u|u[j]))*rays[j/ne].scale;
                    let y=du-corr;let t=sum+y;corr=(t-sum)-y;sum=t;
                }
                if let (Some(a),Some(b))=(&old.hei_middle,&stocks.middle){
                    let du=(a.energy_ref[j]-b.energy_ref[j]+birth_u_middle.as_ref().map_or(0.,|u|u[j]))*rays[j/ne].scale;
                    let y=du-corr;let t=sum+y;corr=(t-sum)-y;sum=t;
                }''')
one('            prepared_above,birth_above,','            prepared_above,birth_above,prepared_middle,birth_middle,')
one('old.heii_above.as_ref().map_or(0.,|p|p.number.iter().sum::<f64>());','old.heii_above.as_ref().map_or(0.,|p|p.number.iter().sum::<f64>())+old.hei_middle.as_ref().map_or(0.,|p|p.number.iter().sum::<f64>());')
one('stocks.above.as_ref().map_or(0.,|p|p.number.iter().sum::<f64>());','stocks.above.as_ref().map_or(0.,|p|p.number.iter().sum::<f64>())+stocks.middle.as_ref().map_or(0.,|p|p.number.iter().sum::<f64>());')
one('next.heii_above=stocks.above;','next.heii_above=stocks.above;next.hei_middle=stocks.middle;')
one('''            let (birth,emitted)=if self.config.heii_split{''','''            let (birth,emitted)=if self.config.hei_split{
                let (p,l)=self.transport.inject_bands(&geometry,1./s.a-1.,dt)?;
                (StageStocks{primary:p.low,above:Some(p.high),middle:Some(p.middle)},l)
            }else if self.config.heii_split{''')
one('StageStocks{primary:p.below,above:Some(p.above)}','StageStocks{primary:p.below,above:Some(p.above),middle:None}')
one('StageStocks{primary:p,above:None}','StageStocks{primary:p,above:None,middle:None}')
one('''        for &n in &s.photons {''','''        if let Some(p)=&s.hei_middle{
            let rays=self.transport.ray_geometry(&geometry)?;
            for j in 0..self.transport.cell_count(){
                let scale=rays[j/self.energies.len()].scale;
                let lo=24.59;let hi=54.42;let tol=16.*f64::EPSILON*hi;
                if (s.photons[j]>0.&&s.photon_support_hi[j]*scale>lo+tol)
                    || (p.number[j]>0.&&(p.support_lo[j]*scale<lo-tol || p.support_hi[j]*scale>hi+tol)){return Err(err("AXBI_HEI_ENDPOINT_SUPPORT"))}
            }
        }
        for &n in &s.photons {''')
one('''        let mut du = 0.0;
        let ne = self.energies.len();''','''        if let (Some(a),Some(b))=(&full.hei_middle,&half.hei_middle){dn+=a.number.iter().zip(&b.number).map(|(a,b)|(a-b).abs()).sum::<f64>();}
        let mut du = 0.0;
        let ne = self.energies.len();''')
one('if let (Some(a),Some(b))=(&full.heii_above,&half.heii_above){du+=(a.energy_ref[j]-b.energy_ref[j]).abs()*ray.scale;}','if let (Some(a),Some(b))=(&full.heii_above,&half.heii_above){du+=(a.energy_ref[j]-b.energy_ref[j]).abs()*ray.scale;}\n                if let (Some(a),Some(b))=(&full.hei_middle,&half.hei_middle){du+=(a.energy_ref[j]-b.energy_ref[j]).abs()*ray.scale;}')
one('s.heii_above.as_ref().map_or(0.,|p|p.energy_ref[j])) * ray.scale','s.heii_above.as_ref().map_or(0.,|p|p.energy_ref[j])+s.hei_middle.as_ref().map_or(0.,|p|p.energy_ref[j])) * ray.scale')
one('        include_str!("axbi_heii_split.rs"),','        include_str!("axbi_heii_split.rs"),\n        include_str!("axbi_multithreshold.rs"),')
one('''        Ok(text)
    }
    pub fn save_checkpoint''','''        if let Some(p)=&s.hei_middle{
            text=text.replacen("AXBI_CHECKPOINT_V5","AXBI_CHECKPOINT_V6",1);
            for v in [&p.number,&p.energy_ref,&p.support_lo,&p.support_hi]{text.push_str(&list(v));text.push('\\n');}
        }
        Ok(text)
    }
    pub fn save_checkpoint''')
one('''        if (self.config.heii_split && (lines.len()!=15 || lines[0]!="AXBI_CHECKPOINT_V5")) || (!self.config.heii_split && (lines.len()!=11 || lines[0]!="AXBI_CHECKPOINT_V4")) {''','''        let (version,len)=if self.config.hei_split{("AXBI_CHECKPOINT_V6",19)}else if self.config.heii_split{("AXBI_CHECKPOINT_V5",15)}else{("AXBI_CHECKPOINT_V4",11)};
        if lines.len()!=len || lines[0]!=version {''')
one('''        let state = DriverState {
            a: v[0],''','''        let hei_middle=if self.config.hei_split{Some(PhotonState{number:parse_list(lines[15])?,energy_ref:parse_list(lines[16])?,support_lo:parse_list(lines[17])?,support_hi:parse_list(lines[18])?})}else{None};
        let state = DriverState {
            a: v[0],''')
one('            heii_above,\n            photon_inactive_number,','            heii_above,hei_middle,\n            photon_inactive_number,')
one('        let diagnostic=if let Some(p)=&s.heii_above{self.transport.merge_heii_states(&primary,p)?}else{primary};','        let diagnostic=if let Some(p)=&s.heii_above{self.transport.merge_heii_states(&primary,p)?}else{primary};\n        let diagnostic=if let Some(p)=&s.hei_middle{self.transport.merge_heii_states(&diagnostic,p)?}else{diagnostic};')
p.write_text(s)
