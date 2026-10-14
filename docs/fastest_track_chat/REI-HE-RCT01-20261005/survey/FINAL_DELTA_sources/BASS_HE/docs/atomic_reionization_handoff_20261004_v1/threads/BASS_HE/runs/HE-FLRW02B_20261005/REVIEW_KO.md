# HE-FLRW02B: 혼합 H/He 독립 기준값과 보존 검사의 식별 한계

## 판정과 새 소비기 결과

독립 수치 reference와 기존 두 native 시험의 보완은 완료했다. 상위 HE-FLRW02B_OWNER_NATIVE_MATCHED_ABSORPTION_REGRESSION은 partial / OWNER_NATIVE_RESULT_PENDING이다. 이 스레드의 Rust 실행·consumer mutation은 0이다.

소비기 3dceea736f9aaa363617a9a6a5bb2854d9ff9986의 FINAL_INTEGRATION.json과 final_crate.log를 실제 읽었다. 84개 native 시험(새 FLRW 21개 포함)의 성공은 owner 실행 증거로 수신하며 재실행하지 않았다. connected_cell은 n_he_cm3=0의 순수 H 연결이다. 기존 mixed HHe fixture와 별도 source 시험을 합쳐 이번 혼합 3종/3노드 두 scale 검사가 실행됐다고 할 수 없다. owner point-test의 2e-12를 기존 제안의 5e-14 허용오차로 바꾸어 해석하지 않는다.

## 직접 유도: 3개의 감지되지 않는 재분배 자유도

20/35/70 eV에서 활성 채널을 (HI20,HI35,HI70,HeI35,HeI70,HeII70)로 놓으면 photon-bin 합은

P=[[1,0,0,0,0,0],[0,1,0,1,0,0],[0,0,1,0,1,1]].

총 전자 행은 (1,1,1)P, 총 흡수 에너지 행은 (20,35,70)P다. heat+binding 합을 포함해도 rank=3, nullity=3이다. 한 null basis는 (0,-1,0,1,0,0), (0,0,-1,0,1,0), (0,0,-1,0,0,1)이다. 충분히 작은 양성 사건 재분배는 photon/total-energy/total-electron 장부와 scale 관계를 모두 보존한다. 이것은 이 검사들의 정보량에 관한 결과이며 현행 코드의 결함 판정이 아니다.

세 bin 합에 HeI35/HeI70/HeII70의 독립 source-bound 값을 추가하면 rank=6이다. 실제 제안은 단순하게 3x3 채널을 전부 기준값과 비교한다. 기존 F01 source-value 시험을 무효화하거나 다시 실행한 것이 아니다.

주입 control에서 HeI70의 d=3.78554525509848e-22 cm^-3 s^-1을 HeII70으로 옮겨 모든 사건을 비음수로 유지했다. 그룹별 photon 합과 총 흡수 에너지 잔차는 0이지만 HeII source-reference의 symmetric relative residual은 1/3이다. 두 구현의 sigma를 동시에 두 배로 바꾸는 control도 ledger/scale 관계는 보존하지만 reference residual=1/2로 검출된다. 둘 다 인위적 반례다.

## reference와 실제 검증

기존 fixture를 유지했다: proper nH=1e-4, nHe=8.3e-6 cm^-3; fractions=(.01,.019,.001); photon=(2e-5,2e-6,2e-7) cm^-3; a0=.25. Verner et al. 1996 DOI 10.1086/177435의 공개 Table1 첫 세 행과 실제 provider를 결속했다. c=2.99792458e10, MPC_CM=3.085677581491367e24, EV_ERG=1.602176634e-12를 유지했다. fit threshold와 binding energy를 교체하지 않는다.

Decimal log-form 80/120자리와 mpmath direct-product 100자리로 계산했다. 9개 고유 단면적 중 양수6/guard-zero3, 유일한 상태는 base+proper 두 scale+comoving 두 scale의 5개다. 고정-energy 순간 검사이지 팽창 이력은 아니다. 정확한 숫자와 단위는 REFERENCE_SUMMARY.json 및 ZIP의 GOLDEN.json에 있다.

새 Python tests 11개 통과. 80/120 최대 상대차 6.35990e-79, Decimal/mpmath 단면적 차이 1.72835e-95, reference ledger 잔차 5.23431e-120. binary64 입력을 정확한 실수로 lift한 비교의 차이는 5.15237e-16이다. 마지막 값은 Rust 중간 연산이나 libm 반올림 인증이 아니다. 이들 모두 finite fitted-source reference이며 물리적 정확도 또는 rigorous interval enclosure가 아니다.

시험 2개에서 Decimal 기본 28자리 문맥 때문에 생긴 1e-28 잔차는 test-local precision100으로 수정했다. source나 허용오차는 바꾸지 않았고 실패 로그를 보존했다. 최종 proposed_consumer 파일의 124개 f64 literal이 GOLDEN 반올림과 일치하며 기존 두 test 이름이 유지됨을 정적 검사했다. Rust compile/run은 NOT_RUN이다.

## 동기화와 다음 실행

소비기 최신 관측 c433eaee7b120a5bfb7c35e802c4b218315bf210까지 관련 Rust source 변화는 없다. 추가 FLRW03의 owner 다음 이론 노드는 REI-CHAT-FLRW04_EVENT_WEIGHTED_CONSUMER_CONTRACT다. 그 이론·history를 여기서 중복 수행하지 않았다.

다음은 같은 HE-FLRW02B의 owner native completion이다. 새 기준값을 포함한 기존 두 시험만 실행하거나 이미 동등한 결과가 있으면 수신한다. 84개 전체 suite 재실행·tolerance 확대·fit clamp·새 원자 계산은 하지 않는다. RCT 제외, HE-F2 WAIT, HE-F3 WAIT, HE-L1/L2/L3 PARKED_OPEN, Eq55 NOT_RUN, physical HOLD를 유지한다.

Git에는 이 리뷰·상태·요약 기준값·다음 지침을 게시한다. 전체 Python 코드, 입력 provenance, 70자리 GOLDEN, 보완한 Rust 두 시험, 실패/성공 로그는 BASS_HE_FLRW02B_REFERENCE_20261005_v1.zip에 있다. 실제 cloud object/size/archive hash는 후속 DELIVERY_RECEIPT.json이 소유한다. Git 요약만으로 전체 native 제안을 재현했다고 하지 않는다.
