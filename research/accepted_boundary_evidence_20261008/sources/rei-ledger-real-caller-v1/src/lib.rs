//! Explicit opt-in diagnostic adoption seam. No native evaluations are performed here.
use canonical::Wide;
use ledger::{
    Allocator, Context, DiagnosticStore, FailAt, NativeReceipt, Proposal, Publication, R,
};
use native_detailed::igm_source_step::SourceTrial;
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum DiagnosticOptIn {
    #[default]
    Disabled,
    Enabled,
}
/// The caller supplies its existing canonical request; no owner/scientific gate is inferred.
pub struct DiagnosticRequest {
    pub context: Context,
    pub original_increment: [Wide; 11],
    pub original_private_gate: bool,
}
#[derive(Debug)]
pub struct ReceiverReceipt {
    pub publication: Publication,
    pub native: NativeReceipt,
    pub observed_native_calls: sidecar::Counters,
    pub legacy_trial: SourceTrial,
    pub additional_rhs_evaluations: usize,
}
/// Receives an already evaluated real DetailedTrial from the existing native path.
/// Disabled mode does not reserve an attempt or touch the store. Enabled mode adds
/// acceptance/bookkeeping only. SourceTrial acceptance is invoked inside Proposal.
/// The returned legacy trial is an unchanged mirror, not a fabricated accepted state.
pub fn receive_native_trial(
    opt_in: DiagnosticOptIn,
    trial: sidecar::DetailedTrial,
    allocator: &Allocator,
    store: &mut DiagnosticStore,
    request: DiagnosticRequest,
    fail: FailAt,
) -> R<ReceiverReceipt> {
    if opt_in != DiagnosticOptIn::Enabled {
        return Err("DIAGNOSTIC_RECEIVER_DISABLED".into());
    }
    let counters = trial.counters;
    let legacy_trial = trial.legacy.clone();
    let proposal = Proposal::from_native_trial(
        allocator.reserve()?,
        request.context,
        store.snapshot().generation,
        trial,
        request.original_increment,
        request.original_private_gate,
        false,
    )?;
    let native = proposal
        .native_receipt()
        .ok_or("missing native acceptance receipt")?
        .clone();
    let publication = store.apply(&proposal, fail)?;
    Ok(ReceiverReceipt {
        publication,
        native,
        observed_native_calls: counters,
        legacy_trial,
        additional_rhs_evaluations: 0,
    })
}
