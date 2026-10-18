# 백업·GitHub 전수 목록과 실제 반영

## 2026-10-18 추가분

기존 2026-10-16 조사를 보존하고 `resume_20261018/`에 새 관측을 기록했다. 기존 Codex 검토를 재사용했으며 추가 독립 검토는 수행하지 않았다.

| 저장소 | 현재 원격 브랜치 | 모든 상태 PR |
|---|---:|---:|
| rei_bianchi | 232 | 192 |
| bass | 253 | 169 |
| rec_bianchi | 118 | 100 |
| BASS_HE | 79 | 74 |
| WU088_HH | 117 | 108 |
| bass_cr | 155 | 79 |
| 합계 | 954 | 722 |

페이지네이션을 끝까지 수행했다. 시점이 다른 저장소들의 관측이며 원자적 동시 snapshot은 아니다. 10월 16일 대비 신규 PR은 27개다. 정확한 head와 변경 목록은 `resume_20261018/GITHUB_DELTAS.json`, 명령·exit는 `GITHUB_COMMANDS.json`에 있다. REI의 새 문서 72개와 다른 공급자의 기존 보고서·검토를 읽었다.

로컬 백업 조사는 이전 명명된 28개 경로의 모든 항목과 프로젝트 내 별도 압축·bundle 파일을 포함한다. 현재 고유 항목은 **6,955개 / 37,525,890,024 bytes**, 이전 대비 새 항목은 **101개**, 크기·mtime가 달라진 기존 항목은 0개다. 이전 toolchain 압축 파일 한 개는 현재 경로에서 보이지 않는다. 이 작업은 파일을 삭제하지 않았다. 이전 조사에서 누락되기 쉬운 target 메타데이터와 디렉터리 symlink도 별도로 재관측했으며 target을 따라가지는 않았다.

새 package 86개 중 ZIP 37개의 member 목록과 작은 README·handoff·review 문서 125개를 읽었다. 나머지 49개는 bundle/patch 등 비컨테이너 또는 미지원 형식으로 명시했다. 전체 archive 해시·CRC 검산이나 완료된 과학 계산을 반복하지 않았다. 작은 archive 문서의 원문은 repo 밖 private 경로에 보관하고 공개 목록만 남겼다.

## 실제 반영과 실행

1. **PR171 positive native reference 재사용:** 원본 native `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`에 결속된 공개 코드·실제 결과 547개 파일을 가져왔다. source commit `57533355976fe10e574d01d338dcc0e9ab9d22a5`의 기존 C9 판정을 재사용했다. 이후 head `c07ba9b839aa003a7b9afb3c6be9adce24761eeb`의 차이는 최종 백업 영수증 5개 추가뿐이며 과학 source/output은 바뀌지 않았다.
2. 저장된 q0와 q=+0.1 관측점 **18개씩 전부**에서 abundance 그림 4개와 CSV 2개를 만들었다. proper time은 native a0 이후 elapsed seconds, Tgas 그림은 실제 시간 순서를 유지한다. H/He 수 abundance의 분모는 nH+4nHe이며 전자는 별도 표시한다. 새 물리 적분은 0회, plotting은 1회/exit0/5.692530077998526초다. 상세 보고서는 `../../bass_source012_source_age_reference_20261016/pr171_reuse_001/REPORT.md`에 있다.
3. **Rate-table C10 구현 반영:** 현재 원격 branch의 `a7e227f01f4dc49491d3138eba9b4985e9f9c57f`를 기존 checkout에 합쳤다. 기본 point 경로는 같은 직접 계수 bundle을 한 번 준비해서 재사용하고 table은 opt-in이다. 기존 C9 scoped PASS를 재사용했다. local point 측정 1.342x는 해당 cohort의 값이며 전체 EoR/NCP64 가속으로 일반화하지 않는다. derivative/Newton table 사용과 완전한 21-state 결합은 HOLD다.
4. **H/He/D S10 native 결과:** PR192 `14837d300d7845bbe50bc7068f058e1591c581e6`의 source·완료 결과를 task 경로로 가져왔다. 기존 4개 완료 이력과 의도된 inner-unresolved 정지를 재실행하지 않았다. 이는 constant prescribed off-shell Bianchi, 제조 D 결함 등 고정 회귀 모델의 scoped 결과다. PR193의 78-file `budget_native.rs`와 PR192의 79-file `nested_budget.rs`를 동일 산출물로 취급하지 않는다.
5. **BASS 접점의 미실행 시험을 실제 실행:** PR193 `267b6e0d7baa416d94e15560e1e61e60132af5b4`의 기존 standalone Rust 시험 10개를 처음 컴파일·실행했고 **10/10 PASS**다. compile 0.5455602690344676초, test 0.021983178099617362초, exit는 각각 0이다. 이는 셀 전체 팽창 guard·clock·threshold의 해당 시험 범위이며 전체 donor 검증이나 native receiver 연결은 아니다.
6. **RUN10의 실제 첫 실패 확보:** 게시된 재개 명령으로 원본 `spectral_edge_support.rs`를 변경 없이 컴파일했다(exit0, 2.9806365609401837초). 시험은 **4 PASS / 2 FAIL**, exit101이다. `first_cell_count_energy_and_positivity`와 `deuterium_crossing_band_is_represented`가 `MomentConvergence`에서 멈췄다. 허용오차·코드·native guard를 완화하거나 재시도하지 않았다. 이 port의 native 연결은 HOLD이며 원시 stdout/stderr를 보존했다.

## 공급자 결과의 경계

- BASS_HE #74의 새로운 같은-source Radau/DOP853와 q0 시간 정제 결과를 재사용한다. cutoff-strip spectral plateau와 장시간/전역 각도·EoR는 HOLD다.
- bass_cr #79의 공통 입력 MIDEXP 결과는 제조 photo-only 모델이다. 원 native Grackle 열 반응이나 PreparedAbsorption의 동등성으로 승격하지 않는다.
- bass #169는 source-only retarded massive-stress 결과이며 현재 prescribed 배경에 stress를 두 번 더하는 항으로 자동 결합하지 않는다.
- WU088_HH #105–108의 기존 유한/complex-energy/on-shell Born 결과는 아직 실제 k_HH(T) 공급자가 아니다.
- REC #99/#100은 이번 관측에서 head가 바뀌지 않았다. 기존 source-qualified candidate와 시간 정제 HOLD를 유지한다.
- R9 Unit8 `6391f3f8bbf34f16c7b36013d424183786a51086`에는 실제 PRIMAT C의 64개 BBN 표본과 조건부 17상태+B_R 사상, LiH·Compton 하위 결과가 추가됐다. 완료된 계산과 기존 검토를 재사용한다. 이 BBN prior를 REI의 cosmology·clock·핵종/전하 inventory에 결속하는 작업은 남아 있다. Li 전하 진화는 BDF 독립 비교 실패로 HOLD다. 원 R9 checkpoint128 이후 residual 후처리는 NumPy API 오류로 exit1이었고, 복구 프로세스의 현재 생존/종료는 관측하지 않았으므로 RUNNING으로 쓰지 않는다.

## 다음 실행과 남은 과학 작업

RUN10의 두 `MomentConvergence` 실패를 원본 수치 규칙과 결속해 분류·수리한 뒤에만 그 spectral port를 진행할 수 있다. BASS guard는 전체 donor와 **선택한 정확한 receiver 계보**를 결속하는 단계가 남았다. 완료된 S10·PR171 계산, 백업 검산, C9 검토를 반복하지 않는다.

전체 FLRW·signed Bianchi 시간/age/spectral 수렴, 전구간 abundance, 활성 isotope network 및 NCP64 scaling은 아직 완료되지 않았다. τ/observer tail은 abundance 작업의 선행 blocker로 만들지 않는다. 기존 deadline과 누적 비용은 초기화하지 않았으며 CI green이나 GOAL_DONE을 주장하지 않는다.

**상태: PAUSED_RESUMABLE / GOAL_DONE=false.** 게시 및 백업의 실제 SHA는 `resume_20261018/DELIVERY_RECEIPT.json`을 읽는다.
