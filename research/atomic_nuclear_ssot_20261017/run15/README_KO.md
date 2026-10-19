# RUN15 재개 결과와 현재 SSOT

## 성과와 미완료 항목

RUN13 원본333 파일과113 source/input을 현재 Git 및 실제 재다운로드한 Drive ZIP에서 복원·대조했다. 원래 m=1,2 standard/tight 네 endpoint의21개 관측량씩 총84개도 재적분 없이 정확히 재구성했다. 기존 완료 RUN13/RUN14 native 이력의 재실행은0회다.

이번 작업에는 실제 실행환경 문제가 있었다. 새 optical n4/n6/n8 standard 및 n8 tight 네 coupled IVP를 완료하고 로컬 archive의 342개 파일 roundtrip을 검증한 후, 외부 게시 전에 작업 디렉터리의 모든 작업 파일이 보이지 않게 됐다. 두 agent도 같은 상태를 확인했다. 원인은 확정되지 않았으며 파일을 삭제하는 assistant 명령은 없었다. 네 이력의 raw state/packet/ZIP bytes는 현재 복원하지 못했다. 이 네 수치는 실제 실행 대화에서 회수한 기록으로 분리하며 재시작 가능한 endpoint로 취급하지 않는다. 해당 raw history의 원격 전달은 실패한 상태다.

그 뒤 원본을 다시 Git/Drive에서 확보하고, 해시가 맞는 소스를 회수했으며, 독립된 새 source로 fixed-gas spectral 진단과 native quadrature 개발을 실제 완료했다. 이 postloss 산출물은 소스·입력 identity·결과·검증파일이 모두 현재 존재하며 아래 명령으로 재현할 수 있다.

## 1. 실제 읽은 SSOT

- Repository: https://github.com/cosmosapjw-quantum/rei_bianchi
- Original recovery branch: research/rei-atomic-run13-m2-recovery-20261018
- 실제 원격 source HEAD: `3dcb5f7aed8d33ff64f7952e9465f4239a216c89`. 사용자 handoff의 b164611은 이전 checkpoint다. 이 HEAD에는 RUN13 original source/result backfill이 이미 게시돼 있어 같은 backfill을 중복하지 않았다.
- 현재 작업 branch: `research/rei-run15-subh-optical-enclosure-20261019`
- Source checkpoint: `9777d519f2fd6ab521b10c6ee67b8f20e9dd6f04`
- 원본 RUN13 ZIP: 41,075,268 bytes; SHA256 `6912c7f90dedaaee312d3fdc3248e4e8839409c0fb2944262de945e1b2f34e96`. 이 값은 이번 환경에서 실제 바이트를 계산한 값이다.
- 원본 RUN13 README/RESUME/DAG_PROGRESS/SOURCE_IDENTITY/manifest와 saved results, RUN10 source/provenance, 뒤에 발견한 RUN14 UNIT01/02 raw analysis를 읽었다. RUN14 JSON 두 개는 소실 후에도 다시 다운로드해 원래 SHA 및 Dropbox content hash와 대조했다.
- 원래45-node/26-node DAG 원문은 recovery/dag에 byte-exact로 보존한다. 원래 DAG를 줄이거나 다른 노드로 교체하지 않았다.

기존 main/production/atomic owner와 historical archive는 수정하지 않았다. 선택한 과학 노드는 `P4-S4C-SPECTRAL-EDGE-SUPPORT/SUBTHRESHOLD-SURVIVOR-RESOLUTION`이다.

## 2. 새로 실행하고 보존한 fixed-gas 결과

원래 160개 birth sample, GL8, 첫 cell의 원래 source count, native geometry 및 H/D gates를 유지했다. Gas는 원래 m2 checkpoints로 정의한 PCHIP를 고정했다. Tight는 초기 상태 포함13 knots, standard는18 knots다. 아래 값은 직접 계산한 sub-H-fit **core survivor**이며 단위는 comoving m^-3이다.

| Gas 경로 | Energy GL | Time GL | Core survivor |
|---|---:|---:|---:|
| Tight13 | 6 | 16 | 1.1803145224978455e-10 |
| Tight13 | 8 | 16 | 1.1803145305926034e-10 |
| Tight13 | 12 | 16 | 1.180314530581173e-10 |
| Tight13 | 12 | 24 | 1.1803145305811728e-10 |
| Standard18 | 12 | 24 | 1.180315129027609e-10 |

뒤 설정을 분모로 한 상대 변화는 energy6→8 +6.858136308903119e-9, energy8→12 −9.684150537524571e-12, time16→24 −2.1900428633674603e-16, tight13→standard18 +5.070225921291e-7이다. 마지막 대조는 PCHIP knot 배치와 저장된 solver 경로를 함께 바꾼 민감도다. Same-grid ODE tolerance 비교가 아니다.

Tight13의 energy12/time24에서 terminal binding preimage를 panel 경계에 명시적으로 넣었다. E_final<H_binding 성분은8.400293020544156e-11, H_binding≤E_final<H_fit 성분은3.402852285267486e-11이다. 이 분류용 binding edge를 absorption fitting edge로 바꾸지 않았다.

양의 H-only opacity로 얻은 조건부 omitted-tail upper는1.3682511605478213e-24 comoving m^-3이다. Lambda_min=65589.60643536107 eV^-1이고 core 최대 birth energy13.600487882177362 eV는 D gate보다 낮다. 이 tail 값은 **core quadrature error·부동소수점 roundoff·실제 gas-path error를 포함하지 않는다.** Numerical core+tail을 엄밀한 전체 interval로 부르지 않는다.

독립 scalar native-geometry/adaptive optical-depth 검사와 vector 계산의 최대 tau 상대 차이는1.6150603077136338e-10이다. 따라서 마지막 energy/time 차이를 그대로 실제 정확도로 승격하지 않는다. Fixed-gas 전체 script wall time은2.330270231999748초였고5개 setting을 실행했다. 새 focused tests5/5 PASS 및 한 번의 independent owner static review를 포함한다. Native IVP는0회다.

전체 숫자·소스·입력 hash는 postloss_diagnostic/FIXED_GAS_OPTICAL_RESPONSE.json을, 자세한 유도는 notes/DERIVATION_AND_SCOPE_KO.md와 postloss_diagnostic 문서를 따른다.

## 3. 기존 결과와 소실 전 새 native 결과

다음 원래 RUN13 값은 현재 존재하는 saved state에서 다시 계산했다.

| 이력 | sub-H-fit survivor, comoving m^-3 |
|---|---:|
| m1 standard | 3.963580101474543e-12 |
| m1 tight | 3.963580101474519e-12 |
| m2 standard | 8.255385244169650e-12 |
| m2 tight | 8.255385244169626e-12 |

Standard m2를 분모로 한 m1/m2 차이는0.5198794502929087이다. 전체 survivor가 안정적이어도 이 작은 성분은 수렴하지 않았다. DeltaP+sumDeltaA−DeltaB=DeltaR는 fsum과Decimal100으로 일치했다. Ledger 일치는 spectral error bound가 아니다.

소실 전 이번 실제 native coupled 실행의 완료 수치는 다음과 같다. **이 표는 transcript evidence이며 raw state/packet bytes를 제공하는 표가 아니다.**

| Optical rule | rtol | 사건 구간 | 상태 차원 | sub-H-fit survivor |
|---|---:|---:|---:|---:|
| n4 standard | 3e-11 | 11361 | 45717 | 1.1803048042732013e-10 |
| n6 standard | 3e-11 | 15176 | 49533 | 1.1803140405809306e-10 |
| n8 standard | 3e-11 | 18993 | 53349 | 1.180314048527879e-10 |
| n8 tight | 6e-12 | 18993 | 53349 | 1.1803140485278792e-10 |

앞 설정을 분모로 한 native n4→6 상대차7.825358073504074e-6, n6→8 6.732910044120797e-9, 동일 n8 packet의 tight−standard2.1900437578051546e-16을 실제 계산했다. n8tight의 total survivor는5.108957615367321e-7, temperature는9994.351248166906 K로 실행 출력에서 회수했다. Native uniform m=4는 실행하지 않았다. 광학 core의 node order n과 uniform refinement m을 섞지 않는다.

현재 존재하는 postloss fixed-gas reference와 위 coupled 값은 gas 경로와 증거 보존 상태가 다르다. 서로의 차이를 즉시 continuum error 또는 nonlinear feedback error의 인증값으로 쓰지 않는다.

## 4. 코드·실행환경·실제 검증

공식 rustc/cargo/rust-std1.94.1의 총119,463,700 bytes를 SHA 대조·safe tar 점검 후 설치했다. 원래 gas crate를 --release --offline --locked로 빌드한571,904-byte binary의 SHA는 `3454e9e401560df188c7410de29d0712c4afe235e9899021e5314766ab778c8b`로 역사적 binary와 같다. 공식 checksum을 대조했으며 PGP 검증은 수행하지 않았다.

새 postloss native crate는 확실한 원문 production prefix324행과 exact main.rs를 사용한다. 누락된 원래 tests를 추측 복구하지 않았다. 새 binary는569,800 bytes, SHA `ec88048296f47a4683595aeddcafe2453cfef85bdada53189143913b076e8f66`이다. 세 제조 source controls(kT4 eV)에서 모든 weights 양수·node 내부·mass 상대차≤1.66e-16·physical mean 절대차≤1.78e-15 eV를 확인했다. Narrow-band의 local-coordinate M2 차이3.908668023718045e-9와 QUADPACK roundoff warning도 보존했다. 이 검사는 원래50,000 K source native IVP의 반복이 아니다.

현재 검증 가능한 증거에는 original333/113, endpoint84, exact gas build, native3controls, Python5tests/5settings, 원래 DAG와 RUN14 raw JSON이 있다. 소실 전 실제 실행했던 Rust160/Python11/endpointguard10/newprotocol19/native9/theory7/gascomparison9/archive17 tests의 요약은 보존하되, 소실된 로그를 현재 원문으로 제공했다고 주장하지 않는다. 이 숫자들을 새 실행 또는 독립 과학 IVP 횟수로 중복 집계하지 않는다.

환경은 Python3.12.14, NumPy2.3.5, SciPy1.17.0, Rust/Cargo1.94.1, Linux x86_64 glibc2.39이다. 실제 명령과 stdout/stderr는 개별 receipt와 postloss_runtime_delivery에 있다.

## 5. 현재 한계와 다음 연구

- 새 네 native raw history의 외부 전달은 미완료다. 소스 일부와 두 enclosure JSON은 기존SHA 일치로 회수했지만 전체 `run_joint.py`/`build_packet.py`, packet 및 342개 case 파일의 바이트는 현재 없다. 원래 exact restore verifier는 보존용이며 이 누락 상태에서 통과할 수 없다.
- 원래 source checker는 없는 historical contract path를 요구했고, sparse Git 전체status는 promisor fetch 네트워크에서 실패했다. 실패를 남기고 실제 sealed manifest와 범위가 지정된 Git blob/byte 검증으로 원본 복원을 완료했다.
- Native source control의 독립 QUADPACK roundoff warning, narrow-coordinate moment conditioning, scalar/vector tau 차이를 정확도 한계로 유지한다.
- 지정된 PCHIP path의 fixed-source energy refinement를 검증했다. 실제 gas 경로의 knot 사이, continuous-source nonlinear opacity feedback 및 rigorous core error는 아직 미확립이다. 두/세 유한 표본에서 asymptotic order나 Richardson15 bound를 선언하지 않는다.

다음 과학 작업은 같은 기존 노드 안에서 실제 gas trajectory의 event 사이 오차를 통제하고, 고정 경로의 energy integration과 연속 source feedback을 분리하는 일이다. Continuous spectral refinement, angular convergence, birth-time continuum, whole donor domain, full EoR, Einstein feedback, FLRW-CONV, BI-SIGNED, ISO-COUPLE full, Li/Be 및 nuclearT1–T8은 전부 유지한다. 상세 지위는 SCIENTIFIC_ADMISSIONS.json을 따른다.

## 6. 최소 재개 명령

먼저 Git의 run13/git_transport/restore.py로 원본 payload를 복원한다. 완료된 RUN13 IVP를 다시 실행하지 않는다. 새 fixed-gas 진단은 다음처럼 새 output에 실행한다.

```bash
python3 research/atomic_nuclear_ssot_20261017/run15/postloss_diagnostic/postloss_fixed_gas_optical_response.py \
  --source-root /ABSOLUTE/CHECKOUT/research/atomic_nuclear_ssot_20261017/run13/recovered \
  --output /ABSOLUTE/NEW_OUTPUT/FIXED_GAS_OPTICAL_RESPONSE.json
```

Postloss native 빌드는 해당 README의 materialize.py와 build_and_check.py를 사용하며 원래 source-root/toolchain-prefix/output-root를 명시한다. 기존 출력은 덮어쓰지 않는다.

최종 clean Git 재현과 archive SHA/백업 위치는 후속 DELIVERY 및 RESUME_DELIVERY.json에 기록한다. Upload acknowledgement, 원격 metadata, download byte verification, 계산 재현은 각각 별도 결과로 표시한다.
