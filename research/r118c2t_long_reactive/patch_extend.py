from pathlib import Path
p=Path('rust/rei_microphysics/src/axbi_covariant_transport.rs');s=p.read_text()
a='    pub fn n_energy(&self) -> usize {'
assert s.count(a)==1
s=s.replace(a,'''    /// Append high cells without changing any existing edge bits.
    pub fn extend_high_cells(mut self,extra:usize)->Result<Self,ForwardError>{
        let n=self.n_energy();
        if n+extra>1024{return Err(bad("AXBI_COVARIANT_GRID_RESOLUTION"))}
        let ratio=(self.edges[n]/self.edges[0]).ln()/n as f64;
        let top=self.edges[n];
        for k in 1..=extra{let q=top*(ratio*k as f64).exp();
            if !q.is_finite()||q>50000.||q<=*self.edges.last().unwrap(){return Err(bad("AXBI_COVARIANT_GRID_DOMAIN"))}
            self.edges.push(q);
        }
        Ok(self)
    }
'''+a)
p.write_text(s)
p=Path('rust/rei_microphysics/src/axbi_covariant_driver.rs');s=p.read_text()
def one(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a))
 s=s.replace(a,b,1)
one('    pub reactive_hi: bool,','    pub reactive_hi: bool,\n    pub reactive_extra_high_cells:usize,')
one('            reactive_hi:false,','            reactive_hi:false,\n            reactive_extra_high_cells:0,')
one('                "reactive_hi" =>','                "reactive_extra_high_cells" => number!(reactive_extra_high_cells),\n                "reactive_hi" =>')
one('            || !(8..=1024).contains(&self.transport_cells)','            || self.reactive_extra_high_cells>1024-self.transport_cells.min(1024)\n            || (self.reactive_extra_high_cells>0 && !self.reactive_hi)\n            || !(8..=1024).contains(&self.transport_cells)')
one('''            CovariantTransport::new(&source, reference, config.transport_cells, qmin, 512.0)?
                .with_threads(config.transport_threads)?;''','''            CovariantTransport::new(&source, reference, config.transport_cells, qmin, 512.0)?
                .extend_high_cells(config.reactive_extra_high_cells)?
                .with_threads(config.transport_threads)?;''')
one('        let energies = (0..config.transport_cells)','        let energies = (0..transport.n_energy())')
one('    fn validate_heii_mode(&self,s:&DriverState)','''    /// Exact axial extrema for the physical-density-fixed LRS branch, up to
    /// bisection and the existing background quadrature. Directional energy
    /// scale is between the two axial scales; |s/H| decreases in expansion.
    pub fn required_source_q_bounds(&self)->Result<[f64;2],ForwardError>{
        if self.config.same_h{return Err(err("AXBI_SOURCE_ENVELOPE_SAME_H_UNSUPPORTED"))}
        let a0=1./21.;let a1=1./(1.+self.config.end_zbar);
        let g0=self.background.point_at_scale(a0)?.geometry()?;
        let g1=self.background.point_at_scale(a1)?.geometry()?;
        let mut min:f64=1.;let mut max:f64=1.;
        for k in 0..3{
            let r=g0.scale_factors[k]/g1.scale_factors[k];min=min.min(r);max=max.max(r);
            if g0.hubble_per_s[k]<0. && g1.hubble_per_s[k]>0.{
                let(mut l,mut h)=(a0,a1);
                for _ in 0..64{
                    let m=(l*h).sqrt();if m==l||m==h{break}
                    if self.background.point_at_scale(m)?.geometry()?.hubble_per_s[k]<0.{l=m}else{h=m}
                }
                let g=self.background.point_at_scale((l*h).sqrt())?.geometry()?;
                max=max.max(g0.scale_factors[k]/g.scale_factors[k]);
            }
        }
        Ok([13.6/max,100./min])
    }
    fn validate_heii_mode(&self,s:&DriverState)''')
p.write_text(s)
