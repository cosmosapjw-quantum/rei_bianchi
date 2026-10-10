# ACCEL02 복구 EVENT003 독립 판정

**새 256-grid 전구간 계산의 보존·domain 검사는 범위 한정 PASS이고, 128→256 spectral 비교는 FAIL이다.** N1과 기존128-grid 시간 검증, BASS의 기존 reduced history 수신 판정은 보존한다. N2 전체 및 N3 비등방 과학비교는 아직 승격하지 않는다.

이번 판정은 소실된 이전 EVENT003의 대화 수치가 아니라, 새 `EVENT_COUPLED003_RECOVERED`의 실제 RESULT·IDENTITY·history와 exact as-run source에 근거한다. 실제 복원한 native binary는 `3e3a3ef4d89019d791f4e2f4cf25108ac2c6d5e365c58a928d9ff8a85234a0ac`이다. C06 ZIP의 `c76771…`과 혼용하지 않는다. 새 계산은128-grid의 원자료를 다시 계산하지 않았다.

## 실제 확인한 범위

256 energy×2 angles, r=0, rtol=1e-11에서 mean-z15.9→4를 218 event segment, 629.20s에 완료했다. initial-energy 정규화 residual의 최대는6.6493278602e-11, initial nH 정규화 number residual의 최대는5.5014857431e-10이다. 두 값 모두 기존1e-9보다 작다. 여기서 최대는 모든 기록된 segment endpoint와129 common epoch의 합집합이다. 연속 시간 전체의 엄밀 오차 bound가 아니다.

현재 driver의 각 accepted BDF step 검사를 읽었고, actual RESULT의 accepted photon nonnegative·gas fraction/EOS·finite 상태가 모두 통과했음을 확인했다. 저장129states의 finiteness, photon nonnegativity, gas domain, JSON과NPZ의 gas값도 별도 산술로 확인했다. gas accepted extrema는 대략20K≤T≤12355.80K이다. 원 EVENT002의 all-accepted gas domain은 당시 계측하지 않았으므로 여전히 NOT_EXPLICITLY_MEASURED다.

## spectral 판정

원자료에서 비교 metric을 독립적으로 다시 계산했다. 65epoch subset과129epoch 각각 그 집합의 fine-grid 최대 amplitude로 정규화했으며, 보고된 모든 수치와 정확히 일치한다. source·radiation energy·H/He photoionization·primary photoheat 의무와 ionic/thermal observables를 포함한24fields 중23개가 각 집합에서 기존1e-3를 초과한다. 최대는 mean-z4.1362923391의GammaHeI에서0.1401807633이다. 모든 비교 field의 fine amplitude가 양수였으므로 zero-channel 처리 차이가 이번 판정을 바꾸지 않는다.

대표129epoch 오류는GammaHI0.1269181, GammaHeI0.1401808, GammaHeII0.0631533, xHII0.0017910, T0.0041346이다. source number의 reference-volume rate도0.1150456 차이이며, 전체 proper primary-photoheat는0.0163288 차이다. 따라서 gas trajectory만 보고 source/heat의 spectral 의무를 생략해서는 안 된다. 반대로 일부 보존 residual이 작다는 사실도 spectral 정확도를 보증하지 않는다.

후처리 코드는 저장state, 동일source, 동일SIGMA를 사용하며 gas RHS나 ODE를 다시 풀지 않는다. 본 reviewer 자체는 SIGMA도 호출하지 않았다. 원래 저장Gamma/photon 재구성 agreement와source/binary identity 검사를 읽고, 새 비교 산술을 독립 계산했다. primary photoheat는 photoelectron excess power이며 cooling·Compton·CI·expansion을 포함한 총thermal source가 아니다.

## 다음 승격 조건과 주장 한계

수정 대상은 실제 source/opacity breakpoints에 대한 characteristic spectral quadrature다. source smoothing, band 확장, negative clipping, 허용기준 완화로 통과시켜서는 안 된다. 다음 새 discretization은 전체15.9→4에서 비교해야 하며, 바뀐 grid의 temporal evidence도 함께 확보해야 한다. 이번256-grid는 한 tolerance만 실행했으므로 독립적인256 same-grid 시간 수렴 증명이 아니다. 기존128-grid 시간 PASS를 복사하지 않는다.

이번 결과는 conditional20K/residual-HII IC,10–50000eV HM12, primary-only CaseA 및 prescribed isotropic CMB bath의 유한-grid 해석이다. CR/RCT, secondary cascade, 실제 anisotropic CMB, observational EoR, observer visibility 또는 새 native history의 BASS 수신을 완료로 표시하지 않는다. BASS N4는 기존 reduced cells의 scope를 유지한다.

`SAVED_ARITHMETIC.json`은 실제 입력 hash와 산술 검토 결과를, `SPECTRAL_DECISION.json`은 machine-readable 승격/보류 판정을 담는다. 복구 boundary report의 inventory hash는 그때 읽은 역사적 snapshot이며 현재 inventory identity는 이번 최종 판정에서 다시 pin했다.
