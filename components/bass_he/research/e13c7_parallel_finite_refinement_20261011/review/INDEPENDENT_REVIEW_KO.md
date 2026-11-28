# E13C7 독립 판정: local finite refinement 채택, heavy NCP 전달 준비 완료

**판정은 local 8경로에 대해 `PROMOTE`, 남은 2,331경로 NCP 작업에 대해 `READY`다.** 실제 heavy 계산, 실제 OpenMPI 실행 및 64-rank 가속률은 모두 `NOT_RUN`이다. Physical·continuum·production·receiver는 `HOLD`를 유지한다. 이 판정은 원래 고정 captured OFF 문제와 상속된 directed-interval 포함 증명의 전제 안에서만 성립한다.

검토자는 후보 scientific kernel·wrapper·입력·검증 설계를 작성하거나 수정하지 않았다. 이번 독립 검토의 후보 모듈 import, 과학 kernel 호출, MPI 호출은 모두 0이다. 실제 source와 저장된 결과를 읽고, 독립적인 Fraction 계산 및 실제 bytes/SHA 검증으로 사전에 선언된 기준을 평가했다. 병렬 실행기 하위 검토도 후보 생성과 분리된 역할에서 수행했다. [전체 기계 판정](INDEPENDENT_DECISION.json)

## 1. 채택하는 결과

완료된 local 작업은 총 **24개 path work item·56개 fresh segment enclosure·38,656 coefficient evaluation**이다. 이 수치는 같은 경로의 서로 다른 N/P 진단을 별도 work item으로 센다. 새로 채택하는 고유 경로는 아래 8개다. [실제 결과와 합산 검토](LOCAL_ANALYSIS_REVIEW.json)

| 최종 N | Precision | 채택 경로 |
|---|---:|---|
| 1024 | 60 | 105, 409, 1162, 1976 |
| 512 | 60 | 106, 414, 1620, 2344 |

8개 N512 primary의 old/new raw 272쌍 모두 overlap·nesting·폭 비증가를 통과했다. 네 N1024 진단은 기존 old interval뿐 아니라 대응 N512의 34쌍도 모두 만족하므로 그 네 경로에 한해 N1024를 선택했다. N32/P60/P80의 precision 비교 136쌍은 모두 겹쳤다. 같은 N128의 새 bound가 기존 방법보다 우월하다는 주장은 `NOT_ESTABLISHED`이며, 해당 대조 결과는 채택하지 않고 보존한다. [Primary](PRIMARY_OUTPUT_REVIEW.json) · [Resolution](RESOLUTION_OUTPUT_REVIEW.json) · [Precision](BRANCH_PRECISION_REVIEW.json)

원 weight가 이미 한 번 적용된 interval을 사용하여 다음 네 집합을 직접 합산했다.

\[
I_X^{C7}=I_{X,\mathrm{prior}\,6}^{C6}
+I_{X,\mathrm{local}\,8}^{C7}
+I_{X,\mathrm{bulk}\,2331}^{\mathrm{old}}
+[0,0]_{X,95}.
\]

이 집합들은 중복 없이 원 OFF 2,440개 경로를 덮는다. Retained interval은 full interval에서 interval subtraction으로 얻지 않았다. 종별 A/B/H total은 old와 new 양쪽에서 같은 세 종 interval의 합이다. 선택된 raw endpoint와 전체 direct sum에 interval intersection을 적용하지 않았다. 모든 absolute 17개와 correction 17개, 총 34개 predecessor bridge 및 새 full nesting을 정확 유리수로 확인했다. [입력·분할 검토](STATIC_INPUT_REVIEW.json) · [전체 합산 검토](LOCAL_ANALYSIS_REVIEW.json)

| 전체 OFF enclosure 폭 | E13C6 이전 값 | 이번 local 채택 후 | 감소율 |
|---|---:|---:|---:|
| Photon `P_final` | 6.146898919840214965239e−17 | 6.081259221168360060912e−17 | 1.067850627248661017884% |
| Heat `H_total_eV` | 3.898810089742915645520e−16 | 3.883292513115486482735e−16 | 0.3980080145030192819636% |

이번 채택 후에도 남은 bulk가 전체 photon 폭의 99.86027006235353%, heat 폭의 99.95893153175415%를 차지한다. 이는 그대로 보존된 old bulk 폭을 새 full 폭으로 나눈 값이다. [폭 점유율 계산](INDEPENDENT_DECISION.json)

이 수치는 남은 2,331경로에 기존 enclosure를 유지한 상태의 실제 finite sum이다. 미래 bulk 실행으로 얻을 폭 감소를 미리 포함하지 않는다. 분석 semantic과 CSV의 실제 bytes도 독립적으로 재계산했다. [전체 합산 검토](LOCAL_ANALYSIS_REVIEW.json)

## 2. 수학적 전제와 보존한 의미

고정 gas stage·source·mask 아래의 방정식은 선형이며 첫 photon stock은 정확히 0이다. Source-off 95경로는 두 구간 모두 q=0이므로 초기값 문제의 유일성으로 P=0이다. 저장된 old absolute/correction 34항의 양 endpoint도 실제로 모두 0이다. 따라서 이 95경로를 새 quadrature 대상에서 제외한다. [입력·분할 검토](STATIC_INPUT_REVIEW.json)

경로 사이에는 계산 의존성이 없지만 한 경로 안에서는 구간 순서를 보존한다. 다음 incoming correction에는 이전 outgoing correction과 captured stitch residual을 한 번씩만 포함한다. Moment는 감쇠 없이 누적하고 photon stock은 마지막 endpoint만 사용한다. Signed energy seam은 실제 부호를 유지하여 전역 energy ledger에서 뺀다. 검토에서는 저장된 center/radius 및 interval 관계를 이 정의로 대조했다. [저장된 경로 관계 검토](BRANCH_OUTPUT_REVIEW.json)

Node 1620 및 2344의 미세한 natural threshold 차이는 원 captured branch의 일부로 남긴다. Cutoff에 맞추어 energy를 잘라내거나 source/mask를 재선택하지 않는다. Bulk 2,331경로의 ordinary branch 정적 감사와 event 경로의 고정 branch 의미는 구별되어 있다. 상속된 kernel의 동일 bytes를 유지했으며, ledger의 consistency와 같은 코드 재현을 독립 coefficient oracle로 간주하지 않는다. 전역 반경의 보편적인 N⁻² 법칙이나 물리적인 참오차 감소도 주장하지 않는다. [전체 판정의 전제·한계](INDEPENDENT_DECISION.json)

## 3. NCP에 전달할 계산과 자원 해석

봉인된 heavy scope는 **남은 2,331개 일반 경로를 N1024/P60에서 한 번만** 계산하는 것이다. 총 4,662개 fresh segment, **9,547,776 coefficient evaluation**에 해당한다. 기존 6경로·정확 영해 95경로·이번 local 8경로는 제외한다. 짧은 과학 재현, N512 전체 사전 실행, 추가 precision sweep은 이 작업에 포함되지 않는다. 최종 전역 Fraction 합산과 독립 수용 판정은 반환 후 Chat에서 수행한다. [선택·비용 검토](LOCAL_ANALYSIS_REVIEW.json) · [최종 실행 봉인](FINAL_EXECUTION_SEAL_REVIEW.json)

실제 local parallel pilot는 **4개 computing process, 서로 다른 CPU affinity [0]–[3], 8개 N512 경로, wall 24.49429002699617초**로 완료됐다. 각 process exit code는 0이다. 이 실행은 local transport이며 OpenMPI 실행을 대신하지 않는다. [병렬 독립 검토](parallel_read/PARALLEL_READ_REVIEW.json)

NCP 설계는 최대 64개의 computing MPI rank와 별도 launcher를 사용한다. 모든 MPI rank가 계산하므로 별도 rank0 controller를 예약하지 않는다. 정적 LPT는 측정된 branch class 비용을 기준으로 비싼 경로를 분산하고, 최종 collection은 node 순서로 정렬한다. 현재 WORK_PLAN의 64-rank shard 목록과 비용 합은 Fraction으로 독립 재현했다. 이론 기여의 초기 63-worker 권고는 채택되지 않은 제안으로 보존되며 최종 실행 계약과 혼동하지 않는다.

시간 모델은 기존 동일 workload의 기록된 host 비율과 이번 local class별 elapsed mean을 사용한 외삽이다. N1024의 한 worker 환산 약 **26.63시간**, 이상적인 64-rank 약 **24.97분**, 효율 80%/50%를 가정한 약 **31.21분/49.93분**은 측정된 NCP bulk 시간이 아니다. 실제 64-rank scaling은 `NOT_RUN`이다. [시간·스케줄 검토](LOCAL_ANALYSIS_REVIEW.json)

실측 최대 local worker RSS는 50,496 KiB다. 이를 64배 한 3.08203125 GiB는 memory scenario이며, rank당 1 GiB는 별도의 주소 공간 cap이다. RAM을 채우는 것이 목적이 아니다. 실제 host의 affinity·관측 quota·가용 memory로 rank 수를 제한하고 적어도 20%의 memory reserve를 둔다. 없는 cgroup 제한 파일은 `UNOBSERVED`로 기록하며 무제한 quota나 provider 신원을 추정하지 않는다. [자원 판별 검토](parallel_read/PARALLEL_READ_REVIEW.json)

## 4. 실패 및 수정의 보존

**검토자의 첫 center/radius assertion 오류 35개를 보존했다.** 초기 검토식은 outward-rounded 직렬화 interval의 양 끝점을 다시 더한 더 강한 조건을 요구했다. 실제 상속 증명은 저장된 exact center와 radius의 합에 recentering을 포함하는 조건이다. 검토식을 그 조건으로 바로잡았고 tolerance를 추가하지 않았다. 후보 코드·결과는 바꾸지 않았으며 과학 계산을 다시 실행하지 않았다. [수정 근거](REVIEW_CHECK_CORRECTION.json) · [첫 실패 원본](BRANCH_OUTPUT_REVIEW_FIRST_FAILURE.json)

실행 boundary의 두 실제 문제가 별도로 수정됐다. Wrapper interrupt는 이전 구현에서 살아 있는 자식을 남긴 채 failure archive를 반환했다. 첫 실패를 실제 sleeping child로 재현하여 보존했고, 수정 후에는 child exit −15와 종료 후 packaging을 확인했다. 두 archive 각각의 payload 9개와 manifest, 총 10개 member의 실제 bytes/SHA를 독립 검증했다. 실제 MPI의 process tree 종료까지 검증한 것은 아니다. [Interrupt 수정 검토](NCP_ENTRYPOINT_REPAIR_REVIEW.json)

외부 경로에 놓인 return을 package 상대 경로로 표시하려다 발생한 ValueError도 보존했다. 수정은 표시 경로 분기 하나에 한정되며, 34개 exact metric과 numerical semantic이 같다. 저장된 local 8경로로 수행한 return-reduction rehearsal의 exact endpoint는 이전 별도 N512-only 분석과 같다. Rehearsal의 CSV와 semantic도 각각 독립 재계산에 일치한다. 새 과학 호출은 0이다. [Return reducer 검토](RETURN_REDUCER_REHEARSAL_REVIEW.json)

병렬 runner의 파일 머리말에 있는 import 순서 설명에는 비차단 한계가 남는다. Fresh launch의 자원 사전 확인 순서는 맞지만 명시적 resume에서는 저장 완료 검증을 위한 vendor import가 host preflight보다 앞선다. 이 resume 경로는 과학 `ctx.run`을 호출하지 않는다. 이 설명 차이를 실제 재실행으로 해석하지 않으며 독립 보고서에 기록했다. [병렬 독립 검토](parallel_read/PARALLEL_READ_REVIEW.json)

## 5. 최종 실행 신원과 판정 한계

| 식별자 | 실제 SHA-256 |
|---|---|
| Scientific SOURCE_LOCK | `386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f` |
| Final EXECUTION_LOCK | `c04cfde1838563d95389e499de9bcbe505a7d67f6bda1fff4476af953c8cc4f4` |
| Local analysis semantic | `da8e607c193643b3f21a07130d654e3bbc8292599f7f4543989647222fb9f929` |
| Local admission candidate | `52be78b951f71daf41892f6dd93aeb2df6f8c3cd9af9f3628e0cdd84ed61b55a` |
| Local width CSV | `1162429edd4de506001a3bf27556d26891d1f0dfb8762bd68a169431ca0e04d2` |
| Preserved pilot EXECUTION_LOCK | `649dee06365b89251f62f6fd131f6cdc34fd61481084214a5c97d2eae7db5336` |

Final execution lock은 실제 **10,078 bytes**다. 그 안의 **60개 파일**을 모두 실제 bytes/SHA로 확인했고, scientific source pin 17개 및 runtime Python 파일 10개의 closure도 확인했다. 최종 봉인 독립 검토는 **171개 확인 통과, 실패 0개**다. 이전 pilot는 보존된 당시 WORK_PLAN과 당시 execution lock에 결합하며 새 N1024 봉인과 섞지 않았다. [최종 봉인 검토](FINAL_EXECUTION_SEAL_REVIEW.json)

`READY`는 이 정확한 코드·입력·scope의 전달 준비 판정이다. NCP host에서 실제 OpenMPI 실행, 환경 전달, rank binding과 완료 증거가 아직 없다. 2,331경로의 actual return 없이는 bulk refinement를 채택할 수 없다. Physical·continuum·production·receiver 및 provider attestation의 기존 한계도 그대로 유지한다. 백업 업로드·원격 readback과 사용자용 최종 handoff prompt는 delivery owner의 별도 작업이다.
