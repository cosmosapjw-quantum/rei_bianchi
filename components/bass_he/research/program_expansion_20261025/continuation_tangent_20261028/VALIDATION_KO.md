# TANGENT13 R6/C6 — 실제 검증과 runner 교정 이력

## 실제 판정

R01 실행 pin `3beb35dc7dea7a60642497dc373c98e75ca07536`에서 단 한 번 실행한 targeted campaign은 **8 PASS, 0 FAIL, 0 ERROR, 0 SKIP**이다. 과학 certificate construction은 1회, predecessor campaign 재실행은 0회다. 후보를 다시 찾지 않고 저장된 algebra/inequality를 읽는 독립 certificate reader도 PASS다. 소스·입력 identity와 실행 명령은 `evidence/REPAIR1_EXECUTION_PIN.json`, `evidence/validation/repair1/START.json`에 있다.

| Geometry | 엄밀한 바깥쪽 십진 표시 | 정확한 유리수 폭의 근삿값 |
|---|---|---:|
| HEMISPHERES | [0.6184085476376238, 0.6184085476376327] | 8.794662532001996e-15 |
| CAPS | [0.0607568813452193, 0.0607568813452364] | 1.6987466706439967e-14 |

저장된 정확한 양 끝점과 폭은 `evidence/validation/repair1/SAVED_PLOT_DATA.json`이 권위다. 두 폭 모두 정확한 유리수 비교로 `<=1e-10`을 만족하고, 새 구간은 각각 QUARTIC12의 기존 최소값 구간 안에 있다. 위의 십진 양 끝점은 고정 16자리 격자에서 아래/위 방향으로 반올림했다. 이 표의 폭은 십진 표시 폭과 구별되는 정확한 fraction 차이의 근삿값이다.

## 실제로 실행한 8개 검증

1. 이차 다항식·근 bracket·도함수 조건 및 잘못된 bracket 거부.
2. 정확한 3×3 선형계 해와 특이계 거부.
3. EXFOR와 독립적으로 만든 square/dual 예제의 정확한 최솟값 1/4.
4. 음의 coefficient를 포함한 moment interval의 수동 기대값.
5. 원본 EXFOR와 predecessor saved input identity 및 재사용 outer vertex 제약.
6. 실제 두 dual의 비음수 multiplier·잔차 0 및 교란된 certificate 거부.
7. 실제 square witness와 네 contracted window 및 위반 witness 거부.
8. 새 bracket의 순서·폭·기존 bracket 포함·십진 반올림 및 잘못된 폭 거부.

정확한 unittest 이름과 실행 출력은 `evidence/validation/repair1/stderr.log`, 집계는 `TEST_REPORT.json`, 별도 reader 판정은 `CERTIFICATE_READER.json`에 보존했다. 8개라는 수는 중복된 assertion 수가 아니라 실제 unittest method 수다.

## 최초 실패와 진단에 따른 교정

최초 S05 실행은 worker output이나 과학 control을 만들기 전에 중단됐다. runner가 namespace-local child PID를 host `/proc`의 PGID와 비교하여 다른 host process group의 누적 CPU 711.220077 s를 귀속한 것이 원인이다. 이 수치는 실제 TANGENT13 CPU가 아니다. 실제 full runner+waited-child CPU는 0.045071 s, wall은 0.0060649999941233546 s였으며 child exit는 -9, control 실행은 0개다. 원본 `evidence/validation/initial/`은 수정하지 않았다.

첫 진단 대안은 parent-children proc 파일을 요구했으나 해당 host가 그 interface를 제공하지 않아 실패했다. 과학 imports/calls는 0이며 그 진단의 측정 불가능한 CPU/wall은 null로 보존했다. 이를 성공으로 바꾸지 않았다.

최종 교정은 `setsid` 이후 child가 자신의 local PID/PGID와 `/proc/self` host PID/PGID를 exec 전에 기록하고, parent가 이 handshake를 검증하여 host group만 측정하는 것이다. 종료 신호는 local process group에 보낸다. 최종 CPU는 monitor와 독립적으로 full `RUSAGE_SELF`와 waited children을 합산한다. 과학식·입력·정밀도·producer·reader·8 controls·plotter는 변경하지 않았다. 두 번째 과학 없는 진단이 CPU 0.067687 s, wall 0.13149636599700898 s, exit 0으로 통과했다.

독립 nonauthor 심사는 이 진단과 source를 읽어 `PASS_SCOPED_REPAIR_PREEXEC`로 판정했다. 실제 게시·ref/parent/tree readback 및 두 provider 백업을 갖춘 R01에서 local source 10개 identity를 대조한 뒤 한 번의 targeted campaign을 허용했다. 이는 같은 실패를 맹목적으로 반복한 것이 아니라 관찰된 namespace 기작을 교정한 실행이다.

## 자원과 이력 해석

| 실행 | Full runner + waited children CPU(s) | Wall(s) | 결과 |
|---|---:|---:|---|
| 최초 science launch | 0.045071 | 0.0060649999941233546 | monitor 오류, controls 0 |
| Targeted repair1 campaign | 0.17276599999999998 | 0.16480660199886188 | 8 PASS, construction 1 |
| 두 science launch 누적 | 0.217837 | 0.17087160199298523 | 원래 CPU120/wall300 범위 안 |

Targeted cap은 CPU119 s / wall299 s / AS768 MiB / 1 thread다. 실제 최대 child RSS는 16232 KiB다. 위 누적값은 과학 없는 별도 runner diagnostic 비용을 포함하지 않으며, 성공 diagnostic 비용은 앞 절에 별도 제시했다. unittest 내부 0.026 s와 tool command duration은 full runner CPU 또는 wall을 대신하지 않는다. 원격 Wolfram CPU/wall은 null이다.

`RESOURCE_RESULT.json`의 `rerun_count:0`은 그 launcher invocation 내부의 자동 재시도 횟수다. 프로젝트 전체 이력은 **최초 launch 실패 1회 + 진단된 targeted retry 1회**이며 science repair reserve는 **0**이다. 선행 EXFOR11·QUARTIC12·HARMONIC10·KINEMATIC08·PHOTON05의 성공·실패·partial 기록은 그대로 유지한다.

## 독립 검토와 admission

사전 proof/source/repair review와 실제 saved output review는 동일한 nonauthor 한 pass의 연속 단계다. 실제 출력 심사 근거는 `review/ACTUAL_RESULT_REVIEW.json`에 기록한다. 이 단계의 work product 완료와 최종 local node admission은 구별한다. Saved-only plot, 최종 결과 보고, C9 admission이 끝나기 전 과학 DAG 표기는 **12/17**, 중앙은 **28/88, HE delta 0**이다.
