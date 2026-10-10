# REC_REI_COLD_INTAKE01

독립 Astra review도 `PASS_SCOPED`다. 저장된 네 row와 build/campaign receipts를 재계산했으며 review 중 build·campaign·편집은 없었다.

source-pinned REC PR83의 baseline/refined z=20·15.9 네 저장 endpoint를 REI PR101의 공개 isotope/EOS/geometry API로 읽었다. 새 HyRec history나 interpolation을 실행하지 않았다. intake는 PASS_SCOPED이며 원자 provider는 HOLD_RAW_TEMPERATURE_DOMAIN, 저온 물리 사용과 Bianchi IC 채택은 HOLD다. 독립 Astra review는 별도 후속 gate다.

H1 중성·이온 밀도는 nH(1-xe), nHxe이며 He4는 중성으로 보존했다. 다른 isotope/He 이온 slot은 정확한 0이다. metadata는 원래 HyRec cutoff 이후 중성 He mapping을 명시한다. xe는 H 핵당 전자수이며 QHII가 아니다. matter temperature Tm을 사용하고 Tgamma는 metadata로만 유지했다.

공개 IsotopeNumberState::new, try_legacy_hhe_projection, try_legacy_hhe_eos 및 AxisymmetricPoint(a,0,H,0)를 실제 native 실행에서 호출했다. charge-neutral thermal closure의 u=3/2 kb Tm(nH+nHe+ne)는 binding·광자 energy를 포함하지 않는다. legacy number density는 proper m-3/1e6, energy는 erg cm-3=10 J m-3이다. snapshot은 FLRW 축 세 개만 담는다. coupled derivative·CR·photon·chemical ledger는 실행하지 않았다.

Decimal80 oracle은 고정 binary64 입력의 수학식을 평가한다. 최대 상대 오차 1.890368943688204e-16은 64epsilon=1.4210854715202004e-14 이내다. species normalization, charge, proper-SI conversion, Tm roundtrip, FLRW scale/rate와 exact structural zero를 검사했다. baseline/refined 저장값의 최대 상대차는 6.304660458642791e-7로 기존 1e-4 한계 이내다.

각 row에서 AtomicProvider::reference().raw_coefficient(K2,Tm,A)를 호출해 RAW_TEMPERATURE_DOMAIN을 얻었다. unavailable record에는 numerical coefficient를 기록하지 않았다. 입력 Tm 약 6.14–9.40 K는 raw 구현 guard 100 K 아래다. intake 결과가 저온 provider의 물리 타당성을 허용하지 않는다.

최초 build는 E0369(ForwardError의 PartialEq 부재)로 FAIL했다. 원 stderr·stdout·receipt를 그대로 보존했다. Astra 허가에 따라 assert_eq를 정확한 matches! 패턴 검사로 한 번 수정했고 repair build exit 0 뒤 단 한 번의 4-row campaign exit 0를 수행했다. 총 build 2회, intake campaign 1회, HyRec/history 0회, targeted saved-output tests 8개 PASS다. 추가 science 실행이나 retry는 없다.

재현 명령은 새 output 디렉토리에서 `python3 intake.py`다. 이번 기록의 repair 경로는 `python3 intake.py --repair-closeout`이고 원 실패가 존재할 때 한 번만 허용된다. `python3 -m unittest -v test_intake.py`는 저장 결과만 검사한다. native target binary는 Git에서 제외했다.

다음 gate는 독립 Astra review이며, 다음 물리 work unit에는 source-backed 저온 atomic/thermal provider와 Bianchi background 채택 결정이 필요하다.
