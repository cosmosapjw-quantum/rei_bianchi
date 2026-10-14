# rei_bianchi 통합 개발계획 v2 — 원자물리 재사용 중심

2026-10-12 KST. 결정: `ATOMIC_REUSE_OBSERVABLE_FIRST`. 직전 `SCIENTIFIC_FAST_TRACK_RESET`과 사용자가 제공한 추가 감사 2건·원자 재사용 계획/DAG/handoff 3건을 통합한다. **개발계획의 채택이며 새 physical EoR 계산·원자 채널 admission은 아니다.**

## 1. 이번에 바꾼 중심과 다음 작업

**기존 H/He 반응·열·광자 결합 수치 골격에 EoR용 rate/domain 공급자와 실제 배경·광원·초기조건을 연결해, x_e(t)와 T_g(t)를 해로 얻는 경로를 주력으로 삼는다.** 이미 계산된 미시물리를 사용하고, 부족한 소비 인터페이스와 물리 폐쇄를 연결한다. 새로운 원자 엔진을 처음부터 만들거나 모든 정밀 원자 연구의 완결을 기다리지 않는다.

직전 계획의 PR104 reduced baseline, prescribed-x_e 수송과 Thomson 진단은 독립 기준·대조 경로로 유지한다. 이제 이 경로를 모두 끝내야 비평형 결합 연구를 시작하는 순서는 아니다. PHYS36과 C12 full-history/고정밀 인증 경로는 계속 비차단 선택 경로다. 여기서 선택 경로인 “full native”는 기존 C12의 대규모 전구간 계산·인증을 뜻하며, 기존 Rust microstep을 재사용하는 일 자체를 금지하는 말이 아니다.

다음 실행 묶음은 **`RUX-P0: 한 EoR 시나리오의 입력·rate/domain 연결과 첫 결합 구간`**이다. RUX00/02/03/04의 필요한 입력 결정을 같은 구현 작업에 포함하고, 입력이 갖춰지면 RUX05의 첫 FLRW 구간까지 바로 진행한다. 새 전역 감사나 새 solver 설계만으로 끝내는 회차를 만들지 않는다. 입력이 실제로 부족하면 부족한 필드와 한 가지 구체적인 선택/공급 작업을 남기며, 동일 자료의 N2 감사를 반복하지 않는다. 저장 결과 활용과 독립 수송 진단은 그동안 계속 진행할 수 있다.

원래 17개 RUX ID와 의무는 `PLAN.json`의 대응표에 보존했다. 문서/PR 수를 완료조건으로 삼지 않고 첫 구간, 이력, 관측량 산출물 중심으로 묶는다. 과거 2026-10-04 GLOBAL_DAG와 PHYS35·직전 계획 원문은 역사적 기록으로 보존하며 새 계획이 현재 우선순위만 대체한다.

## 2. 추가 감사에서 채택한 것과 수정한 것

| 항목 | 통합 결정 |
|---|---|
| 기존 원자물리 성과 활용 | 기본 H/He 단면적·채택한 반응률·흡수/가열 moment·사건 장부는 주 경로의 구성요소다. 소속 repo가 HE/CR이라는 이유로 모두 선택 경로로 밀지 않는다. |
| F08 결합 이력 | 이미 수행된 15개 이력과 248,000 accepted trials를 기존 성과로 유지한다. 첫 결합 엔진이 아직 없다는 출발점으로 돌아가지 않는다. |
| source만 바꾸면 EoR 실행 가능하다는 기대 | 현재 primary에는 FT03 rate 직접 호출과 온도·시간·광자 대역 제약이 있다. 실제 새 구현은 rate/domain 주입과 time/source/경계 어댑터다. |
| RUX00 전역 authority 점검 | 이번에 확인한 pin은 재사용하고, 실제 선택할 공급자·실행 경로만 확인한다. 7개 repo와 모든 archive의 완전한 동기화를 연구 선행조건으로 삼지 않는다. |
| RUX02/03/04 입력·owner 고정 | 새 물리 계산에 필요한 국소 조건으로 채택한다. 서로 독립인 입력과 owner 작업은 병렬화한다. 기존 결과·처방 이력·수송 진단에는 전역 gate로 적용하지 않는다. |
| RUX06 수송을 새 physical input 뒤에 배치 | 기존 수송과 저장 증거의 재사용은 독립적으로 한다. 새 물리 입력의 구체적인 Bianchi 실행에만 해당 입력 조건을 적용한다. |
| RUX10/11을 전구간 paired history 뒤에 배치 | 첫 admitted 전자 이력부터 구간 τ와 그림을 만든다. 전구간 paired 결과와 observer-tail 처리는 그 주장에 필요한 시점에 요구한다. |
| RUX12–14를 최종 그림 뒤에만 활성화 | 중간 관측량/민감도/오차 예산이 필요성을 보이면 선택 활성화한다. 최종 불확실성을 채우는 연구가 최종 gate를 기다리는 순환을 제거한다. |
| Case A/B 이분법 | 명시적 재결합 광자 수송, Case-A escape 장부, 일관된 Case-B/OTS 중 선택한 처리의 사건별 소유권을 명시한다. |
| 광학깊이·편광·patchiness | 구간 τ, visibility, polarized sky, Q_V/21cm은 각각 별도 주장이다. 하나의 구현이나 gate로 함께 승격하지 않는다. |

## 3. 지금 확보한 성과와 실제 구현 상태

### 기존 결과는 그대로 사용한다

| 자산 | 확인/보존 범위 | 이번 계획에서의 사용 |
|---|---|---|
| PR104 RUN002 | 고정 reduced 모델의 z=20→4+ 14개 사례; 엄격한 DOP853 비교는 FLRW/최대 shear 두 사례 | 배경·이력·광원 정규화의 참고와 reduced 대조군. τ_total이나 homogeneous chemistry의 검증으로 바꾸지 않는다. |
| F08 | Git campaign summary에 15 runs, 248,000 accepted trials, 0–10^13 s, 조건부 이산 paired-history 상태가 존재 | 기존 결합 실행과 장부의 성과. 새 구현의 구조를 재사용하고 이미 있는 그림·endpoint 표를 다시 활용한다. |
| SYNC02/03 | 기존 REC–REI–BASS 연결; SYNC03에는 finite-cell 전자 이력의 조건부 τ/visibility와 저장 그림 | 실제 receiver API와 시간·observer 계약을 재사용한다. full BASS build나 physical EoR 완료로 확대하지 않는다. |
| HE EoR MICRO-0 / E13 | 사용자 감사가 반응률 family·보존 solver 복구 및 2,440 finite-path 결과를 보고 | 선택된 기본 rate family는 core 후보, 고정밀 source/moment 개선은 필요 시 선택. E13의 수치 폭을 물리 모델 오차로 사용하지 않는다. |
| CR photon-stock | 사용자 감사가 182 panels/5,824 points의 순간 흡수·가열 진단을 보고 | 적용 가능한 광자–기체 moment/장부를 소비한다. wide propagated error와 hard-particle 확장은 별도다. |
| HH PHYS11 | 사용자 감사가 33 photon groups의 반응·열수지와 조건부 응답을 보고 | 이름 붙은 반응의 stoichiometry·에너지·민감도를 필요 시 사용한다. native root/full-history/continuum은 상속하지 않는다. |

F08과 SYNC03의 위 실행 상태는 이번에 원본 Git 기록을 읽어 확인한 **과거 실행 증거**다. 이번에 재실행한 결과가 아니다. HE/CR/HH 세부 숫자는 첨부 감사가 보고한 범위이며 관련 원본 전체를 이번에 재검산하지 않았다.[F08][SY3][R104]

F08의 `paired_history.csv`는 현재 Git 파일상 15개 endpoint 행이다. 이것만으로 연속 시간곡선을 복원했다고 하지 않는다. 기존 PNG를 재사용하거나 endpoint 비교를 그리고, 시간곡선이 필요하면 source manifest가 가리키는 해당 compact/full 이력만 가져온다. SYNC03의 기존 201개 공통 시각 그림도 새 적분 없이 활용할 수 있다.[F08][F08CSV][SY3]

F08은 고정 source=5×10^-15 photon/H/s, birth energy=13.7 eV, 초기 T≈50,000 K, 약 0.317 Myr 구간의 제한된 실험이다. He 광이온화의 일반 EoR 조건을 시험하지 않는다. SYNC03의 τ 역시 이 finite interval과 명시적인 truncated observer tail에 조건부다. PR104의 Δτ≈−2.61×10^-5와 SYNC03의 Δτ≈+3.44×10^-12는 입력·모델·구간이 다른 결과이며 서로의 부호 검증이나 반증이 아니다.[PR][SY3][R104]

### 재사용 가능한 엔진과 필요한 변경

현재 Git 소스에는 `paired_runtime`이 기하 전파→source 주입→각도 합산→`primary_stage_step_conservative`/`primary_stage_root`→방향별 생존비율 반영→장부 누적을 수행하는 구성이 있다. `coupled_primary`의 implicit 단계와 사건 장부는 실제 자산이다.[CP][PR]

반면 `PrimaryStage` 입력은 현재 n_H, He/H, 평균 H 중심이고 내부에서 FT03 모델·계수를 직접 호출한다. primary 유효 온도는 30,000–110,000 K, paired guard는 35,000–60,000 K이며 상수 H, t≤10^13 s, 10–20 eV 노드, 미구현 upper guard 등 fixture 범위가 남아 있다. 원자 공급자의 넓은 함수 평가 영역은 EoR 소비 영역의 검증과 같지 않다.[AP][CP][PR]

최소 구현 변경은 다음 세 곳이다.

1. **Rate/domain 연결:** 선택한 EoR 반응률·냉각/가열 공급자와 적용 영역을 기존 stage에 주입한다. 실제 RHS가 그 공급자를 호출하도록 한다. 새 point 경로만 바꾸고 기존 FT03 root/interval 인증을 그대로 붙이지 않는다. 엄밀 interval 경로를 사용하려면 그 경로도 같은 공급자와 영역을 사용해야 한다.
2. **시간·광원·경계 연결:** 실제 a_i(t), H_i(t), proper density, 초기 상태, 분광 source와 경계 flux를 고정된 fixture 상수에서 분리한다. He 관련 주장은 source의 에너지 support와 맞춘다.
3. **소유권 연결:** primary가 이미 처리하는 흡수·thermal work를 외부 수송이나 보조 homogeneous evaluator에서 다시 더하지 않는다. 광자 redshift work와 에너지/각도 경계 flux는 history 쪽에서 한 번 처리한다.

`AtomicProvider::record`의 `consumer_admission=false`와 `physical_support_resolved=false`는 legacy raw 경로가 물리 소비자로 자동 채택되지 않았다는 뜻이다. Grackle 계수 자체가 무효라는 판정이 아니다. 이를 true로 바꾸거나 guard 숫자만 늘리는 작업은 물리 연결의 완료조건이 아니다.[AP]

현재 Git `lib.rs`에 `paired_runtime` export가 없고 조사한 pin의 `axisym_radiation.rs` 경로는 찾지 못했다. 사용자 감사가 관측한 Dropbox axisym 파일과 Git pin의 동일성은 미확인이다. 이 차이를 기존 실행 엔진의 부재로 확대하지 않는다. 다음 구현에서는 실제 사용할 entry point 한 개와 필요한 source delta만 확인한다.[LIB][PR]

## 4. 중심 모델과 폐쇄

### 상태·단위·기하

첫 목표는 비기울어진 균질 LRS Bianchi I의 비평형 H/He–열–이온화 광자 모델이다. metric signature는 (−,+,+,+), t는 가스/정상 관측자의 proper time, 에너지와 단면적은 같은 가스 정지계로 정의한다. c와 k_B를 유지한다. 자연단위를 암묵적으로 사용하지 않는다.

gas 상태는 (x_HII,x_HeII,x_HeIII,u_th), radiation 상태는 기존 양의 packet measure 또는 각도 q·에너지 g별 상태다. `N_gamma,g`만 저장하면 방향 정보나 bin 내부 spectrum은 결정되지 않는다. N_gq와 필요 에너지 moment/packet 상태, 또는 명시된 bin 내부 폐쇄를 유지한다. T_g는 선택한 EOS와 u_th에서 얻거나 입자 수 변화 항을 포함해 직접 진화시킨다.

고정 기준 comoving 체적의 광자 수를 N_gq, 그 proper 체적을 V(t)=V0 a_V^3(t)로 두면

\[
\Gamma_{s,gq}=c\,\frac{N_{gq}}{V}\langle\sigma_s\rangle_{gq},\qquad
\mathcal H_s=n_s c\sum_{gq}\frac{N_{gq}}{V}
\langle\sigma_s(E)(E-\chi_s)\rangle_{gq}.
\]

Γ는 s^-1, H는 에너지/(proper volume·time)이다. per-H 코드에서는 고정 기준 체적의 H 핵수로 나누는 변환을 한 곳에서 한다. 대표 에너지 하나나 N/U 두 moment가 일반적인 opacity·heating moment를 유일하게 정하지 않는다. 사용한 spectral closure와 그 오차를 기록한다. Verner fit의 photon cutoff와 binding energy χ_s도 구분한다.[AP][HR]

기하·흡수·source 장부의 개략식은

\[
\dot N_{gq}=S_{gq}+S^{\rm rec}_{gq}
-V\sum_s n_s\Gamma_{s,gq}
+F^E_{g+1/2,q}-F^E_{g-1/2,q}+\mathcal F^{\Omega}_{gq}.
\]

여기서 F^E는 높은 에너지에서 낮은 에너지로 향할 때 양인 signed 경계 flux로 정의한다. 내부 에너지 경계의 수량은 인접 셀 사이에서 상쇄되고 전천의 angular redistribution 합도 0이다. 경계 밖의 유입·유출과 팽창에 의한 광자 에너지 변화는 별도 장부에 남긴다. 기존 packet 구현에 이미 반영한 Jacobian을 다시 곱하지 않는다.

기본 H/He 네트워크에서 H− 등 음이온을 포함하지 않을 때

\[
n_e=n_Hx_{\rm HII}+n_{\rm He}(x_{\rm HeII}+2x_{\rm HeIII})
\]

이고, 단일온도 비상대론적 단원자 기체의 u_th=(3/2)n_tot k_B T_g를 사용한다면

\[
\dot u_{\rm th}+3H_V(u_{\rm th}+p)=\mathcal H-\mathcal C
\]

와 종 변화·binding/radiative energy 장부를 일관되게 연결한다. 기존 primary의 thermal work와 외부의 팽창 냉각을 중복하지 않는다. 이 식들은 선택한 모델의 계산 계약이며 이번에 새 수치해를 얻었다는 뜻이 아니다.

### 사건 소유권과 선택적 원자 채널

| 과정 | 주 경로의 처리 | 확장할 때 필요한 것 |
|---|---|---|
| HI/HeI/HeII photoabsorption | 같은 photon loss 사건에서 ionization·binding·primary heat를 함께 계산 | 같은 사건을 다른 evaluator/opacity sink에서 중복 차감하지 않음 |
| 재결합 복사 | 명시 수송+Case A, Case-A escape+에너지 장부, 또는 일관된 Case-B/OTS 중 선택 | 서로 다른 폐쇄의 sink/source를 합쳐 사용하지 않음 |
| local HI opacity와 effective MFP | 같은 흡수 population에는 하나의 owner | 분리된 phase/absorber에 둘 다 쓰려면 중복 없는 분해와 energy/photon 귀속을 정의 |
| HE 총 전이율 | 적용 가능한 scalar rate로 소비 | 미해결 differential spectrum을 검증된 emissivity로 바꾸지 않음 |
| HH ion-pair | 이름 붙은 stoichiometric source로 취급 | H+와 H−를 만들면 즉시 free electron 증가가 아님. H− 상태 또는 검증된 제거 폐쇄와 수정된 전하식을 요구 |
| RCT/CR 고급 채널 | baseline의 선택된 OFF를 유지할 수 있음 | 물리 에너지·moment·지원 영역·deposition이 정의된 채널만 조건부 ON |

이름이 CR인 repo에서 가져온 photoabsorption 도구와 hard-particle CR 채널을 구별한다. 기본 H/He chemistry가 core라는 사실과 HE의 모든 정밀 differential source가 baseline에 필요하다는 주장은 다르다. 자세한 대응은 `ASSET_OWNER_MAP_KO.md`에 있다.

### 남아 있는 천체물리·공간 폐쇄

x_e(t)를 직접 계산해도 stellar/AGN spectrum, emissivity, escape fraction, density/clumping 및 초기 history는 외부 입력/모델이다. source가 intrinsic emissivity, incident background, initial stock, boundary flux 중 무엇인지 구분한다. comoving emissivity에는 comoving 체적을, proper emissivity에는 proper 체적을 곱한다. 이미 전파된 background intensity를 같은 흡수를 다시 적용할 intrinsic source로 자동 변환하지 않는다.

처음에는 문헌/관측에 근거한 한 가지 source family와 기존에 정한 배경·초기조건을 선택한다. Bianchi에 FLRW 기반 source/halo prescription을 사용할 경우 수송 효과를 분리하기 위한 가정임을 명시하며 Bianchi 구조 형성을 동시에 예측했다고 하지 않는다. PR104의 scalar 방출률은 spectral emissivity·초기 T·종별 상태 전체를 공급하지 않는다.

homogeneous x_HII는 patchy Q_V가 아니다. PR104의 Q 기반 ne 폐쇄는 reduced 대조군에서만 유지한다. 주 경로에 Q를 추가로 곱하지 않는다. Q_M/Q_V, density–ionization correlation, spatial topology와 21cm power에는 RUX15의 별도 공간/IGM 폐쇄가 필요하다.

## 5. 실제 실행 묶음과 산출물 순서

| 실행 묶음 | 포함하는 RUX 의무 | 반드시 남길 산출물 |
|---|---|---|
| **RUX-P0 — 다음 필수** | 선택 공급자의 RUX00, RUX02/03 병렬, RUX04 및 RUX05 준비/첫 구간 | 필드별 입력 결정, 실제 rate/domain·time/source 연결 코드, 가능하면 첫 FLRW coupled interval의 상태·장부·그림. 입력 부족 시 정확한 결손과 한 가지 구현 가능한 공급/선택 작업 |
| RUX-P1 | RUX06/07 Bianchi 첫 구간과 RUX08 FLRW history의 독립 부분 | 같은 source의 Bianchi 구간, 지원 영역 안의 FLRW 다중 epoch 이력, 중간 그림·구간 τ |
| RUX-P2 | RUX09, RUX10, RUX11, RUX16 | matched histories, Δ 관측량·오차, source-backed 구간/전체 τ 구분, 선택한 주장 범위의 배포 |
| 독립 결과·대조 | RUX01, PR104 baseline, 기존 FT-B1A/B1B 기능 | 보존된 F08/SYNC03 그림·endpoint 비교, prescribed 수송/Thomson 대조. 새 물리 입력의 대기를 공유하지 않음 |
| 선택 확장 | RUX12–15, C12, PHYS36 | 중간 관측량의 오차 또는 연구 질문에 실제로 필요한 채널/정밀도/공간 정보 |

RUX-P0의 source intake는 알려진 v2/P01/P02A/P03A/source-delta 후보를 중복 없는 한 입력 계보로 확인한다. 파일명에 PRODUCTION이 있거나 archive가 존재한다는 사실로 admission을 선언하지 않는다. 반대로 10월 10일 N2의 당시 결손을 현재 모든 입력의 부재로 반복 선언하지도 않는다. PR104의 배경·스칼라 source와 C12의 보존된 입력은 이미 알려진 후보로 놓고, 실제 새 소비 경로에 필요한 필드만 비교한다.

신규 물리 실행에 필요한 필드는 epoch·time map·a_i/H_i, proper H/He density, 초기 종/열/광자 상태, spectral source history와 단위, source/escape/clumping 가정, 재결합/opacity/energy owner, rate/thermal domain 및 실행 callback이다. 자료가 불완전하면 같은 archive 재감사 대신 **P0 physical-input selection**으로 이름 붙인 한 개의 작업에서 문헌에 근거한 시나리오를 선택하고 모델 가정으로 고정한다. null을 0으로 바꾸거나 F08 source를 물리 광원으로 재라벨하지 않는다.

물리 실행 전에 입력을 고정하되 개발 중 반례나 유효영역 실패가 나오면 실패를 보존한 새 scenario revision으로 수정할 수 있다. 결과를 맞추기 위한 사후 조정과 정당한 모델 개정을 구별한다.

## 6. 비교·수치 오차·주장 범위

### 두 종류의 대조군

처방된 이력의 수송 대조에서는 ne도 동일하게 고정한다. **주 경로의 coupled 대조에서는 초기 상태·광원·rate·평균 H/밀도 등을 고정하고 ne와 T는 각각 다시 진화시킨다.** endogenous 결과인 ne를 고정하면 그 비교는 one-way 실험이 된다.

물리 Bianchi O_B, 물리 FLRW O_F 외에 Bianchi의 평균 H와 동일한 등방 수송 O_isoHB를 두면

\[
O_B-O_F=(O_B-O_{\rm isoHB})+(O_{\rm isoHB}-O_F)
\]

로 수송과 배경 경로의 기여를 정리할 수 있다. 이는 선택한 counterfactual을 통한 정확한 차분 분해이며 비선형 효과의 유일한 원인 분해는 아니다. 같은 평균 H 등방 수송을 같은 물질의 Einstein-FLRW 해라고 주장하지 않는다. 순수 등방 source/opacity·초기 복사와 작은 shear의 조건부 선형/이차 응답은 진단으로 사용하고, 유한 shear·tilt·anisotropic source까지 보편화하지 않는다.

균질·comoving·cold 전자의 고정 cosmic-time 경계에서 τ=∫cσ_Tne dt는 방향독립이다. 방향별 관측 redshift 경계에는 별도의 시간 매핑이 필요하다. visibility에는 적분 변수와 observer tail을 명시한다. 물리 전체 τ를 보고할 때 미공급 tail을 0으로 두지 않는다. cold Thomson과 CMB polarized sky는 UV photoabsorption/chemistry와 별도 소비 경로다.[SY3]

### 필요한 정확도만 새로 평가한다

새 실행은 목표 관측량의 최소 진폭 A_target과 절대 floor를 미리 적고 E_num(ΔO)≤0.1 A_target을 출발 예산으로 사용한다. time·angle·energy·보간 오차는 필요한 paired difference에 배분한다. 이는 새 fast-track의 실행 설계이며 기존 C12/FT03/PHYS의 기준을 소급 완화하지 않는다. 기존 finite certificate는 해당 공급자·입력·수치 구조에만 남긴다.

수치 오차, atomic model/rate uncertainty, source/escape/clumping, geometry/IC, spectral/spatial closure를 구별한다. 시나리오 범위를 통계 posterior로 부르지 않는다. signed step 차이와 finite enclosure 폭을 전 구간 물리 오차로 취급하지 않는다. source systematic이 큰 경우에도 조건부 물리 응답을 보고할 수 있지만 그것을 관측 식별성·새 발견으로 승격하지 않는다.

동일한 기존 F08/SYNC02/03·원자 정밀 계산을 반복하지 않는다. 이번에 바뀐 provider, domain, 시간/광원 연결, 장부와 관측량에 필요한 검증을 수행한다. 기존 root/interval 보증이 적용되지 않는 새 point 실행은 그에 맞게 numerically checked로 보고하며 엄밀 인증이라고 하지 않는다. 새 주장/알고리즘에 대한 범위 한정 독립 검토는 유지한다.

### 자원·중단 조건

경량 코드·입력 연결·첫 구간·저장 결과 분석은 현재 실행 가능한 환경에서 진행한다. 환경이 실제로 제공하지 못하는 부분만 local Codex로 넘긴다. NCP는 측정된 wall/CPU/RSS 또는 구체적인 비용 근거가 있는 독립 이력·매개변수·해상도 사례에 사용한다. RUX04/07을 모든 종류의 NCP 작업에 전역 gate로 적용하지 않고 각 작업의 자기 입력과 정확도 조건을 요구한다. 새 coupled EoR sweep에는 실제 연결과 짧은 구간 확인이 필요하다. 순차 적응 time loop의 선형 64배 가속은 가정하지 않는다.

입력 부족, provider 영역 이탈, 구현 오류, 수치 비수렴, 물리 폐쇄의 한계, 실행환경 문제를 분리한다. 지원 영역 밖으로 extrapolate하거나 clipping/guard 변경으로 성공을 만들지 않는다. 목표 신호가 해상도 아래이거나 nuisance와 퇴화하면 해당 상한/한계를 산출하고 다른 관측량을 선택한다. 고정밀 원자 연구를 무기한 선행시키지 않는다.

## 7. 보존 상태와 이번 변경 범위

기존 Physical HOLD, [160,161] FAIL, tick160, auxiliary escape FAIL, PHYS35의 소진 first/replay, S0 HH/RCT/CR OFF, 기존 정밀/native 결과의 적용 영역을 변경하지 않는다. OFF는 해당 baseline의 설정이며 다른 소유자의 원자 연구를 정지시키는 지시가 아니다. PHYS36은 계속 DEFERRED_NONBLOCKING / NOT_RUN이다. 선택 채널을 새 모델에 넣으려면 그 모델의 이름·입력·장부·주장을 따로 기록한다.

이번에는 계획·DAG·다음 실행 인계·자산 소유권/출처와 활성 포인터를 갱신했다. 새 연구 실행, 테스트, provider import, archive 내부 admission, 다른 repo/PR 수정, 외부 job/자동화 변경은 하지 않았다. 새 RUX 과학 노드들은 NOT_RUN이며 과거 F08/SYNC03의 완료 증거와 구분한다.

## 출처와 인계

`SOURCE_MAP.json`은 첨부 5개의 원문 identity와 실제 확인한 Git pin/범위를, `ASSET_OWNER_MAP_KO.md`는 소유권과 source-domain 차이를 담는다. `CODEX_START_KO.md`는 다음 RUX-P0 실행의 구체 인계다. 원래 17개 노드의 상태를 거짓으로 완료 처리하지 않고 새로운 scheduling overlay만 채택했다.

[F08]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/runs/rei_fastest_v1/paired/campaign_summary.json
[F08CSV]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/runs/rei_fastest_v1/paired/paired_history.csv
[SY3]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/docs/research_sync/REI-REC-BASS-SYNC03-20261007/README_KO.md
[R104]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/REPORT_KO.md
[AP]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/rust/rei_microphysics/src/atomic_provider.rs
[HR]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/rust/rei_microphysics/src/homogeneous_rates.rs
[CP]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/rust/rei_microphysics/src/coupled_primary.rs
[PR]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/rust/rei_microphysics/src/paired_runtime.rs
[LIB]: https://github.com/cosmosapjw-quantum/rei_bianchi/blob/633e0bd26b40bf59e8dfe6b977edb6e6dacc144d/rust/rei_microphysics/src/lib.rs
