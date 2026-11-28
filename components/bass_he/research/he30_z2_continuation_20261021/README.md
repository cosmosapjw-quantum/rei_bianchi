# HE30: 독립 matter/radiation stress의 z=20→2 preliminary 결과

**237개 완료 궤적을 재사용해 parameter sweep와 시간 진화 그림을 만들었고, 독립 검토는 `PASS_SCOPED_PRELIMINARY`다.** 이번 BASS_HE 작업의 새 과학 IVP·상세 성능 benchmark·NCP 실행은 모두 0이다. 원본 D3는 이전 작업에서 계산되었다. HE30은 복구·물리 검토·벡터 후처리·공유 자원 실행기·그림·REI 후속 D8의 저장 표본 bracket에 기여한다.

핵심 문서는 [물리·실행 계약](CONTRACT_KO.md), [심층 최적화 연구](OPTIMIZATION_RESEARCH_KO.md), [20단계 장부](RESEARCH_LOOP_LEDGER_KO.md), [DAG](DAG.json), [과학 검토](evidence/INDEPENDENT_RESULT_REVIEW_KO.md), [코드 검토](evidence/CHANGED_CODE_REVIEW_KO.md)다. 파일별 source/raw/figure SHA는 [catalog](results/CATALOG.json)와 [figure manifest](plots/FIGURE_MANIFEST.json)에 있다.

## 그림과 실제 데이터

| 산출물 | 읽는 법 |
|---|---|
| [Parameter sweep PNG](plots/parameter_sweep_z2.png) · [SVG](plots/parameter_sweep_z2.svg) | 같은175점의 z2 endpoint를 (Π_m,Σ_F), (Π_r,Σ_F) 두 평면으로 표시. 색은 초기 shear. 점은 중첩될 수 있다. |
| [7개 shear plane PNG](plots/sweep_all_shear_planes.png) · [SVG](plots/sweep_all_shear_planes.svg) | 부호 있는 초기 P_m,P_r의 정확한5×5값. 셀 간격은 categorical이며 연속 surface를 보간하지 않는다. |
| [z20→2 시간 진화 PNG](plots/time_evolution_z20_to_z2.png) · [SVG](plots/time_evolution_z20_to_z2.svg) | Σ_i=.003에서 다섯 초기 성분 조합. 각 norm과 total을 분리하고 z4 exact join을 표시. |
| [Signed cancellation PNG](plots/signed_cancellation_evolution.png) · [SVG](plots/signed_cancellation_evolution.svg) | Σ_i=0, P_m,i=−P_r,i=±.0003 두 경우와 isotropic control. |
| [Endpoint CSV](results/endpoints.csv) | 모든237개 초기축·guard·원본 SHA·z2 값. |
| [Selected histories CSV](results/selected_histories.csv) | 대표 그림8개 case의153개 저장 epoch와 signed/norm 값. |
| [전체 compact NPZ](results/histories.npz) | 237×153 관측량 배열, lossless binary64, 4,688,444bytes. ODE restart용 full raw_y가 아니다. |
| [Late reversal brackets CSV](results/late_reversal_brackets.csv) · [JSON](results/LATE_REVERSAL_BRACKETS.json) | REI의 D8 후속: 네 부호 반전의 저장 인접표본 구간. |

## 표본 집합과 규약

초기 shear는 {0,.0003,.001,.003,.01,.03,.1}, signed matter P_m은 {−.0003,−.0001,0,.0001,.0003}, signed radiation P_r은 {−.001,−.0003,0,.0003,.001}이다. Joint175점과 기존 radiation baseline91점의 overlap35점을 제거하여 nominal231점, 여기에 guard6점을 더하면237점이다. Initial shear orientation은 s_i≥0이다.

각 history의 mean redshift z̄=1/a−1은20→4→2, epoch는121+33−1=153이다. nominal full40/guard full56의 이전 full-state prefix와 tail이 정확히 이어진다. 이 데이터는 reduced8 실행 결과가 아니다.

직교정규 LRS basis D=diag(−1,−1,2)에서 σ=sD, π_X=p_XD로 쓰면

\[
\Sigma_F=\frac{\sqrt6|s|}{H},\quad S=\frac{\sqrt6s}{H},\quad
P_X=\frac{8\pi G}{c^2}\frac{\sqrt6p_X}{H^2},\quad\Pi_X=|P_X|,
\qquad\Pi_{\rm total}=|P_m+P_r|.
\]

SI energy-density stress와 proper-time H를 사용한다. κ_E=8πG/c⁴이면 κ_Ec²|π_X|/H²와 같다. 반수축 norm과는 √2 차이가 있다. matter는 fm=.1 massive collisionless nonbaryonic 성분, 나머지는 isotropic dust이다. radiation은 photon+massless neutrino의 합이다. 현재 ne_source=None이므로 native H/He chemistry를 결합한 결과로 해석하지 않는다.

## 실제 물리 결과

초기 Σ_i=0, P_m,i=+.0003, P_r,i=−.0003의 완전한 total-stress 상쇄는 유지되지 않는다. z2에서 P_m=+5.79655317e−6, P_r=−3.98448076e−5, Π_total=3.40482544e−5, signed S=−3.14595906e−5가 된다. 반대 성분 부호에서는 S=+3.14586629e−5이며, 두 궤적을 정확한 ±대칭이라고 단정하지 않는다.

초기 stress가 모두0이어도 Σ_i=.003이면 이방적인 팽창으로 후속 성분 stress가 생긴다. z2의 P_m=−1.01548439e−7, P_r=−2.44498856e−6, Σ_F=1.53645041e−4이다. 완전한 isotropic control의 Σ_F(z2)=2.07606e−20 같은 부동소수점 잔차는 원자료에 그대로 보존했다.

joint175점 중22개 저장 궤적에서 |S|>1e−12인 비영 표본의 부호 변화가 관찰된다. 그중 Σ_i=.003의25점은 z4에서 모두 양의 shear이고, z2에서 다음 네 점만 음수가 된다. 아래는 저장 표본만으로 얻은 열린 mean-redshift 구간이다.

| P_m,i | P_r,i | 반전이 있는 저장 표본 구간 z̄ | S(z̄=2) |
|---:|---:|---:|---:|
| −.0003 | −.001 | (2.8729833462, 2.9353050508) | −3.56363825e−5 |
| −.0001 | −.001 | (2.5192408407, 2.5758703349) | −2.26357874e−5 |
| 0 | −.001 | (2.3546766722, 2.4086580994) | −1.61356931e−5 |
| +.0001 | −.001 | (2.1978077332, 2.2492649203) | −9.63573431e−6 |

숫자는 exact event root나 유일성 증명이 아니다. 양·음의 signed S를 갖는 인접 저장 표본의 bracket이며 보간과 root solver는 사용하지 않았다. CSV에는 양쪽 표본값·index·case/raw SHA를 담았다.

## 재현과 NCP 자원 정책

기존 저장 데이터로 그림만 재생성한다.

```bash
python3 research/he30_z2_continuation_20261021/src/analyze_saved.py --plot-saved
python3 research/he30_z2_continuation_20261021/src/late_reversal_brackets.py
```

237개 완료 receipt의 재사용과 실제 자원 계획은 다음과 같이 읽는다.

```bash
python3 research/he30_z2_continuation_20261021/src/continuation.py
python3 research/he30_z2_continuation_20261021/src/shared_runner.py \
  --dry-plan --max-workers 64 --reserve-cpus 2 --reserve-gib 16
```

예상 상태는 REUSED_COMPLETE237/pending0/worker_starts0이다. 이 catalog를 다시 과학 pending으로 만들지 않는다. 현재 local actual run도 이 상태를 기록했다. NCP에 새 과학 입력이 생기면 같은 runner API를 입력·결과 identity가 정의된 worker와 연결한다.

runner는 affinity/cgroup quota/실제 CPU idle·RAM·CPU lease의 교집합에서 신규 worker를 배분하고, one native thread와 content identity lock을 쓴다. 다른 세션의 존재를 전체 중지 조건으로 삼지 않는다. 기본64CPU/128GiB의 무부하 가정에서는 CPU2개/RAM16GiB를 남긴 최대62 worker이며 reserve 옵션으로 변경 가능하다. 1GiB/worker는 admission budget이고 실측 RSS가 아니다. 실제 NCP speedup/scaling은 측정하지 않았다.

## 확인한 정확도와 범위

- source/raw/tail/prefix SHA와 정확한121-prefix/33-tail 연결:237/237 PASS.
- 초기 물리축 오차≤1.04e−17, Frobenius shear 대응 오차≤4.17e−17.
- 최소 sampled brightness=.5424751214, N0 저장 배열의 최대 |N0−1|=0.
- 6개 saved refinement pair의 최대 z2 차이: ΔΣ=3.57013e−13, ΔP_m=1.06785e−14, ΔP_r=1.65619e−16, relativeΔH=3.46834e−13.
- 공유 runner의8개 좁은 검사 PASS, 파일 I/O fixture 외 새 science 없음. independent changed-code review blocking finding0.
- 기존100개 serialization 복구의 nfev/timing/RSS 등은 null을 유지했다.

이 판정은 유한 resolution의 collisionless preliminary 결과다. brightness는64 angular sample, Hamiltonian residual은 construction consistency, guard는6개 비교점의 근거다. 연속분포 전체의 오차한계·관측 likelihood·production chemistry·CMB 분석으로 승격하지 않는다.

## 동시 upstream 작업과 통합

초기 intake에서는 D3 원자료가 백업에만 보였다. 게시 직전 최신 REI PR199를 다시 읽어, 다른 세션이 source/results `3a525e3e16f1ba9393818a800327cc58597fd7b5`와 최종 상태 `744438f4512c7df1646aad0136ddc435b27200b0`를 게시한 사실을 확인했다. [실제 관찰 원문](evidence/UPSTREAM_FINAL_STATUS_OBSERVED.md)을 보존했다. HE의 네 그림은 같은 원자료의 별도 파생 표현이며 기존 upstream13종과 합쳐 새로운 science run으로 세지 않는다. D8 bracket은 해당 최신 상태가 남긴 다음 노드를 직접 완료하는 추가 소비 결과다.

957 branch ref 목록과 선택된 관련 원문을 조사했고, 다른 대화 내용은 Personal Context unavailable, Drive HE listing은1000 cap이라는 한계를 기록했다. 전 branch의 모든 파일이나 모든 대화 전체를 읽었다는 주장은 하지 않는다.

게시·백업의 실제 commit, archive hash와 provider ACK는 [delivery](delivery/)를 따른다. 원본 D3 archive와 HE compact package를 구별한다. 상세 이어받기는 [Codex handoff](CODEX_HANDOFF.md), [다음 대화 handoff](NEXT_THREAD_HANDOFF.md)에 있다.
