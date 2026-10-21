# 독립 Astra R6/C9 — root의 build64 수정 부록

## 판정

**PASS_SCOPED_ROOT_BUILD64_REPAIR. 남은 blocking finding 0개.** 기존 검토와 같은 episode에서 root가 발견한 CLI 상한 문제를 닫는다. 기존 게시·백업·인계로 진행할 수 있다. 별도 검토 gate나 native 재실행은 요구하지 않는다.

root의 finding은 `make_manifest`가 build concurrency를 1..4로 제한하여 사용자가 요청한 64코어 호스트 실행 준비를 막는다는 것이다. runtime 수정은 해당 상한과 오류 문구를 **1..64**로 바꾼 한 줄이다. 기본값 1은 유지된다. README 실행 명령은 `env -u CARGO_TARGET_DIR`, `--build-jobs 64 --max-workers 64`를 사용하며 실제 자원 admission 조건을 명시한다.

## 직접 확인한 수정과 시험

보존된 PRE_REPAIR 세 파일과 현재 파일의 diff를 모두 읽었다. 12개 파일 manifest의 크기와 SHA256을 직접 대조하여 **runtime 1개·시험 1개·README 1개만 변경되고 나머지 9개가 동일**함을 확인했다. 실제 자원 admission을 담당하는 `campaign.py`의 SHA256은 `4f1c2a2d37525a87fa94ddd7a56123fa58787a7827600d0981a6b9041097854b`로 유지된다.

실제 `build64_repair/OUTCOME.json`, 빈 stdout, unittest stderr를 읽었다. 명령은 다음과 같다.

```text
python3 -m unittest -v test_cli.RecipeTests.test_build_jobs_64_resource_contract_and_65_rejected
```

표적 시험 1개가 exit 0, process wall 0.07310534799762536초로 끝났다. 검사한 계약은 여섯 build/test job의 `cpu_slots=64`, `nominal_memory_mb=65536`, Cargo `-j 64` 전달, manifest 유효성, 65 요청 거부이다. 추가 native 실행은 0회이며 전체 시험 suite도 반복하지 않았다. 기존 21개 PASS와 이번 표적 1개 PASS를 현재 코드에서 전체 22개 suite를 다시 실행한 결과로 서술하지 않는다.

## 자원 계약과 과학적 범위

64 build slot은 64GiB nominal 예약이다. 이는 peak RSS 측정값이 아니다. 기존 scheduler의 실제 affinity·cgroup CPU quota·사용자 상한·메모리 admission 및 20% reserve는 그대로다. 실제 자원이 요청을 수용하지 못하면 `NOT_RUN_RESOURCE_ADMISSION`을 남긴다. 64코어/128GB는 요청한 NCP 사양이며 이번 검토에서 관측한 호스트 사양이 아니다.

이번 수정은 prepared runner의 인위적인 상한을 제거한다. **실제 NCP 64코어 빌드·backlog 실행·가속은 새로 수행되거나 입증되지 않았다.** 기존 3-worker 로컬 관측, 18개 native receipt, 두 shard 비교는 원래 범위대로 재사용한다. 새로운 native 방정식·수치 방법·provider·CSV 스키마·pin 변경은 없다. V12/V13/SSPRK의 원래 backlog와 완료된 Radau19·borrowedN2·원본V14 84 제외 규칙을 유지한다. 새로운 과학 모델 수는 0이며 기존 HOLD와 production NOT_ISSUED를 유지한다.

## 보존된 원문과 현재 코드 결속

원본 독립 검토 두 파일의 바이트를 변경하지 않았으며 아래 SHA256을 직접 재확인했다.

| 문서 | SHA256 |
|---|---|
| `INDEPENDENT_REVIEW.json` | `82088d1dc7d368dd24d128dbee7127637e8fb4738cff0945351edc3c155bfa47` |
| `REVIEW_KO.md` | `74f8c06179f66900c15813862a879aaf714e79396fbcfaa242b0671afa8ee213` |
| 이전 `CODE_CHANGED_FILE_MANIFEST.json` | `dd686ea1eee2437dea754d771098ee9b87a93b53780d99f3de6a18813c13a7a9` |
| 현재 `CODE_CHANGED_FILE_MANIFEST_BUILD64.json` | `8f1614487c3ea617d1eda8776d8594988c0d2e4160dc8c5f974232d6220071e5` |

현재 `campaign_cli.py`의 SHA256은 `72400cf4d204f7975bdfdd98f9d9e29e4fe654162f86e0714f5353e7ed051531`이다. 모든 before/after 파일 identity와 시험 원문의 크기·해시는 동반 `ROOT_REPAIR_ADDENDUM.json`에 있다. 이전 검토의 manifest를 소급 변경하지 않으며, root의 최종 게시에서는 현재 manifest와 이 부록을 함께 사용한다.

검토자는 `/root/independent_review`로 구현·native 실행·Git/provider 변경을 수행하지 않았다. 이미 읽은 physmath-research-loop 1.3.0의 SKILL, POLICY_INTEGRATION, CODING_LOOP, SUBAGENT_MODE, THEORY_LOOP 지침을 같은 episode에 적용했다. ROOT_CONTRACT와 물리적 admission 범위는 불변이다.
