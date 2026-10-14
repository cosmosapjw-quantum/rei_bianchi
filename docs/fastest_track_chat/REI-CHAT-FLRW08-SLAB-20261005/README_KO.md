# FLRW08: 실제 첫 수락 반 단계의 연속시간 잔차

Run: REI-CHAT-FLRW08-SLAB-20261005. Logical task: REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL.
판정: FIRST_COMMITTED_HALF_SEMIDISCRETE_DEFECT_ENCLOSED__PAIRED_GLOBAL_PHYSICAL_HOLD.

## 이번 결과

실제 F08 T0_FLRW 첫 macrostep의 첫 committed half, 0..625000000 s를 대상으로 했다. 원 actual_records[0].audits[1]을 사용하며 버린 full-step audits[0]을 사용하지 않았다. Native와 기존 campaign을 다시 실행하지 않았다.

고정된 실제 에너지 node의 barycentric redshift map에서 연속시간 generator lambda_j=H*E_j/(E_j-E_(j-1))를 도출했다. 같은 node와 f64 계수들을 정확한 실수로 해석한 semidiscrete 목표이며, literal finite-precision program의 dt->0 극한이나 spectral continuum 주장이 아니다. 각도합이 닫히는 FLRW에서 gas4+active photon9의13변수 계를 사용한다. 13.6eV 아래 photon은 no-feedback passive reservoir로 남고 삭제하지 않는다. 물리 chi와 fit cutoff를 구분하며 최저 active gap에 실제 index15를 쓴다.

실제 두 endpoint의 선형 재구성에 대해 64개 시간 interval 전체의 residual을 감쌌다. 초기 scaled cube radius=.02, sup|F|<.008853, Picard contraction<.442865로 시간구간 전체의 tube를 닫았고 T는[48426.01,51611.75]K다. 이를 원 endpoint root box로 대신하지 않았다.

Interval Jacobian/lognorm 및 Metzler 비교원리를 사용해 첫 half endpoint의 오차를 제한했다. 위쪽으로 반올림한 상계는 xHII1.169e-7, xHeII2.698e-11, xHeIII2.182e-12, w2.945e-8 eV/H, lnT5.830e-8, T.002915K다. 행렬 지수 상계는 shifted positive Taylor64항과 norm-tail로 계산했다.

원 Python 원자식에 기반한 두 독립13D IVP는 모두 상계 안에 있었다. Native T=49997.72263855906K, semidiscrete 수치 T=49997.72136162063K, 차이=-.0012769384338753298K다. Native에서0인13.675eV node에 수치해는1.1626637806992342e-6 photons/H를 만든다. 이것은 narrow discrete root box와 continuous-time error의 차이다. 두 수치해의 일치가 bound의 근거는 아니다.

Generator의 두 번째 에너지 moment에는 H*E*gap이 추가된다. 이는 fixed-grid 시간극한에도 남으므로 시간오차와 spectral projection 오차를 분리한다.

## 검증과 한계

Decimal60자리 directed 사칙연산, 문서상 correctly-rounded exp/ln에 outward neighbor를 추가하는 산술에 의존한다. Fraction60개/100자리 transcendental18개/interval unit3개/transport red-green1개를 검사했다. 전체 결과에 대한 formal verifier나 독립 reviewer는 없다. 재현 runner4명령 exit0이며 interval certificate는 새로 계산했고 두 IVP 저장결과를 다시 비교했다. 실제 새 IVP는 이 작업 전체에서2회, native와과거campaign은0회다.

전체 macro, Bianchi counterpart/paired contrast, 전체 F08, physical atomic accuracy, spectral/angular continuum은 여전히 미인증이다. 기존 auxiliary escape 상대진단 FAIL도 보존한다. 다음 half2에는 이번 연속오차를 초기오차로 전달하고 새 discrete root box로0으로reset하지 않는다.

## 재현 패키지

REI_CHAT_FLRW08_SLAB_20261005.zip: 93647 bytes,49 entries,48 manifest payload files.
SHA256: 0930677e58a01488538bea048a98f872f19c0628875d3fe88ed7c85778b93f86.
Drive: https://drive.google.com/file/d/1e7GptuaOcTjmbASmGRfdQSJg6qUOztNo/view?usp=drivesdk
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW08_SLAB_20261005.zip

ZIP의 rei_chat_flrw08_slab_20261005 아래 REPORT_KO.md, SEMIDISCRETE_DEFECT_CONTRACT.json, research/, results/SLAB_CERTIFICATE.json, RESIDUAL_SLICES.json, JACOBIAN_MAJORANT.json, INDEPENDENT_IVP_CHECK.json과 실패기록을 보존했다. 이 repo 폴더에는 요약8개만 추가했다. 재현은 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/run_checks.py --output NEW_DIRECTORY다.

Strictlocal<2e-4/publicwidth<2e-3, [160,161]FAIL=2.1245050576368385e-4,tick160,physicalHOLD를 유지한다. 원 production/source-lock/runtime 반환은 수정하지 않았다.
