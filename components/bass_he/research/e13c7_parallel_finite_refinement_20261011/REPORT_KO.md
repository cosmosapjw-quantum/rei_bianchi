# BASS_HE E13C7 — 경량 연구 완료와 중량 병렬 정밀화 인계

연구 노드: `HE_E13C7_PARALLEL_FINITE_REFINEMENT01`  
작성일: 2026-10-11 UTC  
계승 기준: [BASS_HE PR22](https://github.com/cosmosapjw-quantum/BASS_HE/pull/22), `019dc4f6451b3076eb6c21f8836a6040b232e945`

## 1. 이번 루프의 결론

짧은 계산과 분석을 ChatGPT 연구 환경에서 마쳤고, NCP에는 **새로운 OFF 2,331경로의 N1024/P60 정밀화 한 번**만 전달한다. 이미 끝난 경로, 정확히 영인 경로, 전체 예산의 가벼운 Fraction 합산은 중량 작업에서 제외했다. 이번에 실제로 실행한 것은 24개 경로 작업, 56개 새 구간 enclosure, 38,656회 coefficient evaluation이다. 새 NCP 중량 경로 실행은 0이며, 실제 Open MPI 실행과 64 rank 가속률도 아직 측정되지 않았다.

로컬 8경로의 새 enclosure를 반영하면 전체 OFF의 광자 구간 폭은 1.06785%, 열 구간 폭은 0.398008% 줄어든다. 이 변화는 나머지 2,331경로를 이전 enclosure로 유지한 **현재의 실제 유한 합산 결과**다. 아직 계산하지 않은 중량 경로의 개선을 미리 더하지 않았다. 그 중량 경로가 현재 광자 폭의 99.8602701%, 열 폭의 99.9589315%를 차지하므로, 다음 계산 자원은 이 집합에 쓰는 것이 타당하다.

독립 최종 판정은 **PROMOTE_SCOPED_LOCAL_FINITE_REFINEMENT_AND_READY_HEAVY_HANDOFF**다. 판정과 해시는 `review/INDEPENDENT_DECISION.json` 및 `review/INDEPENDENT_REVIEW_KO.md`에 기록되어 있다. 수용 범위는 같은 captured input에 대한 조건부 유한 enclosure 정밀화다. **physical·continuum·production·receiver는 HOLD**를 유지한다.

## 2. 끊긴 작업에서 회수한 실제 증거

이전 전송 실패 영수증을 보존하고, 이후 생성된 E13C6 실제 반환 ZIP 두 건을 검증했다. 실제 ZIP bytes/SHA, 반환 내부의 수치 semantic projection, 분석 semantic projection, CSV bytes를 확인했다. 156개의 독립 intake 확인에서 실패는 없었다.

| 항목 | 앞선 반환 | 최근 반환 |
|---|---:|---:|
| ZIP bytes | 274,477 | 274,620 |
| 기록된 호스트 | cosmosapjw | s1a0e5abed09 |
| 사용 가능 affinity | 0–23 | 0–63 |
| 실제 과학 자식 affinity | `[0]` | `[0]` |
| 같은 4경로 N512/P60 과학 시간 | 26.693812809초 | 48.764258135초 |
| Python / libmpdec | 3.12.3 / 2.5.1 | 3.12.3 / 2.5.1 |
| provider attestation | NOT_ASSERTED | NOT_ASSERTED |

두 반환은 기존 Chat 기준과 동일한 수치 semantic `c9321b00102920e8aedbcc2f9f5cdcd374e67742f346754b928cc873d0e25f23`, 분석 semantic `d975525df1f0d3a1cc18a254c05cc92d36677e2538438e71a420644ab46a7db2`, CSV SHA `6285d1a77ab0321da9ff2db63d579549f52dfa871da0051e65d69f3eab32a0d4`를 갖는다. 원격 원본 소스 전체가 반환 ZIP 안에 들어 있지는 않으므로, 원격 소스 검증 영수증과 실제 로컬 기준 파일의 대조라는 증거 범위도 구분했다. 이 사실로 provider 신원이나 64코어 실행을 주장하지 않는다.

최근 반환의 단일 작업자 48.764초 재현은 이미 소모한 증거다. 다음 NCP 작업에서 재현이나 별도 속도 기준 측정이라는 이름으로 다시 돌리지 않는다. 두 ZIP와 intake 원문은 `evidence/return_intake/`에 포함된다.

## 3. 연구 대상과 보존한 물리 정의

대상은 OFF의 captured first-two-step 2,440경로, 4,884구간이다. KF/GM을 OFF와 합치지 않는다. 기체 단계, source switch, 종별 mask, 초기값, 경로 가중치, photon carry와 에너지 seam을 이전 연구와 동일하게 고정한다. 입력 binary64는 그 값의 정확한 실수로 올린다. CSV에 보이는 십진 문자열을 새로운 물리 초기값으로 해석하지 않는다.

각 구간에서 \(s=\log a\), \(u=s-a_j\), \(0\leq u\leq h_j\)를 쓰며,

\[
P'(u)=q(u)-\Lambda(u)P(u),\qquad
\Lambda(u)=\sum_i\lambda_i(u)\geq0,\qquad
E(u)=E_{0j}e^{-u}
\]

인 같은 선형 문제를 다룬다. 검증된 세 directed-Decimal kernel은 bytes까지 그대로 보존했다. `nonlinear_upper`라는 내부 필드는 선형 ODE의 coupling remainder를 뜻하며, 지배 방정식이 비선형이라는 뜻은 아니다.

첫 photon stock은 영이다. 다음 구간으로 전달하는 correction은 앞 구간의 true-minus-captured correction과 정확한 captured stock stitch residual을 더한다. 누적 moment를 감쇠시키지 않으며, 최종 photon stock은 마지막 끝점의 값만 쓴다. 구간 출력에 이미 포함된 frozen-minus-captured를 다시 더하지 않는다.

에너지 seam은

\[
J_j=\bigl(E_{0,j+1}-E_j(h_j)\bigr)P_j(h_j)
\]

의 **부호를 가진 실제 구간**으로 합산하고 에너지 ledger에서 뺀다. `anchored` 표지만으로 작은 seam을 버리지 않는다. native erg 값은 exact binary64 lift of `1.602176634e-12`로 한 번만 나눈다. CHI와 branch cutoff는 서로 다른 역할을 유지한다. 양의 경로 가중치도 한 번만 적용하고, A/B/H total은 이전·새 결과 모두 같은 종별 interval의 합으로 정의한다.

### 두 사건 경로의 해석

node1620의 step2/segment0 끝점은 exact realification에서 binary64 cutoff54.42보다 약 \(1.6755\times10^{-15}\) eV 작지만 captured HeII mask가 켜져 있다. node2344의 step2/segment1에서는 captured E0가 100.00000000000004 eV이고 source_on이 참이다. 이를 새 자연 임계값 선택과 일치한다고 주장하지 않는다. 에너지를 clamp하거나 mask/source를 바꾸면 원래 선언한 연구 대상이 달라지므로, 이번에는 같은 captured branch를 유지해 명시적으로 검토했다.

중량 2,331경로는 이 사건 경로들을 제외한 보통의 두 구간 경로이며, 별도의 strict whole-natural-branch 정적 검사를 통과했다. 전체 4,884구간의 heat 계수 양성과 2,444개 exact 시간·photon·eta·weight seam도 확인했다. 상세 유도는 `SCIENTIFIC_CONTRACT.md`와 `theory/BULK_REFINEMENT_DESIGN_KO.md`에 있다.

## 4. 전체 경로의 분할과 영 경로의 증명

| 집합 | 경로 | 구간 | 이번 처리 |
|---|---:|---:|---|
| 이전 수용 0,101,102,410,413,700 | 6 | 14 | 기존 N512 증거 재사용 |
| source-off 2345–2439 | 95 | 190 | 정확한 영임을 증명하고 계산 생략 |
| 새 로컬 105,106,409,414,1162,1620,1976,2344 | 8 | 18 | 이번에 N512 완료, 일부 N1024 수용 |
| 나머지 중량 집합 | **2,331** | **4,662** | NCP N1024/P60 한 번 |
| 전체 OFF | **2,440** | **4,884** | 중복·누락 없는 직접 분할 |

영 경로는 \(q\equiv0\), \(P(0)=0\)이다. 유한 선형 ODE의 유일성으로 \(P\equiv0\)이고, 흡수·열·적색편이 moment 및 signed energy seam도 모두 영이다. source CSV/node 값과 각 경로의 기존 **34개 interval 끝점 쌍이 모두 [0,0]**임을 실제 데이터로 확인했다. 단지 폭이 영이라는 검사만으로 비영의 상수 구간을 영으로 취급하지 않았다. 따라서 이 95경로에는 coefficient 계산이 필요하지 않다.

중량 집합은 HI만 활성인 691경로, HI+HeI 918경로, 세 종 모두 활성인 722경로다. 경로 안의 두 구간 carry는 순서를 유지하고, 서로 다른 경로만 병렬화한다. 이전 6경로와 새 로컬 8경로는 중량 목록에 없다.

## 5. 여기서 끝낸 경량 실행

로컬 환경은 affinity0–8, 실제 CPU quota8, 메모리 cgroup 상한8 GiB였다. 과학 실행에는 최대4개 단일 CPU·단일 thread 프로세스를 사용했다. 구간/path마다 180초, 프로세스마다 주소공간1 GiB를 상한으로 두었다. 이 환경에는 실제 Open MPI 실행기가 없으므로, local transport 실행과 합성 protocol control을 MPI 실행 증거로 올리지 않았다.

| 경량 실행 | 경로 작업 수 | 구간 enclosure | coefficient evaluation | 판정 |
|---|---:|---:|---:|---|
| 대표 8경로 N512/P60 | 8 | 18 | 18,432 | 272개 raw 비교 전부 nest/nonincrease |
| 4경로 N1024/P60 | 4 | 8 | 16,384 | N512 대비 136개 비교 전부 nest/nonincrease |
| 4경로 N32/P60, N32/P80, N128/P60 | 12 | 30 | 3,840 | precision/branch/동일 N 진단 완료 |
| 합계 | **24** | **56** | **38,656** | 재실행 없이 완료 |

N512 대표 실행은 전체 launcher 경과시간 **24.494290초**였다. 개별 경로는 약6.79–16.36초였고, 프로세스의 최대 관측 RSS는50,496 KiB였다. N1024 네 경로는 각각 약17.04,16.67,21.06,25.85초였다. 이들은 실제 pilot 측정값이며 full2331 또는64 rank 속도 측정값이 아니다.

### 정밀도와 같은 N 비교에서 확인한 한계

N32의 P60/P80 비교 136개는 모두 겹쳤다. 양의 P60 폭에 대한 최대 끝점 변화 비율은 약 \(1.0277424\times10^{-32}\)였다. 영 폭은 정확한 동일성을 별도로 확인했다. 이 근거로 관측한 pilot에서는 Decimal60의 자리수가 주요 폭의 병목이라는 증거가 없지만, 모든 입력에 대한 정밀도 독립 정리를 주장하지 않는다.

N128의 동일 N 비교에서는 **새 공식의 우위가 확립되지 않았다**(`NOT_ESTABLISHED`). 일부 remainder와 끝점의 작은 차이를 전체 수용 가능성이나 새로운 물리 개선으로 올리지 않았다. N32/N128 control은 기계적 수용 기준을 충족하지 않는 경우를 포함하므로 최종 enclosure에 사용하지 않는다. 이 부정 결과도 원자료와 함께 남겼다.

## 6. N1024를 한 번 선택한 이유

N512를 이미 완료한 네 보통 경로에서 N1024를 추가 계산했다. 아래 폭 비율은 새 폭/기존 N512 폭이며, 작을수록 더 좁다.

| Node | 활성 종 | 광자 폭 비율 | 열 폭 비율 | 실제 시간 배율 |
|---|---|---:|---:|---:|
| 105 | HI | 0.382431 | 0.345140 | 2.20182 |
| 409 | HI | 0.351680 | 0.340070 | 2.17803 |
| 1162 | HI+HeI | 0.321553 | 0.320462 | 2.16961 |
| 1976 | HI+HeI+HeII | 0.444400 | 0.365061 | 2.26803 |

네 경로의 광자·열 폭은 N512에서 **55.56–67.95% 더 감소**했고, 관측 시간은 약2.17–2.27배였다. raw34개 비교가 전부 안쪽에 들어오고 폭이 증가하지 않았으므로, NCP에서는 N512 전체를 먼저 돌리지 않고 N1024 한 번만 실행한다. 이는 유한 enclosure 폭과 실제 비용을 근거로 한 해상도 선택이며, 사용자가 정하지 않은 물리 허용오차를 도입한 것은 아니다.

전체 radius에는 incoming·coupling·rounding 성분이 남는다. 관측된 네 pilot의 축소율을 모든 경로나 총 radius의 보편적인 \(N^{-2}\) 수렴 법칙으로 해석하지 않는다. 그림과 원데이터는 `figures/`에 있다.

## 7. 현재 실제로 얻은 전체 OFF 구간

node105,409,1162,1976에는 N1024를, node106,414,1620,2344에는 N512를 선택했다. 이전 수용6경로를 그대로 유지하고, 나머지 중량2,331경로에는 아직 이전 enclosure를 사용한다. 각 집합을 서로 겹치지 않게 나눈 뒤 끝점을 Fraction으로 직접 더했다. 원래 interval에서 다른 interval을 빼는 일반적인 구간 뺄셈이나 새·기존 구간의 intersection은 쓰지 않았다.

| 관측량 | E13C6 전체 폭 | 로컬8 반영 후 전체 폭 | 감소율 |
|---|---:|---:|---:|
| P_final | 6.146898919840215e−17 | **6.081259221168360e−17** | **1.06785063%** |
| H_total_eV | 3.898810089742916e−16 | **3.883292513115486e−16** | **0.39800801%** |
| A_total | 7.530754442886631e−17 | 7.444568266027889e−17 | 1.14445608% |
| B_total_eV | 1.456362680355627e−15 | 1.443087023422928e−15 | 0.91156256% |
| Z_eV | 4.196687262531690e−21 | 4.181425532942058e−21 | 0.36366135% |
| anchor | 5.736193478629603e−32 | 5.710668465348222e−32 | 0.44498174% |

이 값은 원래 captured 가중 정규화와 관측량 정의를 그대로 따른 폭이다. 17 absolute와17 correction의 전체34개 구간이 이전 전체 구간 안에 들어오며, 모든 predecessor bridge가 정확히 맞는다. 표의 십진수는 표시용 반올림이고, 실제 수용·합산에는 JSON과 CSV에 저장된 정확한 유리수를 사용했다. 분석 semantic은 `da8e607c193643b3f21a07130d654e3bbc8292599f7f4543989647222fb9f929`다.

## 8. NCP에서 할 일과 시간·메모리 판단

NCP의 새 계산량은 **2,331경로 ×2구간 ×구간당2 coefficient 평가점 ×1,024분할 =9,547,776회 coefficient evaluation**이다. 각 rank는 하나의 경로를 온전히 계산한 뒤 다음 경로를 맡는다. 세 종 경로의 비용이 더 큰 것을 반영해 실제 로컬 mask별 평균 비용으로 deterministic LPT 배정을 만든다. 연속 node 범위를 단순히64등분하지 않는다.

64개 rank 모두 계산한다. 이 구현에는 MPI controller rank가 없고, 외부 Python launcher가 가벼운 진행 확인과 결과 수집을 맡는다. 따라서 최대64개의 계산 rank를 사용할 수 있다. 실제 사용 개수는 affinity·관측 quota·메모리·pending 작업 수를 읽은 뒤 `--ranks auto`가 결정하며, 스펙 설명만으로64개를 강제하지 않는다. topology에는 논리 CPU와 물리 core를 구분해 기록한다. 각 rank는 서로 다른 허용 OS CPU에 고정되고 thread 관련 환경은1이다.

### 시간은 시나리오로 제시한다

로컬 N1024의 활성 종별 평균은 HI 약16.854초, HI+HeI 약21.063초, 세 종 약25.854초다. 이를 실제 경로 수에 곱하고, 같은 E13C6 작업의 최근 반환/Chat 시간 비율1.930954를 적용하면 다음 추정이 나온다.

| N1024 중량 집합 | 추정 또는 가정 |
|---|---:|
| 로컬 단일 작업자 환산 | 49,648.894초 |
| 최근 기록 NCP 단일 작업자 환산 | **26.6305시간** |
| 64 rank 이상적 시간 | **24.966분** |
| 64 rank, 병렬 효율80% 가정 | **31.208분** |
| 64 rank, 병렬 효율50% 가정 | **49.932분** |

같은 호스트 ratio라도 코어 전체 사용 시 주파수·스케줄러·공유 자원·I/O의 영향이 달라질 수 있다. 이 표는 실제 가속률 측정이 아니며, 실제 host/rank receipt가 반환될 때 갱신한다. 별도 N512 full benchmark나 이미 완료한 4경로 재현으로 시간을 쓰지 않는다. Batch 상한은7,200초, 각 경로 상한은180초다.

### 128 GB를 채우는 것이 목표는 아니다

최대 관측 RSS50,496 KiB는 약49.31 MiB다. 이를 단순히64배 하면 약3.082 GiB이지만, 이는 로컬 pilot을 확장한 메모리 시나리오다. launcher는 관측 RSS를 상한으로 가정하지 않고 **rank당1 GiB 주소공간 제한**을 적용하며,64rank에64GiB 및 launcher 여유를 보수적으로 예약하고 실제 가용 메모리의20% 이상을 남기는 정책을 쓴다. 주소공간 상한, 실제 RSS, 머신 RAM 용량은 서로 다른 값이다.

이 문제의 무거운 부분은 검증된 Decimal coefficient/enclosure 계산이므로, 의미 없는 배열을 만들어 RAM을 채울 이유가 없다. 독립 경로를 충분히 공급하고 비싼 경로를 고르게 나누는 데 CPU를 사용한다. 검증된 Decimal을 binary64 Fortran으로 바꾸면 같은 인증 수치 경로가 아니므로 이번 node에서는 바꾸지 않았다. native certificate 구현은 별도 rounding·포함 증명이 필요한 후속 연구다.

## 9. 실행 경계, 독립 검토, 실패 보존

과학 SOURCE_LOCK은 `386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f`로 변하지 않았다. 최종 EXECUTION_LOCK은 `c04cfde1838563d95389e499de9bcbe505a7d67f6bda1fff4476af953c8cc4f4`이며60개 실제 파일과10개 runtime Python 파일을 묶는다. Pilot 당시의 lock과 WORK_PLAN은 별도 보존했다. 최종 N1024 계획을 과거 N512 실행의 identity로 소급하지 않았다.

독립 검토는 전체 입력56,355개 확인, branch 결과13,340개, primary8결과8,080개, resolution결과3,626개, 정밀도136개 비교, 로컬 분석2,715개 및 병렬 모듈61개 확인 등을 수행했다. 이 개수는 서로 다른 검토 항목이지 독립적인 물리 실험의 개수가 아니다. 최종 상세 판정이 모든 해시와 각 검사 범위를 결합한다.

처음 독립 checker는 outward serialization interval을 정확한 내부 center-radius ball보다 강한 조건으로 검사해35개 assertion에서 실패했다. 그 원본과 실패 기록을 남긴 후, 정확한 ball 포함 및 반지름 재중심화 관계로 검토 조건을 고쳤다. 후보 kernel과 계산 결과를 바꾸거나 허용오차를 늘리지 않았다. `review/REVIEW_CHECK_CORRECTION.json`에 근거가 있다.

병렬 실행기의32개 합성 protocol control은 LPT, 순서 독립 수집, 변조·누락 검출, source/N/P 다른 재개 거부, create-only 출력, 실패·timeout 보존, 자동 retry0, root 옵션 조건과 quota/memory 경계를 확인했다. 이는 실제 MPI 테스트가 아니다. NCP에서 root limit 파일이 보이지 않던 관측에 맞춰 파일 부재를 `UNOBSERVED`로 기록하고, 관측한 더 강한 제한은 적용한다. 보이지 않는 제한을 무제한이라고 보고하지 않는다.

Wrapper의 초기 interrupt 처리에서는 계산 launcher가 살아 있는데 실패 ZIP을 만들 수 있었다. 실제 harmless sleeping child로 첫 실패를 재현·보존했고, 새 wrapper가 자식 종료를 확인한 뒤 파일을 수집하도록 고쳤다. 수정 뒤 자식 exit−15, 생존false, 원래 KeyboardInterrupt 보존과 실제 ZIP member bytes/SHA가 검증됐다. 이 경계 시험의 과학 kernel/MPI 호출은0이다. 실제 MPI process tree 종료까지 미리 검증했다고 주장하지 않는다.

반환 directory가 package 밖에 있을 때 analyzer의 표시 경로 처리에서 ValueError가 나던 문제도 작은 실행 경계 수정으로 해결했다. 과학 정의와34개 값 및 semantic은 같았다. 완료한 로컬8을 이용한 반환 reduction rehearsal도 정확히 기존 분석을 재현했다. 실제2331 반환 reduction은 아직 실행하지 않았다.

## 10. 다음 상태와 인계

NCP는 `code/ncp_execute_batch.py`로 sealed heavy batch만 수행하고, per-path 결과와 host·source·completion·failure receipt를 실제 bytes 그대로 ZIP으로 반환한다. NCP에서 전체 Fraction 합산을 별도 작업으로 하지 않는다. 결과가 돌아오면 이 연구 스레드에서 `code/reduce_returned_batch.py`로 prior6 + local8 + returned2331을 정렬된 정확한 유리수 끝점 합으로 처리하고 독립 과학 판정을 이어간다.

완료 marker만 보고 결과를 수용하지 않는다. 입력/source/lock identity, 모든 실제 결과 bytes/SHA, ordered semantic,34개 raw 관계와 전체 predecessor bridge를 확인한다. 일부 결과가 기존 구간 안에 들지 않으면 원자료를 보존하고 해당 gate에서 HOLD한다. clipping, intersection, 이전 값으로 숨겨 대체하기, 자동 재시도는 없다.

실패 시 첫 영수증과 partial 결과를 보존한다. 이후 명시적 resume은 동일 lock·N/P·입력에 대한 검증된 완료 경로만 재사용한다. 실제 시도된 미완료 경로를 다시 계산하려면 정확한 node 목록을 명시해야 한다. 미확정 invocation 수를0으로 바꾸지 않는다.

백업본에는 원래 OFF 경로 전체, source CSV, prior budgets, 변경하지 않은 kernel, 실행기, 모든 로컬 결과, 독립 검토, 계약과 내부 handoff를 포함한다. 사용자는 추가 첨부 파일을 제공할 필요가 없다. ZIP 실제 bytes/SHA를 먼저 확인하고 fresh directory에 복구한다. 다운로드 파일명에 `.bin` 등의 suffix가 붙어도 **실제 반환 경로의 bytes를 검증**하므로 이전의 part002 이름 의존 문제를 반복하지 않는다.

원격 업로드 ACK와 이름·크기 readback은 업로드 확인이다. 원격 ZIP을 다시 내려받아 전체 복구한 증거로 부르지 않는다. 이번 로컬 완성 archive의 실제 member bytes/SHA는 별도로 검사한다. 외부 cloud ID와 archive 자체 해시는 archive 밖 delivery receipt와 사용자용 `NCP_LOCAL_CODEX_HANDOFF_KO.md`에 둔다. 자체 hash를 내부에 넣는 순환 참조를 만들지 않는다.

## 근거 파일 안내

- 수치 정의: `RESEARCH_CONTRACT.json`, `SCIENTIFIC_CONTRACT.md`, `SOURCE_LOCK.json`.
- 원본·분할: `INPUT_PROVENANCE.json`, `inputs/INPUT_INDEX.json`, `inputs/OFF_OLD_PATHS.jsonl`, `inputs/EXACT_ZERO_CERTIFICATES.json`.
- 실제 경량 실행: `runs/LOCAL_PRIMARY_N512/`, `runs/LOCAL_RESOLUTION_N1024/`, `runs/LOCAL_BRANCH_CONTROLS/`.
- 현재 전체 예산: `analysis/LOCAL/LOCAL_ANALYSIS.json`, `LOCAL_ADMITTED_CANDIDATE.json`, `LOCAL_FULL_WIDTHS.csv`.
- 시간·자원: `analysis/RESOURCE_ALLOCATION.json`, `analysis/NCP_SCHEDULE_64_PREVIEW.json`.
- 독립 판정: `review/INDEPENDENT_DECISION.json`, `review/INDEPENDENT_REVIEW_KO.md`와 개별 원문.
- NCP 실행: `EXECUTION_LOCK.json`, `inputs/WORK_PLAN.json`, `docs/PARALLEL_PROTOCOL.md`, `NCP_HANDOFF_INTERNAL_KO.md`.
- Open MPI root 선택의 공식 문서: https://www.open-mpi.org/doc/v4.1/man1/mpirun.1.php 및 https://docs.open-mpi.org/en/v5.0.7/man-openmpi/man1/mpirun.1.html. 코드는 실제 uid0일 때만 명시 옵션을 전달하며 그 선택을 receipt에 기록한다.
