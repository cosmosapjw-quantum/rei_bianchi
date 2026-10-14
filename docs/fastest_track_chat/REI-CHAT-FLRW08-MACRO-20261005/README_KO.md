# FLRW08: 첫 FLRW macro의 연속시간 오차 전파

판정: FIRST_FLRW_MACRO_SEMIDISCRETE_ERROR_ENCLOSED_WITH_INHERITANCE. Logical FLRW08 paired/global 인증은 아직 partial이다.

실제 T0_FLRW 첫 macro t=0..1.25e9s에서, 첫 committed half의 연속오차를 두 번째 half 초기 불확실성으로 전달했다. 동일13변수 fixed-energy-grid 실수계의 종료점 오차 상계는 xHII<2.474e-7, T<0.006163K다. 기존 이산 root box로 연속오차를 reset하지 않았다.

b2=exp(M2)b1+integral_0^1 exp((1-s)M2)R2 ds. HII의 b1=1.16800893280610e-7, 전파된 b1=1.30912366937497e-7, 새 local forcing=1.16391471912594e-7, 합성상계=2.47303838850091e-7이다. 초기오차를 빼면 다른 IVP의 local error만 얻는다. 이 사례의 실제 numerical differences는 우연히 local-only bound에도 포함되므로, reset오류를 이 수치사례가 직접 반박했다고 주장하지 않는다.

Half2 uncertain-initial Picard self-map 좌변0.008953530400533<rho0.02, contraction<0.442863912443. T tube=[48423.80,51609.40]K. 새64개 전체 time interval에서 residual을 제한했고 양의행렬급수와 tail로 오차를 전파했다. 독립90자리 matrix exponential의13성분도 모두 upper 안이다.

이전 DOP853/Radau의 각 firsthalf endpoint에서 두 번째구간만 이어 적분했다. NativeT=49995.447962130966K, continuedT=49995.44541381825K, 차이=-0.00254831271740841K. 두 numerical endpoint 최대 scaled차이는3.33067e-16이다. Native root xH 폭6.04e-14와 연속시간오차는 다른 대상이다.

원 archive와48개 payload identity를 확인한 뒤 firsthalf proof를 조건부 의존성으로 계승했다. 이전 증명/native/cargo/fullhistory 재실행0. 새13D IVP2회, focusedtests4개, 64interval residual, 13matrix-action 비교. 최종3명령exit0. 초기오차누락 helper의 red/green과 기존 auxiliaryescapeFAIL을 보존했다. Scientific source와 tolerance 변경0.

이 결과는 첫 macro 종료점의 semidiscrete 시간오차에 한정한다. 모든 중간시각에 같은 날카로운 bound, BI차분, wholehistory, spectral/angularcontinuum, atomicaccuracy 또는 formal proof를 승인하지 않는다. Decimal/libmpdec primitive와 명시적 parentcertificate에 의존한다.

전체 보고서, 입력, 새 코드, interval 증거와 고정 supplier는 REI_CHAT_FLRW08_MACRO_20261005.zip의 rei_chat_flrw08_macro_20261005/ 아래에 있다. 232307bytes,96entries. SHA256=6b85f159badd02a0eae8d69511c37f6a6199907e3327177712609cd76ba93a60.
Drive: https://drive.google.com/file/d/10RWZfDdi-by6cqUYDw5JI2CPDZHVm1mB/view?usp=drivesdk
Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FLRW08_MACRO_20261005.zip

재현: python research/run_checks.py --output NEW_DIRECTORY. --fresh-ivp는 half2 IVP2개만 추가한다. 다음은 실제 BI 첫macro 각도별 photon/source/endpoint 입력과 paireddefect 연결이다. 대규모campaign은 반복하지 않는다. 기존 local<2e-4/publicwidth<2e-3,[160,161]FAIL/tick160/physicalHOLD 및 원 CODEX_SYNC/runtime_returns/F00/F03/FT03/S0를 보존한다.
