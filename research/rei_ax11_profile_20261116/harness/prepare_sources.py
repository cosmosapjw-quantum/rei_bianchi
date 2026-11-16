#!/usr/bin/env python3
"""Build isolated original and instrumented trees from verified original bytes.

No production source is changed. All edits are performed in cloud, then the
resulting source archive is transferred to the native executor verbatim.
"""
from pathlib import Path
import hashlib, json, shutil, sys

REPO = Path(__file__).resolve().parents[3]
UNIT = Path(__file__).resolve().parents[1]

def sha(b): return hashlib.sha256(b).hexdigest()
def once(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:100])
    return s.replace(a, b, 1)

def background_patch(s):
    s = once(s, '    panels: usize,\n}', '''    panels: usize,
    // Shared only by exact clones of this immutable model; keeps Send + Sync.
    profile: std::sync::Arc<std::sync::Mutex<Ax11BackgroundProfile>>,
    cache_enabled: bool,
}
#[derive(Debug, Default)]
struct Ax11BackgroundProfile {
    calls: u64, hits: u64, misses: u64, failures: u64, nanos: u128,
    cache: std::collections::VecDeque<(u64, BackgroundPoint)>,
}''')
    s = once(s, '            panels,\n        };', '''            panels,
            profile: Default::default(),
            cache_enabled: std::env::var("AX11_CACHE").as_deref() == Ok("1"),
        };''')
    s = once(s, '    pub fn point_at_scale(&self, a: f64) -> Result<BackgroundPoint, ForwardError> {', '''    pub fn profile_snapshot(&self) -> String {
        let p = self.profile.lock().expect("AX11_PROFILE_MUTEX");
        format!("background_inclusive,{},{},{},{},{}\\n", p.calls, p.hits, p.misses, p.failures, p.nanos)
    }
    pub fn point_at_scale(&self, a: f64) -> Result<BackgroundPoint, ForwardError> {
        let start = std::time::Instant::now();
        let key = a.to_bits();
        {
            let mut p = self.profile.lock().expect("AX11_PROFILE_MUTEX");
            p.calls += 1;
            if self.cache_enabled {
                if let Some(point) = p.cache.iter().find(|(k,_)| *k == key).map(|(_,v)| *v) {
                    p.hits += 1;
                    p.nanos += start.elapsed().as_nanos();
                    return Ok(point);
                }
            }
            p.misses += 1;
        }
        // Every miss executes the original arithmetic and validation verbatim.
        let result = self.point_at_scale_uncached(a);
        let mut p = self.profile.lock().expect("AX11_PROFILE_MUTEX");
        if let Ok(point) = result {
            if self.cache_enabled {
                if p.cache.len() == 32 { p.cache.pop_front(); }
                p.cache.push_back((key, point));
            }
        } else { p.failures += 1; }
        p.nanos += start.elapsed().as_nanos();
        result
    }
    fn point_at_scale_uncached(&self, a: f64) -> Result<BackgroundPoint, ForwardError> {''')
    return s

def driver_patch(s):
    s = once(s, '    initial_energy: f64,\n}', '''    initial_energy: f64,
    profile: std::sync::Arc<std::sync::Mutex<Ax11DriverProfile>>,
    lazy_spectrum: bool,
}
#[derive(Debug, Default)]
struct Ax11DriverProfile {
    timers: std::collections::BTreeMap<&'static str, (u64,u128)>,
    components: Option<[f64;6]>,
}
struct Ax11Timer {
    profile: std::sync::Arc<std::sync::Mutex<Ax11DriverProfile>>,
    name: &'static str,
    start: Instant,
}
impl Drop for Ax11Timer {
    fn drop(&mut self) {
        let ns = self.start.elapsed().as_nanos();
        let mut p = self.profile.lock().expect("AX11_PROFILE_MUTEX");
        let v = p.timers.entry(self.name).or_default(); v.0 += 1; v.1 += ns;
    }
}
impl Driver {
    fn ax11_timer(&self, name: &'static str) -> Ax11Timer {
        Ax11Timer {profile: self.profile.clone(), name, start: Instant::now()}
    }
    pub fn last_error_components(&self) -> Option<[f64;6]> {
        self.profile.lock().expect("AX11_PROFILE_MUTEX").components
    }
    pub fn profile_snapshot(&self) -> String {
        use std::fmt::Write as FmtWrite;
        let p = self.profile.lock().expect("AX11_PROFILE_MUTEX");
        let mut out = String::new();
        for (k,(n,ns)) in &p.timers { writeln!(&mut out,"{k},{n},{ns}").unwrap(); }
        out
    }
}''')
    s = once(s, '            initial_energy: 0.0,\n', '''            initial_energy: 0.0,
            profile: Default::default(),
            lazy_spectrum: std::env::var("AX11_LAZY").as_deref() == Ok("1"),
''')
    # Timing scopes are explicitly inclusive, nested, and include error exits.
    for name in ['geometry_map','inject','evaluate','chemical_stage','tentative','moments','output_batch','save_checkpoint_budget']:
        marker = ('pub fn ' if ('pub fn '+name+'(') in s else 'fn ') + name + '('
        start = s.index(marker)
        body = s.index('{', start)
        s = s[:body+1] + '\n        let _ax11_time = self.ax11_timer("'+name+'_inclusive");' + s[body+1:]
    s = once(s, '    pub fn adaptive_step(&self, s: &mut DriverState) -> Result<bool, ForwardError> {', '''    pub fn adaptive_step(&self, s: &mut DriverState) -> Result<bool, ForwardError> {
        let _ax11_time = self.ax11_timer("adaptive_inclusive");
        self.profile.lock().expect("AX11_PROFILE_MUTEX").components = None;''')
    s = once(s, '''        let mut e = 0.0_f64;
        for i in 0..3 {
            e = e.max(
                (full.gas.fractions[i] - half.gas.fractions[i]).abs()
                    / half.gas.fractions[i].abs().max(1e-5),
            );
        }
        let w = w_erg_per_h_to_ev(half.gas.w_erg_per_h)?;
        e = e.max((w_erg_per_h_to_ev(full.gas.w_erg_per_h)? - w).abs() / w.abs().max(1e-6));''', '''        let mut e = 0.0_f64;
        let mut parts = [0.0_f64;6];
        for i in 0..3 {
            parts[i] = (full.gas.fractions[i] - half.gas.fractions[i]).abs()
                    / half.gas.fractions[i].abs().max(1e-5);
            e = e.max(parts[i]);
        }
        let w = w_erg_per_h_to_ev(half.gas.w_erg_per_h)?;
        parts[3] = (w_erg_per_h_to_ev(full.gas.w_erg_per_h)? - w).abs() / w.abs().max(1e-6);
        e = e.max(parts[3]);''')
    s = once(s, '        f(e.max(dn / n.max(1e-8)).max(du / u.max(1e-8)))', '''        parts[4] = dn / n.max(1e-8);
        parts[5] = du / u.max(1e-8);
        let metric = f(e.max(parts[4]).max(parts[5]))?;
        self.profile.lock().expect("AX11_PROFILE_MUTEX").components = Some(parts);
        Ok(metric)''')
    # Public output_row remains identical and fully formats its spectrum.
    declaration = '''    pub fn output_row(
        &self,
        s: &DriverState,
        case: &str,
        history: &mut impl Write,
        abundances: &mut impl Write,
        spectra: &mut impl Write,
        ledgers: &mut impl Write,
        feedback: &mut impl Write,
    ) -> Result<(), ForwardError> {'''
    replacement = declaration + '''
        self.output_row_mode(s,case,history,abundances,spectra,ledgers,feedback,true).map(|_| ())
    }
    fn output_row_mode(
        &self, s: &DriverState, case: &str,
        history: &mut impl Write, abundances: &mut impl Write,
        spectra: &mut impl Write, ledgers: &mut impl Write, feedback: &mut impl Write,
        materialize: bool,
    ) -> Result<usize, ForwardError> {'''
    s = once(s, declaration, replacement)
    spec_start = s.index('        let gr = self.background.point_at_scale(1.0 / 21.0)?.geometry()?;', s.index('    fn output_row_mode('))
    spec_end = s.index('        let (nr, ur) = self.residuals(s)?;', spec_start)
    original_block = s[spec_start:spec_end]
    block = '''        let spectrum_bytes;
        {
        let _ax11_time = self.ax11_timer("spectrum_inclusive");
        if self.lazy_spectrum {
            spectrum_bytes = self.ax11_spectrum(s, case, spectra, materialize)?;
        } else {
            let mut full_spectrum = Vec::new();
''' + original_block.replace('                    spectra,', '                    &mut full_spectrum,') + '''
            spectrum_bytes = full_spectrum.len();
            if materialize { spectra.write_all(&full_spectrum).map_err(ioerr)?; }
        }
        }
'''
    s = s[:spec_start]+block+s[spec_end:]
    # Match final return of output_row_mode (before next implementation section).
    out_start = s.index('    fn output_row_mode(')
    close = s.index('\n    }\n}', out_start)
    part = s[out_start:close]
    i = part.rfind('        Ok(())')
    assert i >= 0
    part = part[:i]+'        Ok(spectrum_bytes)'+part[i+len('        Ok(())'):]
    s = s[:out_start]+part+s[close:]
    s = once(s, '''        self.output_row(s, case, &mut hv, &mut av, &mut pv, &mut lv, &mut fv)?;
        let terminal_spectrum_reserve = if save_spectrum { 0 } else { pv.len() };
        if !save_spectrum {
            pv.clear();
        }''', '''        let spectrum_bytes = self.output_row_mode(s, case, &mut hv, &mut av, &mut pv, &mut lv, &mut fv, save_spectrum)?;
        let terminal_spectrum_reserve = if save_spectrum { 0 } else { spectrum_bytes };''')
    helper = '''
impl Driver {
    pub fn ax11_reserved_spectrum_bytes(&self, s: &DriverState, case: &str) -> Result<usize, ForwardError> {
        self.ax11_spectrum(s, case, &mut std::io::sink(), false)
    }
    // Exact same Display values, arithmetic and row delimiters. On discarded
    // steps only repeated common formatting and complete row assembly are skipped.
    fn ax11_spectrum(&self, s: &DriverState, case: &str, out: &mut impl Write,
                     materialize: bool) -> Result<usize, ForwardError> {
        let p = self.background.point_at_scale(s.a)?;
        let ne = self.energies.len();
        let gr = self.background.point_at_scale(1.0 / 21.0)?.geometry()?;
        let g = p.geometry()?;
        let mut angular = Vec::new();
        for cell in &self.source.angular_cells {
            let ray = CharacteristicRay::new(1.0, [(1.0-cell.mu*cell.mu).sqrt(),0.0,cell.mu],0.0)?;
            angular.push(cell.count_fraction * ray.solid_angle_jacobian(&gr,&g)?);
        }
        let norm = angular.iter().sum::<f64>();
        let prefix = format!("{case},{},{},{},{},{},", self.config.q_ref,p.sigma,p.time_s,s.a,1.0/s.a-1.0);
        let energy: Vec<String> = self.energies.iter().map(|e| format!("{e},{e},")).collect();
        let mut bytes = 0usize;
        for (k,weight) in angular.iter().enumerate() {
            let mu = self.ray(k,s.a)?.direction[2];
            let angle = format!("{mu},{},",4.0*std::f64::consts::PI*weight/norm);
            for (i,&e) in self.energies.iter().enumerate() {
                let stock = s.photons[k*ne+i];
                let tail = format!("{stock},{}\\n",stock*e);
                let row_bytes = prefix.len().checked_add(energy[i].len())
                    .and_then(|n| n.checked_add(angle.len())).and_then(|n| n.checked_add(tail.len()))
                    .ok_or(err("AXBI_OUTPUT_CAP"))?;
                bytes = bytes.checked_add(row_bytes).ok_or(err("AXBI_OUTPUT_CAP"))?;
                if materialize {
                    for part in [prefix.as_bytes(),energy[i].as_bytes(),angle.as_bytes(),tail.as_bytes()] {
                        out.write_all(part).map_err(ioerr)?;
                    }
                }
            }
        }
        Ok(bytes)
    }
}
'''
    s += helper
    return s

def main():
    dest = Path(sys.argv[1]).resolve()
    assert not dest.exists(), 'Never overwrite a source package'
    manifest = json.loads((REPO/'research/rei_igm_sync_20261116/plus_recovery/SOURCE_RECOVERY_MANIFEST.json').read_text())
    original = dest/'original'
    shutil.copytree(REPO/'rust/rei_microphysics', original/'rust/rei_microphysics',
                    ignore=shutil.ignore_patterns('target','.git'))
    # Original driver resource rows and original lib exports are restored from
    # actual historical bytes; every one of the17 entries is hash-checked below.
    for rel, pin in manifest['files'].items():
        b = (REPO/rel).read_bytes()
        if rel == 'rust/rei_microphysics/src/lib.rs':
            b = (UNIT/'harness/original_lib.rs').read_bytes()
        if rel.endswith('/axbi_driver.rs') and sha(b) != pin['sha256']:
            s = b.decode().replace('            4096 => Ok(3968 * 1024 * 1024),\n','')
            s = s.replace('            4096 => Ok(128 * 1024 * 1024),\n','')
            s = s.replace('![256, 2048, 4096].contains', '![256, 2048].contains')
            b = s.encode()
        assert len(b)==pin['bytes'] and sha(b)==pin['sha256'], (rel,len(b),sha(b),pin)
        target = original/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b)
    joined = b'\nAXBI_SOURCE_BOUNDARY\n'.join((original/p).read_bytes() for p in manifest['files'])
    assert sha(joined)==manifest['source_identity_sha256']
    # Extra harness files are separately pinned, not mislabelled original corpus.
    shutil.copy2(UNIT/'harness/ax11_profile_window.rs', original/'rust/rei_microphysics/examples/ax11_profile_window.rs')
    candidate = dest/'instrumented'
    shutil.copytree(original,candidate)
    bg = candidate/'rust/rei_microphysics/src/axbi_background.rs'
    dr = candidate/'rust/rei_microphysics/src/axbi_driver.rs'
    bg.write_text(background_patch(bg.read_text()))
    dr.write_text(driver_patch(dr.read_text()))
    # New scoped invariance tests are appended to an isolated integration test.
    extra = UNIT/'harness/ax11_invariance.rs'
    if extra.exists(): shutil.copy2(extra,candidate/'rust/rei_microphysics/tests/ax11_invariance.rs')
    pins = {str(p.relative_to(dest)):{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
            for p in sorted(dest.rglob('*')) if p.is_file()}
    (dest/'SOURCE_PACKAGE_MANIFEST.json').write_text(json.dumps({'original_corpus':manifest,
           'candidate': 'AX11 bounded instrumentation; modified compiled identity is distinct',
           'files':pins},indent=2)+'\n')
    print(json.dumps({'files':len(pins),'bytes':sum(x['bytes'] for x in pins.values()),'root':str(dest)}))

if __name__=='__main__': main()
