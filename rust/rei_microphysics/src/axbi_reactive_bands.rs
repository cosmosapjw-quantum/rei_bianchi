// Included in covariant_transport; below-HI state is reversible, not an inactive ledger.
#[derive(Clone, Debug, PartialEq)]
pub struct FourBands {
    pub below: PhotonState,
    pub low: PhotonState,
    pub middle: PhotonState,
    pub high: PhotonState,
}
impl CovariantTransport {
    pub fn empty_four(&self) -> FourBands {
        FourBands {
            below: self.empty_state(),
            low: self.empty_state(),
            middle: self.empty_state(),
            high: self.empty_state(),
        }
    }
    pub fn partition_four(
        &self,
        p: &PhotonState,
        g: &GeometrySnapshot,
    ) -> Result<FourBands, ForwardError> {
        let a = self.partition_bands(p, g)?;
        let b = self.partition_edge(&a.low, g, 0)?;
        Ok(FourBands {
            below: b.below,
            low: b.above,
            middle: a.middle,
            high: a.high,
        })
    }
    pub fn move_four(
        &self,
        p: &FourBands,
        g: &GeometrySnapshot,
    ) -> Result<FourBands, ForwardError> {
        let mut out = self.empty_four();
        for s in [&p.below, &p.low, &p.middle, &p.high] {
            let a = self.partition_four(s, g)?;
            out.below = self.merge_heii_states(&out.below, &a.below)?;
            out.low = self.merge_heii_states(&out.low, &a.low)?;
            out.middle = self.merge_heii_states(&out.middle, &a.middle)?;
            out.high = self.merge_heii_states(&out.high, &a.high)?;
        }
        Ok(out)
    }
}
