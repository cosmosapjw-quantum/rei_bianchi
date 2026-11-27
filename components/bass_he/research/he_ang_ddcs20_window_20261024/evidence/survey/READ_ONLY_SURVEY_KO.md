# Read-only local intake survey

## 작업 범위와 identity

이 조사는 root Astra가 지정한 기계적 read-only intake다. 과학 코드, 기존 ledger, figure, repo 문서는 수정하지 않았고, test/catalogue/diagnostic/plot/solve를 실행하지 않았다. 산출물은 `he_next_survey/local/`에만 썼다. 요청된 역할은 lower-tier coding/mechanical intake executor다. API/tool로 관측한 runtime model identity는 없다. 역할 명칭과 대화의 model self-identification은 runtime 관측 증거로 승격하지 않는다.

`BASS_HE/AGENTS.md` 및 `rei_bianchi/AGENTS.md`를 읽었다. 후자의 tiered delegation에 따라 frozen scientific contract 전에는 inventory만 수행한다. ASTRA가 정한 입력/허용 경로/명령/상한/중지조건 없이 과학 구현 또는 실행하지 않는다.

## Local repo 상태

workspace, BASS_HE, rei_bianchi 모두 `git ...`는 `not a git repository`를 반환했다. BASS_HE 및 rei_bianchi에 `.git`이 없다. 그러므로 branch/HEAD/status는 **관측 불가**이며 clean checkout으로 보고할 수 없다. controller가 전달한 remote branch/head는 `research/he-ang-source-hex-20261024` / `bf3c21a39b1111497ed77667d05b8a853ffe6646`이다. 이는 별도의 remote supplied identity이며 이 snapshot의 local HEAD가 아니다.

파일별 전체 local inventory와 첨부 20개의 이름·정확한 byte 수는 `inventory.json`에 있다.

## 기존 unit 세 identity 확인

- `BASS_HE/research/he_ang_source_hex_20261024/code/hex_intake.py`: SHA256 `3552737bcd6cd488756f3ae5c70d1e28882bb6163d8fc4f48606689c6ef6f93e`, 요청 pin과 일치.
- `.../evidence/execution/RESOURCE_LEDGER.json`: SHA256 `b1eb4cf0e367f46260997f1e4cebf33228d5e9b7376329370bd91d323ef52450`, 요청 pin과 일치.
- `.../figures/synthetic_tail.png`: SHA256 `ad4d0c340146f440b9f4d3495162859b93dd62a53aa466cb9723f79b195b8735`, 요청 pin과 일치.

`bounded_ledger.json`은 다른 legacy 객체다. SHA `9e7475bbb17684b3bbfeb3abf31b3585bfb843750dc943cddaa0cc66490f732d`이며 RESOURCE_LEDGER가 이 identity를 prior receipt로 보존한다. 최초 inventory 과정에서 이름이 불명확한 ledger pin을 bounded_ledger와 대조했지만 바로 authoritative RESOURCE_LEDGER를 확인해 해소했다. Authoritative ledger mismatch는 없다.

RESOURCE_LEDGER가 기록한 누적 CPU `18.434312000000002 s`, wall `18.739398924000852 s`, same-unit CPU/wall cap `20/60 s`, 실행 횟수 algebra/catalogue/diagnostic/plot `4/3/2/1`을 그대로 보존한다. 실패 및 interrupted START의 `UNKNOWN_NOT_ZERO` 정책을 지우거나 0으로 취급하지 않았다. 과거 suite는 재실행하지 않았다.

## 첨부 텍스트 적용 범위 지도

아래는 source text가 명시한 범위의 분류다. 현재 과학 문제의 수용기준과 최종 적용 판정은 root Astra 소관이다. 원문은 `project_sources/`에 있고, 정확히 같은 내용의 줄번호본을 `01_numbered_source.txt`, `04_numbered_source.txt`, `05_numbered_source.txt`, `07_numbered_source.txt`, `08_numbered_source.txt`에 저장했다.

| 원문 | 현재 atomic angular 연구에도 이식할 수 있는 일반 요구 | 원문이 한정한 과거 CMB/Bianchi 전용 요구 |
|---|---|---|
| `01-Low-ell-Bianchi-Einstein-Boltzmann-Solver.txt` | L38–50: 문서가 아닌 실제 경로/출력 증거, smoke와 validation 구별, same physics/tolerance/output 성능 비교. L179–184: path·placeholder 분리. L279–307: 안정성/수렴/known-limit 수준 분리. L338–361: test와 release claim 정직성. L485–492: 안정 판정 뒤 종료. | 제목/역할 L2–25와 scope L39가 low-ell Bianchi/htt/bass audit를 지정. L44–47, L52–81, L187–277: 11 family, tilt/local boost, Thomson, PSTF, CMB polarization, statistics fitting 등. L83–115의 8 고정 auditor도 그 audit의 역할 구성이지 현재 atomic task에 자동 8-agent requirement가 아님. |
| `04-Adaptive-CMB-Code-Development-Protocol.txt` | L5–24: contract→실제 경로→가설→최소 patch/test→dual audit→plot 증거. L61–80: 변수·단위·부호·known limit·I/O·관측량 의미. L124–193: bounded hypothesis/kill test 및 verifier. L211–278: physmath→physmath-code 순차 감사, plot 직접 판독/변이/claim 축소. L281–306: DAG/next step와 baseline 전 대규모 refactor 금지. | L82–92: gauge/TCA/RSA/UFA/LoS/Bessel/C_l/CAMB/CLASS. L101–110의 경로 예시는 CMB 경로. L224–227 CMB 추가 감사. 현재 Hex/H1에 CAMB/CLASS나 CMB gauge 검증을 요구하는 근거가 아님. |
| `05-Adaptive-CMB-Code-Research-Executor-DAG-Governed-Development-Mandatory-Dual-Audit-Plot-Driven-Adversarial-Loop.txt` | L16–23, L32–46: DAG 복원, minimality, docs/smoke 증거 한계, task에 최소화한 dual audit. L62–97: completed/failed/unknown/blocked 구별과 실제 prerequisite 검증. L144–182: 후보 ≤3, 정확히 하나 선택, kill criterion. L185–243: 허용 실제 실행 뒤 순차 dual audit. L246–285: plot 판독/CRAG/변이. L288–365: 즉시 가능한 fix와 defer 분리, 다음 action/stop. | L5,17–18는 CMB executor임을 명시. L125–135는 “CMB 전용이면 relevant subset”이라는 조건부 목록. L203의 reference와 L222–226의 CMB add-on, L367–373의 gauge/source/LoS/C_l/CAMB/CLASS/zone 예시는 atomic angular에 자동 이식하지 않음. |
| `07-Figure-Residual-Error-Pass.txt` | L10–28: 최종 잔여 오류/축소 인쇄 89–90 mm 및 180–183 mm 가독성. L30–46: overlap/clipping/label/legend/오독. L48–68: bounded 검증과 micro-repair; P0 semantic error면 재설계 분리. | CMB 전용 내용은 없다. 단, L14–17은 1차 수정 뒤 최종 polishing 용도이므로 초기 scientific plot 생성의 전체 protocol로 바꾸지 않는다. |
| `08-Figure-Hostile-Audit.txt` | L10–37: semantic→legibility→layout 우선 감사, 89–90/180–183 mm. L39–75: intent/caption, 단위/normalization/비교 의미/강한 시각 claim 점검. L77–98: bounded 검증과 최소 repair. | CMB 전용 내용은 없다. figure image/caption/본문 제공 시 적용하는 first audit/repair 규칙이며 새 물리 수용기준 자체는 제공하지 않는다. |

## Archive member listing

Rust toolchain 첨부 06(192287020 compressed bytes)은 toolchain 자체이며 listing도 생략했다. unpack, 설치, bootstrap, shell source는 모두 하지 않았다. 나머지 9개 archive는 top-level member 이름/크기만 읽었고 각 `*.listing.json`과 `archive_inventory.json`에 보존했다.

- 10/11/12/13/14: 각각 23/38/103/693/470 members. 이름으로 확인되는 electron-hydrogen/ionization/angular scattering/Hex/CCC/BASS_HE payload는 없었다.
- 15: 4 members. 내부 `rust-offline-rodas5p-rs-20260806.tar.zst`를 포함하지만 nested archive는 열지 않았다.
- 17: 8451 members. lexical angular/Hex hits는 `triangular*.rs` 및 `hex_float.rs`라는 Rust numerical dependency의 false positive다. atomic angular 또는 Hex scattering source라는 증거가 아니다.
- 18: 7 PDF; relativistic cosmology/kinetic theory/fluid/Boltzmann 제목.
- 19: 8 PDF; `1501.04288v1.pdf`, `mnras0380-1387.pdf`, `1-s2.0-S0370157308000884-main.pdf`, `A_1001921711071.pdf`, `PhysRevD.62.043004.pdf`, `9904408v2.pdf`, `9804316v3.pdf`, `1810.06293v1.pdf`. 파일 내용은 이 inventory 범위에서 읽지 않았다.

**제한:** filename listing의 no-hit은 scientific source 부재 증명이 아니다. 불투명 PDF 파일명과 nested archive 내용은 미확인이다. 새로운 input-dependent scientific admission은 이 조사로 만들지 않는다.

## 비과학 환경 관측

Python 3.12.14 / Linux x86_64 / AMD EPYC 9V74 virtual CPU. affinity 0–8(9 visible), cgroup cpu.max=800000/100000(8 CPU-equivalent quota), memory.max=8589934592(8 GiB). lscpu 원본은 `lscpu.txt`. 순간 memory.current는 inventory에 사실값만 기록했으며 실제 사용 가능 메모리로 해석하지 않는다.

관측 설치 metadata: numpy 2.3.5, scipy 1.17.0, matplotlib 3.10.8, pandas 2.2.3, pypdf 6.10.0. sympy/pytest/mpmath distribution은 현재 Python metadata에 없었다. PATH에서 gfortran/mpifort/mpirun/cargo/rustc는 발견되지 않았다. 이것은 전체 시스템 부재 증명이나 설치 권고가 아니다. scientific import/suite 또는 compiler bootstrap은 실행하지 않았다.

## 현재 handback

root Astra의 frozen next-unit contract를 기다린다. 과거 `NEXT_SOURCE_CONTRACT.json`은 실제 H1 ionization differential payload/승인된 bounded generation 없이는 physical HE-ANG `SOURCE_INPUT_PENDING`을 유지하고, 기존 budget으로 full Hex solve를 금지한다. 이 원문을 새로운 scientific interpretation으로 재작성하지 않았다.
