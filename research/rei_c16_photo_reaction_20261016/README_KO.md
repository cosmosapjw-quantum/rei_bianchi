# REI C16B 후속: 광원 스펙트럼 보존 및 H/He 양의 photo-reaction 수송

2026-10-16 KST. `physmath-research-loop`의 bounded **R5/C5–C8** 신규 독립 연구 단위.

## 소스·범위·선행 결과

- 원본 REI 연구 보존: [PR149](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/149) `d5246c500522ffe4efe904f3206a60f9541c7dbd`.
- 최신 실제 native FLRW production 별도 진행: [PR150](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/150) `fd684a90da951ff5d7be9fb711acb1f4b3644f5d`, `HANDOFF.json` 상태 `SOURCE005_ACTUAL_FULL_PAIR_RUNNING_AFTER_ALL5_SCREEN_PASS`. 현재 5-case short screen PASS. q512/q1024 full history는 완료 판정하지 않음.
- 독립 real-Verner Bianchi ray oracle: [PR152](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/152) `bbbd18b5c16eff70bc32ba4296360dceb9060ec4`; original Verner ASCII SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`의 H I, He I, He II **3행만** 실제 테이블 수치 그대로 코드에 고정. 원본 full 185-row 파일로의 byte identity는 주장하지 않음. 파생 구현의 원자모델은 Verner et al. (1996), ApJ 465, 487, [DOI 10.1086/177435](https://doi.org/10.1086/177435).
- 사용 가능한 선행 source/범위: BASS_HE [PR66](https://github.com/cosmosapjw-quantum/BASS_HE/pull/66) native MD14 original spectral split; bass_cr [PR72](https://github.com/cosmosapjw-quantum/bass_cr/pull/72) 단일 고정시각 photo-thermal RHS; REC [PR95](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/95) HyRec H-only synthetic-history gate; BASS [PR163](https://github.com/cosmosapjw-quantum/bass/pull/163) FD96 stress susceptibility; WU [PR91](https://github.com/cosmosapjw-quantum/WU088_HH/pull/91) finite screened outgoing collar **NOT physical HH rates**.
- 문헌 방법 비교: Friedrich et al. (2012), [MNRAS 421, 2232](https://academic.oup.com/mnras/article/421/3/2232/1077406), [Mellema et al. C2-Ray](https://arxiv.org/abs/astro-ph/0508416), [Pawlik & Schaye TRAPHIC](https://doi.org/10.1111/j.1365-2966.2010.18032.x). 문헌들은 species-resolved photon conservation과 heat 경로를 뒷받침하며, 여기의 수치 연산자의 신규성 입증을 뜻하지 않음.

## 정의, metric 및 물리 계약

Metric signature `(-,+,+,+)`:

\[
 ds^2=-c^2dt^2+a^2[e^{-2b}(dx^2+dy^2)+e^{4b}dz^2],\quad
 E_j(a,b)=\frac{q_j}{a}\sqrt{(1-\mu_{0j}^2)e^{2b}+\mu_{0j}^2e^{-4b}}.
\]

각 `Node(q_ev,mu0,n_per_h)`는 양의 source-resolved photon count/초기 수소핵 1개당이며, `q`는 `a_ref=1,b_ref=0`에서의 eV 단위 comoving-reference 에너지. 음성·비유한 값 금지. Cold gas fractions `(HI,HII,HeI,HeII,HeIII)`도 H nucleus 1개당이며 H=1, He=0.08 예시는 manufactured 초기상태. 실제 재결합률·source emissivity 데이터가 아님.

Verner 1996 photo-fit의 H I/He I/He II 문턱은 `13.60/24.59/54.42 eV`, 화학 **binding**은 별개로 `13.598434599702/24.587389011/54.41776 eV`를 사용. 1 Mb=`1e-18 cm²`; 이 실험에서 `n_H`는 고정한 proper `cm^-3`, proper `dt`는 초, `c=2.99792458e10 cm/s`.

수송은 `photon E(q,a,b)`에서 실제 Verner cross section을 매번 재평가하므로 signed shear에 따라 이전 subthreshold node가 ionizing으로 다시 돌아올 수 있으며, 비물리적인 영구 passive 제거를 하지 않음. 이 경로에는 서로 다른 방출 시각의 angular chart 변환이나 full intensity spectral closure는 아직 없음.

## 구성적 연산자

하나의 노드 N 및 하나의 흡수원자 fraction X에 대해 다른 항을 고정하면

\[
 \dot N=\dot X=-kNX,\quad k=c\,n_H\sigma(E)\quad[s^{-1}].
\]

`D=|N0-X0|`, `M0=min(N0,X0)`이면 정확한 양의 pair subflow는

\[
 M(t)=\frac{M_0 D e^{-kDt}}{D+M_0(1-e^{-kDt})},\quad
 M(t)\underset{D\to0}{\longrightarrow}\frac{M_0}{1+kM_0t}.
\]

`expm1` 및 non-singular `phi=(-expm1(-kDt))/(kDt)`로 계산. Pairwise reversible ordering `L_1(h/2)...L_K(h/2)L_K(h/2)...L_1(h/2)`의 **Strang 조합**을 구성하면 fixed terminal geometry / nH 및 no additional physics source에서 2차이다. 이는 서로 다른 pair 연산이 교환한다는 주장이 아니며, He I→He II→He III 순차 원자 전이가 실제 가스 변수로 매번 갱신된다.

한 pair에서 `delta`개의 광자가 species `i`에 흡수되면

- photon N loss=ionizations `delta`
- photoenergy loss=`E*delta`
- binding increment=`chi_i*delta`
- electron photoheat=`(E-chi_i)*delta` (양수)
- photon z-momentum removal=`E mu delta/c`, 현재 gas Euler/momentum partner는 **OPEN**.

이 실험에서는 **기하수송 → 명시적으로 공급된 양의 source 생성 → chemistry** 순서. 수송 전 광자만 기하 work에 기여하며 source는 마지막 시각에서 생성됨. 전체 energy ledger:

\[
 U_{\gamma,0}+U_{\rm src}=U_{\gamma,1}
 +W_{\rm geom}+\sum_i\chi_i A_i +\sum_i Q_{{\rm heat},i}.
\]

`W_geom=Sum N_j(E_j(initial)-E_j(final))`은 음수도 가능하고, chemical pool transfer가 redshift work로 계산되지 않음. HeI 전이 시 생성된 HeII는 photoionize되는 다음 channel에서 사용한다. Thomson, RR/DR, CI, CX, gas thermal temperature, CMB reservoir, stellar EOS, baryonic recoil, full self-gravity는 구현 범위 밖.

## 실제 로컬 계산 및 검증 상태

실행환경은 이 대화의 **ChatGPT sandbox Python 3.13**, 사용자의 Ubuntu 워크스테이션 또는 NCP가 아님. Native subagent `NOT_RUN`: 현재 host dispatch tool 없음. Remote Desktop Commander 사용량 한도로 새로운 접속과 NCP compute를 실행할 수 없음. 이 한계와 이번 Python 테스트는 별개의 상태.

- `python -m unittest -v test_source_aware.py`: **22/22 PASS**. 최초 20 테스트에서 signed transverse blueshift의 부호를 뒤집은 테스트 어설션 1건 실패. 공식 `R(mu0=0)=exp(b)`에 맞추어 테스트 입력의 부호만 교정, 원본 첫 실패 로그 보존.
- 실제 3 species gas+photon ODE를 **독립 SciPy DOP853** (`rtol=2e-12, atol=2e-14`)로 실행하여 복수 pair Strang source의 시간 수렴 검사. 1,2,4,8,16,32,64,128,256 substeps에 대해 마지막 4개 로그-로그 error 기울기 **-1.99919**, 마지막 절대 상태 차이 `3.7938619468214085e-8` (256 steps). Positive number/energy/nuclei 보존 검증.
- 실제 Verner node 때문에 동일한 초기 `N=1`, `U_q=60 eV/H`를 갖는 양의 스펙트럼 `[60 eV:1]` vs `[40 eV:.5,80 eV:.5]`의 HeII photoionizations가 각각 `0.004563002636355888/H`, `0.0011483602332259535/H`, 차이 `0.0034146424031299347/H`. 즉 **N/U 두 모멘트가 흡수 후 정확한 species 결과를 결정하지 못하는 명시적 조건부 반례**. 이것이 general no-go novelty theorem이라는 주장은 하지 않음.
- 독립 Bianchi source-free geometry work control 및 helium nuclei/HI conservation, one-channel exact semigroup, HeI→HeII→HeIII sequential chemistry, 300 seeded random positive inputs, strong tau limit, source births, low-energy and Emax rejection 검증.
- local Wolfram CAS, `D>0` exact pair differential equation, initial condition, semigroup와 `D→0` limit: `{0,0,0,0}`.
- 모든 수치는 `study_results.json`에 보존, 원본 실패는 `first_test_stdout.log`; 실제 실행 stdout은 `local_tests.log`, `study_stdout.log`, 그림 `reaction_refinement.png`.

## 재현 절차

```bash
python -m unittest -v test_source_aware.py
python run_study.py
python build_figure.py
```

Python 3.13, numpy, scipy, matplotlib 필요. 실행 중 `output stdout / result JSON`을 덮어쓸 수 있으므로 immutable scientific archival version을 유지할 때는 복원 복사본에서 실행 권고.

## Next gate

1. 原 source PR150 current transport state와 코드 identity, Grackle Case-A collision owner, MD14 source time/weights와 동일 단위·proper time·energy source identity 정합 확인.
2. Photon nodes의 energy-grid/quadrature convergence 및 gas-neutral change에서 source-consistent photon spectral projection; photon group moments와 실제 flux·thermal+chemical ledgers를 matched comparison.
3. Proper H(a), nH(a), b(a), H/He recombination/thermal source 동적 결합, baryon recoil, full signed cosmological histories 및 CPU64 성능. 현재 코드는 **production solver NOT_ISSUED**, observational predictions NOT_ISSUED.

이 연구는 원래 REI/PR150 native 코드·체크포인트·NCP 실행·설정에 어떠한 mutation도 하지 않음. 향후 최적화/병렬화 claim은 동일 오차 예산·실제 NCP 실행에 의존.

## 게시·백업 실제 상태 (2026-10-16)

- Source-restorable ZIP: `REI_SOURCE_AWARE_HE_PHOTO_REACTION_20261016_v1.zip`, 102560 bytes, SHA256 `52190fea5889be372a8baeb5b14c66b1d89563e6cb49cc397fcbc8b53df120e7`; 11 science payloads and manifests.
- Google Drive backup: `/Google Drive/rei_bianchi_research_backups/REI_SOURCE_AWARE_HE_PHOTO_REACTION_20261016_v1.zip` (object ID `10Uk7BBdF2MvqpxLlC9cdUiyGFuQpVX_U`). Remote whole ZIP independently downloaded; SHA256 byte-identical.
- Dropbox upload: BLOCKED/NOT_RUN because available upload action requires chat file parameter injection, and desktop rclone connector reached monthly capacity. Do not claim dual cloud.
- NCP heavy execution and user-local Ubuntu: NOT_RUN this unit (Remote Desktop Commander monthly quota exceeded). ChatGPT isolated local 22 tests and independent SciPy reference are actually executed.
- GitHub branch is **independent scientific reference**, not production integration; preserve PR150 full-history source005 currently executing on NCP.
