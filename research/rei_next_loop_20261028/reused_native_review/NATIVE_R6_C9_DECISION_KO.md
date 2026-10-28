# finite_thermal_endpoint_20261028: 실제 native R6·C9 감사 결과

## 확정 결과

고정 source b77c7b8d45c48a7e4722e733309430d5ba668b0d에 대한 실제 native reviewer의 두 단계 검토와 발견사항 F1의 한 차례 정정·표적 검증을 완료했다.

| 단계 | 독립 reviewer의 최종 판정 |
|---|---|
| R6 | PASS_SCOPED_R5_AND_CORRECTED_SOURCE_REPRESENTATION |
| C9 | PASS_SCOPED_REPRESENTED_INPUT_AND_FROZEN_SOURCE_DIAGNOSTIC |

완료 집계는 이론 6/10, 코딩 9/10, 합계 15/20이다. 이번 증가분은 R6와 C9 두 단계다. 작업 33/88, 중앙 마지막 관측 28/88, 88 IDs/17 edges, canonical delta 0을 유지한다. 81-check와 158-check는 같은 C8의 별도 보존 근거로 사용했고 합산하지 않았다. atomic-storage의 과거 20/20은 별도 단위다.

실제 REI 온도 갱신, native25, physical radii는 null이다. L4_ready=false, global_physical_completion=null을 유지한다. 단계 완료는 고정된 조건부 caloric 구성과 표현된 source 진단에 대한 독립 검토의 완료를 뜻한다.

## 실제 실행 정체성과 blind 범위

독립 reviewer의 native task ID는 /root/finite_thermal_native_blind_review이다. collaboration.spawn_agent를 fork_turns=none으로 실제 호출했고, list_agents와 reviewer의 실제 응답으로 생성·실행·결과 수집을 확인했다. 외부 GitHub 봇, controller 역할극, Python subprocess 또는 CAS를 이 reviewer로 대신하지 않았다.

호스트는 fork_turns=none이 부모의 주변 대화 이력을 전달하지 않는다고 명시한다. Reviewer는 자신의 입력에서 작업 지시·환경·공통 실행 지침만 보이며 부모의 실질적 대화나 이전 감사는 보이지 않는다고 보고했다. 숨은 context 전달 trace, backend 세부 모델 ID와 서버 process ID는 API에서 관측되지 않는다. 공유 filesystem과 도구 접근은 남아 있으므로, 문서화된 이력 비상속과 실제 지킨 자료 공개 경계를 기록한다. 완전한 OS 격리나 독립적으로 입증된 숨은 context 차단이라고 주장하지 않는다.

초기 packet은 R5의 과학적 본문 전체, 필요한 R3/R4 정의와 구성, source-bath 보충 유도, 원래 finite_thermal.py와 runner, atomic_storage.py, BASS producer 원문, source 입력 정의와 encoding을 포함했다. 이전 판정·완료 집계·선별된 결함 목록·보존 테스트·실행 결과는 보류했다. 원문 코드에 내장된 control 정의, PASS 문자열, 오래된 pending 문구, source witness의 해석은 삭제하지 않았으며 READ_EXPOSURE_LOG.json에 노출을 기록했다. 원문 발췌의 원래 구간과 변환은 initial_packet/MANIFEST.json에 있다.

Reviewer가 PROVISIONAL_R6_C9.md를 먼저 저장한 뒤 SHA256 4f885cc610b08174d466548fe68dbc0bbb491ed6a44460901be6ef6fc59d9b5e를 확인했다. 2026-10-28 15:19:19 KST에 PHASE2_RELEASE.json으로 테스트와 raw 근거를 공개했다. 공개 후 판단은 POST_DISCLOSURE_R6_C9.md에 별도로 저장했다. 두 보고서와 두 읽기 로그는 정정 단계 뒤에도 변경되지 않았다.

## F1: source 온도 관계식의 표현 잔차

독립 검토는 source-bath 보충 문서의 다음 관계를 구분해야 한다고 지적했다.

    T_a^E / T_native = k_src * EV_src / k_B_SI

이 식은 theta_a = k_src*T_native인 반올림 전 정의 관계에 적용된다. 실제 저장된 theta_a, k_src, T_native를 각각 binary64에서 정확한 유리수로 올리면 곱셈 반올림이 남는다. 다음 잔차를 정의한다.

    delta_theta = theta_a - k_src*T_native.

그러면 표현된 입력에 대한 정확한 식은

    T_a^E / T_native
      = k_src*EV_src/k_B_SI
        + delta_theta*EV_src/(k_B_SI*T_native)

이며 동치인 온도차 식은

    T_a^E - T_native
      = (k_src*EV_src/k_B_SI - 1)*T_native
        + delta_theta*EV_src/k_B_SI

이다. theta_a의 단위는 eV, T_native의 단위는 K, k_src는 eV/K, EV_src는 J/eV이다. k_B_SI=1.380649e-23 J/K를 유지한다. 두 번째 식의 각 항은 K이다.

Reviewer는 테스트를 보기 전에 binary64 0.1*3을 반례로 구성했다. 정확히 올린 피연산자의 곱과 반올림된 곱의 차이는 2^-55이다. 이후 공개된 실제 C7 stdout에서도

    delta_theta = -393372660608921 / 40564819207303340847894502572032 eV

가 확인됐다. 실제 입력에서 생략되던 Kelvin 항의 표시값은 약 -1.125334774753963e-13 K이다. exact num/den 값은 correction/STDOUT.json에 보존했다.

finite_thermal.py의 source_temperature_bridge는 이미 theta_minus_kBoltz_native_eV를 반환하고 독립된 theta_eV에서 energy_temperature_K를 계산한다. 따라서 실제 수정은 source 표현 관계식에 대한 governing additive correction 한 건이다. 핵심 코드와 원래 source 값을 변경하지 않았다.

correction/verify_representation_relation.py는 원래 literal packet과 저장된 C7 bridge만 읽고 Fraction으로 정정 비율식·온도차 식을 독립 조립했다. 원래 consumer나 테스트 suite, C8 연구, provider, CAS, IVP는 실행하지 않았다. 정정된 exact 관계가 저장된 값과 일치하고 constant-only 관계가 이 입력에서 성립하지 않음을 확인했다. 한 checker 실행의 exit는 0, stderr는 비어 있으며 complete-child CPU 0.026759 s, wall 약 0.028995485 s, max RSS 10112 KiB였다. 판정은 exact 식과 값의 대응에 근거한다.

Native reviewer가 정정식·checker·원출력·process 기록만 다시 읽고 FINDING_CLOSURE_R6_C9.md에서 F1을 닫았다. 전체 감사나 suite를 다시 수행하지 않았다.

## 확인한 수학·코드 대응

R5의 양의 정의역에서 D=Na+deltaN, E=cv*Na*Ta+Q+W, T_hat=E/(cv*D)는 직접 대수로 지지됐다. saved endpoint의 r0와 r_balance가 aggregate rE에 한 번씩 포함되고, discrepancy의 공통분모 식이 구현과 일치한다. cv를 포함한 JVP와 공통 R·b 정규화의 cancellation은 각 좌표의 미분항을 보존한 뒤 성립한다.

오차 bound는 공급된 eN<D를 요구한다. 양의 직사각형 interval에는 추가로 E-eE>0이 필요하며, 구현이 두 조건을 구분한다. Affine polytope와 일반 monotone EOS 결과는 선언된 이론 범위에서 지지됐고 별도 구현으로 승격하지 않았다. Local-V1의 unweighted count/Q/W는 R01로 환산하며 weighted heat moment의 R01^(5/3)와 구분한다.

C9는 테스트의 고정 유리수 기대값, 독립적인 공통분모/JVP 항등식, 실제 gas slot 선택, 별도 저장 전자·stock 잔차, typed encoding과 unknown physical radius 처리를 읽었다. 실제 원본 3554206-byte BASS 입력, 8281-byte literal packet과 code/test identity를 대조했다. C7 checker는 finite_thermal을 import하지 않고 raw 입력에서 count·gas energy·잔차를 다시 구성하는 보존 근거다.

두 C8 연구는 공통 C7 stdout을 사용하는 서로 다른 저장 데이터 분석이다. rounded endpoint에서 나중에 잔차를 만들면 이미 소실된 정보가 복원되지 않는다. 정확히 보존한 잔차를 나중에 반올림해 전달하는 경로는 다른 정보 집합을 이용한다. Reviewer는 이 차이를 원본 코드와 precision rows에서 확인했다. 81와 158이라는 수치 자체로 과학적 수용을 결정하지 않았다.

## 실제 읽은 범위와 남은 근거 한계

세부 파일·구간은 READ_EXPOSURE_LOG.json, PHASE2_READ_EXPOSURE_LOG.json 및 closure 보고서에 보존했다. 초기 읽기는 finite_thermal.py 전체, run_once.py 전체, R5 §§1–7, R3 정의, R4 구성, source-bath §§3–7 및 manifest에 명시된 producer 원문 전체다. 공개 뒤에는 test_finite_thermal.py 전체, C6 로그, C7 checker와 exact stdout의 필요한 JSON paths, 두 C8 코드와 해당 raw result arrays, 원본 transaction에서 실제 소비하는 finite_owners와 clock·encoding 필드를 읽었다. 큰 JSON을 parsing했다는 이유만으로 모든 의미 필드를 검토했다고 적지 않았다.

과거 He 분기의 history.c·hyrec_params.h와 원래 witness CSV 비교를 새로 재구성하지 않았다. upstream SOURCE_OPERANDS/TUBE/FINITE_TUBE_INPUT_SLICE 전체의 모든 수치 전사를 독립 재검증했다고 주장하지 않는다. 이것은 F2 coverage limit로 유지된다. 현재 producer가 명시하는 inert-He source 모델은 코드와 실제 transaction으로 직접 지지된다. 미열람 범위는 이번 conditional source-caloric 진단보다 넓은 history·물리 admission에 관한 한계다.

기존 C6–C8 capsule 네 개와 필요한 원본 source 하나를 기존 저장본에서 복원해 byte identity를 확인했다. 과거 계산, 116-file 묶음, source ZIP을 재생성하지 않았다.

## 감사 후 소스 확인과 다음 선택

실제 native post-disclosure 보고서가 반환된 뒤 PR240, source owner PR205, 관련 restart PR212의 현재 head와 필요한 파일만 확인했다.

- REI PR240 head는 게시 전 b77c7b8d45c48a7e4722e733309430d5ba668b0d이며 finite_thermal.py blob 880a074f793ba6bb3aa3e1d7958d8116eb239c0e가 유지됐다.
- BASS PR205 head 1e8d7ecc90a304fcd1ddf3ea9a98ad14f88248a0의 원본 transaction blob은 a9ea559f123da6c8f1fe070139bc80145d4582fc로 유지됐다.
- BASS PR212는 f834101d3292f304681349db5d435c6f0c6b559e까지 진행했다. 실제 새 status/theory 파일에는 clock/model mismatch bound와 restart guard 보강이 있으며, 해당 별도 단위의 R6·C9는 여전히 held이다. 이 결과를 이번 frozen source나 physical radius로 대체하지 않는다.

다음 선택은 같은 단위의 R7이다. 검토된 표현 조건 아래 기존 C7·C8 판별 근거를 재사용해 이론 단계의 근거로 채택하는 작업을 선택했다. AUTO_NEXT_NODE=false에 따라 시작하지 않았고 추가 완료수를 올리지 않았다. 전역 source census나 중앙 DAG 재집계도 하지 않았다.

## 비용과 보존

과거 primary-only 부분 하한 16.323598885 CPU s와 presentation 부분 하한 48.263016494 CPU s를 유지한다. 새 표적 검증의 complete-child 0.026759 s는 별도 실제 debit이다. preparation·supervisor·I/O·원격 작업·기타 미측정 비용은 UNKNOWN_NOT_ZERO이며, 이 값들을 현재 전체 비용의 정확한 합계나 전역 budget PASS로 표시하지 않는다.

과거 C6·C7 consumed authorization 및 C8의 닫힌 allocation을 재사용·재개하지 않았다. 새 CPU 1 s/wall 10 s/memory 256 MiB 한정 allowance는 1회 실행 뒤 닫혔고 carryover는 없다. Main 595.225063/600 NO_MORE_IVPs와 미승인 ZIP 제안은 유지된다.

이 보고서는 과학적 판정과 원문 보존의 index다. 실제 Git 게시 commit과 두 provider ACK는 후속 FINAL_DELIVERY_ACK.json에 기록한다. 그 ACK를 얻기 전에 저장 완료를 주장하지 않는다.

