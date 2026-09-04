import Mathlib

namespace REI03A4

/-- In the declared canonical chain, provider review entails every predecessor. -/
theorem providerReviewRequiresAllPredecessors
    (independentAudit targetHostStaticPreflight freshProtectionReadback
      globalLease localLease dispatchIntent nativeWorker runtimeResultAudit
      firstIntervalEligibility providerReview : Prop)
    (h01 : targetHostStaticPreflight → independentAudit)
    (h12 : freshProtectionReadback → targetHostStaticPreflight)
    (h23 : globalLease → freshProtectionReadback)
    (h34 : localLease → globalLease)
    (h45 : dispatchIntent → localLease)
    (h56 : nativeWorker → dispatchIntent)
    (h67 : runtimeResultAudit → nativeWorker)
    (h78 : firstIntervalEligibility → runtimeResultAudit)
    (h89 : providerReview → firstIntervalEligibility)
    (hp : providerReview) :
    independentAudit ∧ targetHostStaticPreflight ∧ freshProtectionReadback ∧
      globalLease ∧ localLease ∧ dispatchIntent ∧ nativeWorker ∧
      runtimeResultAudit ∧ firstIntervalEligibility := by
  have h8 : firstIntervalEligibility := h89 hp
  have h7 : runtimeResultAudit := h78 h8
  have h6 : nativeWorker := h67 h7
  have h5 : dispatchIntent := h56 h6
  have h4 : localLease := h45 h5
  have h3 : globalLease := h34 h4
  have h2 : freshProtectionReadback := h23 h3
  have h1 : targetHostStaticPreflight := h12 h2
  have h0 : independentAudit := h01 h1
  exact ⟨h0, h1, h2, h3, h4, h5, h6, h7, h8⟩

/-- Native execution cannot be admitted without the complete pre-lease chain. -/
theorem nativeWorkerRequiresPreleaseChain
    (independentAudit targetHostStaticPreflight freshProtectionReadback
      globalLease localLease dispatchIntent nativeWorker : Prop)
    (h01 : targetHostStaticPreflight → independentAudit)
    (h12 : freshProtectionReadback → targetHostStaticPreflight)
    (h23 : globalLease → freshProtectionReadback)
    (h34 : localLease → globalLease)
    (h45 : dispatchIntent → localLease)
    (h56 : nativeWorker → dispatchIntent)
    (hn : nativeWorker) :
    independentAudit ∧ targetHostStaticPreflight ∧ freshProtectionReadback ∧
      globalLease ∧ localLease ∧ dispatchIntent := by
  have h5 : dispatchIntent := h56 hn
  have h4 : localLease := h45 h5
  have h3 : globalLease := h34 h4
  have h2 : freshProtectionReadback := h23 h3
  have h1 : targetHostStaticPreflight := h12 h2
  have h0 : independentAudit := h01 h1
  exact ⟨h0, h1, h2, h3, h4, h5⟩

end REI03A4
