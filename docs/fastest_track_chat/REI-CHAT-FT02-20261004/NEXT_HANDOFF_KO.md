# FT02 -> REI-CHAT-FT03_THERMAL_CLOSURE

같은 branch forward/rust-reion-kernels-20260922에서 이론 및 경량 수치를 이어간다. 새 branch/merge, production suite, 전체 Grackle/Rust build 또는 Bianchi history는 실행하지 않는다. 첫 읽기에서 현재 remote identity를 확인한다.

이 폴더의 README_KO.md, TASK_RETURN.json, BACKUP_RECEIPT.json을 읽고 ZIP의 REPORT_KO.md와 필요한 provider record/결과만 계승한다. 기존 전체 감사, FT01 재실행, 닫힌 원자 이론 재검증으로 돌아가지 않는다. ZIP의 원 입력 및 함수별 body identity는 보존돼 있다.

다음 bounded work:
1. raw-reference와 model adapter를 분리하고 disabled/floor/cutoff 정책을 명시한다. tiny를 물리적인0으로 무단 재해석하지 않는다.
2. binding chi SSOT 및 CI raw q와의 source-to-model correction을 고정한다. thermal=-chi*r와 raw cooling을 동시에 빼지 않는다.
3. CaseA escape 또는 명시적 CaseB/재처리, HeII radiative/DR rate-cooling pairing과 ceHeI/ciHeIS effective 항의 소유권을 닫는다. ceHeI/ciHeIS prefactor는 n_e^2*n_HeII, coefficient 단위는 erg cm^6/s다.
4. HeIII cooling/rate energy-moment consistency를 실제 초기화/consumer 단위와 hydrogenic scaling으로 확인한다. 원 source와 동일한 점값만으로 물리 일관성을 승인하지 않는다.
5. 문헌 지원 구간과 선택한 model을 고정한 뒤 별도의 온도-피드백 경량 모형/유한 domain 비교를 실행한다. 원 constant-rate fixture를 소급 수정하거나 toy4800<T<36000 certificate를 물리율에 이전하지 않는다.

5500K/9284K 및 실제 활성 floor/table/threshold event를 포함하는 box에서 smooth Taylor/Hessian remainder를 가정하지 않는다. 216점 derivative 검증은 uniform certificate가 아니다. Provider21개는 schema-valid이지만 admission은false다.

stop condition: 선택한 모델의 species/thermal/photon event 회계, Case, domain과 adapter 정책이 명시되고 작은 독립 기준검증을 수행할 수 있어야 한다. 실제 Rust residual/source-site, interval root/remainder 및 paired history는 후속runtime으로 남긴다. source gap은 targeted source/명시적 대체fit으로 해결하며 임의의 전체 재감사나 불필요한 ab-initio 요구로 바꾸지 않는다.

strict local<2e-4/public width<2e-3와 과거[160,161] FAIL 및 tick160 보존. 다음 결과도 같은 branch에 non-force append하고 기존 Drive/Dropbox 위치에 create-only 이중백업한다. metadata ACK, byte restore, science validation은 별개다.
