# REI IGM 원본 tick160: 두 시점 26-event source와 승인 상태의 대응 검사

2026-11-01 · **하나의 범위 한정 물리·코딩 연구 단위**, 첫 canonical FLRW interval 자체는 미완료.

## 1. 출처와 범위

원본 SCIENCE_OWNER: `cosmosapjw-quantum/rei_bianchi`. Source 공급자는 PR #321 HEAD `9afee1ab4a45a7b4b277e183e7e18c59a8d39f4d`. 해당 HEAD의 성공 GitHub Actions `41266684253` artifact `13067184595`, 30,686,343 bytes, SHA256 `44b322e2ebbd7b915b6958709136d5dc041e2468b0d71f0eb67da013f6aad535`를 직접 다운로드하고 ZIP CRC 및 6개 원본 source CSV의 SHA를 확인했다. 원래 승인된 상태 PR #320 artifact `13064333012`는 12,591,114 bytes, SHA256 `48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7`이다. 두 원본 파일은 이 패키지에 개별 byte-exact 보존된다.

원본 46,080개 공간 노드의 2개 시점(`initial`, `accepted_tick160`)을 읽었다. 세 shape lane으로 라벨된 276,480 source CSV 행은 **전부 동일한 수치 내용의 복제**이므로 세 배의 독립 물리 표본으로 세지 않는다. 원본 source가 출력한 `f_0,f_160`은 각각 별도로 둘러싼 event flux interval의 중간값이다. 하나의 일관된 source realization에서 나온 참 RHS 벡터가 **아니다**. `y_0,y_160`도 각각 interval 내부의 대표값이므로 하나의 동일한 연속 우주론적 trajectory에 대한 두 측정점이라고 주장하지 않는다.

## 2. 새로운 source-conditioned 물리 계산

원래 source-clock 레이블 `Δt = 779495799866.9248 s`를 사용한다. `y=(x_HII,x_HeII,x_HeIII,x_e/H)`에 대해 각 노드별로

```
Delta_y_rep = y_160^rep - y_0^rep
I_2sample = (Delta_t / 2) * (f_0^mid + f_160^mid)
R_proxy = Delta_y_rep - I_2sample
```

를 계산한다. 원본 승인 상태구간 `[y160_lo,y160_hi]`에 `y0_rep+I_2sample`이 포함되는지, 그리고 `Σ|R_proxy|/Σ|Delta_y_rep|`를 검사한다. 이것은 두 시점 source 대용치의 적합성 검사이지 원본 26-event ODE의 물리적 local truncation error가 아니다.

| 채널 | 단순 2시점 대용치가 승인 상태구간 **밖**에 있는 노드 | Σ|R_proxy|/Σ|Δy_rep| | proxy-대표 차의 Pearson | 95백분위 절대차 |
|---|---:|---:|---:|---:|
| HII | 32,946 (71.497%) | 3.9246% | 0.9942825 | 1.3764e-05 |
| HeII | 41,034 (89.049%) | 4.4764% | 0.9996811 | 0.00014289 |
| HeIII | 1,314 (2.852%) | 0.1435% | 0.9999989 | 9.984e-09 |
| electron | 25,284 (54.870%) | 3.3765% | 0.9956621 | 1.3876e-05 |

H II 최대 절대 proxy 차는 `0.0015157220356725838` (분율)이고 대표 온도 약 65,413 K의 반복 구조 노드에서 나타난다. 상위 50개 절대 H II source-proxy 차 노드와 최대 50개 원본 부모 `log(T_hi/T_lo)` 폭 노드의 겹침은 **0**이었다. Pearson(절대 H II 차, parent width)=`0.2546688242272405`로 진단됐다. 이 결과로 실제 실패한 `[160,161]`의 물리적 오차 원인이나 node identity가 정해지는 것은 아니다.

## 3. 공통 부모 원본 solver로 이어지는 유도

다음 진짜 물리 승인 대상은 같은 부모와 source 공유를 유지한

```
D_h(y,theta) = F_h(y,theta) - F_(h/2)(F_(h/2)(y,theta),theta)
```

이다. 기존 `I_2sample` 또는 `R_proxy`를 이 `D_h`와 혼동해서는 안 된다. 임의의 두 대표값/두 source 표본 `(y0,y1,f0,f1)`을 만족하는 유일한 cubic Hermite 보간의 양끝 곡률은

```
c''(0) = [6(y1-y0)/h - (4 f0+2 f1)]/h
c''(h) = [-6(y1-y0)/h + (2 f0+4 f1)]/h
R_proxy = -(h^2/12) [c''(h)-c''(0)]
```

를 정확히 만족한다. 이 보간의 곡률은 원래 source의 실제 이계시간도함수가 아니다. 더구나 함수 `f_λ(t)=f_lin(t)+λt(h-t)`는 양끝 source 값을 유지하지만 시간적분값에 `λh^3/6`을 추가할 수 있으므로, 양끝 자료만으로 joint source-time remainder를 규정할 수 없다. Wolfram에서는 Hermite 관계를 symbolic zero로 확인했다.

## 4. 보존 및 독립 검산

원본 5종 H/He source의 charge stoichiometry로 `nHe/nH = 0.079`가 복원됐고 변화량 전자 장부 항등식의 최대 차는 `6.742011418532011e-16` (분율) 이하였다. 열에너지 `ΔU`와 `photoheat+OTS-escaped`의 양끝 적분치 차이는 다른 냉각·Compton·팽창·결합에너지 및 source 상관이 불명확하므로 **누락된 측정 열률 또는 물리 보존법칙 위반이 아니다**.

Python 구현은 원본 ZIP/내부 SHA/노드·lane/원본 승인 interval을 직접 확인한다. 정상과 `python -O` 테스트 각각 25/25, 독립 Python standard library 46,080개 노드 전수 대조와 65자리 Decimal의 16개 선택 노드 재계산이 완료됐다. 핵심 원본 수치의 의미는 보존했으며, 예전 두 PR321 아카이브와 최신 성공 Actions 아카이브 사이에 `.csv.gz` 수치의 최하위 자릿수 차이(최대 상대 약 1.33×10⁻¹²)가 있어 **현재 성공한 HEAD의 아카이브를 우선**했다. 파일 바이트 비동일성과 물리적 의미 불일치를 동일시하지 않는다.

참고 문헌: Pawlik & Schaye, MNRAS 412, 1943 (2011), DOI https://doi.org/10.1111/j.1365-2966.2010.18032.x. 이 원전의 광자보존 다중주파수 수송 설명은 방법론 배경일 뿐, 이번 소스와 원래 solver에 대한 독립 검증을 대신하지 않는다.

## 5. 과학 상태와 다음 진짜 중앙 단계

이번 새 산출물: **46,080개 노드별 모형 source 대조 레코드** + 10개 온도 decile + 4개 channel summary + 24개 witness 레코드. 원래 46,080개 물리 노드는 재사용한 입력이다. 신규 실험 관측 0개, 신규 원본 IVP 0개. R1–R10/C1–C10 단일 scientific-unit checkpoint는 독립된 20개 실험이나 PR이 아니다.

```
CENTRAL_DAG=28/88_REPORTED
WORKING_DAG=33/88_REPORTED
PHYSICAL_FAST_DAG=4/7_REPORTED
CANONICAL_DELTA=0
ORIGINAL_FIRST_INTERVAL=BLOCKED_AT_TICK160/131072
OLD_LOGT_FAILED=2.1245050576368385e-4
OLD_STRICT_LIMIT=2e-4
L4=false; PRODUCTION=HOLD
NO_MERGE=true; NO_FORCE_PUSH=true; NO_MORE_IVPS=true
NO_TOLERANCE_RELAXATION=true; AUTO_NEXT_NODE=false
```

원본 PR #320–325 및 관련 부모 HEAD는 모두 수정하지 않았다. 실제 `F_h`와 `F_(h/2)`의 공통 부모 26-event map와 상관보존 joint Jacobian/remainder 계산을 원본 source owner에서 실행해야 한다. 이번 source 중간값 2점 근사를 원본 solver에 주입하면 안 된다. 최초에는 `[160,161]` 단일 tick과 기존 실패기록만 대조하고, 검증된 후 기존 승인된 실행 권한 하에서만 전체 interval로 진행한다. 새로운 atomic atlas/불필요한 메타 감사를 추가하지 않는다.
