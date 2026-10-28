# 현재 DR C6–C10에 적용한 프로젝트 정책과 실제 읽기 원장

단위: `rei_dr_finite_temperature_enclosure_20261028`  
기록 작성자: `/root/finite_thermal_blind_reviewer`  
역할: 정책 읽기·적용 범위 정리와 전달 준비 지원. 이번 기록은 새로운 scientific review나 runtime acceptance가 아니다.  
읽기 및 기록 날짜: 2026-10-28 UTC.

## 1. 실제 읽은 원본

아래 네 파일을 실제로 전문 읽었다. `nl -ba`의 전체 출력을 읽었고 출력 잘림이나 미독 부분은 없었다. 행 수와 바이트 수는 `wc -l -c`, SHA256은 `sha256sum`으로 확인했다. 같은 정책을 확인하기 위한 재실행, 추가 문헌 조사, 첨부 ZIP 복원은 하지 않았다.

공통 원본 디렉터리: `/workspace/scratch/cc0531120bc9/project_sources/`.

| 파일 | 실제 읽은 범위 | 바이트 | SHA256 |
|---|---|---:|---|
| `04-Adaptive-CMB-Code-Development-Protocol.txt` | 325행 전문 | 8705 | `8e1140b4922b7556970998465e0ce9126bf644bc108d9b78a73a2bb48027a1dc` |
| `05-Adaptive-CMB-Code-Research-Executor-DAG-Governed-Development-Mandatory-Dual-Audit-Plot-Driven-Adversarial-Loop.txt` | 373행 전문 | 12670 | `8c6d7bd933cd7a80057a10816e692c10816a41d560129b3e8470983d2be2f4a9` |
| `07-Figure-Residual-Error-Pass.txt` | 83행 전문 | 3315 | `37b64cd6d232b3525a838f2f23a05ca44aa99c6362f0a28b695397fbbffc8e22` |
| `08-Figure-Hostile-Audit.txt` | 116행 전문 | 5183 | `46b920c886549a228876ddb7b5651d1a213ff9ad4669843ea4afc3700b4f5bbc` |

04의 contract/code-path reconstruction, 제한된 수정과 검증, PHYS-MATH 및 PHYS-MATH-CODE 검토, 실제 그림 판독을 확인했다. 05의 DAG 선행 조건, 현재 작업에 맞춘 최소 적용, 하나의 다음 단계 선택, 과도한 multi-agent 기본 적용 금지와 종료 규칙을 확인했다. 07의 최종 잔여 오류 점검 및 미세 수정 범위, 08의 의미·가독성·배치 검토와 P0–P3 분류를 확인했다.

## 2. 적용 우선순위와 현재 범위

현재 사용자의 구체적 지시와 승인 범위, 이미 선택된 physmath-research-loop 1.0.0, 현재 고정 DR 질문과 실행 계약을 우선한다. 네 문서의 일반적인 연구·그림 검토 규칙은 이 범위에 필요한 항목만 적용한다. 이 기록은 닫힌 이론 증명이나 정적 검토를 다시 시작하거나, 새로운 전체 suite·reviewer tree·과학 캠페인을 만들지 않는다.

현재 질문은 고정된 실제 DR 세 행과 선택된 kinetic-loss 함수의 표현된 매개변수 기반 유한 온도 구간·log-temperature Taylor 결과다. 실제 source bytes, 최종 구현 identity, 저장된 원시 값, 실제 그림과 검토를 연결해야 한다. 물리 T/native25/radii, RR/Mao, 전체 native callback 반올림 오차, 원자 적합 또는 derivative 불확실성을 새로 채우지 않는다.

## 3. 현재 C6–C10에 필요한 의무

### 3.1 계약·코드·실제 실행 증거의 연결

최종 준비 identity와 실제 실행 소스 해시, 정확한 명령, 원시 stdout/stderr, 종료 상태, 실제 비용을 연결한다. README·주석·완료 문구나 테스트 개수만으로 검증을 대신하지 않는다. 이 DR 단위에서는 signed/clipped 비교, 구간 포함, Taylor 잔차와 상한, zero-step, 양성·underflow·구조적 부재 구분의 실제 출력이 중요하다. 준비된 oracle와 실제 scalar 값을 비교하고, 관측하지 않은 값을 만들어 넣지 않는다.

### 3.2 기존 이론·정적 검토의 재사용과 runtime 판단

R6의 D1–D5 및 binary64 양성 증명, F-ZERO/F-FAMILY/F-PLOT1의 이전 정적 검토는 보존한다. 실제 변경과 새로운 실행 근거에 필요한 비교만 이어간다. 정적 종료와 runtime acceptance를 구분하고, 실제 원시 결과를 읽기 전 C6–C9 완료를 추론하지 않는다. 새로운 이론 또는 구현 결함이 실제로 확인되지 않는 한 닫힌 검토를 반복하지 않는다.

### 3.3 그림은 실제 이미지와 저장 수치를 함께 읽기

생성된 SVG/PNG를 실제로 읽고 저장된 수치 및 의미와 대응시킨다. 파일 존재나 renderer exit만으로 그림 판독을 대신하지 않는다. 현재 패널에서는 signed/clipped 막대의 쌍별 정규화, 수치의 지수와 단위, Taylor 잔차/상한 비율, 각 h 표시를 확인한다. 서로 다른 행의 정규화 막대가 절대 크기 비교로 오해되지 않도록 하고, 진단 잔차 비율을 물리 적합 오차의 증거로 해석하지 않는다. 저장된 14919.863839279506 K의 interpolation-only 지위를 유지한다.

### 3.4 의미·가독성·배치 검토와 제한된 잔여 점검

08의 순서는 P0 의미 불일치, P1 겹침·잘림·축소 가독성, P2 배치, P3 미세 일관성이다. 캡션·축·단위·정규화·색·패널 관계가 실제 주장보다 강한 의미를 만들지 않는지 확인한다. 07은 수정 뒤 남은 오류와 semantic drift를 확인하는 제한된 최종 점검으로 적용한다.

기본 인쇄 폭 약 90 mm와 180 mm에서의 가독성 위험을 고려한다. 실제 하지 않은 인쇄·축소 검증을 통과했다고 쓰지 않는다. 이 가정이 자동으로 별도 렌더링 두 번이나 반복 그림 실행을 허가하지는 않는다. 먼저 실제 이미지에서 오류를 기록하고, 필요한 최소 수정만 현재 승인·예산·실행 계약에 맞춰 결정한다.

### 3.5 실제 결함에 따른 제한된 수정

기존 signed/clipped, 경계·zero-step, 구간 및 precision 비교 같은 구별력 있는 근거를 우선 사용한다. 일반 문서의 mutation·reference 예시를 이유로 새 grid sweep, CAMB/CLASS 전체 비교, IVP, 광범위한 리팩터링을 추가하지 않는다. 새 결함이 확인되면 failure 원인, 바뀐 소스 identity, 수정 범위, 필요한 targeted verification을 연결한다. 같은 상태를 근거 없이 반복하는 재실행을 정당화하지 않는다.

### 3.6 실제 단계와 전달 상태의 갱신

C10에는 실제 완료·실패·제한 상태, 원시 결과, 그림 판독, 독립 runtime 판단, 정확한 파일 identity 및 실제 provider ACK를 보존한다. 로컬 단위 단계 수와 원래 DAG·물리 완료를 구분한다. 현재 단위의 실제 판단 이후, 사용자가 요청한 최신 delta 조사 결과에 따라 다음 한 연구 질문을 선택한다. 이 정책 읽기만으로 다음 질문을 선정하거나 새 stage credit을 주지 않는다.

## 4. 역사적 문서 규칙과 현재 승인 구분

- 네 원문에는 수치 CPU 한도가 없다. 현재 22/62는 이번 사용자의 명시적 승인에서 온 권한이다. 과거 20/60, NOT_APPROVED 또는 실행 보류 문서는 당시 상태의 원본으로 남기고 새 승인 기록으로 현재 권한을 설명한다.
- 기존 CAS 관측량과 전체 예약, 다른 branch의 공통 상속 비용을 다시 더하지 않는다. 실제 실패한 실행과 계측·진단·수정의 비용도 관측 범위와 미관측 부분을 구분한다. 과학 출력이 없다는 사실이 CPU 비용 0을 뜻하지 않는다.
- 04·05의 일반적인 단계별 dual audit·plot loop는 현재 1.0.0과 구체적 작업에 맞춰 적용한다. 05 자체도 현재 TASK·DAG에 맞춘 최소 적용 및 안정된 validated/blocked 상태에서의 종료를 요구한다.
- CMB gauge/LoS/C_ell 등의 일반 항목은 실제 관련 부분에만 적용한다. 원자 DR 성분 검증에 별도의 전체 CMB 벤치마크를 추가하지 않는다.
- 단계 원본·캡슐·ACK 전달은 명시적으로 요청된 증거 보존 작업이다. 문서의 release 제한은 검증되지 않은 결과를 완성된 릴리스나 전역 물리 완료로 주장하지 않도록 적용한다.
- 07·08의 일반적인 심사 모드와 검증 질문 수는 별도 reviewer tree 생성 의무가 아니다. 실제 그림과 해당 claim에 필요한 제한된 검토를 수행하고 판단 이유를 남긴다.

## 5. 정책 기록 시점의 새로운 실행 상황 — root 전달 사실

다음은 이 기록의 작성자가 runtime 산출물을 직접 검토한 결론이 아니라, 이번 작업 지시에서 root가 제공한 현재 상황이다. 이번 기록 작업에서는 해당 실행·진단 파일이나 수정 wrapper를 추가로 읽거나 실행하지 않았다.

- `numeric attempt_01`은 과학 출력 전에 PID namespace 계측 오류로 중단되었다.
- Root는 `os.getpid()`가 5인 반면 `/proc/self/stat`의 PID는 474236이고, `NSpid`는 `474236 5`인 차이를 실제 확인했다고 전달했다.
- Root의 진단 원본 경로는 `execution/PID_NAMESPACE_DIAGNOSTIC_20261028.json`이다.
- Author는 host PID/SID handshake만 수정한 별도 wrapper와 `attempt_02` 경로를 준비 중이다. 이전 실패, 승인 및 소스 원본은 보존된다.
- Root는 이를 실제 진단 근거에 따른 한 차례 productive repair로 처리하고, 승인된 22/62 안에서 별도 실행 dispatch를 할 예정이다. 이 정책 기록은 그 dispatch를 대신하거나 추가 재시도를 허가하지 않는다.

이 상황에서 적용할 의무는 실패 증거와 비용을 남기고, 원인·최소 변경·새 소스 identity·새 attempt 경로·새 dispatch를 연결하는 것이다. 이전 실패를 삭제하거나 성공으로 바꾸지 않고, 수정 wrapper의 실제 실행 및 결과를 읽기 전 runtime 통과를 주장하지 않는다. 기존 과학 함수·oracle·이론은 이번 계측 수정만으로 변경된 것으로 취급하지 않는다.

## 6. 이번 작업의 행위 범위

이 기록 작업에서 수행한 것은 네 정책 원문의 전체 읽기, 파일 크기·행 수·SHA256 확인, 적용 범위 정리, 그리고 이 Markdown 파일 작성이다. 과학 코드 import/실행, CAS, IVP, test suite, renderer, ZIP 복원, 새 캡슐 포장 또는 외부 게시는 수행하지 않았다. 과학 실행 횟수는 0이며, 일반 파일·도구 작업의 미계측 비용을 0으로 주장하지 않는다.

실제 runtime 증거와 root의 단계 결정이 전달되면 그 결정과 원본을 보존하는 C6–C10 캡슐·원장 준비를 별도 지시에 따라 수행한다.
