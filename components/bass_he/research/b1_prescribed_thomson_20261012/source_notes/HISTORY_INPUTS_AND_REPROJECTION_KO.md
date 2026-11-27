# B1 입력 수신과 공통 시계 재투영

## 수신한 실제 원본

REI PR104 계보의 `REI_ACCEL01_C02B_FINAL_20261010.zip`을 기존 Dropbox object
`id:BSpOijBcT10AAAAAAD3yhw`에서 한 번 내려받았다. 실제 30,729,916 bytes와 SHA-256
`3d114d3bea604035e2873b804e965605ea8ff9dc06caebe82e5dadfa735e2857`가 Git에 보존된
[최종 전달 영수증](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/publication/DELIVERY_RECEIPT.json)과 일치했다.

이번 실제 연구 입력에 필요한 원본 11개만 선택 추출했다. 각 파일은 archive의
`RESTORE_MANIFEST.json`에 있는 bytes/SHA와 맞췄고, 두 `history.npz`는 각 원래
`COMPLETE.json`의 data SHA와도 일치했다. 전체 219개 과학 파일의 새 복원 검사를
수행한 것은 아니다. 기존 완료 ODE·원자·수송 suite를 실행하지 않았다.

- FLRW: `inputs/research/broad_history_20261010/evidence/RUN002/flrw_n16384/history.npz`,
  1,179,779 bytes, SHA `93d16f478d2cc28b1f7b3d5287f07432b0e17107b3dd3f684890e77f6133cfa4`.
- Bianchi initial r=+0.1: 같은 경로의 `rp01_n16384/history.npz`,
  1,288,533 bytes, SHA `a2dcad2a81c4ff46b39890366d6fa5c37341e027e741687e35311fbebe66cd17`.
- 같은 RUN002의 `flrw_BASS_CELLS.csv`, `rp01_BASS_CELLS.csv`: 각 16,384개의 원래 N4 셀.
- 원본 `model.py`, `background.py`, 외부 입력·과학 계약과 두 완료 영수증.

Git의 RUN002 폴더에는 257-point `preview.csv`만 있으며 dense NPZ와 N4 CSV는 없다.
따라서 preview를 보간하여 원래 dense history인 것처럼 사용하는 경로를 선택하지 않았다.
입력 복원 내역은 `HISTORY_INPUT_RESTORE.json`, chart 검사와 값은
`HISTORY_INPUT_SCHEMA_AND_CHECKS.json`에 있다.

## Chart, 단위와 closure

두 원본은 정확히 같은 16,385개 `u=x=ln(a/a_i)` 좌표를 갖는다.
`a_i=1/21`, `u_end=ln(21/5)`, 평균 부피 redshift는 z=20→4다.
`t_s`는 해당 배경의 초기점에서 센 proper/normal seconds이고 `H_s`는 s^-1이다.
`ne_cm3`, `nH_cm3`는 proper cm^-3, N4 `ne_eff_m3`는 proper m^-3의 셀 평균이다.
NPZ의 `Q`는 HII filling factor이며 Stokes Q가 아니다.

배경은 `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, `s=db/dt=s0 a^-3`,
`H^2=Hfid^2[Omega_m a^-3+Omega_Lambda]+s0^2 a^-6`인 dust+Lambda LRS Bianchi I다.
기준 파라미터는 h=.6774, Omega_m=.309, Omega_b h^2=.02230, Y=.2453이며,
`nHe/nH=Y/[4(1-Y)]`. 원래 근사는 mH=mp, mHe=4mp다.
상대 scale axes는 초기 gauge에서 b_i=0으로 정의한다.
Bianchi 원본의 마지막 b는 .05905212749063961이다.

전자 이력은 R15 유효 방출률, HG97 Case-B, 고정 ionized-zone T=20000 K,
C_HII=3, HII 영역 안 HII+HeII, 바깥 중성 기체라는 원래 closure다.
`ne=(nH+nHe)Q`이며, HeIII·잔류전자·열진화·RCT spectrum은 이 원본에 없다.
평균 z를 관측 방향별 observed z로 해석하지 않는다.

## 공통 B proper clock에 대한 유도

[원본 model.py](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/f66929c23ea3fa6e39dd4808e5b27d136c568a03/research/broad_history_20261010/model.py)는 각 u 셀의 midpoint에서 H, nH+nHe, A=S/H, B=R/H를 동결한다.
원래 Q는 그 셀에서 capped Q'=A-BQ의 해석해이며, 적분된 Q를 직접 보존한다.
history 기호 h에 대해

\[
J_{h,i}=\int_{u_i}^{u_{i+1}}Q_h(u)\,du,\qquad
\Delta\tau_{h,i}^{\rm REI}
=\frac{c\sigma_{\rm REI}n_{\Sigma,i}}{H_{h,i}}J_{h,i}.
\]

F와 B의 nSigma와 u 셀은 동일하다. 따라서 같은 F의 Q-cell measure를 B proper
clock `dt_B=du/H_B`에 처방하면

\[
\Delta\tau_{F\to B,i}^{\rm BASS}
=\frac{\sigma_{\rm BASS}}{\sigma_{\rm REI}}
\frac{H_{F,i}}{H_{B,i}}\Delta\tau_{F,i}^{\rm REI}.
\]

이것은 **원래 동결 셀 표현에서의 정확한 재가중 관계**다. 서로 다른 시간의
`ne_eff`를 순간 밀도로 복사하는 것이 아니며 Q ODE를 다시 적분하지 않는다.
H(mid)는 원본 배경식을 원래 u-midpoint에서 평가하고, Q의 셀 적분은 기존 tau
증분에서 그대로 재사용한다. 새 timestep이 여러 원본 셀을 포함하면 셀 깊이를 합한다.
그 큰 step 안에서 수송과 산란을 어떻게 배치할지는 B1의 새로운 순서 오차이며,
이 입력의 총 optical depth 일치만으로 수송 정확도가 입증되지는 않는다.

두 Thomson 상수는 기존 N4와 동일하다.
`c=299792458 m/s`, `sigma_REI=6.6524587321e-29 m^2`,
`sigma_BASS=6.6524587e-29 m^2`, 비율은 .9999999951747164다.
추가 a^-3, 1+z, Doppler 인자는 없다.

## 실제 제공한 입력 모듈과 국소 검사

`inputs/project_frozen_histories.py`의 `load_projection()`은 원본 NPZ identity를
확인하고 공통 u, b, Q, proper clock, native/B-clock 셀 깊이를 반환한다.
`coarsen(data,nsteps)`는 16384를 나누는 step 수에 대해 원래 optical-depth measure를
합하고 일치하는 u/b/clock 경계를 선택한다. 새로운 Q 또는 geometry ODE는 없다.

실제 생성한 `inputs/B1_FROZEN_PROJECTED_INPUTS.npz`는 1,635,474 bytes,
SHA `e79806ac898e34de90a69c392467d56bcbe753f10a0028766a36d102c4b60d48`다.
`u,z_mean,b_B,b_F,Q_B,Q_F,t_B_s,t_F_s,nH_cm3`는 edge 배열,
`dt_B_s,dt_F_s,H_B_mid_s,H_F_mid_s,depth_B,depth_F,depth_F_on_B`는 cell 배열이다.

| BASS 상수 규약의 구간 깊이 | 값 |
|---|---:|
| F history / F clock | .03744182108819489 |
| B history / B clock | .03741570883862251 |
| F history / B clock | .03742736057725936 |
| B history minus F history, 같은 B clock | -1.1651738636847542e-5 |

독립된 대수 경로인 원래 N4 셀 평균 × 저장된 B 셀 duration과 새 H-ratio 경로의
비교는 최대 상대차 1.39366e-12, 합계 차 1.38778e-17이었다. 이 차는 누적 t를
차분할 때의 저장 roundoff와 맞는 범위다. coarsen의 depth 합계 보존은 검사한
128–16384 step에서 최대 절대차 1.38778e-17이었다. 판정은
`PASS_SCOPED_INPUT_PROJECTION`이며 기존 history 정확도·새 B1 수송의 검증 판정은 아니다.
실제 검사와 module SHA는 `HISTORY_PROJECTION_VALIDATION.json`에 있다.

## 재사용할 복사장 초기조건의 실제 근거

BASS의 [modeb.py::planck_state](https://github.com/cosmosapjw-quantum/bass/blob/2325a42c0954e949bb57f53976d0c9a9d9a9a362/bianchi/q/modeb.py)는 T_of=None일 때
등방 Planck occupation `f(q)=1/expm1(q)`를 초기화한다. 기존
`tests/test_q7b_modeb.py`는 ln q in [-8,5] 등의 범위에서 이 초기조건의 수송/충돌을 사용하고,
`tests/test_q4_radial.py`는 Planck spectral shift 및 power-law control을 사용한다.
세 파일은 `inputs/upstream_bass/`에 remote Git blob과 byte-identical하게 보존했다.

이는 원래 benchmark의 **무차원 스펙트럼 형태**다. dimensional 복사 온도를 고정한
observed CMB 입력이 아니다. B1이 재사용하면 `q=E_i/(k_B T_gamma,i)` 등의 에너지
척도를 명시하고, 처방된 gas T=20000 K와 T_gamma,i를 혼동하지 않는다.
초기 비편광 Planck test field와 이후 zero photon emissivity를 사용하는 것은
source-free transport benchmark 선택이며 R15의 유효 방출률에서 스펙트럼을 추론한 것이 아니다.
Stokes/coherency의 전체 상수 normalization은 사용한 수송 변수의 정의를 별도로 기록한다.

Q7b 원문에는 중요한 구현 제약도 있다. 비등방 프레임에서 같은 covariant q slice는
같은 physical momentum p가 아니므로, Thomson의 방향 혼합은 **공통 physical p**에서
수행해야 한다. 기존 Planck benchmark에서 발견된 이 구분을 새 연결에서도 유지한다.

## 현재 확인 범위

관련 현재 open PR 10개씩을 갱신순으로 확인했다. REI 최신 관련 head들은
PR112 `2cae28f...`, PR83 `6bf81d2...`, PR113 `efb6362...`, PR110 `17f8d0d...`이며,
BASS는 PR141 `d520c5e...`, PR140 `2325a42...`, PR139 `41fa2d5...`였다.
이 조회에서 새 B1 실행 PR는 발견하지 않았다. 모든 branch의 전수 검색이라는 뜻은 아니다.
`HISTORY_SOURCE_CATALOG.json`에 정확한 refs와 benchmark 원본 identity를 기록했다.

이번 담당 작업은 입력 복원·source 확인·한정된 재투영이다. 새 history ODE 0,
새 photon transport 0, Git mutation 0이다. B1 transport 구현·실행·과학 검토는 root가 통합한다.
