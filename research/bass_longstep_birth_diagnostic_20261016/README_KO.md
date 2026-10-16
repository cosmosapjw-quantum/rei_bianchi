# REI PR159 장구간 화학 수렴의 원시자료 감사와 source-age 반례

**2026-10-16 KST, 독립 샌드박스 이론 R5 + 코딩 C7/C8 진단.**

이 폴더는 REI [PR159](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/159)
head `64a6dc33873e8be494f78e580a577c8083064eb1`의 기존 22개 NCP 결과를 **읽기 전용**으로
재분석하고, 그 계산에서 나타난 비정상적 온도 step-doubling 비율에 대한 해석적인 오류 상쇄
기작을 독립적인 비자명한 양의 제조모형으로 검산한다. 새로운 사용자 Ubuntu/NCP 실행이 아니며
`rei_microphysics` 기존 solver, 원래 PR159 checkpoints, BASS/REI production branch는 변경하지 않는다.

## 실제 소스와 새 관찰

원본 Dropbox/Google Drive 양쪽에 이전에 백업된 `recovery-1f8619c2.tar.gz` 중
Google Drive 아카이브를 **별도로 이 샌드박스에 다시 복구**했다. SHA256
`bf8aaffdae624a6de25d6f8e58fb8c7b3c166f331954d9b841907ab1bc061e4c` 일치.
그 내부 `ncp_evidence/evidence-release.tar.gz` SHA256
`4b43737e74acaa8af935617294e1e04ff647e49336d555512fd3ae4707decfbb` 일치.
22개 `result.json` + 22개 `step_trace.csv`, 총 **44개 파일**의 원시 byte, SHA, 파일 크기를
`evidence/RAW_SNAPSHOT.json`에 base64 그대로 기록한다. 독립 호출 `audit_pr159.py`는
이 스냅샷만 있는 Git checkout에서도 원시 bytes를 복원해 원래 SHA와 비교한다.

REI PR159의 원래 NCP 관측:

| test | COLD_FLRW | SIGNED_MINUS | 근거 |
|---|---:|---:|---|
| long 4→8 / 8→16 온도 차이 비율 | 0.65185327 | 0.65185677 | 원본 `result.json` |
| long 누적 소스 입자수 차이 비율 | 3.99667859 | 3.99668120 | 원본 `result.json` |
| long 16-step max Newton residual | 7.205e-12 | 8.841e-12 | 원본 `result.json` |
| short 온도 차이 비율 | 1.925 / 1.961 | 1.925 / 1.961 | 원본 `result.json` |

원본 `axbi_driver.rs::tentative`는 `geometry_map(mid)`, `inject(dt)`,
`chemical_stage(dt)`, `geometry_map(to)` 순서이다. `transport.inject`는 중점 방출률에
**전체 proper Δt**를 곱해 birth count를 먼저 수송 상태에 추가하고,
`chemical_stage`는 그 상태에 backward-Euler 흡수를 **동일 전체 Δt** 동안 적용한다.
따라서 원래 오래된 광자와 중점 생성 신생 광자의 시간 나이가 같지 않더라도 같은
흡수 연산자가 걸린다. 포톤 수지 자체는 이 오류를 구별할 수 없다.

**해석적 조건부 정리:** 한 셀에서 일정한 광자 에너지/가스와 비음성
종별 불투명도 λᵢ[s⁻¹], λ=Σᵢλᵢ, τ=λΔt, 그리고 기간 전체에 균일하게
태어난 신생 광자수 S= j Δt[/H]를 가정하자. 기존 광자 N₀와 신생 광자의
frozen-cell 정확해는

`N_true=N₀ exp(-τ) + S φ₁(-τ)`, `φ₁(-τ)=-expm1(-τ)/τ`.

현재 mixed birth+BE의 축약형은 `N_BE=(N₀+S)/(1+τ)`. 따라서

`N_BE-N_true=[1/(1+τ)-exp(-τ)] [N₀-S/τ]`.

이 항등식과 species별 energy/number ledger를 Wolfram으로 상징 검산하고 Python
22개 시험을 실행했다. τ>0에서 양의 첫 bracket이 있으므로, 기존 광자의 BE는
정확해보다 광자를 **많이** 남기고, 균일 출생 신생 광자의 full-step BE는
정확해보다 광자를 **적게** 남긴다. 두 오류는 `N₀=S/τ=j/λ`일 때 정확히 상쇄한다.
이는 **frozen uniform-proper-birth 구성**에서의 조건부 정리이지 진짜
Bianchi/Verner/그랙클 시간발전의 완전한 폐쇄가 아니다.

광자 각종 흡수 사건수 `Aᵢ=(λᵢ/λ)[N₀+S-N_end]`를 사용해
`N₀+S=N_end+ΣAᵢ`, `E(N₀+S)=E N_end+Σᵢ IᵢAᵢ+Σᵢ(E-Iᵢ)Aᵢ`를
검증한다. 원래 native는 양의 recombination, collisional microphysics와
`PhotoEvent`에 대해 독립 ownership을 갖는다. 이 축약 수식의 열/결합 원장은
fixed energy, source no geometry work, gas fixed라는 계약 안에서만 성립한다.

**강건한 반례:** `manufactured_birth.py`는 `λ(t)=3[1+0.42 sin(2πt+0.18)]`,
`j(t)=1+0.6 cos(3πt+0.33)`, `N₀=0.265`를 사용한다. 모든 λ,j,N은 양이다.
이 모형에서 BE는 n=4/8/16 순차 차이 비율 `0.6432099598`,
n=128/256/512에서는 `1.9756863`으로 접근한다. 즉 **첫 비율이 1보다 작아도
방법이 점근적으로 1차 수렴할 수 있다는 구성적 반례**이다.
반면 두 cohort를 모두 exact frozen-cell exponentials/φ₁로 처리하고
중점에서 변하는 λ,j를 근사하면 독립 DOP853 준거에 대해 2차,
기존 광자만 BE를 남기는 hybrid는 1차라는 것을 검증한다.
이 수치는 원래 REI native 다중 species 수렴에 대한 예측이 아니다.

## 모듈과 재현

- `recover_pr159.py`: 원래 NCP 복구 아카이브 SHA를 검증하고 source byte 원시자료 추출.
- `evidence/RAW_SNAPSHOT.json`: GitHub에서도 단일 파일로 byte-identity를 복구 가능한 44개 실제 파일의 raw archive.
- `audit_pr159.py`: 22개 original NCP 시험 조건/종료 결과/첫 실패/ratio를 signed Richardson 보조 다항식과 구별.
- `birth_cohort.py`: 수치 안정적 φ₁, 기존/신생/혼합 양의 flux와 species별 수지.
- `manufactured_birth.py`: 독립 DOP853, 양의 시간변화 source/lambda, stiff/pre-asymptotic diagnosis.
- `test_temporal.py`: 22개 새 unittest (actual PR159 archive byte tamper, 4/8/16 source and thermal ratios, fixed-cell identities, high-precision φ₁, conservation, asymptotic counterexamples).
- `evidence/PR159_RAW_AUDIT.json`, `evidence/MANUFACTURED_STUDY.json`, `evidence/MANUFACTURED_COUNTEREXAMPLE.json`, `evidence/TESTS_FINAL.log`.

```bash
cd research/bass_longstep_birth_diagnostic_20261016
python3 -m unittest -v test_temporal
python3 audit_pr159.py
python3 manufactured_birth.py
```

Python ≥3.11, SciPy, mpmath 필요. 이 폴더의 `evidence/RAW_SNAPSHOT.json`만 있어도
GitHub clone에서 native 원시 22개 시험을 검증할 수 있다. 원래 6MB 복구 아카이브는
원래 Dropbox/Google Drive 백업에 유지, 새 논문/소스의 source identity를 대체하지 않는다.

## 실제 결과 판정과 Codex 재개

- `DERIVED + SANDBOX_TESTED`: conditional frozen-cell exact new-old bias identity.
- `SOURCE_VERIFIED`: PR159 실제 NCP 22 결과와 44 byte/sha; t16의 큰 Newton residual.
- `SCIENTIFIC_REVIEW_HOLD`: 긴 구간 native 온도 비단조성의 인과 원인, species/opacity 분해 미실행.
- `NOT_RUN`: 이번 루프에서 user-local Ubuntu, NCP, native Rust compile/reaction ablation.

다음은 source-bound REI PR159 별도 worktree에서 원래 endpoint를 보존한 채
(1) 기존 출생 전부흡수, (2) 새 출생 uniform-φ₁, (3) 동일 birth 기존 Newton을
개선한 독립 실험을 해야 한다. **HE24의 exp(-τ) full-source-birth 참조를
REI의 backward-Euler multi-bin reaction에 그대로 복사하는 것은 위험하다.**
반드시 동일 출생광자 cohort와 old cohort를 분리하고 energy support/number/thermal/binding
수지를 결합해 검증한다. 각각 raw에 absorption optical depth, source number/time,
Newton residual, full chemistry Jacobian condition estimate를 추가해서 반복 실행한다.
이 수치 게이트가 통과하기 전, native dynamic EoR와 전체 광자/가스 운동량 Qᵃ는 HOLD.

문헌: [Cardall & Mezzacappa (2003)](https://doi.org/10.1103/PhysRevD.68.023006)
보존형 상대론적 kinetic 수송;
[Leong et al. (2023)](https://doi.org/10.1093/mnras/stac3828)
시간 의존 H/He RT 코드 비교;
[REI PR159](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/159),
[BASS_HE HE24 PR71](https://github.com/cosmosapjw-quantum/BASS_HE/pull/71),
[bass_cr C21 PR75](https://github.com/cosmosapjw-quantum/bass_cr/pull/75).
