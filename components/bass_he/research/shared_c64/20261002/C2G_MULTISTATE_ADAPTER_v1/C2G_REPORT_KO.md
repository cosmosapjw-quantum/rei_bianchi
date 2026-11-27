# C2g 다중 상태 adapter·공통 공간 reference pilot

C2g를 사전 등록한 범위에서 완료했다. 실제 분자 고유해 solver가 selected states와 exterior guards의 계수·고유값·잔차를 모두 반환하며, 정적 축대칭 ±m partner를 구성하여 C2f rank-5 projector/transport에 연결했다. R=4 및 4.25 a_A의 세 기저 해상도에서 NumPy 직렬과 Fortran/OpenMPI 경로를 실행했다. 새 단위 검사 52개, 독립 사전 검사 8개, 실제 결과의 등록된 판정 314개가 통과했다. 이 수들은 서로 겹치는 구현 불변량을 포함하므로 독립 물리 실험 수로 합산하지 않는다.

전체 C2와 production 인증은 HOLD다. 정확도 보존은 여기서 두 실행 경로 사이의 유한 Galerkin 결과 일치를 뜻한다. 연속체·PDE 오차나 최종 collision dynamics의 정확도 인증을 뜻하지 않는다.

## 구현과 물리 convention

내부 무차원 좌표는 x=r/a_A, 전자 에너지는 H/E_A를 사용한다. 정적 실수 spinless 두 점전하 Hamiltonian, ZA=1/ZB=2, nuclear repulsion 제외, 전자 무한원점 에너지 0, O charge-center 좌표계다. O 좌표의 핵 위치는 zA=-2R/3, zB=R/3이고, rmax=20 a_A의 Dirichlet sphere를 사용한다. 외부 영연장은 L² 비교를 정의하며 실제 외부 파동함수를 구한 것이 아니다.

한 sector당 행렬 조립·eigsh 호출을 한 번만 수행하여 모든 root를 보존한다. 고유쌍은 에너지 정렬 후 각 벡터의 최대 절대 계수가 양수가 되게 위상을 고정한다. 기존 단일 상태 solve API에는 이전 ground probe 위상 convention을 유지했다. 저장값은 실제 C†HC와 C†MC이며, 잔차는 ||Hc−EMc||₂/(||Hc||₂+|E| ||Mc||₂)다. 이 무차원 유한 행렬 잔차와 solver tol을 구별한다. SciPy generalized shift-invert 정의는 [공식 1.17.0 문서](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.sparse.linalg.eigsh.html)와 대조했다.

각 R/기저에서 m=0 root 6개와 |m|=1 root 3개를 독립 계산했다. 선택은 m=0 ordinal 1,2,3 및 ±1 ordinal 0이며, ground와 나머지 반환 root는 guard다. 결과는 selected5+guard7 열이다. ψ±1=G exp(±iφ)/√(2π), ψ0=G/√(2π)를 택하고 ψ−1=ψ+1*로 재구성했다. bright=(ψ+1+ψ−1)/√2, dark=(ψ+1−ψ−1)/(i√2)다. [DLMF 14.30](https://dlmf.nist.gov/14.30)의 표준 구면조화함수와는 명시적 phase convention을 구별한다. ± partner 일치는 독립 음의 m eigensolve 결과가 아니라 대칭성에 의한 구성이다. ETF/회전 동역학의 m 분리를 가정하지 않는다.

서로 다른 R의 계수 배열을 직접 내적하지 않는다. 모든 radial knot의 합집합에 r=16 경계를 더하고, 공통 O 좌표의 양의 가중치 W=r²dr dη dφ를 사용한다. 기본 격자는 radial7/η32/φ5, 95,200점이며 확인 격자는 9/40/7, 214,200점이다. 다항식 exact quadrature로 E†WE=M을 유도했고, 반환 root 공간에서는 (EC)†W(EC)=C†MC를 수치 확인했다. 전체 FEM mass matrix를 별도 수치 생성해 검사했다고 주장하지 않는다.

C2f에 전달한 Hsmall은 H_emb=E M⁻¹H M⁻¹E†W로 정의한 유한 embedded weak-form operator의 실제 C†HC다. 점별 PDE H 적용은 하지 않았다. 이 확장의 쓰이지 않은 주변 공간에서는 H가 0으로 작용하므로 그 공간을 실제 물리적 연속체로 해석할 수 없다. polar transport 이후 열은 혼합 frame이며 개별 고유상태 이름을 붙이지 않는다.

## 실행·정확도

lmax=12/20/28, radial base elements=24/32/40, degree4, radial assembly quadrature14를 사용했다. 실제 radial element 수는 핵 위치를 삽입하여 26/34/42이고, 가장 큰 행렬 차원은 4,843이다. 각 layout은 12개 sector solve/54개 독립 root, 두 layout 합계는 24 solve/108 root다. ± 재구성 후 총 144열을 비교했다. coarse/medium/fine의 반지름 격자는 서로 포함 관계가 없는 격자이므로 변분적 단조 수렴을 주장하지 않는다.

| 지표 | 측정값 | 사전 등록 기준 |
|---|---:|---:|
| 두 backend의 전체 반환 고유값 최대 차이 | 2.753353e-14 E_A | 2e-9 E_A |
| 두 backend의 selected projector 거리 | 1.556986e-14 | 2e-7 |
| 모든 selected/guard Gram의 spectral-norm 오차 | 6.514496e-14 | 2e-10 |
| 반환 frame mass 사상 최대 entry 오차 | 4.962697e-14 | 2e-10 |
| 유한 행렬 상대 잔차 최댓값 | 6.554825e-11 | 1e-10 |
| 기본/확인 격자 cross-R overlap 차이 | 2.997602e-15 | 2e-10 |

별도의 독립 검산은 각도 직교성을 해석적으로 적분하고, Vandermonde로 복원한 radial FEM 다항식에 6점 GL을 적용했다. 저자 3D grid 경로와 비교하여 trace(r²) 최대 차이 9.24e-14 a_A², 기저 projector 거리 차이 2.92e-16, cross-R projector 거리 차이 2.95e-15였다. solver·provider·embedding 모듈을 다시 사용하거나 고유해를 재계산하지 않았다.

| R/a_A | medium→fine selected ΔE 최대/E_A | projector 거리 | trace(r²) 상대 변화 |
|---|---:|---:|---:|
| 4.0 | 0.000961340064 | 0.00577746599 | 0.000690076855 |
| 4.25 | 0.00110863895 | 0.00662167901 | 0.000754133832 |

이 세 지표는 등록한 탐색 기준 0.005 E_A, 0.05, 0.02를 통과했다. 그러나 medium→fine 에너지 변화가 최대 약 1.11e-3 E_A이므로 물리적 오차를 backend 차이인 1e-14 수준으로 말할 수 없다. 현재 남은 불확실성은 계산 경로의 일치보다 기저·box·누락 sector의 정확도에 있다.

반환한 guard와 selected 사이의 최소 관찰 간격은 0.184513798 E_A로 등록 floor 1e-4를 넘었다. |m|≥2, 미반환 root, continuum은 검사하지 않았으므로 전체 spectrum gap의 하한이 아니다. fine cross-R 최소 principal overlap은 0.995883886이고 transport gate 0.5를 넘었다. r=16…20 내부 outer-layer의 selected-span 최대 집중도는 fine에서 3.872827e-10였지만 box 바깥 tail의 상한은 아니다. 유한 R 원자 채널 상관관계도 아직 증명하지 않았다.

## 성능과 실행환경 복구

Fortran binary64/O3/OpenMP/SIMD kernel, no-fast-math, no reassociation, fp-contract=off를 유지했다. 실제 새 host는 quota8코어/8GiB였고 NCP64는 실행하지 않았다. BLAS thread1, MPI는 독립 task rank-stride와 summary-only gather다.

| 실행 | 완료 wall time | sampled owned RSS |
|---|---:|---:|
| NumPy serial 1×1 | 1.894711 s | 99.25 MiB |
| Fortran OpenMPI 2×1 | 1.026307 s | 215.92 MiB |

이 한 번의 동일-workload 관찰에서 wall time 비율은 1.8461다. backend와 병렬도가 함께 변했으므로 순수 Fortran 가속률이나 반복 통계·64코어 scaling으로 해석하지 않는다. 각 layout의 sampled watchdog은 300초/4GiB였다. RSS는 50ms 표본이며 공유 page를 중복 계산할 수 있고 진짜 peak/할당 상한을 증명하지 않는다.

중단 후 host가 교체되면서 mpi4py가 없었다. 첫 MPI 시도는 MPI_INITIALIZATION에서 실패해 물리 작업 0개였고, 오류·로그를 보존했다. 고정 mpi4py4.1.2를 복구하고 독립 검토한 additive amendment에 따라 같은 native layout을 한 번 재시도했다. 코드·원 manifest·물리 기준은 바꾸지 않았으며 NumPy 기준 계산도 반복하지 않았다. 실패 포함 실제 세 launch의 총 wall time은 원래 600초 상한 안에 있다. 원본과 retry 기록을 분리했다.

## 결론과 다음 단일 연구

C2g adapter·공통 공간 사상·bounded finite-reference pilot은 완료했다. 전체 C2, continuum, production, Eq55는 열지 않는다. 다음 node는 `C2H_INDEPENDENT_DISCRETIZATION_AND_EXTERIOR_GUARD_AUDIT`다. 물리적 정확도의 지배 항을 가르기 위해 독립 discretization, angular/radial/box 축의 분리된 수렴, |m|≥2 exterior guard를 우선한다. 기존 24개 solve를 새 이름으로 반복하지 않고 저장된 coefficients와 이번 결과를 기준으로 새 변경분만 등록한다. 다음 구현 순서와 실행 전에 고정할 계약 항목은 C2G_NEXT_HANDOFF_KO.md에 정리했다.
