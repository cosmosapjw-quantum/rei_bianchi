# REI-LRS V12: native thermal-clock 재현

## 판정 범위

PR #150 frozen native owner (`6ea2b1b4b3875c9163cafc45efe720afded43fc4`)의 격리 복사본에 opt-in source-free clock adapter를 추가했다. 기본 solver 경로는 기존 endpoint RHS, injection, `geometry_increment`를 사용한다. 실험 경로는 `Driver::fixed_step -> tentative -> chemical_stage`를 통해 실제 native `igm_point_rhs` 및 thermal/EOS 계산을 호출한다.

초기 상태는 `(HII, HeII, HeIII)=(0.075, 0.12, 0.03)`, `Tgas=15000 K`, `a0=1/21`이다. 광자와 stellar source만 끄고 CI, CE, RR/DR, free-free, CMB exchange는 유지했다. Total-H nuclei normalization과 `dt=dX/H(Xmid)`를 사용했다. 실험군은 owner BE, CI midpoint, CE midpoint, free-free midpoint, CMB midpoint, thermal midpoint, chemical midpoint, full coupled midpoint다. RR/DR은 한 번만 계산하고, 화학 midpoint군은 CI+RR+DR과 그 결합 에너지/냉각 항을 함께 midpoint에서 평가한다.

고정 구간은 세 조건이다: baseline `Xend=1e-5`, baseline `Xend=1e-4`, density×5 `Xend=1e-5`. 각 조건은 N=8,16,32,64,128,256으로 실행했다. 따라서 8군×3조건×6분할=144 실행, 총 12,096 native step이다. 별도 조건이 solver에 이미 정확히 지원되는지 확인할 수 없어 명시된 두 확장 실험은 연구 harness에서 밀도와 구간을 설정한 통제 실험으로 수행했다.

## 결과

독립 V11 Radau 적분은 세 조건 모두 성공했고 569–576 RHS 평가를 사용했다. Radau 끝점 온도는 baseline `Xend=1e-5`에서 14988.760902944214 K, baseline `Xend=1e-4`에서 14890.301774931422 K, density×5 짧은 구간에서 14947.600712439470 K였다. PR #172 기록의 baseline BE N=128 온도와 현재 native 결과는 약 `7.2e-11 K` 차이로 일치한다.

CE midpoint는 세 조건 모두 온도 오차를 줄였고, N=128에서 owner BE 대비 약 97.0%, 97.0%, 97.5% 감소시켰다. 그러나 CE-only 오차는 N=32→64→128→256에서 계속 약 절반씩 줄어 1차에 머문다. CE는 이 통제 상태의 가장 큰 열 항이며, 그 시간을 midpoint로 바꾸는 것이 개선의 인과적 부분을 설명한다. 남은 1차 오차는 endpoint로 남겨둔 화학 반응/상태 및 결합된 에너지 항에서 발생한다. 화학 midpoint만 적용해도 오차 차수는 1차이며 개선 폭은 작았다.

Full midpoint는 온도 방정식과 결합된 CI/재결합 상태 변화, CE, free-free, CMB를 같은 midpoint 상태에서 평가했다. baseline `Xend=1e-4`에서 N을 두 배로 할 때 N=32→64, 64→128, 128→256 차수는 2.173, 1.983, 2.010으로 2차 수렴을 확인했다. 짧은 두 구간에서는 N=128 이후 오차가 대략 `1e-8 K` 수준까지 내려 Radau/부동소수점 차이 바닥에 닿으므로 점근 차수를 주장하지 않는다. 둘 다 거친 분할에서는 2차형 감소를 보였다.

## 보존 및 비용

144 실행 모두 상태와 온도가 양수였으며 photon 잔차는 0이었다. 최대 Newton chemical+thermal 잔차는 `8.81e-12`로 기존 `1e-11` 수렴 허용치 아래다. 총-H 원자 수 예산의 최대 잔차는 `1.02e-11/H`; HeII와 HeIII 예산은 각각 `1.23e-15/H`, `3.83e-15/H` 이하였다. 최대 기록 에너지 잔차는 `1.05e-9 eV/H`다. 더 상세한 채널별 냉각, CI 사건/결합 에너지, RR/DR 냉각·탈출, free-free, CMB 입력, 단열 일은 `evidence/analysis/NATIVE_LEDGER_SUMMARY.csv`에 있다.

기준 N=256에서 독립 RHS 유한차분 야코비안의 스펙트럼 노름을 사용한 step spectral exposure는 세 조건에서 약 `2.14e-5`, `2.14e-4`, `1.06e-4`였다. 이는 이번 구간/분할에서 비강성 노출을 뜻하는 진단값이며 모든 상태/시간에 대한 강성 부재 증명은 아니다. sweep은 91,632 RHS 평가를 합산했고 측정된 native run 시간 합계는 약 5.91초였다(컴파일 제외, 이 로컬 환경). N=128 CE-only 한 실행은 약 0.03–0.06초 범위다. NCP 벽시계와 자원은 측정하지 못했다.

## 검증과 출처

- V11 시작 커밋: `70ad2b58840cc6041152011028d67af14c30bca8`
- native owner: frozen PR #150, `6ea2b1b4b3875c9163cafc45efe720afded43fc4`
- native owner 기본 테스트: `axbi_driver` 13/13 통과
- V12 focused 테스트: `v12_thermal_clocks` 2/2 통과
- 독립 검토: default 경로 구조 보존, source-free gating, 채널 단일 소유 확인; severity 1/2 없음
- native raw CSV: `evidence/NATIVE_SWEEP_RAW.csv`; 독립 Radau 비교/차수: `evidence/analysis/`
- 수정 전 최초 build 실패 및 정확한 frozen contract 경로 보완 기록: `evidence/PREP_BASELINE_BUILD_FAILURE.md`
- 원시 실험의 기존 V11 41개 회귀와 C8 144건은 재실행하지 않았다.

NCP SSH는 지정 키 `/home/cosmosapjw/.ssh/ncp_key`가 이 실행환경에 없어 host key 확인에서 실패했다. 그러므로 NCP의 CPU/RAM/disk/process 점검이나 계산 실행, 이미 외부 백업된 NCP 파일 삭제는 수행하지 않았다. 지정 키와 검증된 host key가 접근 가능한 환경에서 재현하고, 백업 SHA가 확인된 파일만 정리해야 한다.

## HOLD

이번 결론은 source-free native controlled clock 실험에 한정된다. Source-on 전체 2차 수렴, Case-B photon retransport, full EoR, signed Bianchi는 별도 검증 전까지 HOLD다.
