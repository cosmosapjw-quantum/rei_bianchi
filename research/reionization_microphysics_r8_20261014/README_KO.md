# Reionization R8 재현·후속 계산 패키지

2026-10-14. 이 패키지는 이론적 차원 축소, 실제 경량 원자·핵물리 계산, 공개 복사장 후보와 local Codex 후속 작업을 함께 보존한다. 완료된 수치 결과는 각 모듈의 물리 모형·근사·입력 범위에서 사용한다. 전체 correlated Li/daughter, 17종 네트워크 또는 reionization production 계산의 완성을 뜻하지 않는다.

## 실제 완료된 부분

| 모듈 | 실제 산출물과 검증 | 범위 |
|---|---|---|
| `hydrogenic/` | 8종 수소형 입력, n≤20의 210상태·종당 2470 E1 edge, cascade 및 line yield. n20 내부 검사 6190개 | 자발 E1 유한 준위계. 전체 RR·2광자·Case A/B·복사수송은 별도 |
| `daughter/` | 5개 전하비의 수소형 bound/continuum 분포·모멘트·꼬리, 독립 검사 73개. **allowed-beta 4개 모형과 추가 검사 43개** | 갑작스러운 전하 변화. 4개 모형은 F=1/점 Sommerfeld × 무한/유한 환산질량. Qg=18600 eV는 선택한 값이며 correlated He/Li·완전 recoil·교환 보정은 아님 |
| `nuclear/` | native C의 np 포획·역광분해, recoil 문턱과 열평균·열적 표적 MB 확장, 검사 54개 | 선택한 Chen–Savage 1999 진폭. 최신 EFT posterior 또는 전체 moving-target Bose 계산과 구분 |
| `photo/` | Stobbe 복사장 반응 36조건, Planck 기준장 21조건 | 명시된 유한 주파수/차폐 모형과 FLRW Planck 기준장 |
| `reduction/` | cascade의 삼각형 backward adjoint와 독립 forward 계산 | 같은 E1 DAG에서 관측량·대기시간 모멘트 축소 |
| `radiation/` | source C adapter 48검사, Puchwein-v1 59노드 adapter 181검사. **HYREC-2를 실제 소스로 컴파일·실행하여 8000노드 이력 확보**, 7개 기본 검사 | HYREC pin `09e8243d0e08edd3603a94dfbc445ae06cafe139`, upstream FLRW/SWIFT 기준 입력. x_e=n_e/n_H, T_m 초기값이며 고유한 17종 조성이나 재결합 스펙트럼은 아님 |
| `local_codex/vendor_r6/` | 실제 ECG·산란·상관 연산자·분자 입력 생성기·핵 입력 코드 29개 파일. 새 위치에서 native C++ 4검사, 핵 관측 30개와 5개 계약 준비 | 공간 ECG는 물리적 반대칭 Li 해와 구분. PySCF가 필요한 실제 분자 곡선은 아직 미생성 |
| `integration/`, `wolfram/`, `review/` | 최신 원문·source identity, 실제 Wolfram/xAct 반환, 별도 검토와 수정 증거 | 코드 검사·수식 검산·모형 검증의 근거를 분리 |

서로 겹치는 검사가 있으므로 표의 검사수를 독립 검증 횟수로 합산하지 않는다. 기록된 실행 시간은 이 호스트의 측정값이다.

## 먼저 읽을 파일

- `LOOP_RECORD.json`, `GAP_CROSSWALK_R8.json`: 이번 작업과 기존 공백의 연결.
- `integration/CURRENT_SNAPSHOTS.json`, `integration/DELTA_AND_REUSE.md`: HE R10, HH PHYS29, CR moving cluster, REI R7의 실제 최신 결과.
- `daughter/THEORY_AND_RESULTS.md`, `nuclear/THEORY.md`, `hydrogenic/THEORY.md`: 정의·유도·계산식·실행 범위.
- `radiation/SOURCE_CANDIDATES.md`, `radiation/HYREC_EXECUTION.md`: 별·퀘이사·UVB 후보 및 실행한 원시 재결합 기준.
- `local_codex/LOCAL_CODEX_HANDOFF.md`, `local_codex/AVAILABLE_CODE_AND_INPUTS.md`, `local_codex/PROVIDER_CONTRACT.md`: 남은 구현, 실제 동봉 코드, 실행 입력 계약.

REI R7의 이전 Library weighted proof와 이후 GitHub unweighted proof는 서로 다른 artifact다. 최신 게시 pin은 `8bf8e3c18d607334614cfea734f9b10961fbd4d4`이며 두 자료의 수치 상계를 혼합하지 않는다. HH PHYS29 Coulomb 유한창 열평균은 이미 계산되었고, 유한 구적/반올림 전체 인증 등이 남아 있다.

## 필요한 경우에만 선택 재현

C/C++ compiler, make, Python 환경이 필요하다. Python 의존성은 `requirements.txt`에 고정되어 있다. PySCF는 아래 경량 재현의 필수 의존성이 아니며 실제 분자 생성 작업 때 별도로 설치·버전을 기록한다. 기존 결과는 이미 실행되었으므로 전체 suite 반복을 후속 연구의 선행조건으로 만들지 않는다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
source .venv/bin/activate
python run_lightweight.py --list
python run_lightweight.py daughter
```

`run_lightweight.py`는 선택한 모듈만 실행할 수 있다. 이름은 `hydrogenic daughter nuclear source photo cmb cascade runner`이며, 인수를 생략하면 전부 재실행한다. `daughter`에는 allowed-beta 4개 모형과 추가 검산이 포함되어 있다. 재현은 사본에서 시행하여 기존 결과와 로그를 보존한다. `cascade`는 보존된 `hydrogenic/n20` 표를 소비한다.

HYREC는 위 통합 실행기의 대상에 포함되지 않는다. 이미 실행한 결과는 `radiation/hyrec_reference_run/`에 있다. 새 플랫폼에서 재현이 필요한 경우 `radiation/HYREC_EXECUTION.md`의 source archive 추출·6개 C 파일 컴파일·input.dat 실행 절차를 사용한다. upstream에 있던 미리 컴파일된 binary는 이번 기준 실행에 사용하지 않았다.

## 무거운 작업의 현재 준비도

`local_codex/jobs.json`에는 **8개 heavy 작업, 완전한 물리 provider 연결 0개**가 정의되어 있다. 미시 입력과 추가 구현이 필요한 상태이며, local Codex를 실제로 실행하거나 원격 계산을 제출한 상태는 아니다. 동봉된 실제 코드·입력 생성기부터 확장하고 물리적인 executable/deck를 연결한 다음 benchmark와 실행을 진행한다.

```bash
python local_codex/run_jobs.py preflight --out local_runs
```

초기 출력의 `ready: 0, blocked: 8`과 exit 2는 현재의 정확한 상태다. 실제 provider를 연결한 뒤에만 `benchmark`와 `run`을 사용한다. 세부 명령은 `LOCAL_CODEX_PROMPT_KO.md`에 있다. Runner는 입력 해시·repo pin·validation·시간/메모리 예산을 확인하지만 물리적 타당성을 자동 승인하지 않는다. 기존 CR/RCT/HH OFF와 production owner, main merge 경계를 유지한다.

별/AGN emissivity를 직접 넣어 수송하는 경로와 이미 수송된 UVB율을 처방하는 경로는 같은 광자 집단에 중복 적용하지 않는다. BPASS·QLF·FG20 등의 후보와 실행한 Puchwein-v1/HYREC 기준은 각각의 출처·범위를 붙여 사용한다.
