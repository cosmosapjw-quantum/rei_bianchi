# BASS_HE 최신 branch/PR 조사와 다음 단원 선택

## 실제 조사 범위

2026-10-22 UTC의 GitHub 직접 readback이다. 브랜치 page 1의 93개와 page 2의 빈 결과를 확인했으며, 전체 상태 PR 목록 page 1에서 88개를 열거했다. 이 기록은 **모든 branch와 PR의 metadata 목록**과 **선택된 최신/관련 source 본문 조사**를 구분한다. 93개 branch의 모든 파일을 전수 정독했다는 뜻은 아니다. 이 작업의 원격 변경, 이전 과학 계산 실행은 모두 0이다.

저장소 default `main`은 `6ef63136d14dbe68a1c9eff4a43fece78cd87b35`이며 README는 초기 audit-led 0.2.0 연구 release다. 현재 후속 연구 SSOT는 개별 연구 branch에 있다. HE32 PR85, HE33 PR86, HE34-SCR PR88의 최신 pin은 각각 기존 `16a424...`, `bb1259...`, `fd11542...`와 같다.

## 새로 확인한 병렬 HE35

PR87의 제목은 HE34 Lorentz로 남아 있지만 최신 head는 `96338b7d3c04b18e31a080e56b34985d31921104`다. 기존 `0868889acebeb4d9b70d38313a9a694d12bf8766`과의 전체 비교는 `research/he35_finite_mass_pair_20261023/`에 추가된 42개 파일을 보여 준다. 기존 HE34 Lorentz README/THEORY/DAG/validation blob은 HE34-SCR에 보존된 값과 같다.

새 HE35의 CONTRACT, THEORY, READINESS, REPORT, IMPLEMENTATION, pair.py, results, fresh review를 exact pin에서 읽고 저장했다. `MANIFEST.json`은 source Git blob과 저장 byte의 SHA256을 함께 기록한다.

- 모델: 등방 pseudo-Maxwell cross kernel `g dσ/dΩ = κ/(4π)`, caller-supplied κ [m³/s]. 실물 H/He differential transport rate를 채택하지 않았다.
- 새 결과: 임의 상대 drift에서 보존적인 momentum/raw second-moment source, central pressure와 drift heating; common-bulk의 thermal/STF 2×2 generator; positive continuous pressure cone; 두 relaxation eigenvalue.
- 기존 저장 검증: 100개 oracle/보존/limit/C parity 검사의 최대 normalized error `1.8670464648487782e-15` < `5e-13`. 후속 zero-κ branch 및 극단 mass-ratio cancellation repair는 각각 delta receipt로 검증되었다. 이 조사에서 재실행하지 않았다.
- 정확한 범위: 조건부 elastic finite-mass 모형의 완성이다. 실물 transport 보정, reactive B2, physical B3 closure, Einstein feedback는 여전히 열려 있다.
- 상호 참조의 시차: HE35 READINESS의 HE88/PR88 상태는 과거 `f1ddb8...` R1–R4 단계다. 최신 PR88은 이미 `fd11542...` 20/20이므로 해당 stale readiness 문장으로 현재 HE34-SCR을 미완료로 바꾸지 않는다.
- HH135는 D energy bookkeeping adapter이며 matched D PI/RR number/capture moments 자체를 확보한 것은 아니라는 HH136 후속 범위를 유지한다.

## 재사용 가능한 더 오래된 H/He source 구조

PR32 `ca85cfc7353da190613f7fb37a6e0ffed9b51913`의 covariant source derivation/contract와 PR33 `94a34d09ad5810a675b556561e5593b279d30448`의 moving-source derivation/contract도 본문을 읽었다. 두 단원은 common-T/common-velocity perfect-fluid gas, warm FT03 30000–110000 K, H/He inventory와 comoving-isotropic escape closure를 고정한다.

재사용할 수 있는 것은 proper-volume/proper-time event normalization, full absorbed photon momentum, single neutral-reference rest-mass/ionic-energy owner, paired matter/radiation energy-current ledger다. PR33은 common endpoint photon elimination과 7-variable conservative source stage 및 primitive admissibility를 유도한다. 이들은 reactive **STF distribution moment**나 다종 핵반응 daughter/stopping source를 주지 않는다. 현 HE32 20000 K/21-state 계약에 warm provider 자체를 그대로 가져오지 않는다.

## 중복하지 않는 다음 연구 단원

**HE36 reactive STF moment bridge**를 권한다. B2.1–B2.3의 구체적 하위 문제로, 등방 bath의 speed-selective loss가 small Grad-STF perturbation에서 유도하는 number/kinetic-energy/STF source를 동일 rate kernel의 0차/1차/2차 에너지 모멘트에 연결한다. Scalar rate와 thermal moment를 reactive tensor relaxation으로 곧바로 대체할 수 없는 이유를 명시적 양의 kernel 반례로 보인다. 이건 HE35의 elastic pair source와 별도다.

그 다음 SI/per-reference-H/per-baryon adapter, energy-owner ledger와 isotope projection/source alignment를 같은 API에 연결할 수 있다. Empirical rate-fit의 2차 미분이 microscopic fourth moment를 검증한 것으로 승격되지 않게 source gate를 둔다. 핵변환 source의 birth momentum/STF/thermalization이 미제공이면 unknown으로 유지한다.

전체 B1/B2/B3/B4/B5 완성도를 하나의 퍼센트로 만들지 않는다. HE35는 B1의 조건부 정확 모형 donor를 추가했고, 새 HE36은 선택된 B2 모멘트 연결을 닫는 범위다. 실물 mixture closure와 coupled gas/metric pilot은 별도 후속 DAG다.
