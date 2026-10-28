# Sandbox 연구 통합 결과와 다음 DAG

2026-10-22. 이번 범위는 최근 결과 통합과 저장소별 작은 이론·코드 단위의 실행입니다. 전체 reionization 물리계의 수렴·관측 적합 완료를 뜻하지 않습니다.

## 이번 실제 결과

| 저장소 | 완료한 단위 | 판별 근거 | 게시 |
|---|---|---|---|
| BASS_HE | Lorentz l=2 pressure functional; HE33 host check | 17 legacy groups reused on Node;11 new groups; no IVP | [PR87](https://github.com/cosmosapjw-quantum/BASS_HE/pull/87) |
| WU088_HH | D PI/RR energy and particle-count temperature adapter | 72 events+8 domain+27 temperature+1 cycle | [PR135](https://github.com/cosmosapjw-quantum/WU088_HH/pull/135) |
| bass_cr | C22A/B source recovery and SW91 excitation diagnostic | 36 source coefficients;126 Decimal checks;0 ODE | [PR97](https://github.com/cosmosapjw-quantum/bass_cr/pull/97) |
| rec_bianchi | Saved-eight Compton omission budget | 872 saved states;0 ODE; overlaps PR122 Planck budget | [PR123](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/123) |
| bass | Exact affine33-to30 restriction | 3 actual-owner states;12 directions;0 IVP | [PR181](https://github.com/cosmosapjw-quantum/bass/pull/181) |
| vigilode | Lifted full33 adaptive norm | 10 Decimal oracles+5 negative controls; concrete repair closed | [PR79](https://github.com/cosmosapjw-quantum/vigilode/pull/79) |
| rei_bianchi | Zero/tiny-stock absolute-abundance event kernel | 7 manufactured fixtures;9 applicability+5 controls;0 IVP | [PR222](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/222) |

핵심 과학 결과는 다음과 같습니다.

- HE: 일정한 수송 단면적의 Grad 압력 이완률 계수는16/(5√π), 평균 충돌률 대비8/5입니다. 단일 지수 감쇠는 일반적인 유한 시간 해가 아닙니다.
- HH: D PI/RR 세 에너지 장부와 입자 수 변화 온도항을 C99로 연결했습니다. D threshold는 기존 모델의43K 결함 관례를 사용하며 독립 경험적 isotope rate 채택은 아닙니다.
- CR: 원논문 SW91 Table3의36개 계수를 눈으로 확인하고 독립 검토했습니다. 유효한71개 저장점·70구간의 여기 손실은0.0489597873eV/Href이며 전체 경과시간의2.1575%만 덮습니다.2000K 미만은 여전히 미확보입니다.
- REC: 지정 Planck 배경의 누락 Compton 냉각은−2.570630∼−2.575791eV/baryon입니다. PR122가 병렬로 게시한 같은8개 저장 경로의 값과1.78e−15eV/baryon 이내로 일치합니다. 별도8개 계산으로 중복 집계하지 않고 독립 C 구현으로 보존합니다.
- BASS: H/He/Li 원소별 보존량으로33→30 좌표를 정확히 제한했습니다. 실제 owner의 RHS/Jacobian과21개 출력 대응만 검증했고 새 궤적은 적분하지 않았습니다.
- VigilODE: full33 오차 노름을 보존하는 C99 어댑터를 만들었습니다. 극단적 지수 혼합에서 상쇄항을 잃던 첫 구현을 보존하고 extended long double 보상합으로 수정했습니다. 실제 driver 연결과 속도 비교는 다음 작업입니다.
- REI: 절대 abundance와 로그 반응률로 exact-zero onset과1e−104 stock을 처리했습니다. 원래1e−334 이벤트는 binary64에서0이어도 축척화한 소스1e−230을 보존합니다. Manufactured fixture 검증이며 물리적 daughter 분포를 새로 얻었다는 뜻은 아닙니다.

새 cosmological IVP와 NCP 제출은0회입니다. 입력 복구와 패키징은 과학 실행 수에 포함하지 않습니다. SciSpace/Exa 원전 조사와 Wolfram 기호 계산을 사용했으며 공유 식은 theory/SHARED_PHYSICS.md에 있습니다.

## 최신 결과 통합

- HE29 reference4/4와 packed canary는 완료되어 대기열이 비었습니다. HE32의394이력과 HE33을 재사용합니다.
- HH는 PHYS79가 최신이며 PHYS73 NCP raw는 회수 미확인입니다. 검색에서 안 나왔다는 사실을 실행 부재로 해석하지 않습니다.
- CR의 Git PR96보다 새 C22A/B는 백업에만 있었습니다.411payload를 복구하고 모든 신규 Python 코드·테스트·입력과 주요 결과를 PR97에 게시했습니다. 원 commit f03fdf71은 원 bundle의 identity이고 새 부분 게시 commit과 다릅니다.
- REC R3S 실제 NCP5작업 완료와 THERM01의8새 IVP, 별도 thermal-moments8을 구분했습니다. 잘린 THERM01 백업은 후속 정상 archive와157payload 검증으로 복구됐습니다.
- REI C2는214검사 완료입니다. PR221의42e44494는 전달 문서 추가이며 과학 source가 바뀌지 않았습니다. D9는 완료, D10은 별도 준비 노드입니다.
- VigilODE 외부1046heat 이력의 구조적 RHS절감 결과를 재사용합니다. 현재 port NCP 캠페인의 새 반환은 CLOSEOUT_DELTAS를 먼저 읽고 중복 제출하지 않습니다.

## 다음8개 노드

| 노드 | 목적 | 준비도 |
|---|---|---|
| N1 | Wire lifted error metric into an opt-in adaptive client and compare one paired trajectory | READY_TO_DESIGN |
| N2 | Dynamic Compton closure using the existing PR122 eight-case contract | READY_CONTRACT_EXISTS_NOT_RUN |
| N3 | Close the source-domain gap for low-temperature H excitation and collision processes | READY_SOURCE_RESEARCH |
| N4 | Bind D PI/RR thresholds, rate providers and captured-energy moments | READY_SOURCE_AND_ALGEBRA |
| N5 | Transport data and finite-mass baryon pressure exchange matrix | READY_THEORY_AND_SOURCE |
| N6 | Complete C3 coefficient-domain policy and event/Jacobian assembly | READY_BOUNDED_CONSTRUCTION |
| N7 | D10 zero-initial matter-stress generation on35 saved histories | READY_SAVED_DATA_THEORY |
| N8 | Integrate source-qualified thermal/charge/moment components in one closed pilot | WAITING_PHYSICAL_DEPENDENCIES |

N1–N7은 입력 의존성에 따라 병렬로 진행할 수 있고 N8은 선행 물리 입력을 기다립니다. 각 노드의 exact source, 첫 행동, 검증 기준과 예산은 DAG.json에 기록했습니다. 현재 샌드박스에는 Python/NumPy/SciPy/GCC/Node가 있으며 gfortran/rustc/cargo는 PATH에서 관측되지 않았습니다. 이를 모든 새 스레드의 환경으로 일반화하지 않습니다.

## 게시·보존과 제한

7개 저장소의 additive draft PR을 만들고 원격 HEAD 일치를 확인했습니다. 기존 branch를 강제 갱신하거나 merge하지 않았습니다. S0 조사와 S1 코드·근거를 Drive/Dropbox에 각각 저장했습니다. 원격 검증 수준은 ACK+metadata size이며 전체 원격 파일 재다운로드 검증을 새로 주장하지 않습니다. 원 full raw는 지정 원본 백업에 남습니다.

GitHub 전체 CI 통과와 scoped 과학 검증은 다릅니다. 기존 REI root cargo fmt 실패와 test skip 등은 최신 delta에 명시하며 이 작업을 CI green으로 표시하지 않습니다. 원전이 없거나 closure가 열려 있는 항목은 source/model 의존성으로 유지합니다.

재개는 HANDOFF_NEXT_THREAD_KO.md를 읽어 수행하면 됩니다. 사용자가 파일을 수동 다운로드할 필요가 없도록 모든 source pin과 provider object ID를 붙였습니다.
