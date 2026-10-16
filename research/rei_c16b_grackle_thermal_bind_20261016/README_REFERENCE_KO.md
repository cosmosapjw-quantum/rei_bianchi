# 독립 C 계수–Python RHS 및 Radau 국소 셀 검증

원본 PR150 `a42fd7c9849306074a9f7a262628cd852ce34dea`의 물리 함수를 바꾸지 않고 비교한다. `reference_c_bridge.c`는 pinned `tests/data/igm_grackle/grackle_literal_reference.c`의 **변경하지 않은 C 함수 본문**을 포함하여 17개 계수를 노출한다. He II RR/DR는 원본 harness의 명시적 대수 분해를 따른다. `reference.py`는 원본 PR154 Verner 함수, EOS, H/He 화학량론, CI/RR/DR, excitation/free-free, 부호 있는 CMB 교환과 binding/escape를 독립 조립한다. 실제 native RHS 호출은 점검 비교에만 사용하며, Radau 적분은 native backward-Euler map을 호출하지 않는다.

점검은 T=10,100,8000,10000,100000 K, q_ref=0,±0.1, He 유/무, photon 유/무의 60 상태이다. 계수·진단·photo Gamma/heat·전체 RHS·7개 ODE 성분 **4980 비교, 실패 0**, 최대 상대 차이 `7.560317720113775e-15`이다. 구조적 0은 정확히 일치한다. 필드별 최대 차이는 `evidence/reference/point_component_maxima.json`에 있다.

국소 셀은 a=.1, nH=`0.00018981984507140265 cm^-3`, nHe=`1.543260998559575e-5 cm^-3`, TCMB=27.255 K, mixed fractions [.31,.23,.17]이다. 20/40/80 eV는 실제 native 물리 에너지이다. reference q 에너지를 그대로 물리 에너지로 오인하지 않는다. 모든 native Case-A 과정은 활성 상태이며, photon=0은 photo만 없는 전체 충돌·냉각 모델이다.

| Case | Finest n | Endpoint physical norm | 원래 33 관측시각 최대 norm | Finest endpoint order |
|---|---:|---:|---:|---:|
| recomb8000 | 128 | 3.33716e-5 | 3.33716e-5 | .99878 |
| collision1e5 | 128 | 7.01141e-5 | 7.01141e-5 | .99927 |
| mixed1e4 | 1024 | 4.09569e-5 | .00272292 | 1.00188 |

동일 horizon에서 n32,64,128을 사용했다. Mixed는 초기 photon depletion 동안 n128 자체 시각 격자 최대 오차가 .0209758로 드러나므로, endpoint 결과만으로 전체 궤적 정확도를 승인하지 않았다. 같은 입력으로 사전 승인된 256,512,1024 단계까지 연장했다. n512의 원래 관측 격자 오차 .00538543도 실패로 보존한다. n1024 자체 시각 격자 최대 오차는 .00280372, 고정 관측 격자 512→1024 order는 .98391이다. 새로운 시각은 저장한 Radau dense cubic polynomial로 평가하며 선형 보간하지 않는다.

Radau rtol1e-9와 더 엄격한1e-10을 모두 실행했다. **최종 reference/ledger authority는 사전 승인된1e-10**이며1e-9는 tightening control로 보존한다. 1e-9의 log-photon dense 출력에서 일부 photon ledger 상대 잔차가 1.32e-10까지 나와1e-10 목표를 근소하게 넘었다. 이를 숨기거나 허용 오차를 넓히지 않았다. 기존1e-10 자료의 모든12 case 전체 기록 시각은 energy≤3.512e-12, photon≤1.529e-11, charge≤8.14e-16로 목표를 만족한다. 양쪽 원자료 및 잔차는 `reference_ledger_summary_both_tolerances.json`에 있다. 두 reference endpoint 차이는 native 오차보다 충분히 작다.

Radau의 정확히 0인 photon subsystem에서 약-2e-39 roundoff가 처음 관찰되어 실패를 보존했다. 수학적으로 불변인 0 mode를 적분 변수에서 제외하고, 양의 source-free photon mode는 log 좌표로 적분한다. 값이나 rate를 clip하지 않는다. log mode가 exp underflow로 0이 되면 오류이다. Pulse 경계에서는 적분기를 정확히 다시 시작하고 각 열린 구간의 상수 source를 사용한다. `INTEGRALS`에는 escape,CMB,thermal,binding,photo input,source count/energy 및 photo/CI/RR/DR event 적분이 모두 있다.

추가 cold/CMB-heating/no-He/tiny-ion/signed-geometry/pulse 비교는 제어 실험이다. `strong_absorption` n32 endpoint 오차 .01219는 명시적으로 **ACCURACY_NOT_ADMITTED**이며 일반 stiff 정확도를 주장하지 않는다. Pulse n32 endpoint 오차가 작아도 초기 transient 최대 오차까지 .005라고 주장하지 않는다. 실제 MD14 연속 spectrum은 3 delta node와 다른 모델이므로 이 Radau와 직접 동일시하지 않는다. `refinement_observations.json`은 native 현재 위치 source와 별도 birth-cohort source의 spectral subdivision, angular, transport-cell 축을 구별한다. Source-born cohort의 finest-neighbor norm은 각각1.753e-13,2.186e-4,.003044이며 이전 차이보다 감소한다. 이는 유한 격자 관측이며 continuum 오차 증명은 아니다.

재현 시 원본 native source archive를 별도 위치에 풀고 native worker의 example을 빌드한 뒤 다음처럼 실행한다. C 원본 디렉터리와 Python 위치는 환경변수로 지정할 수 있다.

```bash
export C16B_NATIVE_ROOT=/path/to/pinned/native
export C16B_PYTHON=/path/to/python-with-numpy-scipy
bash run_reference.sh --point-binary /path/to/native_campaign \
  --manifest evidence/native/campaign/frozen_manifest.json
```

이미 보존한 Radau 원자료로 native 출력만 다시 비교하려면 `--skip-point --reuse-reference`를 추가한다. `render_reference_plots.py`는 저장된 자료만 읽어 Tgas, H/He fractions, photon/H 및 temporal-error PNG/PDF를 만든다. 그림은 **고정 a의 local cell**이며 cosmological z20→4 이력이나 production 결과가 아니다. 1e-9/1e-10 곡선 차이는 그림 해상도에서 구별되지 않는 reference-control 수준이다.

실행은 OMP/OpenBLAS/MKL 각각1로 제한했다. 최초 전체 reference 적분 캠페인은15.38s, peak RSS123836KiB였다. 이후 mixed dense-output 갱신은 해당 case만 적분했고, 나머지는 원자료를 재사용했다. 준비 경로/JSON scalar/파일 선택/dense metadata 오류와 최초 잘못된 endpoint-only 분류는 모두 `evidence/reference`에 남긴다. 최종 물리적 수용 판단은 controller의 독립 검토 몫이다.
