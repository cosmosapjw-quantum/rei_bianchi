# REI-CHAT-FT02-20261004: provider source/domain 연구

판정: SCOPED_SOURCE_MAP_AND_LIGHT_CHECKS_COMPLETE__PHYSICAL_ADMISSION_OPEN.
다음 ready node는 REI-CHAT-FT03_THERMAL_CLOSURE다. canonical F00~F09, 원 fixture/source lock 및 science gates를 수정하지 않았다. 이 폴더는 연구 요약·반환·백업·인계이며 전체 보고서, 소스, 21개 provider record, 상세 검증결과와 manifest는 아래 ZIP에 있다.

## 재현 패키지

- 파일: REI_CHAT_FT02_20261004.zip
- bytes: 136708; ZIP entries: 41
- SHA-256: 3edbe70f57877acb04c84ddbe8c43d485c5f501f87d5eb09b660e1502dfeec04
- Drive: https://drive.google.com/file/d/1C3hkkoGtoBqro72ZED5qxMi4hyT0PG83/view?usp=drivesdk
- Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FT02_20261004.zip
- 두 provider 저장 완료 및 ID/path/size 확인. 원격 checksum은 connector 출력에서 제공되지 않았고 원격 전체 restore는 수행하지 않았다. 위 SHA는 로컬 sealed ZIP의 값이다.

## 주요 결과

1. Grackle 3.4.1 commit af7939494ce65007887ada7b98d1813df6843346의 H/He 원 함수 18개를 선택했다. 원 본문은 보존하고 명시적 기본 macro와 최소 local struct를 붙인 단일 C 파일을 실행했다. 전체 Grackle ABI/build/table interpolation 또는 Rust solver 검증은 아니다. rate_functions.c SHA-256은 a900e726413da39bb24fc506846a09f7e0e4addbd5152197ca76d0e22ad02cea다.
2. 원 scalar API의 units=1 경로에서 flag-off와 일부 cutoff는 0이 아니라 tiny=1e-20을 반환한다. 일부 분기는 units로 나누지 않으므로 S*f(T,S)=f(T,1)이 성립하지 않는다. ceHI(10000K)의 활성값은 4.129922299452811e-24, 비활성값은 1e-20으로 비율은 약2421.353이다. 이는 독립 CGS 이식의 sentinel 해석 문제이며 전체 Grackle code-unit solver의 오류 판정이 아니다.
3. k2 Case A의 5500K 분기 점프는 +1.044957259494%다. k3/k5는 9284K에서 각각 1e-20에서 1.91682081648e-22/3.01076761786e-35로 바뀐다. k4의 작은 DR jump, CaseB 1e9K cutoff, 활성 exponent clamp와 table knot도 별도 처리해야 한다. 진짜 event를 가로지르는 box에 smooth Hessian remainder를 적용하지 않는다.
4. 실제 cool1d_multi_g.F 조립식에서 ceHeI 및 ciHeIS는 n_e^2*n_HeII이고 계수 단위는 erg cm^6/s다. 이름에서 n_e*n_HeI를 추측하면 안 된다. brem의 charge weight는 n_e*(n_HII+n_HeII+4*n_HeIII)다.
5. CI 원 냉각의 q=(2.18e-11,3.94e-11,8.72e-11)erg는 기존 fixture binding chi와 다르다. 상대차는 HI5.92361022e-4, HeI1.69059934e-4, HeII1.50670099e-4다. 같은 사건률 r에 thermal=-q*r, binding=+chi*r를 쓰면 (chi-q)*r가 남는다. 권장 후속 model adapter는 thermal=-chi*r를 단일 소유하고 raw source 대비 보정을 명시한다. raw-reference는 그대로 보존한다. production 자동 채택은 없다.
6. theta=ln(T/Tref), g=dlnf/dtheta, h=dg/dtheta, T=K*w/nu일 때 f_ww=f*(g^2+h-g)/w^2, f_wnu=-f*(g^2+h)/(w*nu), f_nunu=f*(g^2+h+g)/nu^2를 포함한 일반 chain rule5식을 symbolic 검산했다. density prefactor에는 곱미분을 추가한다. Verner sigma의 에너지 1/2차 도함수도 독립식과 교차검산했다.

## 검증

원 C값540점: 최대상대차1.0075875613e-12 < 기준3e-12. T<=1e6K 시험점에서는4.39400654e-14 이하. logT derivative216점: 최대scaled discrepancy3.47871923e-79. Verner값15점/derivative9점: 최대scaled discrepancy1.18390675e-81. 일반 열좌표 symbolic identity5개 및 invalid-input reject6개. Provider record21개가 기존 schema를 통과했고 consumer_admission은 전부false다.

선택 재결합 냉각3개와 Verner3개는 확인된 source-supported 공통 범위를 기록했다. 다른 식의 전역 물리 적용범위는 unresolved이며 Case/부분범위는 literature_subdomains로 분리했다. empirical fit accuracy를 엄밀한 physical enclosure로 만들지 않았다. 표본 parity는 uniform derivative/root/remainder 인증이 아니다.

## 다음 단계

FT03에서 raw-vs-model sentinel 정책, binding-energy SSOT, Case/escape/DR 회계를 닫는다. HeIII CaseA 10000K의 raw cooling/rate는 약3.57309*kBT이므로 실제 초기화/consumer 단위와 hydrogenic energy-moment scaling을 먼저 비교한다. 원전과 같은 값이라는 이유만으로 물리 일관성을 승인하지 않는다. 이후 문헌 지원 구간의 별도 온도-피드백 모형을 작게 검증한다. 기존 constant-rate toy 및 4800<T<36000 certificate를 물리율에 이전하지 않는다.

strict local<2e-4, public width<2e-3, 과거 [160,161] FAIL=2.1245050576368385e-4와 tick160 prefix 보존. heavy solver/history, full Grackle build, Rust production 실행 및 physical admission은 모두0이다.
