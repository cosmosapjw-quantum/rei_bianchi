# REI F4: BASS 광자 수·에너지 예산 아래 P19 H/He 6-moment의 비음수 Li I 경계

**2026-10-30, SOURCE-SCOPED / NO-IVP.** 부모 PR270 `691560db50937dc7e3d33b0547a1ac637cba1e92`. 조건부 BASS number+energy 예산을 *가상*으로 수입했다. 부모 PR270 본문/원본 데이터는 수정하지 않는다. Working 33/88, central 28/88, physical fast 4/7, 신규 original 노드 0.

## Scientific result

원래 BASS 71개 photon-bin energy (5–200 eV)와 original cross-section, Puchwein 2019 Table D1 nominal 여섯 모멘트를 사용한다. 먼저 PR270에서 ∑σPhi=6 constraints를 충족하는 해가 존재했고 Li I는 H/He-blind low-energy bin으로 unbounded였다. 이번에는 외부 BASS 원래 `photon_flux_bins_base*Q_B(z)`에서 광자 수 N_B와 energy-weighted flux W_B를 정확한 *두 scalar equality*로 추가한다. 이는 P19 실측 광자예산이 아니며, 기존 BASS power-law shape를 유지한다는 주장도 아니다.

이제 8×71 비음수 선형계획법의 feasible set은 ∑Phi=N_B 덕에 compact하고, Li I 전리율의 유한 min/max가 존재한다. 일곱 저장 redshift에서 실제 LP 해를 구했고 각 extreme은 8개 양의 photon-bin으로 표현된다. 75자리 mpmath로 선택된 8×8 basis의 exact represented-binary64 primal과 전체 71개 dual constraint를 다시 계산해 모든 14개 certificate를 검증했다. 엄밀한 cross-section 실수값 enclosure가 아니라 floating-source representation에 대한 대수/수치 검증이다.

| mean z | N_B (photons m^-² s^-¹) | Li I min (s^-¹) | Li I max (s^-¹) | original BASS LiI (s^-¹) |
|---:|---:|---:|---:|---:|
| 2.404494 | 1.99512941e+10 | 7.168369730e-13 | 2.722821664e-12 | 2.283675732e-12 |
| 2.789073 | 1.99509639e+10 | 9.813150265e-13 | 2.504352202e-12 | 2.283637939e-12 |
| 3.217095 | 1.99499400e+10 | 1.116325642e-12 | 2.399102213e-12 | 2.283520739e-12 |
| 3.603020 | 1.99474090e+10 | 1.148652795e-12 | 2.377503008e-12 | 2.283231042e-12 |
| 4.024262 | 1.99397805e+10 | 1.155478489e-12 | 2.370875039e-12 | 2.282357856e-12 |
| 4.378370 | 1.99231220e+10 | 1.145694593e-12 | 2.372292834e-12 | 2.280451083e-12 |
| 4.701690 | 1.98879315e+10 | 1.122098684e-12 | 2.378044996e-12 | 2.276423094e-12 |

중앙 z=3.603019593: N_B = 1.9947409e10 photons m^-2s^-1, W_B = 2.5296663e11 eV m^-2s^-1, Li I ∈ [1.14865279485e-12, 2.37750300760e-12] s^-1. 예산 없음 상한 무한, N만 고정할 때 상한 3.02886037515e-12, W만 고정할 때 상한 5.71403555712e-12. 두 예산을 모두 고정하면 Li I 허용 구간이 확연히 좁아진다. 기존 BASS Li 전리율이 구간 안에 들어오는 것은 전체 여섯 모멘트의 일치를 뜻하지 않는다.

## Independent verification tiers

- Source-locked: PR270 source ZIP의 SHA-256 및 원 BASS Python/model, REI saved7 원본 SHA를 별도로 보존·검사. No new IVP.
- Constructive: 7×2 HiGHS endpoints and 14 high-precision mpmath primal/dual certificates. CAS Wolfram: H/He blind ray에 대한 zero six-moment, number budget은 lambda, energy budget은 E*lambda 증가 확인.
- Software: Python `unittest` 12/12 PASS (초기 test-only 이름 오류 2건과 수리 이력 보존). Native different-author R6/C9 NOT_RUN. CLI CPUS and host overhead not all measured; UNKNOWN_NOT_ZERO.
- Scientific claim: BASS photon number/energy 가정 아래 frozen snapshot LP only. P19 실제 photon budget, BASS original source replacement, REI self-consistent chemistry, opacity, τ_T, CMB, posterior 모두 미계산.

## Latest cross-repo census and next physics

PR271은 98개 동결 이온 사건의 P19 D1 에너지 원장, VigilODE PR118은 BASS 원본 127 endpoint와 25쌍 τ 데이터, BASS PR258은 독립 Einstein–Vlasov photon geometry, CR PR125는 RR 방출 photon source를 제공한다. 하지만 현재 고정된 REI/BASS/P19의 공통 스펙트럼+isotope inventory+H/nHref/nb/K/clock을 제공하는 인증된 adapter는 없다. 다른 branch를 물리 input으로 임의 대체하지 않는다. 정확한 다음 조치는 isotope/source owner에 의한 광자 N/E 예산 및 Li 진단 우선조건, 원래 REI full17 화학, BASS full21, 초기·경계·geometry 결합 확인이다.

**Bounded decision:** `PASS_SCOPED_CONDITIONAL_BUDGET_CONE`, `F4=PARTIAL`, `L4=false`, `NO_MORE_IVPs=true`, DAG unchanged.
