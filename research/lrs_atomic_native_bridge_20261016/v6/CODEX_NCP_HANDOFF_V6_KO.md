# Codex 자동 실행 Handoff: REI-LRS V6 → 실제 PR150 source-on FLRW 다단계

**이 문서를 받은 Codex가 직접 실행할 일이다. 사용자는 아무것도 다운로드·전송·실행하지 않는다.** GitHub 최신 source 및 필요시 기존 사용자 승인 범위의 Dropbox/Google Drive/NCP를 Codex에서 직접 사용한다. 이 문서의 `REI-LRS V6 midpoint`는 이미 ChatGPT 샌드박스에서 시험한 Python **독립 reference**다. 원본 NCP/Rust production에 아직 반영되었다고 주장하지 않는다.

## 1. 읽어야 하는 현재 source와 권위

- Repo `https://github.com/cosmosapjw-quantum/rei_bianchi`, 프로젝트 `AGENTS.md` 우선.
- 원본 V5 PR #158: `research/rei-lrs-certified-atomic-native-bridge-20261016`, **확인 당시 HEAD** `3006d48026b422f4c3db030638eb3091ac517734`.
- 새 V6 연구 Draft PR 및 branch: GitHub에서 `research/rei-lrs-v6-midpoint-casea-20261016`를 확인한다. 기본이 되는 PR #158 head SHA와 V6 commit HEAD 및 source blob identity를 다시 읽는다.
- V5 소스 `research/lrs_atomic_native_bridge_20261016/{RESEARCH_V5_KO.md,recomb_dominated_v5.py,study_v5.py,donor/rate_table.py,donor/owner_grackle_rates_129.csv,native_pr150_source_step.rs}`.
- V6 신규 소스는 `research/lrs_atomic_native_bridge_20261016/v6/{README_V6_KO.md,midpoint_recomb_v6.py,recomb_thermal_midpoint_v6.py,test_midpoint_v6.py,run_dense_multichannel_v6.py}`와 나머지 실행기·실측 결과.
- 실제 PR #150 FLRW production의 **현재 HEAD를 새로 읽는다**. 이전 검사상 `0f6965f79326e58d52bc9023065dccd75132c49b`, package-only recovery 진행. `research/flrw_covariant_transport_20261015/LATEST_RESUME.json`이 옛 실행 snapshot일 수 있으므로 PR body, 최신 resume, current original Rust source 및 사용 가능한 NCP raw folder를 비교한다.
- 보조 repo: [BASS_HE HE23 PR #70](https://github.com/cosmosapjw-quantum/BASS_HE/pull/70) TOTAL H/He nuclei density parity 및 Newton chemical+energy gate; [bass_cr C21 PR #75](https://github.com/cosmosapjw-quantum/bass_cr/pull/75) `q_PR150=q_C20/a_ref` 및 source-age temporal quadrature/positive photon work; [rec_bianchi PR #98](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/98) 초기에 해당하는 HyRec FULL H/He로 **재이온화 Case-A 공급원으로 혼합하지 않는다**.

### 이미 검증한 실제 숫자 (중복 비용 금지)

- V5 실제 NCP 저밀도 시험: Python 25/25, Rust 20/20 PASS, native point parity 968항 최대 상대오차 1.30e-7, native source-on **단일 단계** event/energy junction 상대잔차 ~2.60e-15, 1.32e-15.
- Grackle 3.4.1 Case-A source owner/129점 interpolant는 10–24k K 내부만 사용. 원본 Rate table sha256 `33396b071c840b40ad79d68ee626de59f12bb2cf0b1df2159627efd7fde42aec`.
- V5에서 고밀도 nstar=.1 cm^-3 source-free H-only 재결합은 1차 수렴: `DeltaX=.0003125`에서 T 오차 .00157188 K.
- **V6 샌드박스 경량 실행**: 동일 H-only `DeltaX=.0003125`의 implicit-midpoint T 오차 약 8.9e-7 K; H-only/He-only/HHe-mixed source-free Grackle dense Radau 수렴 2차, V4+V5+V6 샌드박스 pytest **114/114 PASS**. V5 reference 일부분을 새로운 구현으로 수정하지 않았다.

## 2. 코드 변경 기작과 수학

각 재결합 종 j에 대해 처음 ion count `I0`, electron count `e0`, gas thermal energy `U0`를 받는다.

`a(Tmid)=PairExact(I0,e0, DeltaX*nstar_cm3*exp(-3Xmid)*alpha_j(Tmid)/(H/H0)/H0_s)`.

`Q(Tmid)=a(Tmid)*Lambda_j(Tmid)/(alpha_j(Tmid)*EV_ERG)`.

`Tmid = (U0-Q(Tmid)/2)/(1.5*kB*(npart0-a(Tmid)/2))`.

실제 구현은 `midpoint_recomb_v6.py`의 brentq constrained 1D solve다. 원래 fixed-alpha pair map을 버리는 것이 아니라 *rate/cooling evaluation point*만 중간 상태로 바꾼다. `npart0-A/2`에는 해당 재결합에서 자유전자 하나가 감소하는 효과가 포함된다. End gas stocks/thermal/binding/escaping photon energy update가 각 event에 대해 양수성과 보존성을 유지한다. **donor domain을 벗어나면 FAIL, 무의미한 extrapolation/clamp/energy residual correction 금지.**

한 channel의 frozen-rate exact subflow를 temperature-dependent alpha/cooling에 그대로 적용하는 것이 V5 dense source-free에서 1차 오차를 유발했다. Wolfram 2차 Taylor 확인:

`frozen - continuum = -(DeltaX^2/2) k*k_prime * [B(B+D)]^2 + O(DeltaX^3)`;

`k(midpoint)`에서는 2차 계수 잔차 0. 하지만 전체 coupled PR150 transport/source/hydro scheme의 2차 수렴을 자동 주장하지 않는다.

## 3. 자동 소스 확보·실행

사용자에게 ZIP을 다운로드하라고 하지 말고 GitHub에서 clone/fetch한다. Dirty 원본 checkout을 변경하지 말고 별도 Git worktree를 선택한다. V6 independent branch와 PR150 original owner를 서로 다른 worktree에 read-only로 확보한다. PR150 owner source/commit과 native binary identity를 기록한다.

로컬 Python 환경에서 target 테스트:

```bash
cd <isolated_rei_checkout>/research/lrs_atomic_native_bridge_20261016/v6
python3 -m pytest -q test_midpoint_v6.py
python3 run_dense_v6.py
python3 run_dense_multichannel_v6.py
python3 run_mixed_v6.py
```

기존 검증 114건을 처음부터 무조건 전부 반복하지 말고 변경한 source에 대한 9개 V6 targeted+관련 V5 native parity로 시작하라. 필요할 때만 확장한다.

### NCP 직접 접속 (이미 승인됨)

```bash
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

NCP `s1a0e5abed09`, 64 vCPU / 125 GiB, Rust `/root/.cargo/bin/rustc`. Host workload를 조회한 뒤 기존 R9/BASS/REI native job과 충돌하지 않는 create-only 작업 폴더에서 실행한다. 기존 작업을 종료/재시작하거나 checkpoint/raw를 덮어쓰지 않는다.

**실제 새 최소 native 목표**: PR150의 `AxbiSource::inject → CovariantTransport::prepare → PreparedAbsorption::evaluate → IgmPhotoInput → igm_point_rhs`를 원본 immutable initial state에서 **연속된 여러 단계**로 실행. 동일 initial spectral support, gas nuclei (total-H density), He abundance, source budget, thermal state, geometry와 time variable에서 `dt`, `dt/2`, `dt/4` (가능하면 `dt/8`)를 비교한다. 각 스텝별 photon production/absorption, absorber and electron changes, thermal/binding/escape, expansion redshift/shear work를 하나의 physical ledger로 연결하여 동시에 보존시킨다. 단순 single-step Euler를 반복했다고 production solver와 동등하다고 주장하지 않는다.

적어도 source-on FLRW/zero-shear에서 실제 Grackle selected RR+DR/cooling과 native full RHS의 차이를 CI/CE/freefree/CMB 항별로 분리한다. BASS_HE HE23의 total hydrogen nuclei density and simultaneous Newton fraction+energy residual gate를 재검토한다. bass_cr C21 source-age q normalization/time integration도 대조한다.

유효원자 온도 10–24 kK 경계를 넘어가면 그 실험은 `OUT_OF_DOMAIN`으로 보존하고 다른 승인된 물리적 donor를 확보하기 전까지 확대하지 않는다. 훨씬 강한 stiffness에서는 추상적 성능 비교보다 실제 Newton residual, positivity, conservation, independent IVP agreement를 우선한다.

## 4. PASS/HOLD 및 마감

- 이론 도출/Python midpoint: V6 source-free standalone testing PASS (scope limited).
- Native Rust source-on MULTISTEP: NOT_RUN in V6 sandbox, Codex가 실행해 판정할 의무.
- 전체 reionization, full photon spectrum reprocessing, Case B, CMB/thermal native production: HOLD until appropriate source-native validation.

각 스텝의 canonical source/input/status/output SHA, `nHtot` vs `nHI`, independent ODE event/energy and empirical order, resource time, failure history를 남긴다. Negative values or source-domain violation, existing owner interference, per-event+energy simultaneous acceptance failure 발생시 정확한 계통만 stop하고 유효 결과는 보존한다. 테스트가 불합격이라고 임의 tolerance를 넓히지 않는다.

변경된 코드와 원시 재현 결과를 V6 독립 Draft PR(또는 그 다음 제한적 PR)에 push, **원본 PR150/v3/rux merge 금지**. Google Drive `REI_RESEARCH_BACKUPS/rei_bianchi/REI_LRS_MIDPOINT_V6_20261016/` 및 Dropbox `bianchi/research_backups/rei_bianchi/REI_LRS_MIDPOINT_V6_20261016/`에 create-only 백업한다. **실제 원격 readback SHA256**을 두곳에서 확인하고 실패는 별도 상태로 남긴다.

완료시 한국어로 original/after commit, 수치적 1차→2차 메커니즘, 실제 native source-on multi-step results, dt convergence, nuclei+electron+photon+thermal+binding+escape+shear work, resource usage, independent source-parity, dual cloud remote SHA, open physical HOLD, exact next runnable task를 보고한다. 필요한 준비/파일 전송은 Codex가 수행하며 사용자 추가 다운로드·터미널 입력 요청은 하지 않는다.
