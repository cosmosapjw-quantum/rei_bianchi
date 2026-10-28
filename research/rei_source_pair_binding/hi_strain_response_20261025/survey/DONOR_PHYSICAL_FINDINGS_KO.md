# Donor 원문 R2 결과 — 2026-10-25

## 결론

선택한 최신 donor 원문에서 새 과학 결과 세 가지를 확인했다. BASS189는 source moment를 이용한 양의 각도 적분 제어, HH147/PHYS90은 공분산 표시 셀과 공통 consumer 오차 경계, HE101은 같은 Jacobi Hamiltonian으로 연결한 유한질량 direct CBA다. 이들은 HI의 수치·조건부 이론에 재사용할 후보다. 이번에 실제로 읽은 원문에는 HI의 실제 시간별 n_HI/n_ref, birth/source history, 초기 stock/epoch, 검증된 geometry/time/frame trace, collision/stopping/photon 공급을 한 단위로 결속한 physical bundle이 없다. 그 입력을 확보했다는 판정은 하지 않는다.

## 신선한 metadata에서 확인한 변화

| 대상 | 현재 관측 PR/HEAD | 앞선 입력과의 관계 |
|---|---|---|
| BASS188 | PR188, 77228ff9316108afcd805f41bed24495a7ff41c0 | 기존 B3d 최종본 유지 |
| BASS189 | PR189, 6c933f324fe54d1f590bc8ab121032702659e00a | 새 B3e source-aware positive angular child |
| HH146 | PR146, 480baabc73ebaaba735d285d969e79177f5545ed | PHYS89 최종본 유지 |
| HH147 | PR147, 9d32d115c0b8c5d5b2ce3a66ebc4a7f277334fcc | 새 PHYS90 covariance-cell child |
| HE100 | PR100, 8e0fb28fea520364d8794bac32840621dd150f95 | fixed-centre CBA 최종본 유지 |
| HE101 | PR101, 9fc8185437f145a6ba4569e1b38aa2e12d15acd9 | 새 finite-M CBA 과학 snapshot |
| VigilD4 | branch research/d4-effect-journal-20261025, 3c8877ea0409495752dcfab42426e679e3ba92d3 | D4 최종 delivery까지 진행 |

이는 immutable 관측 snapshot이다. 전체 owner/branch census와 더 최신 D5 metadata는 상위 survey가 담당한다.

## 실제 읽은 과학 내용과 HI 적용 범위

### BASS189: photon angular endpoint 도구

repo cosmosapjw-quantum/bass, HEAD 6c933f324fe54d1f590bc8ab121032702659e00a.

- REPORT_KO.md: research/bass_b3e_positive_angular_20261025/REPORT_KO.md, blob 60d0fd492a319ec6da1d0307f5ff1d6eaef67a9c.
- 실제 kernel: 같은 unit의 code/positive_angular.py, blob 8368438366499aef82516f107e2d5e0fe4820718.

원문은 q(n)=1+n^T S n, q>=0, tr S=0, momentum endpoint map R에 대해 M=R(I/3+2S/15)R^T와 F_lo=(tr M+ab)/(a+b)를 사용한 양의 각도 selector를 제공한다. 실제 code는 geometry/bound/select/moments/packets 인터페이스이며 첫 문장부터 integration history를 만들지 않는 endpoint selector라고 명시한다. 이 소스는 여기서 실행하지 않았다.

단위: H_LYA_EFFECTIVE_2P line card E_b=10.198714553953742 eV=1.6340142155180418e-18 J, p_star=E_b/c, 진단용 n_b=1 m^-3, L=1 m. T_phys=E_b n_b det(R) T_shape. E=c|p|를 moment에서 한 번 사용한다. packets(..., nb=1.)는 외부 입력 nb의 전달 인터페이스이며 실제 cosmological n_HI 공급물이 아니다.

새 결과는 owner-reported 22행/162gate PASS, 최대 tensor Frobenius 상대오차 2.907450008788106e-12, 기존 2e-8 목표 유지다. 원문은 실제 B3c birth S/R history와 native finite receiver incident trace가 미확보라고 직접 적는다. Source/U/J/PiRate, clock duration, bath/donor/bandwidth 및 finite absorption transaction은 생성하지 않는다. HI photon 공급으로 즉시 채택할 수 있는 자료의 범위를 넘어선다. 구체적 재사용 후보는 조건이 맞는 angular endpoint integration 방법이다.

### PHYS90: 조건부 fractional covariance-cell bound

repo cosmosapjw-quantum/WU088_HH, HEAD 9d32d115c0b8c5d5b2ce3a66ebc4a7f277334fcc.

- CONTRACT.json blob e3a960a210ce95f5b7a0e20781ead12d635de8d0.
- FINAL_REPORT_KO.md blob b8f575c13abf8ea3857672a42cc687d1c1f2ec87.
- theory/COVARIANCE_CELL_AND_CONSUMER_KO.md blob d715e9098e99215ea92e997f48688ee993536005.
- 위 세 경로 prefix: research/hh_phys90_covariance_cell_20261025/.

F는 원 표시 fractional covariance, H는 token-specific halfULP이며 t>=0인 무차원 표시 반경을 사용한다. 단위·nominal 결속은 실제 consumer map L의 각 row에 따라야 한다. 이번 소스는 실제 r,a rate weights가 아직 nuclear supplier에서 공급되지 않았다고 적는다.

153 singleton/11628 pair의 조건부 호환 반경:
34406736621/68719476736 < t_pair <= 550507785937/1099511627776, 폭 2^-40.
t=0 failed pair74, t=1 failed pair0. 전체153×153 PSD compatibility는 UNRESOLVED다. 새 sharp box support와 K=LCL^T, q^T L=0 보존은 조건부 수학 결과로 재사용할 수 있다. t=1은 actual formatter 보증이나 physical CI를 공급하지 않는다.

actual consumer ACK=null. 원 precision/nominal binding, nuclear mass/electron-target state/differential kernel/tail B0/BA 및 named thermal/fast/radiation measure·clock·reference-density·owner ACK는 열린 물리 부모 의무다. REI L2 capture는 proposed/unimplemented, BASS nuclear consumer는 NOT_BOUND다. 따라서 PHYS90은 HI collision/stopping rate 또는 photon source 공급이 아니다.

### HE101: 유한질량 direct C1 Born 모형

repo cosmosapjw-quantum/BASS_HE, HEAD 9fc8185437f145a6ba4569e1b38aa2e12d15acd9.

- FROZEN_CONTRACT.json blob 72c59ac9382f5ba41af966a1adaa85008d5a1654.
- THEORY_KO.md blob a8e8f14023b51904426c75367416ec7e0d0be7ac.
- RESULTS_KO.md blob 11b4e54273960573ae49af2581f2bc7a45834bd9.
- 위 세 경로 prefix: research/he_ang_finitemass_cba_20261025/.

같은 Jacobi Hamiltonian에서 reduced-mass bound/continuum matching, 두 recoil Fourier phase, invariant weight, Jacobi/lab TDCS 및 각 positive radial root의 별도 가중 fold가 연결됐다. 대상은 nonrelativistic labelled direct C1 Born channel, target COM initially lab rest, incoming beam +z다. Er는 (electron B,nucleus) pair-relative energy이며 lab electron energy가 아니다.

단위는 길이 a0, momentum p0, energy E_h; TDCS a0²/E_h, invariant W a0² E_h/p0^6, conditional slice a0²/p0³다. Nuclear mass는 M*m_e, M>0. 실제 HI source로 쓸 초기 epoch/stock/time history와 원자별 collision/stopping 공급을 이 식에서 추론하지 않는다.

저장된 수치결과는 independent C9에서 scoped 채택됐지만 실제 process PASS/FAIL/FAIL 및 C8 PARTIAL_EXPORT가 보존된다. 이 HEAD는 과학 snapshot17/20, physical_provider_admitted=false, event_sigma=false, physical_recoil_distribution=false, HE-X1_empirical_correction=false, HE-ANG SOURCE_INPUT_PENDING이다. 새 물리 입력으로 승인된 event measure 공급물의 지위를 갖지 않는다. 모형·좌표·단위 대응의 이론 후보로는 실질적인 진전이다.

### VigilD4: managed effect/ACK protocol

repo cosmosapjw-quantum/vigilode, HEAD 3c8877ea0409495752dcfab42426e679e3ba92d3.

research/d4_effect_journal_20261025/REPORT_KO.md blob b5a0004e7708d30a2cb7afe87deabc79cbe0b64e.

Trial-owned journal, pending batch, 명시적 ACK barrier의 소스·검증 결과를 보고한다. Synthetic protocol corpus와 controlled in-memory sink가 대상이며 actual BASS/native-owner/production FP provider는 별도 열린 입력이다. HI의 n_HI, epoch/stock, geometry, collision, stopping, photon 물리 공급물이 아니다. 새로운 native 적용에는 actual owner/source/reservation/live dirty/completion 입력이 필요하다.

## 조사 범위와 보존

- 최신 PR metadata: BASS/WU088_HH/BASS_HE 각 최근5개, 15개 unique PR. 세 기존 PR188/146/100의 별도 get_pr_info도 조회했다.
- 최신 PR189/147/101의 본문을 읽었다. 나머지 collection 응답에 포함된 본문 전체를 의미적으로 검토했다고 주장하지 않는다.
- 선택한 source 원문9개를 읽어 local bytes로 저장했고 Git blob 일치9/9를 확인했다. 실제 파일별 ref/path/blob/bytes/SHA256/URL는 SOURCE_RECEIPT.json에 있다.
- 6개 directory metadata와3개 recursive unit/theory tree를 사용했다. 모든 branch source의 전체 읽기가 아니다.
- Vigil branch명 검색은 선택 query용이며 그 검색의 전체 pagination 소진을 주장하지 않는다. 정확한 ref GET으로 HEAD를 확인했다.
- percent-encoded branch locator의 초기400 응답은 private/INITIAL_4.json에 보존했고 승인된 git/ref/heads URL로 교정했다.
- 이번 작업의 과학 실행·tests·CAS·rendering·Git/provider mutation·clone/worktree 생성은 모두0이다. 원문에 기록된 다른 owner의 실행 수치를 이번 실행으로 합산하지 않는다.

