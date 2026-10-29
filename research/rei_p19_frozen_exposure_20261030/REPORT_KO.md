# REI × Puchwein 고정시각 7표본의 시간구간별 photon event/energy 노출량

**Unit:** `REI_P19_FROZEN_PROPER_TIME_EXPOSURE_20261030` · Parent REI [PR271](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/271) HEAD `2a667c23de02f19d973f41174480ed1809918aa2`.

## 근거와 한계

- 원본 PR271 master ZIP 429,682 B를 바이트 SHA/CRC 및 29/29 내부 payload SHA로 확인하고 복원했다. 19/19 Python, mpmath 56/56 선행 재생 결과를 원본과 분리하여 보존했다. 새 17상태 IVP나 화학방정식은 계산하지 않았다.
- Puchwein et al. 2019 MNRAS DOI [10.1093/mnras/stz222](https://doi.org/10.1093/mnras/stz222)의 D1 비평형 UVB 중 기존 PR261에서 선택·검증한 13개 knot와, PR262 ON_refined 17상태의 7개 **다른 모델** 저장상태 및 proper-time 표본만 쓴다. BB13 GLS nominal은 기존 조건부 보정이고 관측 후방분포가 아니다.
- 기존 고정 상태의 `rate=particles/Href/s`, `Q_heat=eV/Href/s`를 보존한다. 새 출력은 **각 구간에서 가정한 보간 모델의 exposure**이며 원래 300K bath의 진화·P19 bath 진화·전체 recombination·국소 온도 변경·tau·CMB 관측을 재구성하지 않는다.

## 새 유도: 양의 로그선형률 노출량

양수 양끝 source `a,b`와 시간 길이 `Δt>0`에 대하여 구간 내부를 `r(s)=a exp[s log(b/a)]`, `s=(t-t_i)/Δt`로 **명시적으로 가정**하면:

\[ I_{\log}=\Delta t\frac{b-a}{\log b-\log a},\qquad I_{\mathrm{trap}}=\frac{\Delta t}{2}(a+b).\]

연속 극한 `a=b`에서는 둘 다 `Δt a`. 양의 로그평균과 산술평균 관계로 `I_log<=I_trap`; **이 순서는 가정한 두 보간식 사이의 순서이며 실제 미상 연속 곡선의 오차상계가 아니다.** `r`와 `Q_heat`는 서로 별도 로그선형 함수로 보간한다. 각 photo 사건 j에 대해

\[N_j=\int\lambda_j dt,\quad E_{\rm ion,j}=I_jN_j,\quad E_{\rm abs,j}=E_{\rm heat,j}+E_{\rm ion,j}.\]

처음부터 `Q_abs(t)=Q_heat(t)+I_j lambda_j(t)`로 정의하여 임의의 두 보간 함수를 독립적으로 조합한 후 합으로 적분한다. `Q_abs` endpoint만 따로 로그보간하면 에너지장부가 깨지는 결함을 첫 RED 실행에서 발견·교정했다.

## 실제 산출물과 새 물리 데이터

- 시간 구간 6개, 사건 7개, UVB 시나리오 2개: **84개 사건-구간 적분**, 12개 구간/시나리오 총계, 2개 전체 시나리오 총계, 14개 누적 proper-time knot. 실제 숫자들은 CSV·RESULT.json에 보존했다.
- 기존 저장 구간: `z_mean=4.701690090`에서 `z_mean=2.404494425`로 진행, 기존 `Δt=4.590199321205e+16 s` (신규 time evolution 아님).

| source prescription | loglinear 사건수 [Href⁻¹] | loglinear 광가열 [eV/Href] | 이온화 저장 [eV/Href] | 총흡수 [eV/Href] | 전자 수 보간 비교 차이 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `P19_D1_fiducial` | 16.084006 | 76.1075178 | 302.926646 | 379.034164 | 0.85324% |
| `P19_D1_BB13_GLs_nominal` | 14.5899329 | 69.2682465 | 276.933006 | 346.201253 | 1.11539% |

같은 source를 사다리꼴로 처리하면 fiducial 16.2224221 events/Href 및 76.8745795 eV/Href photoheat, BB13 nominal 14.7545033 events/Href 및 70.1527283 eV/Href photoheat다.

### 사건별 적분량 (양의 loglinear 보간)

| species | P19 fiducial 사건수 [Href⁻¹] | P19 fiducial 광가열 [eV/Href] |
| --- | ---: | ---: |
| H1 | 8.57367906 | 31.2934766 |
| D | 0.000216274484 | 0.000789385891 |
| T | 6.21858661e-16 | 2.2682504e-15 |
| He3 | 0.000915934639 | 0.00546553769 |
| He4 | 7.50919473 | 44.8077863 |

저장 knot에서 H1와 He4 photon-electron *source share*의 선후가 바뀌는 구간은 `z_mean=4.024262`와 `3.603020` 사이다. 각 group rate의 두 양끝 로그보간과 `z_mean`의 time-linear label 보간을 같이 사용한 **설명용 proxy**는 `z_label≈3.709245`이다. REI/P19 physical crossing redshift는 아니다.

## 교차 검증, 연구 DAG 및 부족한 입력

- 새 독립 mpmath 90자리 **168/168** positive logmean values 비교 PASS; 최댓값 상대차 `8.12e-16`. Python unit **12/12 PASS**; Wolfram 닫힌 적분식 잔차 0. 원본 PR271 Python 19/19 및 mpmath56/56은 다시 실행했으나 신규 단위 과학 완료에 더하지 않는다.
- **원 working 33/88, central 28/88, physical-fast 4/7, delta 0**. 새로운 scoped static exposure 데이터 단위 1/1은 원 DAG88의 물리 노드 완료가 아니다. F4 PARTIAL, L4 false, NO_MORE_IVPs true.
- 실제 저장된 193-sample BASS native trajectory와 명확한 K/nHref/nb/clock/초기동위원소 정합, REI full chemical/Jacobian 및 source-owned photon spectrum은 여전히 필요한 입력이다. 이번 계산은 해당 gate를 통과하지 않는다.

## 재현

```bash
python -m unittest discover -s tests -v
python code/exposure.py
python code/reference_mp.py
python code/plot_exposure.py
```

산출물: `results/INTERVAL_84_EVENT_EXPOSURE.csv`, `INTERVAL_12_SCENARIO_EXPOSURE.csv`, `TOTAL_2_SCENARIO_EXPOSURE.csv`, `CUMULATIVE_14_KNOT_EXPOSURE.csv`, 두 PNG, `RESULT.json`, `MP90_VERIFICATION.json`. 원본 source ZIP은 `source_archive/PR271_SOURCE_FULL.zip`로 정확히 잠금.
