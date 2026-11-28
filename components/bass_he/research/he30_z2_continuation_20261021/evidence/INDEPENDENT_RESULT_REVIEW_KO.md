# D3 독립 결과 검토: LRS Bianchi I의 matter/radiation 분리 pilot

검토일: 2026-10-21. 검토자: `/root/physics_literature`. 검토자는 D3 ODE runner 및 이번 새 후처리 구현을 작성하지 않았다. 한 번의 범위 한정 결과 검토이며, 새 ODE 실행·재시도·benchmark는 모두 **0회**다.

## 1. 판정과 대상

**과학 데이터와 이를 제시한 4개 그림을 `PASS_SCOPED_PRELIMINARY`로 채택한다.** 독립적인 초기 matter/radiation signed quadrupole을 가진 collisionless non-tilted LRS Bianchi I의 고정 유한 격자에서, 평균 redshift `z̄=20→2`의 231개 nominal 궤적과 6개 resolution guard가 완결되어 있다. 새 그림을 실제로 열어 검토했으며 결과는 §8과 JSON sidecar에 기록했다.

그림 생성에 필요한 원데이터가 이미 존재하므로 새 z=4→2 continuation을 실행할 이유가 없다. 원본 `CHECK.json`의 `PENDING_INDEPENDENT_RESULT_REVIEW`는 당시 실행 기록으로 그대로 보존한다. 이 문서와 `INDEPENDENT_RESULT_REVIEW.json`이 후속 독립 결과 채택 기록이다. 이는 실측 제약·연속 parameter 공간 전체·native H/He reionization 결과의 채택으로 범위를 넓히지 않는다.

원본 archive:

`/workspace/scratch/39bb8df06b79/investigation/backup/recovered/REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz`

SHA256: `7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498`.

직접 읽은 복구 root:

`/workspace/scratch/39bb8df06b79/investigation/backup/recovered/REI_UNIFIED_D3/`

분석 source: PR147 commit `3b85dedce84d37b3e165da00685a8a984950aafe`의 pinned vendor. 원본 실행의 코드 identity와 복구된 파일들을 SHA256로 대조했다. 운영상 직렬화 수정 전후 runner identity는 각각 `49d4464ecb4682846ace0d07411d3a9f9e49bc494fa8d641b567306725374d97`, `a7bf1a82140778a37a957e4dea4b42a2dbf227c8175c68804439305c70b51b64`이며, 실제 물리 kernel/config/solver/runtime 변경은 없다.

## 2. 직접 읽은 증거와 재사용한 검토

직접 읽은 source는 `adapter.py`, `components/component_adapter.py`, `components/unified_pilot.py`, `components/plot_extension.py`, 그리고 `vendor/canonical_fv.py`, `vendor/species_hierarchy.py`, `vendor/lrs_boltzmann.py`다. 원래 contract, component contract, source manifest, B1/B2 manifest·CHECK·STATUS, 운영 수정 기록, 초기 contract review를 함께 읽었다.

`review_saved_d3.py`를 한 번 실행하여 model/solver를 import하지 않고 237개의 저장 배열을 읽었다. 이 계산은 SI 단위와 Frobenius 정의, signed 성분 합, 초기 축, state/time 대응, parameter 집합, 6개 guard의 저장 endpoint 비교만 수행했다. 모든 read path와 SHA256는 `INDEPENDENT_DATA_READBACK.json`에 수록했다.

동일한 prefix/tail 검사를 중복 수행하지 않고 backup 담당자의 `D3_RAW_REUSE_READBACK.json`을 재사용했다. 이 audit는 237개 모두의 raw/tail/prefix raw/input/result hash, exact 121-point prefix, exact join, exact 32-point append, finite arrays와 153 epochs를 확인했다. 과거 100개 직렬화 실패의 독립 raw audit도 `PASS_DATA_ONLY_RECOVERY`이며 failed case는 없다. 직접 읽은 리뷰와 신규 readback은 서로 다른 역할을 가진다: 전자는 provenance와 완전한 재시작 상태, 후자는 현재 결과의 물리 정의와 admissible scope를 확인한다.

## 3. 유한 parameter 격자와 완료 상태

| 구분 | 실제 구성 | 판정 |
|---|---|---|
| 초기 shear norm | `Σ_F,i={0,0.0003,0.001,0.003,0.01,0.03,0.1}` | 초기 `s_i≥0` orientation 고정 |
| 초기 signed matter stress | `P_m,i={−0.0003,−0.0001,0,0.0001,0.0003}` | radiation과 독립 축 |
| 초기 signed radiation stress | `P_r,i={−0.001,−0.0003,0,0.0003,0.001}` | matter와 독립 축 |
| joint plane | `7×5×5=175` nominal | 모든 실제 sample 존재 |
| 기존 radiation baseline | 91 nominal | 이 중 35개가 joint plane과 동일 |
| unique nominal | `175+91−35=231` | physical axes와 case ID 모두 중복 없음 |
| refinement guard | 6개 | matching nominal과 같은 물리 축 |
| 전체 | 237개 | 모두 COMPLETED; nominal `40×153`, guard `56×153` |

이 계산의 `P_m`·`P_r`는 아래 정의의 signed amplitude이다. 사용자 요청의 비음수 크기 `Π_m`·`Π_r`는 각각 절댓값이다. 부호와 취소 정보를 보존해야 서로 반대인 성분을 구분할 수 있다. gamma와 neutrino는 각자의 moment state를 갖지만 초기 brightness amplitude는 공통이고 collisionless operator도 같으므로, 두 radiation 종을 독립 parameter로 탐색한 결과는 아니다.

## 4. 식·norm·단위·물리 closure

코드는 orthonormal 공간 성분에서

\[
D=\mathrm{diag}(-1,-1,2),\quad \sigma_{ab}=sD_{ab},\quad
\pi^X_{ab}=p_XD_{ab},\quad p_X=(P_{\parallel,X}-P_{\perp,X})/3
\]

를 쓴다. 따라서

\[
\Sigma_F=\frac{\sqrt6|s|}{H},\quad
P_X=\frac{\sqrt6\kappa_t p_X}{H^2},\quad
\Pi_X=|P_X|,\quad \kappa_t=\frac{8\pi G}{c^2}.
\]

`s,H`는 초⁻¹, `p_X`는 J m⁻³이다. 통상 Einstein 상수 `κ_E=8πG/c⁴`를 쓰면 `κ_t=c²κ_E`로 변환한다. vendor의 half-contraction shear norm `√3|s|/H`와 사용자 Frobenius norm은 `Σ_F=√2 Σ_half`로 구분되어 있다.

\[
\dot s+3Hs=\kappa_t(p_m+p_r),\qquad
\Pi_{\mathrm{tot}}=|P_m+P_r|,
\]
\[
\pi_m:\pi_r=6p_mp_r,\qquad
\sigma:\pi_X=6sp_X.
\]

실제 계산은 signed stress 합을 Einstein source로 사용한다. norm의 합을 source로 넣거나 초기 cancellation을 isotropy로 오인하지 않는다. isotropy control은 `Σ_F=P_m=P_r=0`일 때만 적용한다.

matter sector는 기준 epoch에서 전체 matter density의 0.1을 배정한 `m/T_ref=30`의 비바리온 collisionless canonical-momentum component와 나머지 dust다. 고정 Killing-momentum weights가 보존되고 `rho,p_perp,p_parallel`을 해당 moment quadrature로 계산한다. 별도의 phenomenological stress-relaxation closure를 도입하지 않았다. `ne_source=None`이며 실제 H/He chemistry·전리원·photoheating 또는 전자의 자기일관 feedback은 실행하지 않았다. 이 부재는 이번 collisionless preliminary pilot의 명시적 모델 범위다.

앞선 물리 노트의 algebra 검산은 canonical moment에 대해

\[
\rho_m'+3(\rho_m+\bar p_m)+6b'p_m=0
\]

를 packet 수준에서 유도했다. Wolfram 결과는 정확히 0, 저장된 4-state 직접 numerical check의 최대 scaled residual은 `8.840402339423898e−16`이다. 이 결과는 같은 vendor hash에 대한 moment 정의 검산으로 재사용하며 전체 trajectory에 대한 별도의 ODE 오차 증명으로 확대하지 않는다. 식과 원전은 `PHYSICS_REUSE_KO.md`, 실제 tool 영수증은 `TOOL_EVIDENCE.json`에 있다.

## 5. z=4 join과 수치 결과의 범위

각 궤적은 `x=ln(a/a_ref)`, `a_ref=1/21`을 유지한다. 원래 121개 epoch가 `x=0→ln(21/5)`이고 기존 full state에서 시작한 33개 tail epoch의 첫 점은 그 endpoint와 같다. 중복 join 1개를 제외한 32개를 이어 붙여 `x=ln7`, `a≈1/3`까지 총 153개 epoch가 된다. `b`, signed shear, 4개 radiation energy/number hierarchy와 proper-time accumulator를 포함한 모든 40/56개 state가 보존된다. 변경된 `a_end`는 domain endpoint이며 reference normalization과 cosmology는 유지된다.

평균 redshift는 `z̄=1/a−1`이다. 방향별 관측 redshift를 뜻하지 않는다. `elapsed_proper_s`는 z̄=20부터의 경과 시간이며 절대 cosmic age는 아니다.

이번 independent saved-data pass의 최대 차이는 다음과 같다.

| 검토 항목 | 최대 절대 차이 또는 잔차 |
|---|---:|
| 초기 3개 물리 축 | `1.0408340855860843e−17` |
| SI stress → signed `P_m` | `0` |
| SI stress → signed `P_r` | `3.2526065174565133e−19` |
| SI shear → `Σ_F` | `4.163336342344337e−17` |
| half/Frobenius adapter | `0` |
| signed component sum | `2.168404344971009e−19` |
| tensor cross identity | `4.235164736271502e−22` |
| gamma/nu number monopole − 1 | 모두 `0` |
| Hamiltonian reconstruction relative residual | `2.220446049250313e−16` |

마지막 Hamiltonian 항목은 코드가 같은 algebra로 H를 재구성하므로 **construction consistency**다. 독립 제약전파 또는 Einstein evolution 정확도의 증명으로 취급하지 않는다.

모든 저장 epoch에서 H와 각 energy가 양수다. massive 최소 cell population은 `2.1837545547005117e−65`, gamma/nu reconstructed brightness의 64-node 최소값은 모두 `0.5424751213728825`다. brightness 검토는 저장 epoch와 64개 angular sample에 한정된다.

6개 guard는 refined `ellmax=12, radial×angular=48×24`와 nominal `ellmax=8,24×12`를 **물리 초기 축으로 재매칭**했다. 저장 endpoint에서 다시 뺀 차이는 원래 CHECK와 모두 exact 일치한다. 6개 중 최대값은 `|ΔΣ_F|=3.5701298281608576e−13`, `|ΔP_m|=1.0678464744937922e−14`, `|ΔP_r|=1.6561865811073884e−16`, `|Δb|=7.122080702970379e−14`, `|ΔH/H|=3.468336728928989e−13`다. 기존 threshold `2e−6`를 통과한다. 선택된 6개 resolution control의 endpoint 일치이며 모든 연속 parameter에 균일한 정확도를 보장하는 인증은 아니다.

## 6. 실제 분리 stress 결과와 해석

다음 값은 완성된 nominal raw의 z̄=2 endpoint에서 직접 읽었다. 표의 `u=√6s/H`는 signed shear이다.

| 초기 `(Σ_F,i,P_m,i,P_r,i)` | 최종 `P_m` | 최종 `P_r` | 최종 `u` |
|---|---:|---:|---:|
| `(0,+3e−4,−3e−4)` | `+5.79655317e−6` | `−3.98448076e−5` | `−3.14595906e−5` |
| `(0,−3e−4,+3e−4)` | `−5.79607716e−6` | `+3.98424684e−5` | `+3.14586629e−5` |
| `(0.1,+3e−4,+1e−3)` | `+2.19164103e−6` | `+4.76327992e−5` | `+5.31143210e−3` |
| `(0.1,−3e−4,−1e−3)` | `−8.80950281e−6` | `−2.07930270e−4` | `+4.94282701e−3` |

처음 shear와 total stress가 0이어도 matter와 radiation이 각각 비등방이면 isotropic state가 아니다. 첫 두 행은 성분의 서로 다른 evolution 때문에 초기 total cancellation이 유지되지 않고 shear가 생기는 실제 예다. nonrelativistic·작은 shear 극한에서 matter stress는 대략 a⁻⁵, radiation은 a⁻⁴로 희석되므로 이 경향은 물리식과 정합적이다. 이 scaling은 해석용 근사이며 저장 trajectory를 power law로 대체하지 않았다.

정확한 isotropic control `(0,0,0)`은 전체 trajectory의 `max(|Σ_F|,|P_m|,|P_r|)≤2.3516109906448768e−19`다. 반대 부호 두 궤적의 크기는 가까우나 정확히 같지 않으며, nonlinear LRS 모델에 가정하지 않은 부호대칭을 적용하지 않았다.

## 7. 100개 직렬화 실패의 provenance 처리

100개 case는 raw/tail 저장 이후 `np.bool_`의 JSON 직렬화 단계에서 실패했다. 완전한 요청 epoch·exact endpoint·prefix/tail identity가 보존되어 독립 data-only recovery로 완료가 확인되었다. `nfev`, 원래 in-memory `solver_success/message`, worker timing/RSS가 유실된 case에 대해서는 해당 값을 null로 남겼다. 복구된 metadata를 solver의 실제 관측 로그로 꾸미지 않았다.

운영상 고친 부분은 native bool 변환, 기존 허용 상한 안의 case deadline, 원래 identity를 보존한 repair sidecar다. 137개 당시 pending tail은 수정 runner로 완료되었다. **이번 검토는 어느 case도 재실행하지 않았다.** 이 provenance 한계는 명시적이며, 현재 raw를 이용한 고정 격자 preliminary plot 채택을 막는 물리적 결함은 발견되지 않았다.

## 8. 그림 검토 기록

원래 D3 archive에는 z=2 결과 그림이 포함되어 있지 않았다. 이번에는 parent가 작성한 `research/he30_z2_continuation_20261021/src/analyze_saved.py`와 그 결과를 검토했다. 후처리 source는 원본 raw/receipt/source hash, case axes와 완전한 epoch identity를 대조한 뒤 저장된 observables를 stack한다. `histories.npz`는 원래 `raw_y`를 대체하지 않는 후처리 전용 자료다. `--plot-saved`는 그 compact product hash를 대조하여 새 ODE 없이 그림만 만든다.

다음 네 PNG를 실제로 열었다. 최종 파일의 SHA256는 JSON sidecar의 `figure_review.files`에 기록했다.

| 파일 | 실제 확인 |
|---|---|
| `parameter_sweep_z2.png` | 동일한 175개 joint endpoint의 matter/radiation norm을 별도로 표시. 초기 shear 색 범례, 0을 보존하는 symlog 축, 겹치는 sample 설명 확인. |
| `sweep_all_shear_planes.png` | 7개 고정 shear plane마다 25개의 실제 값. signed 비균일 초기 축을 categorical로 명시하며 interpolation 없음. color 하한 아래 isotropic residual은 `0*` 및 `<1e−7` 설명으로 표시되고 원자료에는 유지. |
| `time_evolution_z20_to_z2.png` | `Σ_i=0.003`에서 5개 대표 seed의 `Σ_F,Π_m,Π_r,Π_total`. mean z̄=20→2, z̄=4 join, 153 epochs 표기 확인. 수정 후 네 비음수 norm 축 모두 0부터 시작함을 재확인. |
| `signed_cancellation_evolution.png` | 양·음의 초기 성분 취소와 isotropic control을 구별. signed `P_m,P_r,P_total,√6s/H`의 부호와 0선, z̄=4 join이 모두 보임. |

첫 rendering에서 norm time plot의 symlog 자동 y범위가 넓은 음수 빈 공간을 만든 점을 지적했다. `set_ylim(bottom=0)`라는 표시 수정 한 번 후 해당 PNG만 다시 열어 해결을 확인했다. 이 수정은 data와 science model에 영향을 주지 않는다. `selected_histories.csv`에는 signed `P_total` 열도 추가되었다. 추가 과학 검사·재적분은 수행하지 않았다.

확인한 최종 norm PNG SHA256: `080fb03ea95a8164ae9a0b4f9b8204762c88763f4b41a36cf63ab12a95a52fb4`. 첫 시각 검토와 파일 hash 기록 사이 parent의 재생성이 병행되었으므로, 수정 전 화면의 hash는 확립되지 않았고 그에 대한 임의의 hash를 주장하지 않는다. 최종 hash는 위와 같이 재확인한 수정 후 그림에만 결합했다.

## 9. 유지할 범위와 handoff

채택 범위는 현재 frozen background, canonical massive matter fraction·mass ratio, collisionless radiation, 초기 positive shear orientation, 명시된 signed finite grid와 z̄=20→2이다. 초기 CMB/관측 제약, radiation 종별 독립 IC, 일반 non-LRS geometry, baryonic H/He 반응과 reionization observable은 이번 데이터가 평가하지 않았다. 그 결과를 주장하려면 해당 새 항·초기 조건·donor 계약이 필요하지만, 현재 pilot 완료를 위해 그 추가 작업을 선행시키지 않는다.

다음 과학적으로 유용한 단계는 baseline을 재적분하는 일이 아니라, BASS_HE에서 provenance가 확정된 `n_e(a)` 또는 H/He rate/thermal donor를 준비하여 photon의 `Γ_T=cσ_T n_e` 항에 대한 명시적 adapter를 별도 실험으로 연결하는 것이다. neutrino와 비바리온 matter stress에 electron collision을 대입하지 않는다. 오늘의 최적화는 불변 canonical quadrature·Legendre matrix 캐시 및 저장 history의 batch 후처리에 한정해 물리 결과를 보존한다.

이 검토의 source/raw 판정은 완료되었으며, publication·backup·새 postprocessor 성능 주장은 parent의 각각 독립된 영수증을 따른다.
