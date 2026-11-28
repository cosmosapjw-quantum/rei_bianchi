# THEORY06 재현 계약

현재 user turn에서 필요한 새 short scientific checks는 이미 완료됐다. 이 문서는 이후 실제 재현에 필요한 입력과 해석을 기록한다. 파일 hash나 serialization을 위해 완료된 science를 재실행하지 않는다.

## 입력과 환경

먼저 SCIENTIFIC_CONTRACT, source_map/CURRENT_SOURCE.json, SOURCE_FUNCTIONS 및 네 proof를 읽는다. Parent는 BASS_HE PR33 head `94a34d09ad5810a675b556561e5593b279d30448`, rate source는 rei_bianchi PR114 head `a5c958c414dea41216b445c05f58df837f05cacb`다. Source decimal을 exact real analytic function으로 해석한 수학적 certificate와 실제 native float 실행을 구분한다.

Wolfram batch 입력의 code는 각각의 CALL_INPUT.json에 완전히 보존돼 있다. Primitive와 combined final은 Wolfram Language 15.0.1 Linux-x86-64로 수신됐다. xAct 최종도 같은 kernel version과 실제 xTensor 1.3.0을 반환했다. Rate call의 kernel metadata는 미수신이므로 같은 버전으로 실행됐다고 단정하지 않는다.

| 독립 새 batch | exact call input | 기대된 과학 출력 |
|---|---|---|
| Primitive | evidence/PRIMITIVE_DIFFERENTIAL_CALL_INPUT.json | 17/17, scalar inverse·whole-cube bounds |
| Actual rates | evidence/RATE_ENVELOPE_CALL_INPUT.json | 20/20, rational-power 76·exp 5 내부 witnesses |
| xAct final | evidence/XACT_CONTINUATION_CALL_INPUT_v2.json | 8/8, tensor residual 17개 모두 0 |
| Combined full source | evidence/FULL_SOURCE_CERTIFICATE_CALL_INPUT.json | 12/12, H=500000000, exact HB와 q 및 7행 majorants |

xAct wrapper는 공식 `https://xact.es/download/xAct_1.3.0.tgz`를 받아 입력에 적힌 SHA256 guard와 비교한 뒤 로드한다. xPerm external backend는 false다. 입력을 실행하는 환경이 package나 network를 제공하지 않으면 그것은 환경 제약이며 tensor identity의 반례가 아니다.

## 결합 입력 확인

Combined batch에 삽입된 rate cap JSON은 RATE_ENVELOPE_RESULT의 coefficient/derivative/kinetic/sigma 여섯 field 묶음이다. SHA256 `ef9fcb4d6d18d388bc45ae71844b1f8d3c284e529185898d195cdf28add69546`인 rate result를 소비했다. Primitive 소비 경계는 L_T=1400 K, L_beta=3e-6, L_gamma=2e-7, L_delta=4e-6이며, 그 전제인 whole-cube inclusion을 따로 읽어야 한다. 미분 majorant 산술만으로 domain inclusion을 추정하지 않는다.

## 원래 실행과 이후 수정의 구별

원 CALL_INPUT과 raw는 실행 당시 상태 그대로다. 실패한 xAct v1도 별도로 보존돼 있다. Final wrapper의 metadata append는 이후 재현 때 두 인자 형태 `AssociateTo[result, {rules...}]`나 `Join`으로 고칠 수 있지만, 원 입력 파일을 덮어쓰거나 수정 코드를 현재 actual input이라고 부르지 않는다.

Combined result의 긴 JSON 일부가 생략된 원응답도 유지한다. Normalized에는 수신한 exact core certificate와 7행 vector를 보존하고 네 미수신 scalar를 null로 남겼다. 그 값이 필요한 이후 consumer는 수신된 B,q와 정식으로 exact scalar를 도출하고, '원 kernel이 해당 field를 반환했다'고 기록하지 않는다. 새로운 재현의 출력은 compact core JSON과 보조 vector로 나누면 같은 capture 문제를 피할 수 있다.

## Native 연결

Native source 구현, point/RHS/ODE/history campaign은 이 THEORY 재현 경로에 들어 있지 않다. CODING_CONTRACT의 adapter가 구현된 다음에는 실제 source/input/precision/bounds/Jacobian/owned events/finite ledger/residual의 identity를 함께 기록하는 별도 CODING 검증이 필요하다. 현재 8 Picard update의 값은 theorem error estimate이며 그 native 증거를 대신하지 않는다.
