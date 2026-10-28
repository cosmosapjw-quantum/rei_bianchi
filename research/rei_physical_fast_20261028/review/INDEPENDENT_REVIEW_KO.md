# 독립 검토: 조건부 UVB 보정·실제 history adapter·17상태 그림

2026-10-28. **PASS_SCOPED_CONDITIONAL_UVB_ADAPTER_AND_FIGURE.** 실제 관측 공분산을 이용한 진폭 보정, 공개 Lumina 이력의 영역 제한 adapter, ON_refined 기본 선택, 저장된 17상태의 단일 축 그림을 채택한다. 현재 범위를 막는 finding이나 필요한 수리는 없다. 물리적 F4 전체는 **PARTIAL**이다.

검토자는 이론·입력 전사·구현·실행·그림의 작성자가 아니다. 요청 tier는 Astra이고 실제 runtime model identity는 UNKNOWN이다. 사용자가 지정한 `skill://user/6aa0657100b08191b7d67482d1f97c1d/physmath-research-loop`의 내장 **1.0.0** SKILL 및 RESEARCH_POLICY, THEORY_LOOP, CODING_LOOP, EVIDENCE_AND_HANDOFF, RUNTIME_AND_LEGACY를 읽었다. 이전 1.3의 stage-only 규칙을 이 요청에 적용하지 않았다. READY 이후 한 차례 원자료·수식·코드·실행 로그·실제 PNG를 읽었다. 검토자가 새 fit, test, IVP, CAS 또는 그림을 실행하지 않았고 재귀 검토자도 만들지 않았다.

## 계산과 물리적 대응

BB13의 7개 값은 log10[Gamma_HI/(1e-12 s^-1)]이고, Table 2의 100C를 나눈 전체 covariance는 dex²다. Cholesky 풀이가 비대각 원소를 유지한다. beta=(1ᵀC^-1r)/(1ᵀC^-1 1), Var(beta)=1/(1ᵀC^-1 1), 명시적 residual quadratic과 subtraction identity가 서로 맞는다. 실제 2점 correlated fixture는 대각 covariance와 다른 답을 내므로 상관구조를 형식적으로만 읽는 검사가 아니다.

실제 결과는 beta=-0.04742695606588649 dex, A=0.8965469633906246, 고정 EOS 통계 sigma_beta=0.02988205841395996 dex다. chi²는 21.900744469615276에서 19.381736839571925로 줄고 nominal dof는 6이다. 이는 주어진 template과 통계 covariance에 조건부인 재보정으로 채택한다. 이 chi²는 진폭 하나로 redshift별 shape 차이가 충분히 해소되지 않았다는 제한을 남긴다. 같은 자료에 적합한 결과를 독립 held-out 검증으로 승격하지 않는다.

EOS residual의 부호는 d+theta*v−m−beta로 일관된다. amplitude를 제거한 theta의 unconstrained 값은 9.004877721814005이고, 허용 [-1,1]에서 +1 경계가 선택된다. 이때 A=1.073999833174361, chi²=15.721474783438493이다. 구현은 nuisance가 amplitude와 퇴화하면 나눗셈을 피하고 양 끝점을 보고한다. 경계 profile은 내부 optimum이나 주변화 posterior가 아니며, Jeans/history systematic covariance는 제공되지 않아 적합에 포함하지 않는다.

Puchwein의 59행 fiducial nonequilibrium 표는 실제 여섯 integrated moment를 공급한다. Gamma의 단위는 target당 s^-1, heating은 target당 eV/s다. 따라서 y*Gamma, y*heating, I*y*Gamma와 흡수 에너지의 합이 올바르며 4pi 또는 c를 다시 곱하지 않는다. proper-volume 값에는 proper nHref를 한 번 곱한다. 이 단위·event/heat 대응은 producer test로 확인됐다. 이 부분 adapter는 새 charge/population RHS를 실행하지 않으며, 기존 전하·바리온 event ownership을 바꾸지 않는다.

하나의 A를 여섯 moment에 공통 적용하는 것은 고정 spectral shape 가정이다. HI 관측만으로 helium/heating 여섯 개가 각각 보정되었다고 주장하지 않는다. 두 photon bin의 event weight를 바꾸면서 Gamma를 고정하면 heating이 달라지는 구성도 맞다. 이는 UV 자료의 현재 정보 내용을 설명하며, 새로운 보편적 no-go 주장은 아니다.

## 정의역·실제 공개 자료·부분 bath

원본 UVB support는 0≤z≤15.1, 관측과 보정 support는 2.4≤z≤4.75로 분리된다. log-positive interpolation, exact-knot zero, zero endpoint를 포함하는 구간의 명시적 linear-rate 처리가 구현되어 있다. z=20이나 fit support 밖의 요청은 거부되며 끝점 clamping이나 작은 양수 floor가 없다. 관측값만 보간하는 별도 adapter는 wᵀCw와 서로 다른 query의 wᵀCw'를 반환한다. 이 covariance를 미측정 interpolation error까지 포함한 오차로 부르지 않는다.

T, n_e, Li rate, MeV photon, CR yield, stopping/escape, inverse-weak bath, H, shear, IC는 null/MISSING_INPUT으로 남는다. 보정된 UV moment는 완전한 열화학 bath가 아니다. 특히 기존 300 K IC/bath와 새 8 K 후보는 자동으로 교환되지 않는다. 기존 substantial-shear donor에 관측 Lyalpha inference를 연결할 때의 redshift·sightline·frame 조건도 문서에 보존되어 있다.

Lumina의 실제 공개 수치 자료를 읽고 적용한 점은 유효한 진전이다. SFRD 246행, HI 258행, HeIII 294행, cumulative tau 981행을 사용한다. 원문의 수치/열 provenance와 source support가 기록되어 있고, 원래 파일 순서는 보존하면서 interpolation용 순서만 증가 z로 맞춘다. HI는 z=4,3에서 unavailable, HeIII는 z=3에서 available로 구별된다. 이들은 simulation/global history이며 관측 covariance나 모든 local parcel의 ionic IC가 아니다.

HeIII 203행의 labeled quantile 순서 이상은 실제 output에 검출되어 있다. 마지막 raw row에서도 15.87th가 median보다 크고 84.13th가 작으며 min>max다. median만 사용하고 나머지 열을 정렬·교체하지 않는 현재 정책을 채택한다. complement에 따른 label 역전은 가능한 설명이며 확정된 수정으로 취급하지 않는다. 해당 band는 unresolved 상태를 유지한다. 공개된 numerical content의 전사/텍스트 identity와 원격 다운로드 byte identity를 구별한 provenance도 적절하다.

SFRD에서 local Gamma로 가려면 spectral yield, 나이·금속도, escape, comoving/proper 변환과 transport가 더 필요하다. 이 미완료 관계를 실제 공개 자료의 부재와 혼동하지 않는다. cumulative tau 역시 원래 simulation/cosmology 및 z<3 가정을 보존한다.

## 기본 선택과 실제 단일 축 그림

새 entrypoint/config는 요청 생략 시 ON_refined, 명시적 선택 시 OFF_base/ON_base/ON_refined를 반환한다. 저장된 case와 설정을 선택할 뿐 solver를 import/실행하지 않는다. ON_refined의 rtol=2e-8, scaled atol=2e-12는 같은 기존 ON 물리 모형의 수치 설정이며 새 UV 보정의 실행 결과가 아니다. 과거 NPZ/CSV와 300 K profile은 보존되어 있다.

실제 PNG를 original resolution으로 보았다. 하나의 log/log 축, 17개 범례, isotope 색, ion-stage 선/marker 및 Li IV가 모두 읽힌다. 제목·축·범례·caption에 겹침이나 잘림이 없다. n×10^22, H×1, D/He3×10^4, T×10^18, He4×10, Li7×10^9가 각 범례에 명시되고 같은 isotope의 charge state는 같은 배율을 쓴다.

표시 범위 1e-8–2 아래의 양수 999 state-time sample과 t=0 제외가 명시된다. 양수를 floor로 바꾸지 않고 CSV에 원값·배율·표시 상태를 모두 남겼다. positive-time exact-zero/negative gap은 이 case에서 각각 0이며 initial zero는 raw 자료에 유지된다. 배율에 따른 isotope 간 세로 순서 변화와 elapsed time의 의미도 명확하다. 새 time sample이나 IVP는 없고 이번 A를 기존 abundance에 곱하지 않았다. **그림 PASS_SCOPED**, 추가 render는 필요 없다.

## 실제 검증·범위·다음 행동

producer suite 9/9 PASS, 실패/오류 0, 첫 attempt exit 0이다. calibration child CPU 0.161047 s와 관측 wrapper 0.001877 s, saved-data render의 관측 증가 0.956201 s를 실제 영수증에서 확인했다. 이 검토는 해당 실행의 재수행이 아니다. 알려진 source survey는 metadata/delta 범위로 기술되어 있고, unavailable Personal Context 및 실패한 첨부를 읽었다고 주장하지 않는다. 검토자는 51개 repo나 모든 과거 blob의 추가 전체 감사를 수행하지 않았다.

완료되는 것은 **조건부 HI UV 입력 보정, 부분 radiation/history adapter, 기본 selector, 요청된 saved-history 그림**이다. physical F4는 PARTIAL, physical fast 4/7, global working 33/88, central 28/88, 기존 phenomenological pilot 7/7을 유지한다. full source calibration·새 physical trajectory를 이 단위의 PASS와 합치지 않는다.

필요한 다음 물리 작업은 high-z history에서 일관된 local bath를 구성하고, 별도의 hard-photon/CR/nT/stopping 입력과 IC·T/n_e/H·관측 전달을 연결하는 것이다. 현재 결과를 게시·보존하는 데 추가 test, IVP, review cycle 또는 재승인은 필요 없다. BUDGET_CLOSEOUT의 main 606.634374, presentation 63.924256494, planning 20.819461885 CPU s 및 원래 policy cap 복귀는 누적 debit과 UNKNOWN_NOT_ZERO를 지우지 않는다.
