# R9 Unit6: 외부 계산과 독립인 이론·코딩 연구

2026-10-16. 이번 연구는 T4의 저장 잔차 진단, T6의 수소형 2광자 연속방출, T7의 Be7 전자포획 연결을 실제 코드와 수치 결과로 확장했다. 세 단위에서 합계 **18개 검증이 통과**했다. 독립 검토의 최종 판정은 `review/IMPLEMENTATION_REVIEW.json`을 따른다. 이 결과는 각 단위의 명시된 모델에 한정되며, 전체 reionization 모형이나 실제 daughter 연속상태의 완성을 뜻하지 않는다.

그림에서 수치를 추출하지 않았다. 공개 원전의 식을 유도·정규화하고, 이미 회수한 cascade 및 BBN donor를 사용했다. 이번 실행의 물리적 Hamiltonian 작용과 NCP 작업은 각각 0회다. 외부 작업의 실행 상태는 관측하지 않았으며, 외부 solver와 Unit5·PR150 코드는 변경하지 않았다.

## 결과 요약

| 단위 | 새 계산과 실제 결과 | 검증 | 허용되는 해석 |
|---|---|---|---|
| A / T4 | 저장 잔차의 streamed QR/TSQR 압축. 같은 소형 입력에서 직접 계산 0.13205초 → QR 0.01160초 | 8개 PASS | 저장 cache에 조건부인 잔차·resolvent bound의 경량 평가 |
| B / T6 | 실제 8종 × 4개 shell, 총 32개 혼합물의 E1 + 2광자 source. 최대 에너지 회계 잔차 1.42×10⁻¹⁴ eV | 4개 PASS | 고립된 terminal 2s reservoir의 방출 및 선언된 입사 flux 응답 |
| C / T7 | 8개 전하별 EC 채널, 22개 상태 adapter, 실제 donor의 조건부 노출·시간 계산 | 6개 PASS | 주어진 포획률에서의 보존적 반응 연결과 조건부 끝점 |

## A. 저장 잔차의 QR 압축

자기수반 행렬 $K$, 저장 기저 $V$와 작용값 $KV$에 대해 Unit5의 정의를 유지한다.

$$C=V^\dagger KV,\quad J=(C+C^\dagger)/2,\quad d=u-Ve_1,\quad E=KV-VJ,$$
$$z=\omega+i\eta,\quad t=(zI-J)^{-1}e_1,\quad r=d+Et,\qquad\eta>0.$$

$A=[d,E]$, $x=(1,t)^T$를 두면 $r=Ax$이다. 행 블록마다 reduced QR을 수행하고 작은 삼각인자를 차례로 축약하면, 전역 $Q$나 전체 $E$를 저장하지 않고도 $\|r\|=\|Rx\|$를 계산할 수 있다. 복소 자료에서는 conjugate transpose를 사용한다. Rank deficiency가 있어도 $R$을 역으로 풀거나 작은 특이값을 잘라내지 않는다.

따라서 기존 scalar bound와 spectral-density bound를 그대로 평가한다.

$$B(z)=\frac{\|u\|\,\|Rx\|}{\eta}+|(u^\dagger V-e_1^\dagger)t|,\qquad B_\rho(z)=WB(z)/\pi.$$

이 bound의 물리적 적용은 자기수반성과 저장 작용값의 정확성에 조건부다. 실제 구현은 부동소수점 진단이며, outward rounding을 적용한 엄밀한 수치 구간은 아니다. $C$와 $J$를 구별하는 합성 검증은 일부러 불일치하는 cache를 사용하며, 그 fixture에서 물리적 full-space bound를 주장하지 않는다. 원래 spectrum/CDF 수렴 기준은 바꾸지 않았다.

추가 workspace는 $O(bm+m^2+m\,\mathrm{batch}+P)$, 계산량은 $O(Nm^2+\lceil N/b\rceil m^3+m^3+Pm^2)$이다. 기존 cache의 $O(Nm)$ 저장은 별도다. NPZ CLI는 배열을 메모리에 읽으며, 파일 자체를 디스크에서 streaming하는 구현은 아니다. 작은 상쇄 fixture에서 QR은 $10^{-10}$ 잔차를 유지했고 raw Gram의 이차형식은 0이 되었다. 이 관측을 모든 Gram 방법에 대한 불가능성 주장으로 확대하지 않는다.

실제 단일 비교는 seed 20261016, $N=512$, $m=32$, float64, 6003개 평가점에서 수행했다. Setup을 포함한 직접 계산은 0.132048875초, QR은 0.011603992초로, 관측 비율은 **11.3796배**였다. 최대 norm 차이는 $2.34479\times10^{-12}$, 최대 bound 차이는 $4.68390\times10^{-11}$로 계약의 scale-aware 허용범위 안이다. 실제 385112차원 NCP checkpoint에서의 성능은 아직 측정하지 않았다.

## B. 기존 cascade의 2광자 성분

입력은 실제 저장된 8종의 $n=3,5,10,12$ 통계적 shell 혼합물이다. 종은 H∞, HeII∞, LiIII∞, H1, D, T, He3II, He4II다. 기존 E1 선의 에너지와 terminal 2s 확률 $P_{2s}$를 보존했다. 시간 원점은 초기 shell 주입 시점이 아니라 **E1 cascade가 끝난 terminal reservoir**이다.

$y=E/\Delta$, $w=y(1-y)$에 대해 원전의 analytic fit은

$$g(y)=w[1-(4w)^{0.8}]+0.88\,4^{0.8}w^{2.33}.$$

정규화는 beta 함수로 직접 얻는다.

$$I=B(2,2)-4^{0.8}B(2.8,2.8)+0.88\,4^{0.8}B(3.33,3.33)=0.08144613055216544.$$

$f=g/I$는 임의로 선택한 광자 한 개의 분포로 적분값이 1이다. 한 decay의 광자수 밀도는 $2f$이며 적분값이 2다. 비상대론적 무한핵질량 rate anchor $8.229352 Z^6\,\mathrm{s}^{-1}$에 기존 Coulomb 선 에너지의 reduced-mass 비를 적용한다.

$$A=8.229352 Z^6\frac{\Delta}{Z^2\Delta_{H,\infty}}.$$

이는 전자 상대좌표 dipole 근사에 따른 질량 스케일링이다. 완전한 recoil/QED 보정이나 정밀 동위원소 수명을 주장하지 않는다. 문헌의 fit 정확도는 거의 전체 스펙트럼에서 약 1%이며, 끝점까지 균일한 오차 보장은 없다. 이는 적분의 수치 허용오차 $10^{-8}$과 별개다.

고립된 reservoir에서는

$$D(t)=-\operatorname{expm1}(-At),\quad N_{2\gamma}=2P_{2s}D,\quad U_{2\gamma}=\Delta P_{2s}D,\quad U_{\rm res}=\Delta P_{2s}e^{-At}.$$

각 bin의 광자수와 에너지를 따로 적분했다. E1, 2광자, 잔여 reservoir의 에너지 합은 최초 여기 에너지와 일치한다.

| 종 | $A$ [s⁻¹] | 수명 [s] |
|---|---:|---:|
| H1 | 8.2248725944 | 0.1215824304 |
| D | 8.2271105755 | 0.1215493569 |
| He4II | 526.60633377 | 0.001898951714 |

H1, $n=3$의 실제 $P_{2s}=0.0394450215000$에서 최종 2광자수 **0.0788900430000**, 에너지 **0.402288550123 eV**를 얻었다. $n=12$에서는 각각 0.0164738183543과 0.0840058928695 eV다. 수율은 초기 precursor 하나당 값이다. 모든 32개 혼합물에서 저장된 $P_{2s}$와 독립 cascade 합이 일치했고, 최대 에너지 회계 잔차는 $1.42109\times10^{-14}$ eV였다.

C99 커널과 Python 자료 드라이버의 build/run은 0.835초, 4개 검증은 0.082초였다. 64/128/256절점 결과를 모두 보존하고 256절점 결과를 최종값으로 표시했다. 새 SCF나 원자 Hamiltonian 계산은 필요하지 않았다.

Li I photoresponse는 기존 Verner 자료의 **5.392–64.39 eV** 범위에서 평가했다. $J=1$ precursor-equivalent m⁻²s⁻¹의 입사 flux를 선언한 선형 응답이며, 우주론적 emissivity에서 local flux를 추론한 결과는 아니다. LiIII∞의 2광자 방출 중 64.39 eV 초과 부분은 **광자수 24.5799%, 에너지 40.2214%**다. 이 source 성분은 보존했고 해당 범위의 흡수 응답은 미결로 두었다. 자료가 없는 단면적을 0으로 치환하지 않았다.

## C. Be7 전하별 전자포획

전자수를 직접 세면 다음 8개 채널을 얻는다. 여기서는 spectator shakeoff를 포함하지 않는다.

$$\mathrm{Be7}^{q}\longrightarrow\mathrm{Li7}^{q},\quad q=0,1,2,3\quad\text{(bound EC)},$$
$$\mathrm{Be7}^{q}+e\longrightarrow\mathrm{Li7}^{q-1},\quad q=1,2,3,4\quad\text{(continuum EC)}.$$

전자는 각각 bound 또는 free pool에서 하나 감소한다. 핵전하와 총 전자수가 함께 하나 감소하므로 중입자수, 중핵수, 순전하는 보존된다. Be4의 bound capture는 결합 전자가 없어 금지된다. Be0의 continuum capture는 Li⁻ 채널이어서 현재 상태공간 밖이며, 해당 비영 hazard 입력은 거절한다. 전하 bin만으로 daughter의 전자 바닥상태를 가정하지 않는다.

기존 17개 상태에 Be의 5개 전하 상태를 보조 reservoir로 붙인 **22개 상태 adapter**를 만들었다. 실제 EC에서 변하는 Be/Li 9개 population의 column generator도 구현했다. 이는 native 17-state solver 통합의 완료가 아니다.

고정한 prescribed hazard $b_q,c_q$에서 소멸량은

$$D_q=Y_{\mathrm{Be},q}[-\operatorname{expm1}(-(b_q+c_q)\Delta t)]$$

이며 bound/continuum 분기는 $b_q/(b_q+c_q)$와 $c_q/(b_q+c_q)$로 배분한다. 별도의 Poisson uniformization과 대조했다. Continuum hazard의 $n_e$는 주어진 밀도이고, 실제 자유전자 소비량은 부호가 있는 별도 ledger로 기록한다. $n_e=n_bY_e$가 동적으로 바뀌는 비선형 plasma의 정확해를 뜻하지 않는다.

실제 donor는 $Y(\mathrm{Be7})=3.784994236672219\times10^{-10}$, $Y(\mathrm{Li7})=2.1819521581308123\times10^{-11}$이다. 원래의 bare Be7 가정을 유지한 채 bound capture만 켜면 변환은 없다. 조건부 완전 변환의 해석적 끝점은

$$Y(\mathrm{Li7})=4.0031894524853\times10^{-10},\qquad \mathrm{Li7}/p=5.315638794034029\times10^{-10}.$$

Be는 제외 reservoir에서 한 번만 옮겼으며 다른 donor 핵종과 원래 정규화 잔차 $+1.62625\times10^{-12}$는 그대로 남겼다. 임의 재정규화는 하지 않았다.

문헌의 약 **106.4일 반감기**는 통계적 hyperfine 혼합을 가진 준비된 hydrogenic Be3 상태에만 조건부로 적용했다. 그 상태가 유지되고 다른 과정이 없으면, 106.4일과 212.8일 뒤 Li 합계는 각각 $2.1106923341491906\times10^{-10}$과 $3.0569408933172453\times10^{-10}$이다. 이는 우주론적 변환 epoch나 모든 전하 상태의 공통 반감기가 아니다.

실제 6개 검증은 0.149초의 unittest 실행에서 통과했다. 내부 검증 구간의 별도 측정값은 0.14305초다. 모든 8개 채널을 단위 population과 donor 규모에서 검증했다. Analytic map과 uniformization의 최대 차이는 단위 규모에서 $1.28786\times10^{-14}$, Poisson 누락 tail의 최대 상한은 $9.72484\times10^{-15}$였다. $10^{-10}$ 규모의 전자 변화량을 큰 수의 차로 잃지 않도록 별도 signed delta를 저장한다.

물리적 열침적은 `null / NEEDS_ENERGY_PARTITION`이다. Bare-nuclear Q, 양쪽 전자 에너지, 포획 전자 운동에너지, neutrino·gamma·recoil 분배가 필요하다. 합성 에너지 회계 검증값을 Be7의 물리적 예측으로 사용하지 않았다. T4의 실제 daughter 분포가 향후 추가 분기와 에너지 분배를 제공할 수 있다.

## 프로젝트 DAG와 후속 연결

세 단위의 상세 재현법은 `README.md`, 구현 기록은 `docs/`, 원전의 실제 열람 범위는 `evidence/*_SOURCES.md`에 있다. 이론 계약 → 구현·실행 → 독립 검토의 역할을 분리했다. 요청한 실행 모델과 관측 가능한 모델 식별값을 구분했으며, 관측값이 제공되지 않은 경우 UNKNOWN으로 기록했다.

SciSpace와 Exa에서 후보를 탐색하고 원전을 확인했다. Wolfram은 연결 및 MCP 오류로 성공한 계산 결과가 없었다. 이 실패는 `evidence/WOLFRAM_ATTEMPTS.json`에 남겼으며, 로컬 계산을 Wolfram 검증으로 표현하지 않는다. 이번 세 단위에는 텐서 미분이 없어 xAct 계산을 실행하지 않았다.

기준 PR151은 `edead5026fdcc4217a9caec5106f7839c6aec5a5`, PR150은 `eb2abcac4f44b7bc4ff532286953fcb4e353c7bb`다. PR150 SOURCE010/011 결과는 별도 owner의 scoped 근거로 재사용했다. 초기 대조 시 PR151에 새 Unit5 실제 실행 결과가 게시되지 않았다는 사실과 외부 프로세스 상태를 구별한다.

T1–T8의 전체 물리 프로그램은 모두 열린 상태다. `progress/DAG.md`에 기존 성과, 이번 진척, 다음 물리 의존성을 표로 기록했다. 실제 Unit4의 64차 유한공간 진단은 재사용하지만 spectrum/CDF refinement는 HOLD이며, W를 이온화 확률로 바꾸지 않는다. Unit5의 재개 코드가 로컬에서 검증되었다는 사실도 실제 128차 결과와 구별한다.

R1–R10 및 C1–C10의 근거는 `progress/STAGES_FINAL.json`에 각각 연결한다. S1은 이론·설계, S2는 실행·검토·전달을 담는 공통 immutable checkpoint다. 단계마다 별도 업로드를 했다는 뜻이 아니다. 각 단계의 백업·게시 위치와 확인 수준은 delivery 영수증에 기록하며, 최종 영수증은 archive 생성 뒤의 실제 업로드·게시 상태를 확정한다. 새 strong no-go 판정은 없다.

## 주요 공개 원전

- Chluba & Sunyaev, 2006, analytic two-photon fit and normalization: https://arxiv.org/pdf/astro-ph/0508144
- Wundt & Jentschura, 2009, nonrelativistic rate anchor: https://arxiv.org/pdf/0909.4836
- Schirmer, 2016, explicit fit and stated accuracy: https://arxiv.org/pdf/1608.03132
- Khatri & Sunyaev, Be7 recombination/capture and conditional hydrogenic rate: https://arxiv.org/abs/1009.3932 ; full text https://wwwmpa.mpa-garching.mpg.de/mpa/publications/preprints/pp2011/MPA3083.pdf
- Verner photoionization data: https://www.pa.uky.edu/~verner/photo.html
