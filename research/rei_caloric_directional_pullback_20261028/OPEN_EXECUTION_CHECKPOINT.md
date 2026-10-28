# 실행 재개 checkpoint — 수치 실행 전

Unit: rei_caloric_directional_pullback_20261028.
Branch: research/rei-caloric-directional-20261028.
Base: 3f299062a0d0d35c17f83a9e6081ca515e9d4c4c.
상태: R1–R10 complete; C1–C5 complete authored preparation; C6–C8 NOT_RUN; C9 static portion reviewed/runtime NOT_COMPLETE; C10 pending.
새 단위15/20; 원래 DAG33/88, 중앙28/88,88 IDs/17edges,delta0.

## 완료된 것

`THEORY_AND_CONTRACT.md`의 전체 구성과 `/root/current_repo_census`의 실제 독립 유도·static review를 재사용한다. 새 발견사항이 없으므로 예방적 수정이나 추가 review cycle은 수행하지 않는다. 식·source identity가 달라지면 영향받는 부분만 검토한다. 준비 파일을 작성했지만 import/compile/test/plot/evaluator 실행은 없었다.

## 다음 실행 전 확인

1. 이 branch의 전달 receipt와 source identity를 확인한다. 기존 source census나 닫힌 suite 전체를 반복하지 않는다.
2. 현재 사용자의 새 수치·presentation allowance 승인을 확인한다. `--execute-authorized` flag 자체는 승인이 아니다. 원래 기준10/30, PR242 종료 상태와 누적 debit을 유지한다.
3. `execution/PREPARED_IDENTITIES.json` 및 unchanged dependency blob을 대조한다. 입력은 exact manufactured A–G, optional H는 NOT_SELECTED다. 실제 recipient EOS나 물리 callback derivative를 추가하지 않는다.

## 승인 후 정확한 단일 수치 명령

단위 root에서:

```bash
python -B -S execution/run_once.py --execute-authorized
```

제안 worker 상한1 CPU-s,10 wall-s,256MiB, 한 worker·한 invocation. `attempt_01`은 독점 생성한다. stdout/stderr/exit와 OS child CPU를 보존한다. 실패하면 해당 원자료를 남기고 멈춘다. 자동 재시도·허용오차 변경·기존 suite 반복은 계약에 포함되지 않는다. C6/C7/C8 판정은 실제 결과를 읽어 별도로 한다.

수용 기준은 정확한 D1/D2/D3 대응, A의11/6과 독립 rational path/error식, B의1/3 및 −1/2와 false-centered5/12, C의(8/3,1,2), D의 endpoint/type/domain 처리, E의 equal-slope 예외, F의 moving-coordinate covariance, G의 callback(11/2,7/3)과 missing-column refusal이다. 검사 수 자체가 과학적 수용 기준이 아니다.

## 성공한 저장 데이터와 presentation 승인 후

```bash
timeout --signal=TERM --kill-after=1s 30s prlimit --cpu=4:4 --as=536870912:536870912 -- python -B figures/plot_saved.py --execute-authorized
```

단일 plot·package invocation,4 CPU-s/30 wall-s/512MiB. 전체 command의 외부 OS accounting과 원시 출력·exit를 남긴다. script 자체 prefix timing을 전체 비용으로 쓰지 않는다. 그림은 저장된 새 결과만 읽고 scientific implementation을 다시 실행하지 않는다. 실제 생성 PNG/SVG를 열어 확인한 뒤 C8 presentation 근거로 사용한다.

그 뒤 같은 독립 reviewer에게 실제 raw 실행·figure를 공개하여 기존 static 판정과 구분된 짧은 후속 판단을 받는다. 실제 finding이 있을 때만 관련 범위의 수정·표적 검증을 수행한다. C6–C10의 실제 완료 단계마다 원문/결과를 게시·이중백업하고 ACK를 확인한다. 새 단위20/20이 되더라도 원래 DAG count 증가나 physical completion은 해당 gate의 별도 근거 없이는 허용되지 않는다.

## 보존할 원장

Planning known lower16.486967885, charged known+reserve16.586967885.
Presentation known lower50.778518494, charged50.928518494.
현재 대화의 이전 F1 Bash display0.037은 PR242의 별도 F1 child0.026759와 다른 provenance이므로 임의 교체·합산하지 않는다.
Main595.225063/600, NO_MORE_IVPs.
UNKNOWN_NOT_ZERO, 닫힌 예약, 타 owner 비용·권한을 유지한다. 정확한 whole-session 비용이나 전역 budget PASS는 주장하지 않는다.

