# BASS_HE RUX03 공급자 패킷 독립 판정

## 판정과 적용 범위

**PROMOTE_SCOPED_BASS_HE_SUPPLIER.** CLAIM_LIST.json의 C01–C06을 명시된 공급자 연구·보고 범위에서 승격한다. 복구된 warm 입력의 선택과 원자 과정 owner 대응, 조건부 재결합·재흡수 유도, 저장된 17개 시점의 RCT/RR 비교, 고정 초기 상태에서의 6개 단색 응답, P03A source-delta 조정, 기존 결과의 제한된 계승을 완료한 것으로 판정한다. 이 범위에서 해결되지 않은 fatal 또는 material 오류는 발견하지 못했다.

이 판정은 전체 owner RUX00/RUX03 완료, 새 native 실행·parity, cold history, 실제 RCT 방출 spectrum/평균 에너지, diffuse-ON 결합 이력, 연속시간 오차 한계 또는 전역 EoR 예측의 승격이 아니다. 해당 상태는 계속 미해결 또는 HOLD다. 원본 candidate의 REVIEW_PENDING 표시는 검토 전 작성 상태로 보존하며, 최종 판정은 DECISION.json이 소유한다.

판정 대상은 REVIEWED_ARTIFACTS.json에 크기와 SHA256으로 묶은 **52개 파일**이다. screening/FREEZE.json의 26개 항목은 모두 실제 파일의 크기·SHA256과 일치했다. 판정 후 추가하는 행정 상태·전달 파일은 이 과학적 후보 집합에 포함되지 않는다. 파일 identity는 과학적 타당성이나 실행 provenance 자체의 대체물이 아니다.

## 검토자 독립성

검토자는 실제 별도 subagent `/root/dropbox_checkpoint`이다. 이 agent는 먼저 Dropbox 원본·receipt와 일부 runtime source를 읽기 전용으로 복구했고, 이후 고정된 이론 후보와 별도 계산 작성자가 동결한 수치 산출물을 검토했다. source 복구 사실은 작성자에게 전달했지만 이론 후보, 수치 코드 또는 검증 설계를 작성하지 않았다. 후보 작성자와 계산 작성자의 역할을 바꾸어 수행한 자기 검토가 아니다.

독립성의 범위는 후보 생성·검증 설계와 분리된 판정이다. 동일한 공동 작업 세션과 공유 파일시스템을 사용했으며, 다른 연구기관·실험 장비·독립 물리 자료로 재현했다는 뜻은 아니다. 검토 중 오류와 조건을 지적했고 작성자가 같은 범위 안에서 수정했다. 최종 후보를 직접 수정하거나 과학 계산을 다시 실행하지 않았다. 추가로 수행한 작업은 원문 읽기, 수식·코드 검토, 파일 identity 확인과 판정 기록이다.

## 주장별 판정

| 주장 | 판정 | 인정하는 결과 | 인정하지 않는 확장 |
|---|---|---|---|
| C01 | PROMOTE | 선택된 PR96 warm extended 입력의 가용성, 실제 callback·단위·domain·owner 대응 | 전역 물리 입력 완결성, 현재 receiver 주입 완료 |
| C02 | PROMOTE | 명시한 조건에서 성립하는 사건 행렬, 에너지 보존, 생존 kernel, 균일 출생식, 다종 OTS, 양의 에너지 measure bound | 미지의 방출 source를 결정했다는 주장, 새로운 물리 정확도·novelty |
| C03 | PROMOTE | 저장 OFF 이력의 17개 시점에서 새로 평가한 RCT/RR 비율 | ON 이력, 모든 시간의 균일 상한, 전역 EoR 비중 |
| C04 | PROMOTE | 고정 밀도·고정 local E에서 6개 probe의 광자수·종·에너지 응답 | 실제 방출 spectrum, 적색편이·gas 변화가 있는 결합 이력 |
| C05 | PROMOTE | 문서화된 P03A docstring delta와 실행 source SHA의 재구성 | 과거 실행을 새로 수행했다는 주장, 원래 과학적 ceiling 확대 |
| C06 | PROMOTE | 기존 B1·PR113·P03A의 출처와 제한을 유지한 계승 및 owner 미완료 상태의 보존 | 기존 계산을 이번 신규 성과로 산입하거나 owner 작업을 닫는 것 |

직접 근거는 각 claim의 evidence 목록과 이 검토에 묶인 최종 파일이다. source·수식·수치·기존 실행의 역할이 구별되어 있으며, 하나의 aggregate score로 합치지 않았다.

## 물리·수학 검토

### 사건 행렬과 local energy

종 순서 `(HI, HII, HeI, HeII, HeIII, e)`와 세 photoionization edge의 행렬 S는 H 핵수, He 핵수, 전하를 각각 보존한다. 누적 binding potential을 `b=(0, χH, 0, χHeI, χHeI+χHeII, 0)`로 두면 각 edge의 binding 증가가 정확히 대응하는 χ다. 같은 사건 수로 photon loss, 이온·전자 생성, binding χ, primary heat `E−χ`를 연결하는 방식은 중복 계상을 막는다.

RCT의 종 변화는 HI ionization edge에서 HeII ionization edge를 뺀 것이다. 직접 자유전자 변화는 0이며 binding 변화는 `−(χHeII−χHI)`다. 이 사실이 RCT 광자의 에너지나 열원을 정하지는 않는다. scalar k(T), 사건 수, source spectrum, 평균 photon energy와 heat/recoil closure를 분리한 최종 문서는 타당하다.

RR kinetic moment `kBT(3/2+d ln α/d ln T)`는 공통 Maxwell 분포와 명시한 단면적 가정 아래의 rate moment 항등식으로 읽어야 한다. 실제 계산은 선택된 FT03 fit과 기존 warm domain에 조건부다. fit을 사용한 식의 정합성은 원자 자료의 실험 오차를 새로 보증하지 않는다. 전체 재결합 source에 대한 photon energy normalization은 최종 ground state, 잔류 excitation·recoil의 처리와 전체 cascade photon 수를 포함해야 한다. 최종 후보는 그 가정과 미공급 source moment를 표시한다.

RR의 R과 RR+DR의 전체 sink를 구별한 수정은 필요했고 반영되었다. DR은 별도 사건·moment로 취급된다. Case A escape에서 명시적 방출로 바꿀 때 기존 escape energy를 그만큼 이동시켜야 하며 새 source를 추가하면서 기존 escape를 그대로 더하는 것은 허용되지 않는다.

### Bianchi 생존·에너지 kernel

비틸트 prescribed Bianchi에서 실제 광선 방향을 따라 `dE/dt=−(H+σee)E`를 사용하고, 각 종의 proper absorption hazard를 `λs=c ns σs(E)`로 잡은 생존 확률은 타당하다. 다른 소멸/탈출을 λout에 넣는 경우 동일 사건을 중복 포함하지 않아야 한다. 각 종 흡수, 명시한 out, 최종 생존의 확률 합은 1이다.

에너지 항등식에는 최종 생존 에너지, 각 종의 binding과 heat, out energy 및 `∫Hparallel E S dt`가 모두 필요하다. 후보의 부호가 맞다. 방향 수축에 따른 blueshift에서는 geometry work가 음수일 수 있다. 단일 photon의 생존 확률에 volume dilution을 다시 넣지 않는 것도 맞다. 이것은 ballistic primary-absorption kernel이며 scattering redistribution, secondary cascade 또는 gas feedback의 해를 대신하지 않는다.

밀도·E·hazard가 고정되고 출생 시간이 균일할 때 `F(τ)=1−(1−exp(−τ))/τ`가 나온다. 초기 시각 일괄 출생의 `1−exp(−τ)`와 구별된다. 종별 확률은 `ps F(τ)`이므로 optically thick limit에서 각 종은 ps에 접근하고 종 합만 1에 접근한다. 이 조건은 최종 후보에 수정되어 있다.

### 다종 OTS와 에너지 measure bound

source당 spectrum을 ηj, 흡수 branching을 ps로 두고 `Bsj=∫ps(E)ηj(E)dE`로 쓰면 재결합-재흡수의 화학 source는 `S(B−I)R`이다. B는 한 재결합당 각 absorber에서 발생하는 사건 수를 담으므로 cascade multiplicity를 허용한다. 통상적 단일종 Case B는 그 행렬의 특수한 폐쇄 조건에서만 환원된다. 다른 종으로 가는 He 재결합 광자를 전체적으로 한 scalar Case B 계수로 지울 수 있다는 결론은 나오지 않는다.

전부 재흡수되는 RR source의 net heat `χj−Σs χs Bsj`는 재결합 kinetic cooling과 재흡수 heat를 함께 계상한 결과이며 부호가 맞다. source energy normalization과 local OTS 가정이 필수다. He photon에 의한 H/He 결합은 Friedrich et al.의 [arXiv:1201.0602 §3.1.2](https://arxiv.org/pdf/1201.0602)에 이미 논의되어 있다. 검토한 범위는 해당 절과 관련 문맥이며 논문 전체의 모든 구현을 검증했다는 뜻은 아니다. 최종 후보가 선행연구를 인정하고 novelty 승격을 요구하지 않는 판단이 적절하다.

양의 emitted-energy measure dW에 대한 응답은 `∫(Ps/E)dW`, `∫(Kheat/E)dW`로 표현할 수 있다. 알려진 총 에너지와 명시된 support에서 kernel infimum/supremum을 쓰는 bound는 선형성과 양성으로 성립한다. 실제 source spectrum을 복원하지 않는다. 시간·방향을 합치는 경우 `dW(b,E,Ω)`와 동일한 조건부 kernel 또는 합동 support가 필요하다. 최종 수정은 이를 명시한다. 유한한 저장 grid의 극값은 연속 support 전체의 extrema 증명이 아니다.

Wolfram 원자료는 사건·binding·RCT 행렬, 에너지 항등식, 균일 출생식과 series 등 해당 symbolic checks를 지지한다. 최초 문법 실패와 수정 성공이 모두 보존되었다. symbolic pass를 source physics의 독립 실험 검증으로 읽지 않았다.

## 실제 입력·owner와 source 권위

선택된 자료는 10–50000 eV의 extended history, 2904 nodes, 17 epochs, 초기 50000 K, elapsed `[0,1e11] s`다. 10–200 eV의 base 자료나 그 다른 HeIII 초기값을 혼합하지 않았다. 입력 archive 87개 원본 항목과 260개 v2 additive 항목의 일치 기록, selected NPZ/JSON 및 PR113 저장 상태 대응이 근거다.

실제 PR96 warm route는 `run_interval.py → native main.rs::rhs → ft03_rhs`다. native thermo의 photon 입력은 0이고 별도 node별 primary PI와 `axisym_coupled_derivative`가 종·광자·열·팽창 장부를 조합한다. `coupled_primary`는 함께 존재하는 대안 경로다. 최종 REPORT의 이 부분은 원래 두 경로를 혼동한 문장을 지적한 뒤 수정되었으며, admission·owner matrix와 일치함을 확인했다.

HM12 초기 UVB와 시간 의존 comoving emissivity의 역할·단위가 분리되어 있다. 실제 FT03 warm rate와 raw Grackle reference를 구별했고, 세 Verner fit cutoff 13.60/24.59/54.42 eV를 binding χ와 같다고 놓지 않았다. RCT source 두 개는 대안이며 합하거나 평균하지 않는다. KF96은 선택된 50000 K에서 rate-domain 내이고 GM25는 명시적으로 거절되었다. raw 5000 K coefficient parity가 cold thermal closure의 admission을 뜻하지 않는다는 제한도 유지되었다.

source map은 정확한 archive/member, 고정 Git commit 및 기존 scope를 구별한다. v2의 `axisym_coupling.rs`는 원래 native execution pin과 다르다는 사실을 보존한다. 이번 작업은 저장 결과를 사용하므로 그 사실이 warm 입력 부재를 뜻하지는 않는다. 새 native interval의 source·clean build·binary 결합은 후속 실행 전에 해결할 별도 gate다.

## 수치 산출물과 검증의 한계

계산 작성자의 실제 성공 실행은 1회이며 exit 0, wall time 1.287163786 s다. 이 중 기록된 numeric phase는 0.030941785 s다. 이번 review가 과학 실행을 반복하지 않았으며 신규 ODE·transport·native build·NCP 실행은 모두 0이다. 코드, 입력 manifest, receipt, 원 로그, 결과 JSON/CSV와 그림을 직접 읽고 해석했다.

새 RR coefficient와 보존된 RCT event rate를 같은 상태에서 비교하면 17개 저장 시점의 비율은 `[3.097824900175699e−7, 3.097839361031057e−7]`다. `nHeIII>0`에서 비율은 `k nHI/(α3 ne)`로 약분되므로 구현과 단위가 맞는다. 이 정도 크기라는 결론은 저장된 OFF 궤도와 선택 source에만 적용한다. PR113의 `3.4318478685512853e−15 events/H`는 기존 저장-grid trapezoid 결과이며 이번 새 노출 적분이 아니다. 그 연속시간 오차는 NOT_ESTIMATED다.

6개 단색 응답은 같은 초기 lower-state density, 고정 E, 1e11 s에서 계산했다. `Qref=40.819325400298 eV`에서 HI/HeI의 조건부 branching은 약 0.349573/0.650427이고 HeII는 열리지 않는다. 초기 일괄 출생 흡수율은 약 3.59629e−6, 균일 출생은 약 1.79815e−6이다. Qref는 에너지 probe이며 RCT의 실제 방출 spectrum으로 지정하지 않았다.

54.42 eV에서의 균일 출생 흡수율 약 0.0107391은 HeII fit edge를 계속 유지하는 고정-E 응답이다. 적색편이가 있는 실제 Bianchi history에 그대로 적용할 수 없다. 최종 handoff가 이 제한을 특히 표시한다. 종별 확률·positivity·photon survival과 binding/heat/잔존 에너지의 합은 frozen 계산에 맞게 구현되었다.

작성자가 수행한 16개 check는 모두 PASS이며 Decimal80 대조의 최대 상대 차이는 Verner에서 약 2.64e−15다. 별도 고정밀 산술 표현과 binary64의 비교는 같은 analytic form의 산술 검산이다. 다른 atomic fit과의 검증, 새 native parity 또는 별도 작성자의 구현 재현으로 확대하지 않는다. 독립 최종 판정은 이 문서의 검토 역할에서 이루어졌다.

P03A는 공개 코드의 docstring 변경을 역으로 적용하면 기록된 실행 SHA를 재구성하고 docstring 제외 AST가 일치한다는 원 증거를 검토했다. retained cap/retained 값 0.011107406480410278과 cap/min-thermal 1.3218886276228445e−8의 기존 제한을 유지한다. 이는 17 epochs·2904 nodes의 finite sampled diagnostic이며 실제 diffuse-ON source admission이나 연속 bound가 아니다.

## 해결된 지적과 종료 근거

검토 중 네 가지 실질적인 정리가 반영되었다. 종별 thick limit을 ps로 고쳤고, RR과 RR+DR의 기호를 분리했으며, 합동 출생 시간·방향 measure의 조건을 밝혔고, 최종 report의 선택 native route를 수정했다. 작은 적분 표기 오타도 수정되었다. 고정된 최종 파일은 이 수정들과 원래의 계산 결과를 함께 보존한다.

evidence와 각 주장의 연결은 충분하고 수학·물리적 가정은 명시되어 있다. 선택된 source와 폐쇄 대안은 서로 구별되며, 이번 실행으로 판별할 수 있는 항목은 실제 실행되었다. robustness는 명시된 finite 범위와 precision checks로 제한되지만 그 이상의 주장을 하지 않는다. 계산 비용은 작고 반복 실행이나 NCP 투입을 정당화할 잔여 위험은 없다. source 주입과 광자·원자·에너지의 동일 사건 연결이라는 원래 동기도 보존된다. novelty나 model 성능을 새로운 결과로 주장하지 않는다.

따라서 이 공급자 단계는 닫고 NEXT_DAG.json의 **HERE_RUX03_EVENT_BRIDGE_02**로 넘긴다. receiver의 실제 선택 RHS에서 동일 사건 bundle을 한 번 소비하는 주입과 영향을 받는 장부 검증이 다음 완료 기준이다. 이 검토가 그 주입을 수행하거나 승인된 것으로 선언하지 않는다. E13C11은 관측량 필요가 생길 때까지 parked이고 기존 B1·11-history campaign·PR113·P03A는 재실행 대상으로 바꾸지 않는다. 추가 review loop나 unchanged scientific replay는 요구하지 않는다.
