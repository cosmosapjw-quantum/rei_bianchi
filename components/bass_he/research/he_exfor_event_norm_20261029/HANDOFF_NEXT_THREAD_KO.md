# BASS_HE 다음 스레드 handoff | 2026-10-29

```text
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
UNIT=HE_EXFOR_IDENTICAL_D_EVENT_NORMALIZATION_20261029
BASE_PR=104
BASE_SHA=89325f8510d2af3abe675326720068d0693845b8
BRANCH=research/he-exfor-event-normalization-20261029
CURRENT_HEAD=read current GitHub branch; never assume this handoff is latest
ROOT=research/he_exfor_event_norm_20261029
CENTRAL_DAG=28/88
INHERITED_HE_DAG=14/18
PREDECESSOR_CONDITIONAL_DAG=2/2
NEW_CONDITIONAL_DAG=2/2
R_TRACK=10/10
C_TRACK=9/10 (C9 distinct independent reviewer NOT_RUN)

먼저 최신 BASS_HE/rei_bianchi/bass/bass_cr/WU088_HH/rec_bianchi PR/branch HEAD,
AGENTS.md, ROOT의 THEORY_KO.md, RESULTS_KO.md, IMPLEMENTATION_CONTRACT.json,
EXTENSION_DAG.json, source/M0475.x4, src/exfor_envelope.py,
tests/test_exfor_envelope.py 및 STAGE_LEDGER.json을 읽어라.
기존 15-row birth source SHA256=1fb9f1479863ecffd072a4b7c762de8d5c8e80b18d6571dfb417d42c945e5264,
PR104와 19/19 새 테스트, 이전 IVP/figure/suite를 무조건 재실행하지 마라.

이번 실제 결과:
- IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871
  exforall/M04/M0475.x4, Git blob c49433293921dbb012d7f1b0387745732a598efa,
  SHA256 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f.
- M0475002: 330MeV CM46/61/73/87deg DA 0.14±0.03/0.16±0.05/0.07±0.05/0.19±0.05nb/sr.
- M0475003: SIG at 320MeV0.61±0.16nb,359MeV0.55±0.15nb, NO 330MeV SIG.
- Nonnegative L-Lipschitz source-coordinate feasibility Lmin=1/700nb/sr/degree;
  central-value Lmin=3/350. Sharp envelopes f-/f+ and full-sphere I integral.
- L=1/200 -> I∈[1.0068860482429433,2.4235391725370239]nb
  under explicitly declared symmetry/azimuth and coordinatewise ERR-S sensitivity.
- Exact Fraction geometry, mpmath analytic antiderivative; numerical decimal endpoints
  NOT outward-rounding-certified. Wolfram independent CAS and NIntegrate checked.
- 19/19 new tests PASS, independent mpmath pointwise quadrature <1e-45nb,
  scipy double ~1e-16nb; two new plots reviewed.
- Git source and tests blobs exactly match local; original source blob identical.
- Native subagent unavailable: C9 distinct independent reviewer NOT_RUN.

Crucial physics HOLD:
1. Verify original Arends1976 detector coincidence, acceptance/efficiency,
   half/full-sphere and per-event vs per-particle DA convention. Neither kappa=1
   nor kappa=2 is source-qualified in this unit.
2. Do not multiply M0475002 330MeV DA by M0475003 320/359MeV SIG;
   no invented interpolation/energy regularity or physical Lipschitz L.
3. Obtain actual photon distribution/history/polarization and target motion/frame;
   then derive physical R_event = nHe ∫Phi_gamma sigma_event with SI units.
4. Only then connect named fast-D pool, source kinetic tensor and independent
   stopping/deposition/Cv/thermalization owner.
5. Keep R_event=null, physical_activation=false, L4=false, production=HOLD.

Next minimal node=HE_ARENDS_EXCLUSIVE_EVENT_CONVENTION_SOURCE_AUDIT.
This is a source acquisition/convention audit, not another invented model fit.
Preserve original science, failed checks, code hashes, remote Git PR/draft state,
Drive/Dropbox per-stage ACK and local ZIP hash. No force push, no merge.
```

## Restore and publication policy

The original full BASS_HE central DAG and predecessor conditional units are not updated by this scoped child. Every stage R1–R10 then C1–C10 has a Git checkpoint and a Drive+Dropbox stage-log entry; C9 is explicitly PARTIAL, not an independent PASS. See `STAGE_LEDGER.json` for exact stage commits and provider URLs. External ZIP success must be checked by actual provider ACK, metadata size, and available hash; do not infer a cryptographic remote reread from metadata alone.
