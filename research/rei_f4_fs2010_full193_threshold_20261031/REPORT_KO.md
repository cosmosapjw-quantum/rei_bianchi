# REI F4 | 완전 BASS193 저에너지 전자 문턱 재구성 결과

**물리 데이터:** 원본 PR300 30개 emission source의 검증된 3,554행에 나머지 source를 계산해 더한 **18,528개 original-grid emission–arrival index 행**과 192개의 arrival 표, 동일 H/He frozen EOS를 사용한 별도의 192행 thermal coefficient 표를 생성했다. `k=0` zero-emission 192행은 원본 PR287과 identity를 보존하도록 명시적으로 채웠으며, `k=192` 최종 방출은 도착 셀이 없다.

**원전:** Ferrett et al., PRA36,3172 (1987), Langer et al., PRA43,1652 (1991), Furlanetto & Stoever, MNRAS404,1869 (2010). FS2010의 <10.2 eV terminal convention만 실행했고 3 keV Table 1은 적용하지 않았다.

**정량적 진전:** conditional original PR287 16×4 quadrature first-absorption photoelectron energy `6.749242464433259e-11 eV/baryon`; sub-10.2eV `8.581099847924098e-12 eV/baryon`, 비율 `0.12714167394554643`. 이전 top30의 `[0.1265429281303,0.131499495798]` 범위가 원래 이산 연산자에서 정확한 수치로 축소됨. `H I + He I + He II + Li I` 최초흡수 합 `4.374110632809568e-12` events/baryon. `N_sec,HI`의 per-electron discrete 상한 `2.943495108593608e-12 events/baryon` (구 relax bound `4.963249567403269e-12`).

**열원 반응:** 조건부 source의 FS terminal 누적 `1.8210951142160422e-23 erg/Href`; 최대 정적 `Tdot` coefficient `1.770297769640156e-23 K/s`. **실제 물리 하한·열화학적 ΔT 아님**, source amplitude의 양의 하한 0, 실제 thermalization time 미확인, 정확한 native REI17–BASS21 연산자 동등성 미확인.

**직접 검증:** 16/16 Python physical tests, full 18,528행의 원본 PR287 kernel과 species별 source-weighted per-pair 비교, whole source PR297 photon and energy budget ≲4.44e-16 상대오차; Wolfram 네 substep algebra identities exactly zero. 새로운 cosmological IVP 0.

**2026-10-31 원본 숫자:** Working 33/88, Central 28/88, F4-fast 4/7; canonical +0; 이번 source-scoped auxiliary 1/1. Production HOLD, F4 PARTIAL, NO_MERGE, NO_FORCE_PUSH, AUTO_NEXT_NODE=false. Genuine distinct-author R6/C9 NOT_RUN.

**독립 경로:** PR #296 (native Rust HHe RHS), #298 (21-종 hybrid weak Jacobian), #299 (frozen tangency/energy port)는 parent PR300과 병합하지 않음. 새 결과는 해당 branch의 계산을 대체하지 않음.

**남은 원전 입력:** FS2010 공식 보간 도구 링크 `https://cosmicdawn.astro.ucla.edu/codes_and_tools.html` → `https://cosmicdawn.astro.ucla.edu/elec_interp.tar`. 원본 `x_int_tables/`, `elec_interp.c`, `xray_interp.c`를 실제 파일로 획득·SHA-256 고정하고 입력 species ionization fractions와 열화/확장 시간 적격성을 확인한 다음에만 next deposition으로 이동. Li 1S/3P 실험 covariance와 BASS native K vs lab n2+n3 operator는 별도 미해결.
