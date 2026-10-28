# 다음 선택 결합: H1 일차전자 source에서 열화·전달까지

## 시작점과 범위

현재 채택된 결과는 `REI-GRID044-ENDPOINT-BINDING-01`의 순간 연산자이다. 다음 단위 후보를 `REI-H1-PRIMARY-DEGRADATION-BINDING-01`로 명명한다. 이 문서는 입력·유도·검토 범위를 정하며 새 적분·IVP·새83·NCP의 실행 허가나 예산 초기화를 포함하지 않는다. 게시·백업 자동화에 대한 owner 승인은 유지된다.

먼저 같은 z=2 endpoint의 **H1_0→H1_1+e_fast** 사건 하나를 선택한다. 이미 채택된 모든 다른 event source는 보존된 입력으로 둘 수 있고, 새 열화 claim은 이 H1 channel에만 한정한다. Neutron·tritium·nuclear·molecular의 전체망이 이 유한 채널 검토의 선행 AND gate가 되지 않는다.

## 필요한 실제 입력

1. 같은 stellar/external_IGM continuum, 같은 reference와 frame에서 energy-resolved primary source를 공급한다. Stationary-target/no-recoil 근사에서는 photon measure에 sigma(E_gamma)와 delta(E_e−E_gamma+chi_HI)를 적용하여 energy source를 구성할 수 있다. 그 원래 measure를 사용해야 하며 저장된 Gamma/P/K 세 모멘트만으로 형상을 선택하지 않는다. 동일한 source moment로 적분되는지 확인한다.
2. 선택 HE 모형의 실제 대상 species·charge·온도·밀도·electron energy 범위에 맞는 stopping 또는 collision provider, secondary outcome, 잔여 fast energy와 thermal/ionization/excitation 분배를 제공한다. Provider 값·단위·범위·오차·원문 출처를 함께 고정한다. 현재 HE101/C8의 미채택 물리 provider나 소진된 reservation을 채택·재승인된 것으로 취급하지 않는다.
3. Isotropic energy-only degradation을 고르면 그 대칭을 명시하고 energy deposition까지만 claim한다. Anisotropic transport나 momentum transfer를 고르면 실제 photon/primary angular measure와 differential outcome·recoil을 추가한다. 임의의 isotropic 또는 monoenergetic spectrum을 실제 공급자로 간주하지 않는다.
4. BASS를 새 transfer에 연결할 때 normal tetrad·metric(-+++)·proper second·SI source 단위를 유지한다. 기하의 signed stress stock과 새 J m^-3 s^-1 transfer를 구분한다. Photon loss, binding gain, fast reservoir, thermal reservoir, external feed가 중복 없이 이동해야 한다.
5. 연속 진화를 선택하기 전에 확장 상태·source의 모든 Jacobian block, finite domain, boundary policy, native runtime/witness 증거, error-control functional을 VigilODE client에 고정한다. 현재 point-domain [0,0]과 caller-asserted witness는 연속 domain certificate가 아니다.

## 정규화와 소유권

Default reference는 현재와 같은 n_ref0 a^-3 bookkeeping density이며 n_ref0=0.19078721280843758 m^-3, a_today=1이다. 실제 source injection은 source S에 포함한다. 다른 physical reference를 선택한다면 R과 그 미분을 함께 정의하여

\[
F=(S-xR)/r,\qquad dF=(dS-Rdx-xdR)/r-Fdr/r
\]

를 사용한다. H1 photoionization event는 기존 owner를 유지하며 새 source template이나 HE receiver가 동일 사건을 다시 소유하지 않는다. HE는 기존 fast-electron reservoir에서 에너지를 받아 열화 channel별로 이동시키고, 이미 REC에서 계수한 photon loss와 binding energy를 다시 만들지 않는다.

## 실행 전 고정할 항목

입력 수신 단계에서 해당 provider의 최신 AGENTS, HEAD, 병렬 반환과 백업 상태를 다시 확인한다. 원본 파일의 정확한 식별자와 유효범위를 선택 input에 연결한다. 저장 source와 provider가 필요한 범위에서 일치하면 다음과 같은 작은 검증 단위를 먼저 고정할 수 있다.

- Energy-resolved source의 zeroth/first moment와 기존 H1 Gamma/K의 일치.
- Source별 energy ledger의 부호·단위·reservoir 소유권.
- 선택 HE provider의 지지집합, positivity, rate/energy scale와 actual target-state 일치.
- 새 quotient/Jacobian block의 독립 미분 비교와 빠진 transfer에 대한 판별 control.
- BASS transport를 선택한 경우에만 actual angular measure·four-force·stress-rate 비교.

이 단계의 CPU/wall/memory/attempt cap, compiler·solver·입력·tolerance, 실패 후 한 번의 표적 수정 범위는 **아직 동결되지 않았다**. 새 unit에 대해 고정하고 independent pre-execution review를 거친 뒤 진행한다. 기존 GRID044/ANGTHERM02/new83 예산 잔여분은 이 새 단위의 예산이 아니다. 현재 science allowance의 잔여량도 자동 재실행 허가가 아니다.

## 채택 후 다음 전이

Selected H1 degradation PASS → 해당 source와 deposition output을 consumer에 실제 연결하고 독립 검토한다. 그 뒤 실제 BASS transfer와 full state derivative가 준비된 선택 모델에 한해 닫힌 gas+radiation+geometry pilot의 L4 계약을 다시 고정한다. L4에는 live H/shear feedback, 선택 model-domain의 energy/charge/census, state-scaled 독립 refinement, external reservoir의 명시가 필요하다. Whole-network completion, 관측 calibration, universal-Bianchi completion은 이 선택 단위와 별개다.

## 재개용 지시

현재 branch의 HEAD와 AGENTS를 먼저 읽고 이 디렉터리의 SCENARIO, SCIENTIFIC_DECISION, REPORT_KO, SOURCE_MANIFEST, RESOURCE_RECEIPT, delivery receipt 및 중앙 DAG를 확인하라. PR219 bootstrap·기존83·GRID044·PR221의 결과와 미지 비용·조건부 범위를 그대로 재사용하라. 새83 전구간, NCP, 기존 suite/IVP를 자동 실행하지 마라. 먼저 같은 H1 channel의 실제 energy-resolved source와 선택 HE physical stopping provider가 도착했는지 조사하라. 미제공이면 부족한 파일·물리 범위를 특정하고 숫자를 만들어 채우지 마라. 각 새 단위의 독립 검토, expected-SHA non-force publication, source ZIP, Dropbox·Drive ACK, DAG 갱신을 유지하라.
