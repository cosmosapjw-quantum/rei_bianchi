# HE25: proper-time birth transport and independent temporal reference

HE24 f3227484c6f349915c18edba8a041c3311928417에서 파생한 별도 opt-in lane이다. HE21/23/24, 기존 PR과 production은 불변이다. 원본 microphysics는 rei_bianchi f7830e2f55e7a1938bc3c98f61b60651f8dae474. 실제 측정과 판정은 results/REPORT_KO.md, VERIFICATION.json, CASES.csv를 따른다.

## 물리와 수치 경로

- physics.py: 고정 covariant momentum 좌표에서 실제 proper-time source `s(t)=H(a) dN/dln(a)`, 50,000-K truncated BB와 isotropic birth angle의 Jacobian pushforward, 원래 Verner cut과 physical binding, native total H/He density, proper-time clock, 분리된 reservoir RHS 및 sparse Jacobian.
- transport.py: 실제 birth proper-time 노드에서 양의 Duhamel source 적분. 각 no-cutoff-crossing substep의 evolving gas/geometry midpoint opacity를 사용한다. 이 frozen-midpoint hazard는 명시된 유한 시간 근사이며 연속 변화 opacity는 독립 reference가 직접 평가한다. event energy와 redshift/shear work는 실제 proper-time 노드에서 별도 적분한다. native gas는 implicit midpoint, source-free CI/RR/DR/thermal/escape/CMB는 원본 소유다. h=0이며 외부 gas work=2Hu를 한 번만 계산한다.
- reference.py: 같은 격자·source·native physical RHS를 adaptive Radau/DOP853로 적분한다. Duhamel map이나 Newton step을 공유하지 않는다. 연속 **시간** 기준해이고 연속 energy/angle 기준해는 아니다.
- owner_server.rs/native.py: 원본 rlib에 연결한 persistent evaluator. 기존 immutable CLI와 3개 상태에서 exact parity. 더 높은 정확도나 upstream Grackle 직접 동등성을 새로 발명하지 않는다.
- birth_cohorts.npz(raw private backup): proper t_birth/a_birth, positive source counts, Eref/mu0, conserved `c*k_perp`, `c*k_parallel`(eV). 실제 E_birth와 direction은 immutable k와 a_birth로 복원한다. 서로 다른 birth history를 N,U만으로 추정하지 않는다. 같은 conserved mode의 선형 superposition은 cohort provenance를 보존하면서 누적한다.

## 한계와 재현

이산 source는 매 순간 positive quadrature를 정규화하여 총 `H S_x`를 맞춘다. 이 정규화는 source의 연속 spectrum을 정확하게 만드는 것이 아니다. m은 넓은 energy 구간을 정제하지만 moving-edge 좁은 strip의 four-node panel은 고정이다. 독립 source moment control이 이 한계를 정량화했다. 따라서 continuous-spectral convergence는 HOLD다.

조건부 짧은 z20→19.998, 원래 초기 fraction/temperature와 prescribed source total을 유지한다. dN/dln(a)는 여전히 prescribed source이며 실제 MD14 emissivity/full EoR가 아니다. source RHS, gas/thermal scales, binary64, 원본 1e-9 밀도 gate와 3e-12 수지 gate는 유지한다. 시간 정제의 Newton 종료는 3e-15로 **강화**했으며 초기 3e-12 control과 별도 비교했다.

NCP 실행 경로는 `/root/HE25_NCP_BIRTH_20261016`이다. `src/run_study.py --mode pilot|temporal|resolution --out NEW_EMPTY_PATH`가 bounded cases만 실행한다. 재실행에는 새로운 빈 경로가 필요하다. 완료된 suite를 변경 없이 다시 실행하지 않는다. 테스트는 `OPENBLAS_NUM_THREADS=1 python -m pytest -q -p no:cacheprovider tests`; 실제 compiled binary가 필요하며 mock을 native PASS로 해석하지 않는다. build/source/binary/dependency identity는 provenance 및 결과에 있다.

완전한 raw와 cohort data는 create-only cloud restoration archive, 소스·compact 결과와 raw native point stream은 GitHub에 보존한다. Git bundle도 별도로 포함한다. 백업의 실제 성공과 byte readback은 BACKUP_RECEIPT.json을 따른다. private SSH 정보와 source PDF는 새 공개 파일에 없다.
