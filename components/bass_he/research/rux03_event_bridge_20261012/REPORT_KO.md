# BASS_HE 다음 연구 루프 — Case A 사건의 실제 RHS 소비

2026-10-12 · `HERE_RUX03_EVENT_BRIDGE_02` · GPT-6 Astra / 연구·코딩 하네스 4.0.0

## 1. 결과

선택된 `rei_bianchi` production 경로에서 CI·RR·DR·광이온화의 원시 사건을 하나의 소유된 Case A bundle로 만들고, 그 bundle을 실제 AXI 우변의 종·전자·광자·열·결합·탈출 에너지 항으로 소비하도록 구현했다. 단일 He III 재결합 변화량을 넣는 시험으로 각 항에 사건이 정확히 한 번 반영됨을 확인했다. 독립 Decimal60 계산과 실제 native 호출의 비교, 두 상태의 검사, 초기값에서 시작한 새 production 구간도 사전에 정한 기준을 통과했다.

이 문서의 실행 판정은 **PASS_SCOPED**다. 후보 작성·검증 설계에 참여하지 않은 검토자의 최종 채택 판정은 [독립 판정](review/DECISION.json)에 기록한다. 이 문서는 그 판정에 제출하는 과학적 주장과 근거를 고정한 것이다. 전체 owner RUX03의 완료나 새로운 물리 시나리오의 승인을 뜻하지 않는다.

| 실제 검증 | 결과 | 사전 기준 / 의미 |
|---|---:|---|
| 변경 경로의 conditional native 시험 | 11/11 통과 | 기존 8개와 추가 사건 시험 3개 |
| FT03 native 시험 | 8/8 통과 | 기존 기준 유지 |
| 전체 workspace native 시험 | 176 통과, 0 실패 | 위 19개와 중복되므로 합산하지 않음 |
| 초기 상태의 원시 사건·에너지 22개 성분 | 최대 상대차이 (1.0942794551\times10^{-12}) | (3\times10^{-11}) |
| 두 상태의 검증 항목 | 48 + 31 = 79개 모두 통과 | 종·전하·광자·에너지·단위·stage/source 일관성 |
| 두 상태의 최대 정규화 invariant 잔차 | (6.0599181261\times10^{-15}) | (10^{-12}) |
| 새 production 적분 | 257 RHS 호출, 17개 저장 시점, 약 2.877초 | (0\le t\le10^{11}\) s, 2904 photon nodes |
| 저장 기준과의 상태 / 22개 기록 항목 차이 | 모두 0 | 기존 비교 상한 (2\times10^{-6}) 유지 |
| 구간의 국소 광자수 / 에너지 잔차 최댓값 | (7.0009691267\times10^{-15}) / (1.7556755934\times10^{-16}) | 기존 ledger 상한 (10^{-9}) 유지 |

증거는 [실행 요약](RESULTS_SUMMARY.json), [주장별 근거](CLAIMS.json), [검증 행렬](VALIDATION_MATRIX.md), [증거 색인](EVIDENCE_INDEX.json)에 연결한다. 원시 결과와 로그는 함께 전달하는 재현 packet의 `evidence/`에 보존한다.

## 2. 무엇을 새로 닫았는가

직전 BASS_HE 루프는 He 재결합 사건과 광자 응답의 supplier 계약을 정리했다. 그 다음에는 그 계약이 실제 계산의 사건 담당과 연결되는지 확인해야 했다. 현재 PR97의 production 경로에는 이미 warm Case A 반응, photon node 흡수와 AXI derivative의 조합이 있었다. 이번 변경은 그 기존 조합에서 **원시 사건의 소유권과 한 번의 소비를 명시하고 검증**한 것이다.

실제 호출 경로는 `ProductionInterval.rhs → NativeConsumer("RHS") → ConditionalSession → SourceBoundConditional → AXI derivative`다. 변경한 `SourceBoundConditional::evaluate`는 상세 평가를 거쳐 동일한 bundle에서 계산한 RHS를 반환한다. 진단용 `EVENTS` 응답도 상세 평가 한 번에서 소비된 사건과 장부를 반환한다. Python probe는 같은 상태에 대해 RHS와 EVENTS를 각각 호출하여 두 응답의 일관성을 비교한다. 이 두 호출을 하나의 native 호출로 세지 않는다.

`Ft03Rhs`는 기존 평가에서 이미 계산한 RR·DR의 포획 운동에너지 power를 노출한다. 새 소비자는 이 원시 power와 사건률을 사용한다. 해당 callsite에서는 과거의 aggregate atomic thermal/escape 결과를 다시 더하지 않는다. 공개 production 경로의 provider 선택은 기존 FT03 Case A로 고정되어 있다. 시험에 쓰인 private provider 대체는 물리 provider를 임의로 승인하는 공개 API가 아니다.

근거: [최종 production 코드](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs), [FT03 원시 power 노출](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/ft03_controlled.rs), [사전 계약](SCIENTIFIC_CONTRACT.md).

## 3. 사건에서 장부로 가는 식

반응 채널 (a=(\mathrm{H I},\mathrm{He I},\mathrm{He II}))에 대해 (C_a,R_a,P_a)는 각각 충돌 이온화, 방사 재결합, 광이온화의 사건률이다. (D_1,D_2)는 He II에서 He I로 가는 두 DR 성분이다. 모두 proper volume 기준 (\mathrm{cm^{-3}\,s^{-1}})이다. 위쪽 이온으로 가는 순 사건률을

\[
J_a=C_a-R_a+P_a-\mathbf 1_{a=\mathrm{He I}}(D_1+D_2)
\]

로 두면, 종과 전자의 생성항은

\[
(\dot n_{\rm HI},\dot n_{\rm HII},\dot n_{\rm HeI},\dot n_{\rm HeII},\dot n_{\rm HeIII},\dot n_e)_{\rm int}
=(-J_H,J_H,-J_{HeI},J_{HeI}-J_{HeII},J_{HeII},J_H+J_{HeI}+J_{HeII})
\]

가 된다. 따라서 H 핵수, He 핵수와 전하는 각각 보존된다. 이 항들은 팽창 희석을 따로 소유하는 기존 기하·stage 경로와 구별되는 상호작용 source다.

(K^{RR}_a,K^{DR}_r)를 이미 평가된 포획 운동에너지 power라 하고, 광이온화 node의 사건률과 에너지를 (P_{aq},E_q)라 하면,

\[
\dot u_{\rm th,int}=-\sum_a(C_a\chi_a+K^{RR}_a)-\sum_rK^{DR}_r+
\sum_{a,q}P_{aq}(E_q-\chi_a),
\]

\[
\dot u_{\rm bind,int}=\sum_a J_a\chi_a,\qquad
\dot u_{\rm esc}=\sum_a(R_a\chi_a+K^{RR}_a)+\sum_r(D_r\chi_{HeI}+K^{DR}_r).
\]

이 식의 (E,\chi)를 erg로 쓰면 power의 단위는 (\mathrm{erg\,cm^{-3}\,s^{-1}})이다. 광자 흡수는 같은 node 사건에서 (-\sum_{a,q}P_{aq}), (-\sum_{a,q}P_{aq}E_q)로 계산한다. 그러면 상호작용에 대해

\[
\dot u_{\rm th,int}+\dot u_{\rm bind,int}+\dot u_{\gamma,\rm abs}+\dot u_{\rm esc}=0
\]

가 성립한다. 외부 HM12 source는 실제 stage의 값을 따로 더하고, redshift·shear work는 기존 기하 경로가 담당한다. source를 0으로 치환하지 않았다.

결합에너지 (13.598434599702,24.587389011,54.41776\) eV와 단면적 fit cutoff (13.6,24.59,54.42\) eV의 차이를 유지했다. native AXI 경계에서는 수밀도 source에 (10^6), energy power에 (0.1)을 곱해 SI로 바꾼다. 광자 상태 (N=a_{\rm rel}^3n_\gamma)와 proper volume 사이의 변환도 원래 stage의 책임을 유지했다. 이는 [코드](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/a5c958c414dea41216b445c05f58df837f05cacb/rust/rei_microphysics/src/axisym_conditional.rs)와 [독립 원시 사건 계산](reference/EVENT_REFERENCE_1STAGE.json)을 함께 확인한 범위의 유도·구현 결과다.

## 4. 왜 보존식 외에 별도 시험이 필요한가

보존적인 사건을 두 번 더해도 위 선형 보존식은 그대로 성립한다. 따라서 작은 에너지 잔차만으로 소비 횟수를 판단할 수 없다.

추가한 시험은 private provider의 He III RR 사건에 
\(\delta R=10^{-12}\,\mathrm{cm^{-3}\,s^{-1}}\)와 사건당 7 eV의 포획 운동에너지를 함께 더한다. 이 값은 도함수 반응을 검사하기 위한 제조된 변화량이다. 실제 AXI RHS에서 He II는 (+\delta R), He III와 전자는 (-\delta R), 결합에너지는 (-\chi_{HeII}\delta R), 열은 (-7\,\mathrm{eV}\,\delta R), 탈출 에너지는 (+(\chi_{HeII}+7\,\mathrm{eV})\delta R)만큼 변해야 한다. 광자·외부 source는 이 변화에서 그대로여야 한다.

`injected_heiii_rr_event_is_consumed_once_by_actual_axi_rhs`는 provider 호출 횟수 1과 이 변화량들을 실제 우변에서 검사해 통과했다. 같은 bundle의 진단·단위 변환 시험, 음의 사건을 거부하는 시험도 추가했다. 시험의 정규화 기준 (2\times10^{-12})와 기존 기준을 실행 뒤 완화하지 않았다. 이 시험은 선택된 seam과 해당 채널의 소비 횟수를 강하게 판별하지만, 모든 가능한 provider에 대한 형식 증명은 아니다.

## 5. 원시 사건과 수치 정합성

초기 상태는 (T=50000\) K, (z=5.807), (n_H=5.935621973155476\times10^{-5}\,\mathrm{cm^{-3}})이며, 선택된 photon nodes는 2904개다. 다음 표는 실제 `EVENTS` 응답을 반올림한 값이다.

| 채널 | PI | CI | RR |
|---|---:|---:|---:|
| H I ↔ H II | (4.24138389893\times10^{-22}) | (5.79917018792\times10^{-23}) | (4.82130091771\times10^{-22}) |
| He I ↔ He II | (4.70742785414\times10^{-23}) | (2.96836560705\times10^{-25}) | (4.30216111664\times10^{-23}) |
| He II ↔ He III | (5.26884308036\times10^{-24}) | (1.30678153233\times10^{-24}) | (6.57562461269\times10^{-24}) |

단위는 모두 (\mathrm{cm^{-3}\,s^{-1}})이다. He II → He I의 두 DR 성분은 (4.15908558430\times10^{-24}), (1.90418351420\times10^{-25}\,\mathrm{cm^{-3}\,s^{-1}})였다.

독립 계산은 후보를 import하지 않고 고정된 FT03/Verner 식과 입력에서 Decimal 60자리 기준을 구했다. 원계산은 Python stdin으로 실행했고, [보존한 생성기](reference/decimal_event_oracle.py)는 그 식과 입력 해석을 재현하도록 남긴 파일이다. 이 파일 자체가 원실행의 진입점이었다고 주장하지 않는다. [원결과](reference/EVENT_REFERENCE_1STAGE.json)와 함께 보존했다. 실제 native 원시 성분과 비교한 그룹별 최대 상대차이는 다음과 같다.

| 비교 그룹 | 최대 상대차이 |
|---|---:|
| CI | (1.0942794551\times10^{-12}) |
| RR | (1.9505015279\times10^{-16}) |
| DR | (1.4131644168\times10^{-15}) |
| PI | (1.0928581777\times10^{-12}) |
| RR 운동에너지 power | (1.5192101982\times10^{-16}) |
| DR 운동에너지 power | (1.2677259482\times10^{-15}) |
| PI 열 power | (1.0883723862\times10^{-12}) |
| PI 흡수 에너지 power | (1.0916698718\times10^{-12}) |

초기 상태는 거의 균형이어서 순 사건률이 큰 양·음 성분의 상쇄로 얻어진다. Decimal 전사와 binary64 중성 분율 계산의 차이는 원시 성분에 약 (10^{-12})의 차이를 만들 수 있고, 작은 순율의 상대오차는 훨씬 커질 수 있다. 그러므로 원시 성분은 성분별 상대차이로, 순 source는 총 사건 규모 또는 총 에너지 규모로 나눈 절대차이로 검증했다. 이 구분은 실행 전에 고정했다. Decimal 자릿수나 이 일치도를 원자 fit의 물리 정확도라고 해석하지 않는다.

초기 상태에서는 48개 항목, 기존 마지막 상태를 입력으로 준 진단 callback에서는 31개 항목이 통과했다. 뒤의 callback은 (a_{rel}=1.0000022148394714)에서 부피·기하·source 변환을 검사하기 위한 저장 상태의 사용이다. 새로운 시간 적분 결과와는 구별한다.

## 6. 변경된 우변으로 실제 적분한 구간

별도의 실행에서 기존 `source_bound_interval.py`가 초기 상태만으로 새 DOP853 적분을 시작했다. 기존 마지막 상태와 이력은 적분이 끝난 다음 비교에 사용된다. solver 설정은 `rtol=2e-10`, `atol=2e-13`, 정규화 `max_step=1/16`으로 유지했다. 실행 receipt에 바인딩된 새 native binary가 실제 RHS를 257회 계산했다.

| 값 | 초기 | (t=10^{11}\) s |
|---|---:|---:|
| (T) [K] | 50000.0 | 49999.7770770447 |
| (x_{HII}) | 0.9999754745282792 | 0.9999754745635018 |
| (x_{HeII}) | 0.9700839024387024 | 0.9700839009905692 |
| (x_{HeIII}) | 0.029861279382071514 | 0.029861280876924804 |
| (n_H\) [cm⁻³] | (5.935621973155476\times10^{-5}) | (5.9355825339806816\times10^{-5}) |
| (n_e\) [cm⁻³] | (6.41804549337503\times10^{-5}) | (6.418002849673917\times10^{-5}) |

온도 변화는 약 (-0.222923\) K다. 17개 저장 시점의 상태와 출력된 22개 비교 항목은 보존된 기준과 차이가 0이었다. 이는 선택된 이산화와 solver 설정에서 이번 사건 소유권 변경이 기존 결과를 보존했다는 실제 실행 증거다. 서로 독립적인 물리 모형의 일치나 연속체 오차 상한을 새로 증명한 결과로 확대하지 않는다. 기존 runner의 `scientific_admission: HOLD`도 원래 의미로 남겨 두었다.

## 7. 실행 이력과 최초 실패

최초 환경 확인에서 local Rust toolchain이 없었다. 좁은 CI 작업으로 clean committed source를 새 target directory에서 release build하고, 기존 receipt 검사기를 통과한 정확한 binary를 여기서 실행했다. 전체 과거 캠페인을 CI나 다른 계산 자원으로 옮기지 않았다.

첫 후보 `38c4f69…`는 native build와 대상 19개 시험을 통과했지만 `cargo fmt --check`가 실패했다. 실제 formatter 출력의 줄 배치와 동등한 단일 식 closure 표현을 그대로 반영한 `a5c958c…`를 다시 build했다. 식·가드·판정 기준은 그대로다. 최종 CI는 formatting, 대상 시험과 전체 176개 시험을 모두 통과했다. 두 build의 binary bytes는 같지만, 최종 source의 실행 provenance는 별도의 최종 clean-build receipt로 확인했다.

첫 local probe는 원래 입력 packet의 `sources/acquisition.json`이 이 작업의 local 복원본에서 빠져 있어 실패했다. 이때 native 호출은 BIND 1회, RHS 0회, EVENTS 0회였다. 원래 PR97의 정확한 metadata 파일을 복원한 뒤 동일 source와 binary로 다시 실행했다. source guard, 입력 hash 검사, 물리식이나 기준을 변경하지 않았다. native build artifact의 7개 고정 입력만으로 전체 provider snapshot이 완성된다고 간주해서는 안 된다. 재현 packet은 이 보조 metadata와 identity를 포함한다.

근거: [format 수정 기록](FORMATTING_REPAIR_v2.json), [입력 복원 기록](INPUT_MATERIALIZATION_REPAIR.json), [최초 실패와 한계](state/NEGATIVE_RESULTS.md), [최종 native build CI](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/38251064189), [전체 verify CI](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/38251064214).

## 8. 정확한 source와 재현

| 역할 | 고정 identity |
|---|---|
| BASS_HE 직전 supplier 기준 | `1d9794b4de07eaa165631b984b4a7c1030671ae6` |
| receiver PR97 기준 | `1400093cdd121d8e6adb51ffeb360102a48653bf` |
| 새 receiver source commit | `a5c958c414dea41216b445c05f58df837f05cacb` |
| 새 receiver tree | `2e96362102caa69c814d477bae5d1c0177b502f9` |
| 실행 binary SHA-256 | `1edf5660e0d451ce0ae066750981c3cf3038fa376a24fed4ec1f378304d6a1e0` |
| 최종 build receipt SHA-256 | `91f5621c6dd630c758af0a85280af32ba7f9eb3f96b27246550e7eba23d3999d` |
| Decimal60 결과 SHA-256 | `57c0ad93cc2cfe8edebf4728bb4405e2457ca5f77e90137896c0132222d7522f` |
| Decimal60 생성기 SHA-256 | `d03e55829d823b9ce3567f5f09ca3c776c2fc6845945a7383e0599039ce752eb` |

hash는 파일 identity이고, 실행·과학적 타당성의 단독 근거가 아니다. 실제 명령·환경·exit status·원시 응답·기준과 결과를 함께 보존했다. native toolchain은 실제 `rustc 1.99.0` / `cargo 1.99.0`, 실행 환경은 Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0이었다. 재현 명령과 필요한 파일은 [재현 안내](REPRODUCE.md)를 따른다.

## 9. 연구 상태와 다음 최소 작업

이번에 닫은 범위는 **선택된 warm Case A conditional production에서의 사건 소비**다. 물리 선택은 기존 primary-only external photons, Case A escape, CR/RCT/HH OFF를 유지한다. RR/DR의 탈출 에너지는 정의하지만 재결합 방출 광자 수나 스펙트럼을 추가로 만들어내지 않는다.

다음 최소 작업은 `HERE_RUX03_PRIMARY_PROVIDER_03`으로 잡는다. 기존 implicit primary의 실제 stage와 같은 provider/event 계약을 연결하고, 영향을 받는 point 평가와 root/interval 평가가 같은 provider를 쓰는지 또는 서로 다른 주장 범위가 필요한지 판별한다. RUX02 입력 admission과 RUX03 provider 작업은 원래의 병렬 구조를 유지한다. 물리적 첫 FLRW 구간인 RUX05로 넘어가기 전에 RUX04의 scenario freeze를 충족해야 한다.

이번 실행을 전체 RUX03, implicit/root 경로, cold/global EoR 또는 BASS visibility의 완료로 소급하지 않는다. 원래 owner DAG의 17개 ID와 의존성은 보존하고 [후속 overlay](NEXT_DAG.json)에 이번 기여와 다음 단계만 더한다. B1·과거 11-history·PR113·P03A 캠페인은 재실행하지 않았고, 새 NCP 작업은 0개다. 다음 재개 지점과 완료조건은 [handoff](HANDOFF_KO.md)에 고정한다.
