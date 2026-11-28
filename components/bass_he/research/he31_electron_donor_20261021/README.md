# HE31 — H/He electron donor, prepared FV moments, ready NCP sweep

실제 복원한 전자 donor를 기존 full40 LRS Bianchi I RHS에 연결하고, canonical
finite-volume moment의 반복 연산을 줄였다. 작은 실제 on/off 비교와 원본 evaluator
대조를 완료했다. 본 단위의 새 실제 결과 범위는 **z=20→4**다. 기존 HE30의 완료된
**237개 z=20→2** 궤적과 네 그림은 그대로 유효하며 재실행하지 않았다.

## 바로 볼 결과

- [연구·구현 보고서](REPORT_KO.md): 조사 결과, 이론, 수치, 성능 범위와 다음 의존성.
- [species evolution](plots/species_evolution.png), [electron density / optical depth](plots/donor_optical_depth.png).
- [on−off 차이](plots/paired_difference.png), [proper elapsed time evolution](plots/time_evolution.png).
- [끝점 표](plots/endpoints.csv), [저장 결과 분석](plots/ANALYSIS_SUMMARY.json).
- [20단계 ledger](RESEARCH_LOOP_LEDGER_KO.md), [DAG](DAG.json).
- [Codex 실행 인계](CODEX_HANDOFF.md), [다음 대화 인계](NEXT_THREAD_HANDOFF.md).

초기 좌표 `(Sigma_F,P_m,P_r)=(.003,+.0003,-.001)`의 한 paired control에서
Thomson-on의 z4 optical depth는 `0.03724155220658596`이다. z4의 Sigma는
on `1.3890261117025876e-4`, off `1.3717105385392087e-4`이며 차이는
`1.731557316337896e-6`이다. 이는 prescribed R15/HG97-B reduced chemistry와
기존 unpolarized photon closure의 사례 결과다. 완전한 H/He·polarization
피드백이나 전체 sweep의 일반적 단조성을 뜻하지 않는다.

## 구현

| 파일 | 기능 |
|---|---|
| `src/electron_donor.py` | HII/HeII/HeIII census, proper/comoving·SI/cgs 계약, immutable identity, ln(a)의 comoving-ne PCHIP, 구간 이탈 거절 |
| `src/prepare_donor.py` | 복원한 R15 NPZ 또는 source-pinned AXBI CSV를 검증된 donor bundle로 변환 |
| `src/prepared_moments.py` | 같은 canonical quadrature를 고정 momentum/weights로 준비, binary64 scalar/batch evaluator |
| `src/bindings.py` | 원본 7파일 SHA, module 실제 경로, 과학 identity와 자원 receipt 분리 |
| `src/receiver.py` | 기존40 physics + optical-depth1, photon-only opacity, 성분별 signed stress, 원자적 완료 결과 |
| `src/campaign.py` | 명시적 sweep 생성, HE30 자원·lease 실행기 재사용, 실패/보류 exit2 |
| `src/analyze_saved.py` | 저장된 결과와 재사용 receipt에서 표·그림 생성, 신규 ODE0 |
| `run_ncp.sh` | 준비된 campaign 실행 후 자동 그림 생성 |

원본 `research/he29_rei_pilot_20261021/vendor/`의 canonical RHS 및 quadrature는
변경하지 않았다. 원본 과학 계보는 rei_bianchi PR147
`3b85dedce84d37b3e165da00685a8a984950aafe`다. 원본의 소유·license 기록은 그대로
둔다. 외부 재사용은 SciPy PCHIP와 DOP853, NumPy, Matplotlib 및 검토한 원전의
수식이다. 외부 저자의 미공개 코드나 원문 PDF를 배포하지 않는다.

## NCP에서 실행

아래 명령은 이 branch의 고정 commit을 checkout한 저장소 root에서 실행한다.
정확한 실행 pin은 [CODEX_HANDOFF.md](CODEX_HANDOFF.md)와
[publication receipt](delivery/PUBLICATION.json)에 있다.

```bash
python3 -m pip install -r research/he31_electron_donor_20261021/requirements.txt
bash research/he31_electron_donor_20261021/run_ncp.sh pilot18_on
```

이미 호환 환경이 있으면 설치는 생략한다. 이 Python 경로에는 별도 native compile이
없다. 기본18개 사례는 **준비 완료·NCP 미실행**이다. 확장175개 설정도 준비했다.

```bash
bash research/he31_electron_donor_20261021/run_ncp.sh joint175_on
```

worker는 native thread1이며 max64, reserve2CPU/16GiB, 실제 affinity/cgroup quota,
현재 CPU 부하·가용 memory와 공통 CPU/case lease로 수를 정한다. 독점 가능한
64CPU 머신에서도 이 기본값의 상한은62다. 18-case campaign은 최대18개다.
현재 실행 중인 다른 세션을 신호로 중단하지 않는다. resource admission의
1GiB/worker는 실측 RSS가 아니다. 시간 예산 안에 완료하지 못한 사례는 exit2와
receipt를 남긴다. 아직 시작하지 않은 DEFERRED는 같은 명령으로 완료 identity를 재사용하며
재개한다. 시작 후 FAILED/TIMED_OUT은 원 receipt가 고정되어 자동 재시도하지 않는다.
원인을 분류해 영향 범위의 작은 수정 또는 명시적 retry 처리를 한 뒤 진행한다.

기본 출력은 `results/ncp_pilot18_on/` 또는 `results/ncp_joint175_on/`이다.
`RUNNER_REPORT.json`, 완료 JSON, `plots/`를 source pin과 함께 돌려주면 된다.
NCP에서 benchmark·237 baseline 재실행·알고리즘 재작성을 할 필요는 없다.

## 실제 입력과 검증 범위

`inputs/r15_flrw/manifest.json`에 source SHA, closure, source cosmology, 현재
bundle identity가 있다. 원래 16,385행의 z20→4 FLRW Q history를 복원한 것이다.
HII+HeII ionized filling region, HeIII=0, residual electrons 없음, T=20,000K,
clumping3의 reduced model이다. donor background와 target background는 다르며
mean a의 일방향 prescription으로 명시한다. source의 과거 검토 상태도 보존했다.

z2를 포함하는 실제 H/He history가 들어오면 `prepare_donor.py axbi`와
`campaign.py prepare --z-end 2`로 같은 consumer를 사용할 수 있다. 현재 R15
bundle에 z2를 요청하면 worker가 시작되기 전에 거절된다. 현재 native AXBI source
generator의 z>=4 guard를 무작정 제거하는 것은 지원되는 z2 물리 source가 아니다.

검증 근거의 권위는 [종합 판정](evidence/VERIFICATION_SUMMARY.json)이다. 첫 clock
rounding 기준 실패와 NumPy bool 직렬화 실패는 `evidence/failed/`에 보존했다.
변경 영향에 필요한 항목만 재확인했고 solver tolerance는 바꾸지 않았다. 상세 속도
benchmark, 새로운 continuum convergence certificate, NCP의 HE31 실측은 없다.
