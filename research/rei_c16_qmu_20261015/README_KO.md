# REI C16: 실제 Q0, Qz 광자 반응과 재결합 광자 모멘트의 실현가능성

2026-10-15 KST. 기존 C15 HEAD 80825585f9fe31d2ee0d5af545ada3fa1f52be72 위의 격리 worktree에서 시행한 독립 이론·코딩 연구. 원래 AX08, BASS, BASS_HE, WU088_HH, bass_cr, rec_bianchi의 생산 코드·체크포인트는 변경하지 않음.

**과학 상태: DERIVED, NUMERICALLY_CHECKED, LOCAL_IMPLEMENTATION_VERIFIED**. 유효 범위는 기존 warm 가스 초기조건을 지정한 짧은 a=0.1999→0.2 source-backed C15 LRS Bianchi I 구간과 별도로 시험한 C11 단일 proper-volume 반응이다. 전체 z20→4 EoR, 완전한 에너지–운동량 Q^a=0, 편광 CMB, observer tau, AX11/12 과학적 승인과 구분한다.

## 1. Positive photon moment cone: exact theorem and construction

Metric -+++, local normal-frame, per hydrogen nucleus, energy eV/H. Axisymmetric radiation energy U, longitudinal c-momentum F and physical anisotropic pressure difference Pi:

U = sum N_i E_i; F = sum N_i E_i mu_i; Pi = sum N_i E_i P2(mu_i), P2=(3mu²-1)/2.

Any nonnegative photon distribution on -1<=mu<=1 obeys the **sharp and sufficient** cone:

- U>=0;
- -U/2<=Pi<=U;
- 3 F²<=U (U+2 Pi).

Proof: m=F/U, v=(1+2 Pi/U)/3; positivity implies m²<=v<=1. Conversely lambda=(v-m²)/(1-m²), and nonnegative photon-energy weights U lambda(1-m)/2 at mu=-1, U lambda(1+m)/2 at mu=+1, and U(1-lambda) at mu=m realize the exact same 0th/1st/2nd moments. Boundary |m|=1 has the exact one-pole limit. Wolfram evaluated the four reconstruction differences to {0,0,0,0}. Code checks 300 random admissible states, degenerate endpoints and invalid samples.

**Source information counterexample:** original true C15 Case-A escaping energy Uesc=0.002134217081027237 eV/H, and even a hypothetical fixed monochromatic photon number Uesc/(30 eV) and F=0, permit positive angular laws with Pi=-Uesc/2, Pi=0, Pi=+Uesc. All have the same energy, number and longitudinal momentum. Therefore an energy-only C11 Case-A scalar does NOT specify a unique radiation Pi or source spectrum. Manufactured monochromatic 30 eV is a mathematical counterexample, *not* a physical recombination source or new collision term. In a specified isotropic-comoving spontaneous emission model the initial Pi might be set to zero as an **additional explicit physical assumption**, but its later transport still produces stress in a shearing metric.

## 2. True original C11 species-specific photon energy and recoil

Independent real code re-executes original C11 H/He accepted source casea.strang_step and each original C10 midpoint photo half and Case-A rec_step without changing source owner. Photo mode i / HI-HeI-HeII species j event:

A_ij = N_i [-expm1(-tau_i)/tau_i] (c dt n_j sigma_j(E_i)), tau_i = c dt sum_j n_j sigma_j(E_i).

The original accepted midpoint proper neutral densities determine rates. Independent NumPy event allocator and scalar implementation compare exactly all three species photo counts, transferred photon energy, and longitudinal c-pz. Physical event transfer:

- Delta U_photon = -sum_ij A_ij E_i;
- Delta U_material,thermal+binding = +sum_ij A_ij E_i;
- required Delta(c p_z)_material = +sum_ij A_ij E_i mu_i.

The last equality is a REQUIRED matter recoil impulse. Original C11 does not evolve material bulk velocity/Euler momentum, so this is a reproducible missing physical operator and **not** an already-closed full Q^mu matter/radiation solver. Case A gives exact scalar escaped energy and recomb event counts but does not give photon number spectrum, momentum or Pi.

Native original Rust MD14 8×8 angular/spectral source with 0.02 photons/H, proper dt=1e10 s at a=.1999: actual photo energy transferred 0.00435587728222434 eV/H, Case-A escape energy 5.861970098983326e-7 eV/H, total energy residual ~1.05e-15 eV/H; reflection symmetric total impulse negligible. On independent, explicitly MANUFACTURED positive directional weighting (1+0.8 mu), conserving the true input number, original C11 accepted photo reactions require nonzero material c Delta pz=0.0011615672752598222 eV/H while the model still has no material velocity. A scalar energy ledger alone cannot certify total Q^mu.

## 3. Actually replayed dynamic Einstein C15 UV and emitter formal escrow

Three real source-backed C15 geometry/gas runs (Sigma_init=0 and +/-0.002 with distinct orientation, radiation+massive BASS positive source) use the original Einstein shear stress dynamics, original MD14 photon births, true H/He Case A chemistry, original Grackle rate table. For each live state the original photon angular Pi reconstructed from the positive packet distribution equals the gravitating instantaneous UV stress, and the formal per-H scalar energy relation is checked:

U_UV+U_thermal+U_bind+U_escape+W_geometric-U_MD14_emitted = constant.

This formal cumulative source-emission debit does NOT evolve a gravitating star/emitter reservoir or its angular stress. Thus C16 computes the **necessary** emitter energy budget but not physical Qstar^a. On the zero-initial-Sigma n32 case:
- total emitted stellar energy 0.19286956870424046 eV/H;
- total Case-A escaped 0.002134217081027237 eV/H;
- photon/electron number ledger residual ~1e-16 per H, energy ~1e-14 eV/H;
- source-emission energy relative to proton rest energy ~2.05558e-10.

Conditional a-posteriori missing-emitter energy density/Hamiltonian H² fraction <=2.43522e-11 for this source if the original gravitating stellar matter must be debited. Conditional maximum |delta Sigma| under missing free-streaming Case-A angular Pi **at FIXED supplied background and linearized shear response** <=2.31008e-16. This bound assumes H>=0.99 min sampled positive H, neutral proper nH bounded by initial nH, positive free-streaming escaped radiation, no secondary absorption, and directional Killing energy gain at most exp(2 total variation |delta b|). Neither result is an all-source nonlinear Einstein conservation theorem or an observer/whole-EoR error enclosure.

## 4. Executed performance and data

Vectorized actual original HI/HeI/HeII momentum, energy and count allocation is compared to independent direct per-packet scalar loop; 32 replicas of original native 192 source packets, five repeats, roughly 53.5x scalar allocation microkernel speed. Three independent Sigma/orientation C15 source histories via ProcessPoolExecutor(3) are verified bitwise identical to serial and throughput ~2.83x in measured 2026-10-15 run. Both figures are limited to these exact subproblems, not production REI AX08 runtime/RAM.

Code: qmu.py, study.py, test_qmu.py. Machine-readable C16_STUDY_RESULTS.json and QMU_STELLAR_CASEA_SHORT_HISTORY.csv. Original sources remain identical. Tests for positive angular moment reconstruction, invalid data, exact C11 event source parity, asymmetry recoil, signed C15 emitter energy and Case-A bound, and time-grid stability were 7/7 PASS; parent regression, native Rust build and fresh restoration are separately required before publication.

## 5. Literature, supplier boundary, next physics

- Pawlik and Schaye, multigroup thermally coupled photon-conserving H/He transfer, https://arxiv.org/abs/1008.1071.
- Raičević et al., transport of actual recombination radiation vs Case A/B approximations, https://arxiv.org/abs/1311.0182.
- Lee, Nungesser and Tod, massless Einstein–Vlasov Bianchi-I evolution, https://arxiv.org/abs/1911.04937.
- Current sibling REI PR #142 separately solves active gamma/nu Einstein/C13 chemistry source, https://github.com/cosmosapjw-quantum/rei_bianchi/pull/142; this C16 instead audits missing energy and momentum source information, not duplicate geometry code.
- BASS PR160 and REI PR140 exact kinetic massive Pi, REI PR137 gamma/nu, native C11/C13 original source retained. bass_cr PR71 requires true positive child moments. rec_bianchi HyRec z20 IC only disabled opt-in. BASS_HE warm-source optical depth has a different physical source; WU088_HH Coulomb results lack an admitted HH rate and remain OFF.

**Next constructive work:** supply source- and transition-resolved emitted recombination photons (N,E,mu) and physical emitter matter four-momentum; evolve baryon velocity and Thomson recoil, then close actual total Q^a on identical source/clock while preserving positive photon and matter stress and the original low-temperature z20 rate domain. C16 provides eventwise source requirements and an exact realizability criterion, not invented missing production rates.

## 6. Reproducibility

From the C16 isolated rei_bianchi worktree:
  export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
  python3 -m unittest discover -s research/rei_c16_qmu_20261015 -p 'test_*.py' -v
  python3 research/rei_c16_qmu_20261015/study.py

An immutable Git payload, independently fresh-restored ZIP and Dropbox/Google Drive byte-identity are verified separately. A cloud copy is NEVER declared completed from an upload command alone.

## Verified release and byte-identical dual cloud backups

The independent source/science commit cf34716245ebcf5e957d9f242fc9d0591c9690b8
was archived as REI_C16_QMU_CASEA_20261015_cf347162.zip, 1,725,089 bytes,
352 entries, CRC PASS. SHA256 =
2537c22ef1e7f61d9c89d3c354d464750e481d65fae4f3b75ac0f98f6b012a4f.
Dropbox and Google Drive authenticated remote full-byte stream readbacks both
matched that exact source SHA. A completely new extraction ran C16-C9 Python
73/73 and newly compiled Rust owner 23/23 tests, 96/96 PASS, then re-executed
C16 actual physics, 19 original Git blob identities and the C15 source state.
Cloud IDs, detailed source tests and performance caveats are in BACKUP_RECEIPT.json
created and committed AFTER the immutable archive. The 3-process parallel result
was 2.83x in the first original run but only 0.87x in independently restored
replay; parallel speedup is therefore NOT robustly established. The actual
3-channel NumPy event allocation microkernel was ~53x faster in both tests.
This scientific release does not alter AX08 native original production input.
