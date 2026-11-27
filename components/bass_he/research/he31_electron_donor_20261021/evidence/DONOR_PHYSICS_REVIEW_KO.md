# HE31 donor·receiver 독립 물리 검토

**판정: PASS_SCOPED_DONOR_AND_RECEIVER_CONTRACT.** donor와 receiver 구현에 대한 독립 검토다. reviewer가 별도로 작성한 prepared moment evaluator의 독립 승인은 이 문서에서 하지 않는다. 새 물리 궤적, ODE, benchmark를 reviewer가 실행하지 않았다.

전자수 식은 nH·xHII+nHe·(xHeII+2xHeIII)이며 He 분율을 He 핵당으로 취급한다. proper/comoving과 SI/cgs를 명시적으로 변환하고, 핵의 comoving 보존을 확인한 후 첫 행 abundance를 고정한다. comoving electron PCHIP는 물리적 knot 범위를 유지하고, 범위 밖 source extrapolation을 거부한다. 입력 metadata·column bytes와 원본/data SHA가 identity를 구성한다. prepared array는 실제 immutable bytes를 쓴다.

거의 균일한 log-a grid의 scalar fast index는 실제 knot 구간을 벗어날 수 있다는 reviewer 제안을 반영해, 현재 구간 포함 확인 뒤 필요하면 searchsorted로 보정한다. source의 첫 zero knot, 전부 중성인 control과 작은 scalar/vector probe의 zero 보존을 확인했다. source endpoint 밖 8 ulp 이내의 부동소수점 차이는 저장 endpoint로만 clamp하고, 실제 z2 연장은 거부한다.

receiver는 동일 donor를 원본 CanonicalFVSpecies와 optical-depth 진단에 넣는다. 원본 40상태 뒤에 41번째 τT를 추가하여 y[0]의 elapsed-time 의미를 보존한다. 새 진단은 같은 RHS의 첫 성분 Href/H를 재사용하므로 τT′=ΓT/H_target이며 canonical moment를 추가 계산하지 않는다. Thomson 충돌은 광자의 energy/number multipole에만 들어간다. neutrino와 nonbaryonic canonical matter의 RHS는 그대로다. signed Pm, Pgamma, Pnu, Pr=Pgamma+Pnu와 Frobenius norm 변환도 맞다.

## 국소 반올림 기준 교정

초기 8개 contract 중 7개는 통과했고, 새 τ 진단의 고정 절대 기준 1e-18에서 1.734723475976807e-18의 차이 하나가 나왔다. 실패 receipt를 evidence/failed/에 보존했다. 원인은 Γ·(Href/H)/Href의 세 binary64 연산과 직접 Γ/H 사이의 반올림이다. positive normal 영역에서 상대오차는 일차적으로 약 4u, u=epsilon/2 이하이므로 수정한 4·epsilon·abs(Γ/H)는 보수적인 대수 기준이다. 원본 DOP853 rtol=3e-11, atol=3e-13은 바꾸지 않았다.

영향받은 target-clock test만 재실행해 상대차 1.1102230246251565e-16, RHS당 FV moment call 1회, gamma-only RHS 최대 절대차 1.0842021724855044e-19을 얻었다. 전체 suite를 반복하지 않고 donor 식과 물리 RHS가 같은 기존 7개 결과를 재사용하는 것이 적절하다. 후속 bindings의 source-path guard·identity 범위 교정과 receiver의 NumPy JSON 변환·자원 hash 추가도 읽었다. 이 변경은 make_model, augmented_rhs, 물리 normalization을 바꾸지 않는 실행 경계 delta이며 JSON에 검사 당시 전체 파일 SHA와 현재 물리 함수 AST hash를 함께 기록했다. 두 receipt와 교정 사유, 실제 읽은 source SHA는 DONOR_PHYSICS_REVIEW.json에 있다.

## 승인 범위

실제 복구된 R15 donor는 16,385행, z20→4의 Q filling-factor history다. HII=HeII=Q, HeIII=0, residual electron 없음, source FLRW cosmology라는 의미를 그대로 둔다. 입력 knot에서 원본 ne와의 최대 상대차는 8.798584423322662e-16이다. 이것은 대상 Bianchi 모형의 mean a에 처방한 전자 history를 통한 photon-opacity sensitivity에 적합한 연결이다.

이 검토는 R15의 과거 COMPUTED_SCOPED_NOT_YET_REVIEWED 표기를 바꾸지 않으며, 새로운 native H/He 연립 chemistry나 full polarized evolution을 승인하지 않는다. 현재 donor로 z20→2를 실행하지 않는다. 이미 완료된 D3 z20→2 collisionless 결과의 승인도 이 donor 검토 때문에 다시 열리지 않는다. 실제 source coverage를 갖춘 다음 donor는 같은 schema로 별도 identity를 가져야 한다.
