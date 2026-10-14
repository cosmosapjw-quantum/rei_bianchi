# BRIDGE05 BOXJOIN: 선언 출력계획과 실제 cohort parent-box 연결

판정: FIXED_STAGE_PARAMETER_ROOT_JOIN_VERIFIED__ENERGY_PARAMETER_OPEN.

첨부 BRIDGE04 OUTPUT의 첫 T0 public macro [0,1.25e9] proper seconds에서, 원 CharacteristicRay::pullback, primary_stage_step_conservative, primary_stage_root를 실제 실행했다. 9개 source subflow와 birth6개, packet1->7이며 이전 gas/photon parent intervals를 지우지 않고 이어받았다. 원격 BRIDGE02 인계는 먼저 읽었고 실제 parent-box transaction을 다음 작업으로 남긴 상태였다. 동일 이름의 다른 artifact를 합치지 않았다.

## 판정의 정확한 범위

PrimaryBox는 gas4와 photon count intervals만 받는다. Energy, pre-evaluated sigma, stage nH/H/dt 및 birth times는 고정 f64 literal이다. 이번 root는 그 조건 아래 incoming gas/count family에 대한 포함이다. Non-degenerate energy interval은 ENERGY_PARAMETER_BOX_UNSUPPORTED로 거절한다. 연속 characteristic이나 방출 quadrature 오차를 root width에 포함하지 않았다.

Birth count box는 binary64 source rate와 cell endpoints의 정확한 S*(r-l)/2 및 저장된 point weight를 감싼다. 이상적인 Gauss abscissa timing uncertainty는 포함하지 않는다. Raw root box와 conservative point의 hull을 다음 parent로 넘겨 두 대상을 모두 보존하며, 다음 source는 그 전체 parent를 다시 검사한다.

원 S0/FT03 HG CaseA HHe CI/RR/두 DR, prescribed H=1e-14/s,nH0=1e-4cm^-3,fHe=.083,gas(.9,.3,.6),w0=13.620772387478219eV/H,13.7eV .05photon/H 및 source5e-15/H/s를 유지했다. 새 lowT/HH/RCT/CR/Peebles provider는 없다.

## 실제 결과

첫 출력 gas point는 (.9001242751942737,.30000028035899995,.5999999439072546,13.62033515372819eV/H)다. 부모 BRIDGE04 저장 first-output gas와 float64 bytes가 같다. 부모 이력을 다시 실행하지 않았다.
최대 macro root q=1.8965372620884808e-15. HII box 전체폭1.4654943925052066e-13, thermal w 폭2.042810365310288e-12eV/H. Exact-rational readout의 온도는 [49995.4465086530528104...,49995.4465086648752629...]K, 전체폭1.182245255499541e-8K다.
Number ledger residual8.816043070955293e-17/H, energy+work residual-1.3322676295501878e-15eV/H. 장부의 point 검증이지 전에너지 family interval이 아니다.

같은 gas/step에서 13.599999999999998eV와13.6eV는 한 ULP 차이지만 HII root point가5.93446648271545e-5 다르고 두 root boxes가 겹치지 않는다. HI sigma가0에서6.346296358990503e-18cm²로 바뀐다. 이것은 원 point API의 버그가 아니라 cutoff를 가로지르는 energy family를 point box로 대체할 수 없다는 반례다.

고정gas의 J_s=p0*h*k_s/(1+h*k)에 대해 dJ_s/dE=p0*h*[k_s'*(1+h*k)-h*k_s*k']/(1+h*k)^2, dA_s/dE=J_s+E*dJ_s/dE, dQ_s/dE=J_s+(E-chi_s)*dJ_s/dE를 검산했다. Energy lift는 sigma뿐 아니라 heat의 explicit energy도 포함해야 한다. Parameter branch 분할을 물리 photon 복제로 바꾸지 않는다.

## 검증과 실패

최종 science1process/13root calls, 독립4gas BEroots29개(그중16개 parameter samples),297scalar 비교. 최대gas차2.60837866245e-16,독립BEresidual2.41675371312e-16,eventrelative3.48502385906e-15. Unit8개 중energyguard1개만red/green,나머지7개tests-after. Macro 실패시 birth/box/ledger/cursor를 전부 되돌리는 테스트 포함. Symbolic4,exactevent64,analyticenergy37점도 확인했다. Native scientific modules13개는 불변이다.

6개 명령을 fresh folder에서 재현했고, exact rational output checker를 따로 추가 실행하여 기록된7명령은 모두exit0이다. 새 reproduce.py는 같은7명령을 순서대로 실행한다. Pilot+freshscience는2process/26roots/58independentroots다. 새IVP/Cargo/fullpaired_trial/과거campaign/부모증명 실행은0회다.

첨부 Rust archive는 tar/xz 끝부분 무결성검사에 실패했다. 이미 추출된 rustc1.94.1/hoststd의 작은compile/run과 실제 science 실행은 성공했으나, archive전체정상/공식서명/정상fullrestore로 표시하지 않는다. 새wrapper State 이름 충돌은 JoinState로 고쳤고 실패로그를 보존했다. 원 물리식이나 tolerance를 바꾸지 않았다.

## 다음과 재현

다음 FT_SPEC_BRIDGE06_PARAMETRIC_ENERGY_LIFT_FIRST_SUBFLOW는 첫source구간 하나에서 energy/sigma/heat의 parameter-family inclusion을 수행한다. 현재 fixed-literal root 성공을 그 family에 승격하지 않는다. 원 remote owner가 갱신되면 먼저 수신한다. Canonical local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD를 보존한다.

전체 REPORT_KO.md, source13개, native 실행binary/stdout, 독립검사기와실패로그는 ARCHIVE.json의 ZIP에 있다. 재현: python reproduce.py --output NEW_DIRECTORY --rustc /path/to/rustc . Network/Cargo/전체history없음. Compilerarchive/font는 포함하지 않는다.

일반 검증수치 배경: Rump2010 Acta Numerica19, DOI10.1017/S096249291000005X. 실제 수치와 범위는 이 연구의 저장 증거이며 physical fit 정확도를 새로 승인하지 않는다.
