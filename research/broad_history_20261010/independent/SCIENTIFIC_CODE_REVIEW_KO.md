# REI-ACCEL01 독립 과학·코드 검토

검토 범위는 고정된 R15 + HG97-B, dust+Λ 배경에서 평균 부피 적색편이 20→4+를 계산한 reduced filling-factor history이다. 이 범위의 과학·코드 판정은 **PROMOTE_SCOPED_REDUCED_HISTORY**이다. 전체 native CR, RCT, HH 정밀도, 온도 진화, 방향별 광자 수송 및 관측 모형 승인은 **HOLD**이다. 차단 결함은 발견하지 않았다. 이 판정은 아래 해시로 묶인 기존 결과에만 해당한다. REPORT_KO.md, DAG.json, BLOCKERS.json, RESUME.json의 과학 주장과 상태 분리까지 검토를 완료했다.

검토자는 후보 방정식·구현·승인 기준·reference를 작성하지 않았다. 기존 공개 함수와 저장 산출물을 읽고 호출하여 확인했다. 독립 reference 구현자도 별도 역할이다. 요청된 review 모델 명칭과 실제 실행 모델 신원은 구분하며, 실제 런타임의 모델 신원은 확인하지 않았다.

## 물리적 의미와 단위

- SFR 정규화와 10^53.14의 단위는 상쇄되어 photons s^-1 comoving Mpc^-3가 된다. 구현은 Mpc^3를 cm^3로 바꾼 뒤 n_H0로 나누며, 이 비율에 잘못된 (1+z)^3을 추가하지 않는다. 재결합에는 물리 밀도를 사용한다. 배경의 m_H=m_proton, m_He=4m_proton 근사는 명시되어 있다.
- Q는 이온화 부피 분율이다. 이온화 영역 내부 n_e=n_H+n_He를 재결합 계수에 넣고 Q를 한 번 곱한다. 평균 전자밀도는 (n_H+n_He)Q이다. Q^2 폐쇄로 혼동하지 않았다. He의 별도 광자 수지와 HeIII, 잔여 전자, 열진화는 계산하지 않았다.
- H^2=Hfid^2(Ω_m a^-3+Ω_Λ)+s0^2 a^-6이며 H_i의 1/(1-r^2) 정규화가 r=s_i/H_i를 충족한다. 고정 평균 a에서 밀도와 source를 유지한다. 따라서 Q와 tau의 +/-r 짝대칭은 이 평균 부피 모형의 예상 결과이다. b의 홀대칭도 확인했다. 이것은 방향별 재이온화 신호를 검증하지 않는다.
- tau는 20→4+의 proper-time 구간 적분이다. 낮은 z의 관측자 꼬리와 높은 z의 이전 이력, HeIII 전환을 포함하지 않으므로 총 CMB tau로 부를 수 없다.
- Case B와 단일 He 전자 폐쇄는 명시적 유효 모형이다. Q=1 이후의 Nexcess는 할당되지 않은 광자 장부일 뿐, 광자 spectrum·열·중성 분율·흡수체 수송의 예측이 아니다.

R15의 주요 계수와 우주론은 로컬 primary text에서도 대조했다. HG97 계수 전사는 source contributor가 버전·바이트 해시로 고정한 외부 출처 계약을 근거로 검토했다. 본 검토의 HG97 primary 재열기 요청은 web DisabledError로 실패했으므로, 원문 전체를 별도로 재인증했다고 주장하지 않는다.

## 수치와 반응 처리

`advance_constant`는 고정 A,B의 해와 Q 적분을 함께 계산한다. 작은 BΔx에 대한 phi2 급수는 subtraction cancellation을 줄이고, overlap 시각 이후 재결합·초과량을 같은 적분에서 누적한다. q=1에서 A<B이면 Q가 감소할 수 있다. source-off, zero-sink와 overlap의 기존 분석해 검사를 확인했다. 추가로 기존 함수의 504개 경계 입력(q=0/.8/1, source=0, sink=0, A≈B, 작은 Δx 포함)을 호출하여 오류·음의 산출물·Q>1이 없음을 확인했다. 이 검사는 임의 크기의 모든 부동소수점 입력에 대한 증명이 아니다.

RUN001의 4096↔8192 max |ΔQ|=1.29633e-7은 1e-7 기준에 실패했고 그대로 보존되어 있다. RUN002에서는 기준을 느슨하게 하지 않고 16384 단계로 정밀화했다. 계약에 처음 적힌 격자보다 높은 해상도를 사용한 수정 run이라는 구분을 유지해야 한다.

| 검증 | FLRW | r=.1 | 허용값 |
|---|---:|---:|---:|
| 8192↔16384 max abs(ΔQ) | 3.24083e-8 | 3.24194e-8 | 1e-7 |
| adaptive reference max abs(ΔQ) | 1.08061e-8 | 1.08065e-8 | 1e-7 |
| adaptive reference max abs(Δtau) | 1.78571e-10 | 1.78463e-10 | 1e-8 |
| reference abs(Δz50) | 1.18093e-9 | 3.90405e-9 | 1e-5 |
| reference abs(Δz90) | 8.81415e-9 | 7.84245e-9 | 1e-5 |

refinement의 Q 오차비는 약 4로 중점 방법의 2차 정확도와 일치한다. 별도 adaptive DOP853 reference는 primary 함수나 reaction을 import하지 않고, terminal overlap event와 capped IVP를 사용한다. source/sink 비의 단조성을 분석적으로 확인하여 overlap 후 release가 없음을 확인한다. 이는 독립 구현 비교이며 물리 모형 자체의 독립 검증은 아니다. 직접 비교는 같은 16,385개 x 지점에서 이루어져 희소 출력의 interpolation error를 섞지 않는다.

18개 저장·재사용 case의 데이터 해시, summary 재계산, 유한성, Q 범위, counter 비음성, 시작·종료 적색편이를 확인했다. reference 실행 영수증의 전후 producer 및 산출물 해시도 일치한다. source/C/T/Q_i 변화는 scenario sensitivity이며 통계 오차대나 현재 관측 fit이 아니다. 엄격한 직접 reference 예산은 fiducial FLRW와 r=.1에 입증되어 있다.

## 재개와 산출물

정상 checkpoint는 재사용되며 config 불일치 및 history 바이트 변조는 거부된다. 완료된 결과는 기본 경로에서 덮어쓰지 않는다. 재사용한 RUN001 결과는 그 실행 당시 runner 사본의 해시를 검증한다. 해시는 변경 감지 수단이지 물리적 정확성의 증명은 아니다.

BASS_CELLS의 시간 간격, 해시, delta_tau 합계를 확인했다. ne_eff는 생산자의 dtau/dt로 정의된 시간평균 밀도이고, 이 projection은 별도 정확도 검증이나 기존 BASS interface의 채택 receipt가 아니다. 현재 NOT_EXECUTED 표기는 적절하다.

이 결과는 실제 전구간 reduced scientific history를 낮은 측정 wall time으로 완주했음을 뒷받침한다. 기존 native solver를 동일 문제에서 몇 배 가속했다는 benchmark나 원래 full-physics 프로그램의 완료를 입증하지 않는다.

재현 검토: `python independent/review_existing.py`. 개별 해시 및 검토 결과는 `EXISTING_EVIDENCE_PROBES.json`과 `DECISION.json`에 기록한다. 검토 범위를 바꾸거나 차단 조건을 완화한 내용은 없다.

## 최종 보고서·DAG 주장 검토

`REPORT_KO.md`, `DAG.json`, `BLOCKERS.json`, `RESUME.json`의 추가 검토를 완료했다. 새 차단 결함은 없다. 기존 승인 기준이나 물리 범위를 변경하지 않았다. 기존 probe를 다시 실행하지 않았고 새 문서의 수치 요약·유도·DAG만 확인했다.

u=r²/(1−r²)에서 K=H_F(a_i)²(a_i/a)^6/H_F(a)²이고, A=A_F/(1+uK)^(1/2), B=B_F/(1+uK)^(1/2)이다. 따라서 overlap 전 고정 x에서 w′+B_F w=−K(A_F−B_F Q_F)/2=−KQ_F′/2가 성립한다. 현재 source의 S/R 증가와 Q_i=0은 Q_F′>0을 보장하므로 w≤0이다. 이는 공유 초기조건·고정 source/baryon/평균 a 아래의 도함수이며 임의 feedback source에 대한 보편 정리가 아니다.

D_F=cσ_T(n_H+n_He)/H_F를 두면 tau의 overlap 전 일차 integrand는 D_F(w−KQ_F/2)이다. 두 모형이 모두 saturated인 영역에서는 w=0이며 −D_F K/2만 남는다. overlap 경계 양쪽에서 Q=1이고 tau integrand가 연속이므로, Leibniz 미분의 이동 경계 기여는 서로 상쇄된다. moving boundary로 인한 별도 일차 jump 항을 더하지 않는 보고서의 유도는 맞다. 검토 중 제안했던 D_F, B_F, K의 정의가 최종 REPORT에 명시된 것을 확인했다. 이 명료화는 기존 승인 기준을 바꾸지 않는다.

저장 CAMPAIGN의 14개 16384-step trajectory에서 측정 wall time 합계는 3.2106087329993898초로 3.21초 표기와 일치한다. FLRW 구간은 1363.9134269 Myr이며, 보고서의 shear 및 source/C/T/Q_i Δtau는 저장 요약과 일치한다. 이 시간은 적분 함수 실행 합계이며 파일저장·문헌·검토·종단간 완료 시간이 아니다. 동일 native 문제와의 비교 가속률도 아니다. 문서가 두 제한을 명시한다. 시간 계획은 조건부 작업 예산으로 표현되며 보장된 완료일로 쓰이지 않았다.

DAG의 모든 dependency ID가 존재하며 순환은 없다. 완료된 reduced 경로와 향후 native H/He/thermal/photons, CR causal lineage, RCT spectrum/heat/recoil, HH chronology/원 precision, residual IC, BASS 수신 경로를 분리한다. BLOCKERS는 full-model 항목을 미완료로 유지하며 source 이름 충돌 해결을 causal model 완성으로 취급하지 않는다. 향후 N1/N2는 병렬 개발 가능하되 N3의 실제 전구간 결합은 양쪽 통과를 기다린다. 이 검토는 DAG의 과학적 범위·논리 정합성에 대한 판정이며 모든 다른 repo의 owner 결과를 새로 독립 재인증한 것은 아니다.

검토한 문서의 정확한 바이트 해시는 DECISION에 추가했다. 본 판정 후 DAG의 S2 및 RESUME의 검토 대기 상태를 완료 상태로 바꾸는 상태 전용 편집은 본 과학적 판정을 바꾸지 않는다. 그 경우 원래 검토 해시를 덮어쓰지 말고 상태 전이와 변경 후 해시를 별도로 기록해야 한다.

`README.md`와 `START_CODEX_KO.md`도 읽었다. compact Git 자료와 원시 NPZ를 포함하는 checkpoint 자료를 구분하며, compact clone만으로 원시 실행을 즉시 재개할 수 있다고 주장하지 않는다. 이미 완료된 결과의 불필요한 재실행을 막고, 새 native 단계의 입력·source domain·오차 예산·독립 review를 요구한다. 실제 원격 게시·백업의 완료 여부는 별도 전달 receipt로 검증할 사안이며 이 과학 검토가 대신 인증하지 않는다.
