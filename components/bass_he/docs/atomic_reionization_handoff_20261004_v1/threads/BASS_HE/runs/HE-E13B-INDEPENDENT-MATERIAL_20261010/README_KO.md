# E13B: 여섯 captured midpoint의 독립 저온 물질 RHS

FINITE_SIX_STAGE_INDEPENDENT_MATERIAL_RHS_PASS__PHOTON_AND_INTERVAL_OPEN.

E13A의 OFF/KF96/GM25 각각 step1/2의 최종 49열 witness, 총6개를 사용했다. 원 archive SHA27b9cb75715888075f55204d54c10d7c61dcf71643ba532349f7a180cef53dc1/922369bytes, 171payload CRC/SHA를 확인하고 16선택입력을 불변으로 재사용했다. material::rhs_selected/igm_rates/coupled::evaluate를 재호출하지 않았다. 새 native/coupled/IVP/eigensolve는0이다.

첫 구현은 mpmath80/120자리, Horner계수와 per-H 화학량론 행렬/열합이다. 두번째는 별도 Decimal110 직접거듭제곱 다항식과 proper-volume event nets다. source literal registry는 공유하므로 두번째 독립 원자모형 인증은 아니다. source의 binary64 상수와 입력을 exact ratio로 올린 실수 대수이며 각 native IEEE 중간연산을 모사하지 않는다. exact decimal literals+mathematical pi는 별도 진단으로만 계산했다.

사전고정 기준: native RHS 상대차1e-12, EOS2e-14; dt*|deltaRHS|/[1e-14,1e-14,1e-14,1e-26]<=1e-3. 원 전체 residual norm<=1도 유지했다. 결과는 RHS24개 최대5.049412744e-16, step-scaled 최대1.569695710e-7, EOS12개2.064872061e-16, RCT owner24개9.833235965e-16, Decimal162개3.894908630e-108, MP80/120 162개7.361245302e-80, 조건부 전체 residual norm 최대0.392087536354다. 모든 기준을 만족했다. E12 GM step7의0.994762는 이6개에 없으므로 소급 인증하지 않는다.

모든6입력은 약2000K에서 CI3종 TINY floor, low-DR 반응/실제cooling0, HeII CE exponent cap active를 선택한다. raw 제외 DR cooling은 비영 진단으로 보존한다. EOS kB1.380649e-16과 Grackle cooling kB1.3806504e-16, 전이 threshold와 RCT35eV 연구closure를 혼합하지 않는다. CMB 부호, ne^2*nHeII metastable CE, freefree charge-squared4, expansion work2Hw, RCT electron0를 유지했다.

새 unit22개(12+5+5 scaffold 오류 후 GREEN), 기호28scalar확인. 초기 zero-identity 시험의 잘못된 relative-zero scale을 실제 profile실행 전에 term크기 기준으로 고쳤고 실패를 보존했다. 과학 계산1회, 고유입력6개에 4산술/literal lane 평가이며 독립4물리실험으로 세지 않는다. 신규 독립심사/intervalcertificate는 NOT_RUN.

Photon A/B는 native 조건부입력이다. residual차이를 native arithmetic assembly, photo algebra, independent material 3항으로 분리했다. 실제 photon transport와 원자fit 참오차, 모든 Newton/node stage, full384, owner adoption은 미승인이다. baselineRCTOFF, actualatomicmomentsnull, physical/productionHOLD, HE-F2/F09OPEN, Gamma alias3.543295FAIL을 유지한다.

전체 Python code/tests, 선택 witness/source/Grackle LICENSE, 상세 유도 및 결과는 immutable ZIP에 있다. Git projection만으로 실행코드 전체가 있다고 가정하지 않는다. 126638bytes, SHA3dd8d8c17cb65182289755015d9d66cec7d446cb62688168db5c5d874d47f757. 기본 reproduce.py는verify-only로 과학/native0; --recompute에서만 새디렉터리에 같은6값계산. 원본 3x384는 어떤 모드에서도 재실행하지 않는다. local fresh restore58payload+CRC와 기본재현exit0 확인. Cloud/Git 완료는 detached DELIVERY_RECEIPT로 판단한다.
