//! Bounded wrapper for unchanged E4 endpoint observation.
//! One cache belongs to one immutable config/history/selection. No gas solve.
use he_fixed_history_readout::Row;
use rei_microphysics::{he_rct::RctSelection, igm_config::HistoryConfig};
use short_hhe_control::{radiation, Fallible};
use std::collections::BTreeMap;

pub fn heldout_epochs() -> Vec<usize> {
    vec![15, 16, 17, 191, 192, 193, 383, 384]
}

pub struct PathCache<'a> {
    cfg: &'a HistoryConfig,
    rows: &'a [Row],
    selection: RctSelection,
    entries: BTreeMap<u64, (usize, f64)>,
    calls: usize,
}
impl<'a> PathCache<'a> {
    /// Rows must come from E4 load_history, which rejects nonzero initial stock.
    /// The borrowed input cannot be replaced during the lifetime of this cache.
    pub fn new(cfg: &'a HistoryConfig, rows: &'a [Row], selection: RctSelection) -> Fallible<Self> {
        if rows.is_empty()
            || rows[0].s.to_bits() != cfg.start.to_bits()
            || rows
                .iter()
                .enumerate()
                .any(|(j, r)| r.step != j || !r.s.is_finite() || r.y.iter().any(|x| !x.is_finite()))
            || rows.windows(2).any(|w| w[0].s >= w[1].s)
        {
            return Err("CACHE_HISTORY_IDENTITY_OR_CLOCK".into());
        }
        Ok(Self {
            cfg,
            rows,
            selection,
            entries: BTreeMap::new(),
            calls: 0,
        })
    }
    pub fn at(&mut self, k: usize, eta: f64) -> Fallible<f64> {
        if !eta.is_finite() || k >= self.rows.len() {
            return Err("CACHE_INVALID_QUERY".into());
        }
        let key = eta.to_bits();
        let (start, mut f) = self.entries.get(&key).copied().unwrap_or((0, 0.0));
        if k < start {
            return Err("CACHE_EPOCH_REWIND".into());
        }
        // Preserve the exact original recurrence and order of floating-point operations.
        for j in start + 1..=k {
            let a = &self.rows[j - 1];
            let b = &self.rows[j];
            self.calls += 1;
            f = radiation::characteristic_path_selected(
                self.cfg,
                a.y,
                b.y,
                eta,
                a.s,
                b.s,
                f,
                self.selection,
            )?
            .n;
        }
        self.entries.insert(key, (k, f));
        Ok(f)
    }
    pub fn calls(&self) -> usize {
        self.calls
    }
    pub fn keys(&self) -> usize {
        self.entries.len()
    }
}
