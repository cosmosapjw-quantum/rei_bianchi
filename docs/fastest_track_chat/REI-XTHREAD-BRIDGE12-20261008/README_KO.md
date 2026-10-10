# BRIDGE12: 실제 첫 cohort cell의 연속시간 잔차

FIRST_CONTINUOUS_COHORT_CELL_ENDPOINT_ERROR_ENCLOSED_CONDITIONAL.

실제 BRIDGE11 첫 cell [0,46757316.98818144] proper s의 native endpoints를 읽고, nH(t)=nH0 exp(-3Ht), E(t)=Eb exp(-Ht)를 가진 순간 FT03 HG CaseA HHe CI/RR/두 DR 계를 새로 정의했다. 이 cell에는 birth가 없으므로 S를 추가하지 않는다. BE로 제거한 photon을 연속 RHS에 넣지 않는다. Initial gas/count는 원 binary64 singleton, birth energy family는 [13.699999999999749,13.70000000000025] eV다.

5 scaled variables, radius .001 physical Picard cube에서 sup|F|=8.818514e-5<.001, sup|Fz|=.000961218<1. 실제 nominal endpoint 선형재구성의 residual을 64개 전체 시간 interval로 감쌌다. Metzler 비교와 explicit positive-series tail, signed residual integral과 Jacobian-error correction으로 종료점 오차를 제한했다.

연속해 minus nominal native의 absolute bound는 HII<6.003822e-10, T<1.485816e-5K다. 같은 parameter의 discrete-root offset까지 포함한 signed error는 HII [2.9483,3.0481]e-10, T [-7.5681,-7.3061]e-6K다. HeIII nominal sign을 root-family sign으로 이전하지 않는다. 새 endpoint Xe/ne/Gamma는 같은 끝점밀도와 E에서 계산; Gamma에 중성분율을 다시 곱하지 않는다. continuous_tau는 null.

독립 80자리 RHS 9profile/Jacobian225component/matrix5component와 DOP853/Radau 5변수 IVP2개로 대조했다. Native/parent32cell/Cargo/다른 owner science 재실행0. IVP와 미분검산은 interval proof 입력이 아니다. 새폴더 4명령 exit0, unit9(1stub RED/GREEN,8after), 기호5/정확64/방향연산60/초월12 확인. 초기 interval normalization dependency와 zero-matrix exact identity 실패는 보존하고 원자식/허용치 수정 없이 고쳤다.

산술은 불변 Decimal60 donor의 directed 기본연산과 correctly-rounded exp/ln 이웃 확장에 조건부다. 독립 proof assistant나 두 번째 전체 interval RHS는 없다. nHe=fHe*nH의 실수 정의와 native frozen product roundoff를 명시했으며 차이는 residual에 포함한다.

이 결과는 첫 cell만이며 전체 macro, 연속방출 quadrature, uniform escape/work, canonical restart, Bianchi, 원자 fit 물리오차는 미승인이다. 기존 local<2e-4,width<2e-3,[160,161]FAIL,tick160,auxiliaryescapeFAIL,physicalHOLD 불변.

다음은 BRIDGE13_FIRST_MACRO_PIECEWISE_CONTINUOUS_DEFECT_CHAIN. 저장된 나머지31cell과 6birth의 jump를 이어받고 이 비영 시간오차를 reset하지 않는다. 추가64격자 표나 전체campaign을 반복하지 않는다.

## 재현

전체 source/실행코드/interval증거/참조/실패로그는 REI_XTHREAD_BRIDGE12_20261008.zip의 rei_bridge12_20261008/ 아래다. 기본 python reproduce.py --output NEW_DIRECTORY 는 새 interval을 다시 계산하고 저장 reference를 확인한다. --reference-ivp만 새2 IVP를 실행한다. Rust 실행은 없다. 이 폴더의 packet_flow.py만으로 전체 proof가 실행되는 것은 아니다.

ZIP 164924bytes,73entries,72payloads. SHA256 526214a43badb06535f6f72d66503e5a7b6ea02fe7e1ec0952dcff4819d4ac05.
Drive 16-V12aZYw3Lo9NyNsKqNexXFuYOJWj63; Dropbox id:BSpOijBcT10AAAAAAD3cCA. Outgoing verification은 R1 id/name/path/size이며 remote restore/independent byte hash는 미실행.
