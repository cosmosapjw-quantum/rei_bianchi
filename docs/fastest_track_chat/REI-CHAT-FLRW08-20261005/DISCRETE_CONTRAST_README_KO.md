> 2026-10-14 보존본: 과거 저장 이산 이력 차분 진단. 현재 진행 지시는 `README_KO.md`을 읽는다.

# FLRW08: 실제 paired history의 시간 차분 분석

2026-10-14 보관 안내: 이 문서와 하위 진단의 `.cuh/` 원시 기록은 현재
체크아웃에서 제거하고 소유자 로컬
`~/.codex/backups/rei_bianchi-cuh-20261014/cuh-51c23b82.tar.zst`에
보관했다. 압축본 SHA-256은
`a7c50be6c2226e835b2a09546feaf7a6d019771e9046151e39fa75d76749749c`다.
아래의 `.cuh/` 입력을 사용하는 재현 명령은 해당 경로를 아카이브에서 복원한
뒤에만 실행할 수 있다. 이 로컬 보관본은 Git 원격에 게시하지 않았다.

완료된 F08의 T0/T1/T2 FLRW–Bianchi I 이력을 재사용해 공통 normal-time endpoint 8,000개를 분석했다. 새로운 이력 생성·원자 모형 변경·허용오차 변경은 없다. 시간 끝점은 1e13 s, spectral subdivisions는 8, angular grid는 8×16이다. 모든 CSV 값은 원래 binary64를 정확한 유리수로 복원해 뺄셈했다. 따라서 아래 값은 저장된 수치 이력에 대한 분석이며 연속해나 물리적 정확도의 인증이 아니다.

| 마지막 시점의 수소 이온화율 차분 BI − FLRW | 값 |
|---|---:|
| T0 | 2.8520446593294224e-7 |
| T1 | 2.8513310623701216e-7 |
| T2 | 2.8509735550130700e-7 |
| T2 − T1 | −3.5750735705164516e-11 |
| 두 refinement 변화의 절대값 비 | 1.9960343339109479 |
| 공통 8,000개 시점에서 최대 \|T2 − T1\| | 2.1002644068346400e-10 |

일차 시간 수렴과 양립하는 관측이다. 3개 값으로 미래의 수렴 차수나 오차 수축률을 증명하지 않는다. `1/3, −2, 8/3` 가중치의 이차 Richardson 값 2.8506155750710843e-7은 이차 bias 전개를 가정한 점 추정치다. 공통 8,000개 시점의 최대값은 모든 T1 16,000개 시점의 최대값이나 연속 시간 supremum이 아니다.

독립 F08 endpoint gas box를 정확히 빼면 T2의 이산 차분은 [2.6998355129315144e-7, 3.0021115970946255e-7] 안에 있으며 양수로 분리된다. T2와 T1의 차분 간 차이의 독립 상계는 2.1131080552017067e-8이다. 이는 서로 독립인 네 endpoint box의 뺄셈으로 얻는 보수적 상계이며 작은 점 변화에 근거해 box의 독립성을 없애지 않았다. `RESULTS.json`의 `exact` 유리수 필드가 상계의 수학적 값이고 `approx` 필드는 표시용 반올림이다.

Ck를 같은 spectral/angular 모형의 k번째 시간 refinement 차분이라고 하자. **모든 미래 k≥2에서** |C(k+1)−Ck| ≤ q|Ck−C(k−1)|, 0≤q<1이고 그 극한이 동일한 continuous-time 모형과 일치한다는 별도 증거가 있으면, T2의 남은 시간 오차는 q/(1−q) × 2.1131080552017067e-8 이하이다. T2 이산 신호 하한의 10%보다 작게 만들려면 q < 0.5609530788616102가 충분하고, 연속 차분의 양수 부호만 보장하려면 q < 0.9274131965882918이 충분하다. 10%는 이 보고서의 진단 목표이며 원래 local<2e-4/public width<2e-3 gate를 바꾸지 않는다. 미래 균일 수축과 continuous-time 일치성 모두 **NOT_ESTABLISHED**다. 이 조건은 시간 오차만 다루며 spectral/angular continuum 또는 물리적 fit 오차까지 포함하지 않는다.

정확한 반례 다항식 P(z)=1−7z+14z²−8z³=(1−z)(1−2z)(1−4z)는 P(1)=P(1/2)=P(1/4)=0, P(0)=1이다. 세 sample을 지나는 이차 다항식에 임의의 A×P(z)를 더하면 측정한 세 값은 모두 그대로이고 z=0 극한은 A만큼 달라진다. 이는 **세 refinement sample만으로 continuum bias를 식별할 수 없다는 반례**다. 원래 ODE를 만족하는 다른 해를 제시한 것이 아니며 해당 수치법의 consistency를 반증하지 않는다.

검증은 별도 Decimal90 계산과 SymPy exact 검사 49개, 비유한 값·중복 시점·미완료 이력·잘못된 grid·실패한 로컬 계수의 거절 fixture 5개를 통과했다. 독립 hosted 리뷰 결과는 `REVIEW.json`에 기록한다. 과학적 판정은 **HOLD**, continuum time-error certificate는 **NOT_ESTABLISHED**다.

재현:

```bash
python3 docs/fastest_track_chat/REI-CHAT-FLRW08-20261005/analyze_contrast.py --out /tmp/rei-flrw08-replay --plot
python3 docs/fastest_track_chat/REI-CHAT-FLRW08-20261005/validate_contrast.py --result /tmp/rei-flrw08-replay/RESULTS.json
```

분석에는 Python 표준 라이브러리만 필요하다. 그림에는 Matplotlib, 독립 validator에는 SymPy가 필요하다. `RESULTS.json`에는 실제 curve/checkpoint 12개 SHA가 기록된다. 입력 원본과 F08 전체 history proof는 변경하지 않는다. Source parent는 `e63ca0735a3e3e7eebbf4498c697d806d375e191`이다. T0/T1은 기존 V1 checkpoint, T2는 compensation을 포함한 V2 checkpoint다. 각각 기존 독립 검증을 받은 이산 이력이며 source bytes를 같다고 주장하지 않는다.

관리형 CPU Devstral Small 2 24B coder를 같은 FLRW08 task에서 실제 3회 호출했다. 합계는 prompt 795 + output 133 = 928 tokens이며 cached input 359 tokens는 prompt에 포함되어 중복 합산하지 않는다. 첫 두 출력의 단일 JSON fence는 원문을 보존한 Host 추출로 처리했고 세 후보 모두 Richardson 계수의 exact validator를 통과하지 못했다. 세 번째 후보의 cubic 계수는 정확하게 검증되어 재사용했고, Richardson 계수는 Host의 SymPy 선형계 풀이로 생성했다. 통합 계수는 원래 고정한 7-residual oracle을 통과했다. 전체 로컬 성공으로 표시하지 않는다. 별도 세 번째 요청 형식 거절은 `NOT_STARTED`, model_calls=0이었다. 원문·실패·관리형 lease·사용량은 `.cuh/fastest-track/REI-CHAT-FLRW08/`에 보존한다. Host 비용과 절감률은 NOT_MEASURED이며 과거 F08의 10,419,630 native tokens/4 dispatch 기록은 유지한다.

독립 GPT-6 Astra/xhigh 검토는 수치/주장 경계의 차단 결함 없이 완료됐다. 지적된 표의 파이프는 escape했고, 기존 음성 fixture 두 개의 원인 구분은 완전한 baseline에 각각 NaN/중복 시점만 넣고 정확한 오류 메시지를 확인하는 Host 보강 검사 두 개로 확인했다. 원 frozen validator는 SHA `e1e636d7305c23b60ad64d813e1477601f56ee989095779fbc7f90a92388c6dd` 그대로 보존한다. 원 검토, 보강 fixture 원문/결과 및 한계는 `REVIEW.json`에 있다. 이 native 검토 1회 실제 누적 사용량은 input 414,828 + output 3,907 = 418,735 tokens다. Cached input 350,464와 reasoning output 1,275는 각각 input/output에 포함되어 중복 합산하지 않는다. 실제 task_complete와 모델/effort는 Host가 원 child transcript와 관리형 lifecycle에 대조했다. 프로세스 종료/비용/절감률을 추론하지 않는다.
