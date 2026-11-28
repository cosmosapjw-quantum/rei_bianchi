> **RECOVERY UPDATE 2026-10-21 10:29 UTC:** Automatic workspace maintenance removed local files during interrupted publication. Code and retained raw27 original cases are being preserved. Prior40-case execution reports below are historical; availability of the remaining13 raw files is under recovery. Do not rerun them or treat all40 as presently available. See RECOVERY_STATUS.json.

# HE29 → REI: matter/radiation 분리 preliminary pilot (2026-10-21)

**Canonical 28건과 matter/radiation 독립 초기조건 12건, 총40개 고유 적분을 완료했다.** 후속18점 view는 새12건과 기존6건을 합친 것이다. 완료된 HE29 reference4/4와 packed canary1/1은 재사용했다. 이 lane은 `rei_bianchi`의 non-tilted Bianchi I 중 **LRS/coaxial finite-resolution pilot**이다. C15의 기존 H/He 결합512행도 실제 저장값에서 정규화했다. 이번 NCP 제출/시작은0이다.

## 최신 결과: matter와 radiation의 초기값도 독립적으로 변화

기본 좌표는 `(Sigma_F,Pi_m,Pi_r)`와 signed `v_m,v_r`다. Canonical matter는 기존 collisionless massive component, radiation은 gamma+massless nu다. 선택한 closure에서 isotropic dust/gas의 trace-free stress는0이다. C15 radiation에는 UV도 포함한다. LRS에서 `Pi_total=abs(v_m+v_r)`이며 일반적으로 `Pi_m+Pi_r`와 같지 않다.

![Final response to independent matter and radiation stress](plots/split_final_response.svg)

열은 최종 `Sigma_F`, `Pi_m`, `Pi_r`, 행은 초기 `Sigma_F=0,.03`이다. 점의 위치는 signed 초기 `v_m={-.0003,0,.0003}`, `v_r={-.0006,0,.0006}`이고 색은 a=.2의 실제 결과다. 각 열의 색 범위는 두 shear plane에서 공통이다. 18점 사이를 보간하지 않았다. v_m≈0인 기존6건은 다시 적분하지 않았다.

예를 들어 `Sigma0=0, v_m0=.0003`에서 `v_r0=+.0006`이면 최종 `Sigma_F=.000180836371633`, `v_r0=-.0006`이면 `.000109367728686`이다. 성분별 magnitude와 상대 방향을 모두 보존해야 이 차이를 해석할 수 있다.

| 구분 | 실제 범위 |
|---|---:|
| 첫 canonical campaign | 새28/28 완료, 실패0 |
| 독립 matter/radiation campaign | 새12/12 완료, 실패0 |
| 후속18점 view | 새12+기존6 재사용 |
| 총 고유 적분 | 40 |
| 새12 initial mapping 최대차 | 1.3877787807814457e-17 |
| 새12 N0 drift | 0 |
| 새12 최소 canonical cell | 약9.911e-31, 양성 |
| 새12 targeted fixtures | 2 PASS, 첫 실행 |
| 검토 이력 | 기존1pass + 사용자 변경 delta1회, 모두 scoped PASS |

같은 source·DOP853·ell8·24×12Gauss3·허용치를 유지하고 massive amplitude만 [후속 계약](SPLIT_INITIAL_CONTRACT_KO.md)에 따라 바꿨다. [18점 endpoint CSV](data/results/split_view_endpoints.csv), [history CSV](data/results/split_view_history.csv), [재사용 identity](data/results/split_view_manifest.json), [delta 검토](evidence/SPECIES_DELTA_REVIEW_KO.md)를 보존했다.

저장값으로 최신 그림만 재생성하는 entry는 `python research/he29_rei_pilot_20261021/src/split_view.py`와 `python research/he29_rei_pilot_20261021/src/render_c15_species.py`다. 적분을 시작하지 않는다. `RUN_READY.sh --dry-plan`은 원래28건, `RUN_READY.sh --campaign split_pilot --out research/he29_rei_pilot_20261021/data/results/split_cases --dry-plan`은 새12건을 읽는다. 둘 다 완료 raw를 재사용하며 현재 pending0이다. 새 output root로 완료 DATA를 숨겨서 재실행하지 않는다.

Git에는 exact UTF-8 source/JSON/CSV/SVG를 게시한다. PNG/PDF는 full archive와 대화 첨부에 보존한다. 아래는 먼저 완료한28건과 C15 저장값 분석의 이력이다.

## 먼저 완료한28건의 성분 분리

사용자의 후속 지시에 따라 **matter와 radiation stress를 분리**했다. 기본 출력은 `(Sigma_F,Pi_m,Pi_r)`와 signed `v_m,v_r`다. 기존 Pi_F는 total의 호환 표시이며 `Pi_total=abs(v_m+v_r)`다. 이28case는 initial Pi_m≈0 단면이고 독립3parametergrid는 아니다. [분리 계약](SPECIES_CONTRACT_KO.md)

![Matter and radiation separately](plots/canonical_species_stress.svg)

![Signed component evolution](plots/canonical_species_signed.svg)

matter stress는 처음 거의0이지만 진행 중 생긴다. radiation과 matter의 부호가 반대면 total에서는 일부 소거된다. component histories는 각각 보존했다.

![28-case magnitude grid](plots/canonical_sigma_pi_grid.svg)

왼쪽은 실제 magnitude trajectory다. 오른쪽 두 panel은 같은 초기 magnitude grid에서 initial stress 방향을 나눈 결과이며 색은 final Sigma_F다. Pi0네case는 두 panel에 공통 표시되지만 실제 unique 실행은28개다. 보간한 연속 surface가 아니다.

![signed trajectories and time evolution](plots/canonical_pilot.svg)

![C15 saved result re-expression](plots/c15_signed_saved.svg)

C15는 a=.1999→.2의 다른 H/He coupled model이다. 첫 저장점은 post-step이며 gravity-source-disabled control에도 physical stress는 남는다.

## 좌표와 초기조건

기본 norm은 Frobenius: Sigma_F=sqrt(6)|s|/H, Pi_F=(8*pi*G/c²)*sqrt(6)|sum pi_s|/H². C15의 deltaP는3으로 나눠 pi_s로 변환하며 signed 합 이후 norm을 취한다. parent half-contraction 값은 각각 /sqrt(2)로 보존한다. H는s^-1, stress는J/m³다.

신규 grid는 Sigma_F={0,.01,.03,.06}, Pi_F={0,.0003,.0006,.0009}, Pi>0마다 stress방향±다. source3b85ded…의 기존 canonical code, gamma/nu, nonbaryonic massive fraction.1, isotropic massive input, ell8,24×12Gauss3, DOP853 rtol3e-11/atol3e-13을 유지했다. a_ref=1/21에서a_end=.2까지101출력시점이다. 전체 분포와 stress 방향을 함께 지정했으며 magnitude두개만으로 autonomous closure를 주장하지 않는다.

## 실제 검증과 실행

| 항목 | 관측 |
|---|---:|
| 새 finite cases | 28 complete /0 failed |
| 원시 state | case마다40×101 +101diagnostics |
| initial Sigma mapping 최대차 | 2.0816681711721685e-17 |
| initial signed stress mapping 최대차 | 9.75781955236954e-19 |
| massless N0 drift | 0 |
| 최소 canonical cell population | 1.491026203638869e-30 |
| derived H² consistency | 2.2170242341817285e-16 |
| 새 Wolfram symbolic residual | 8/8 zero |

H² consistency는 독립 Einstein 인증이 아니다. 독립 한 pass에서 발견된 재개·source-binding·figure·RAMreserve 문제는 작은 수정과 해당 fixture만으로 마감했고 raw28개는 바꾸지 않았다. 실제 실행은 sandbox max2worker이며 NCP 제출/시작0, detailed benchmark0, 완료과학 재실행0이다.

## 최신 자료, 공유자원, 보존

관련7repo의1,214branch refs와 필요한 source/result를 읽고 새 BASS S12/REC U4B 반환을 반영했다. 모든 branch파일 또는 모든 대화를 읽었다는 주장은 아니다. 다른대화 접근오류, Drive범위상한, 미게시 NCP 상태를 그대로 남겼다.

`RUN_READY.sh --dry-plan`은 현재 affinity/cgroup/quota/RAM과 완료결과를 읽는다. 기본 실행은 이미 끝난 이28case를 재사용하며 새로 만들지 않는다. 다른 Codex/science 세션 존재만으로 HOLD하지 않고 가용량과 협력lease에 따라 미완료case만 배분한다. 64CPU/128GiB는 상한이며 실제host관측이 우선한다. 이 lane은 다른미완료campaign을 자동합류시키지 않는다.

- [연구 유도·최적화 판단](RESEARCH_KO.md)
- [고정 계약](IMPLEMENTATION_CONTRACT_KO.md)
- [실제 DAG](DAG_STATUS.json), [delivery](DELIVERY.json)
- [독립 검토](evidence/REVIEW_KO.md)
- [공유자원 정책](RESOURCE_POLICY_KO.md), [source binding](data/SOURCE_BINDING_POLICY.md)
- [pilot CSV](data/results/pilot_summary.csv), [C15 CSV](data/results/c15_normalized.csv)
- [canonical matter/radiation CSV](data/results/canonical_species_stress.csv), [C15 matter/radiation CSV](data/results/c15_species_stress.csv)
- [새 코드 PR82](https://github.com/cosmosapjw-quantum/BASS_HE/pull/82)

실행 가능한 publication pin과 upstream science pin을 구분한다. PR78/81은 Draft/open/unmerged로 유지한다. 일반triaxial, continuous spectrum/시간·공간 수렴, 전체EoR, Grackle동등성, 관측Bianchi/CMB, HPC64속도배율은 HOLD다. 게시·백업 단계의 실제 영수증은 DELIVERY와 evidence에 연결한다.
