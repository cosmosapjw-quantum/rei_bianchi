# C2 독립 검토

판정은 `ACCEPT_SCOPED_UNRESOLVED_AUDIT`이다. 이번 bounded audit는 실패를 보존한 유효한 연구 결과이며, C2 과학적 종료는 승인하지 않는다. `DIRECT_COMMUTATOR_MISMATCH`, `STATE_TRACKING_AMBIGUOUS`, `FINITE_R_MAGNITUDE_UNRESOLVED`를 유지한다.

독립 검토자는 eigensolver·operator·continuation·analysis를 작성하지 않았고, 새로운 eigensolve나 과학적 재계산을 실행하지 않았다. 원 사용자 C2 계약, C1b 인계, 코드, 기존 계산 결과를 읽고 식·원점·부호·내적 measure와 scalar gate 산술을 확인했다. 39 prolate pair 파일과 8 spherical state 파일의 size/SHA, 계약 및 grid/continuation 입력 hash, 실행 당시 source identity를 현재 파일과 대조했다. 검토 대상별 정확한 SHA는 JSON에 고정했다.

## 통과한 범위

- R=0.25, 0.5, 1, 2, 4의 다섯 명시적 점은 등록한 pointwise gate를 통과한다. 점 사이 연속 구간의 인증은 아니다.
- 일곱 점 전체에서 h/p/tail energy 증분 최대는 6.51177e−11 E_A, direct L_O 증분 최대는 1.96643e−12 ħ이다. 이 값은 경험적 method spread이며 exact-state error enclosure가 아니다.
- R=0.5, 2, 8에서 signed charge-center O spherical/prolate 비교와 등록된 ℓ 증분 gate가 통과한다. R2 spherical 증거는 재계산하지 않았다.
- Direct Cartesian derivative, 독립 p derivative, value-only Coulomb force lane의 분리가 유지된다. L_O=L_B+z_B p_x 원점 관계와 dark azimuthal selection 식을 확인했다.
- 공통 O의 실제 공간 내적은 올바른 좌표변환과 rho d(rho) dz measure를 사용한다. 서로 다른 상태 기저의 coefficient dot product로 대체하지 않았다. 모든 m=1 인접 local step은 등록한 gate를 통과했다.
- Fortran은 binary64, 고정 point/patch 합 순서, 독립 output SIMD 및 patch OpenMP를 사용하며 fast-math·reassociation·FMA contraction을 허용하지 않는다. 현재 C2 실제 MPI 실행은 local 4 ranks/3 workers이며 NCP64 실행이 아니다.

## 닫히지 않은 두 수치 문제

R8의 force q20→28 증분은 최대 5.64713e−8, R16은 최대 3.51358e−6으로 등록 기준 1e−8을 넘는다. R16_h의 O direct/torque 차이는 1.36603290012971e−7로 1e−7 기준을 넘는다. 동일 frozen R16_h 상태와 q28에서 원 Python reference와 native force 차이는 8.88178e−16이다. 따라서 그 상태·order에서 native 구현만의 변경으로 이 불일치를 설명할 수 없다. 그 parity는 과학적 force 수렴의 증명이 아니다.

Duffy corner의 큰 종횡비는 유력한 다음 진단 대상이다. R16 base의 첫 radial/각도 cell 폭 비는 약 1:54.6, h refinement는 약 1:81.9이다. Duffy map 후에도 (h_x+h_y u)^−3 종류의 빠른 변화를 남길 수 있으므로 공간 refinement가 고정 order force quadrature를 오히려 어렵게 할 수 있다. 이는 코드와 geometry에서 얻은 추론이며 해결된 원인 인증이 아니다.

m=0의 11→12, 12→13, 13→14, 14→15, 15→16 overlap step은 최대 허용 order48에서도 q32→48 증분이 1.05307e−7부터 1.92786e−7로 기준 1e−7을 넘는다. 실제 normalized overlap은 약0.93167~0.93172이고 전체 34 step의 최솟값도0.897385이다. 실패 원인은 등록된 quadrature gate이며 물리적 branch switching이 관측되었다고 말할 수 없다. 첫 실패 이후 ground 누적 위상이 None으로 유지되는 fail-closed 처리가 올바르다.

## 구현 관찰과 판정의 한계

초기 검토에서 발견한 C2 launcher의 미지원 numpy option과 continuation의 expected archive identity 대조 누락은 science code freeze 전에 수정되었다. bright_nonzero의 ×10 tolerance 비교는 추가 operational magnitude-separation heuristic으로만 해석해야 한다. 그것은 새로 등록된 과학적 error bound도 exact nonzero certificate도 아니다.

다음 단일 dependency는 `C2b FROZEN_STATE_INTEGRATION_CLOSURE`다. 현재 상태를 고정한 채 R8/R16 force 및 위 다섯 m=0 common-O overlap의 독립 적분 수렴을 사전 등록한 integration 계약으로 조사해야 한다. 새로운 eigensolve, threshold 완화, 결과에 맞춘 상태·phase 변경이 필요하다는 근거는 현재 없다.

전체 collision-relevant R 범위, hidden crossing, rank-five cluster, continuum gap/error enclosure, asymptotic closure, collision evolution, cross sections, Eq55, NCP64 scaling은 이번 결과로 닫히지 않는다. scientific_PROMOTE=HOLD, full_certificate_fail_closed=true 및 기존 production/Eq55 gates를 유지한다. 본 검토 시점에 author 최종 report는 아직 생성 전이며, 최종 문서 일치 여부는 별도 읽기로 확인한다.
