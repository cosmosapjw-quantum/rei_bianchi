# 부분 canonical 누적 수리 및 실제 재개

원 PR86/88 복사본과 외부 duration 연구 원본을 변경하지 않고, 별도 연구 복사본에만 구현했다. 원 source/provider/closure/TOL 및 N/E 허용량은 그대로다. `canonical_owner.rs`는 기존 `Wide/Tracked`의 13개 owner와 양의 subnormal 기여를 보존하며, occurrence/coefficient와 전량 소실·부분 mantissa 반올림·readout 손실을 함께 기록한다. NORMAL 회귀와 실제 실패 operand의 exact-rational oracle이 통과했다. 손실은 원 residual 허용량에 더하는 대신 residual의 절댓값에 더해 판정한다. 광흡수 A/B의 손실도 gas residual로 선형 계수를 따라 전달한다.

새 checkpoint는 평탄한 context, 최대 8192 node 및 16 MiB envelope를 사용한다. 부분 k9/18/9 입력의 알려진 HEAD를 고정하고 gas/epoch/grid/기존 owner/proper clock를 보존한다. 13 canonical owner, 누적 loss/occurrence/coefficient 및 active N/E loss를 실제 직렬화한다. 과거 binary64 checkpoint 이전의 산술 손실은 `NOT_MEASURED`이며 이를 0으로 승인하지 않는다.

실제 1·2·1 advance와 같은 다음 시각의 37-field·N/E·source 비교가 통과해 남은 suffix를 시작했다. 합계 8 advance가 accepted 되었고, 마지막 공통 시각은 k11/22/11, ln(a)=-2.56445769079487, z=11.993609904360573이다. 새로운 두 공통 시각 10/11의 모든 37-field 비교가 통과했다. 0.0008 suffix 완료에 필요한 156회 중 148회는 아직 남아 있다.

첫 suffix의 coarse k11은 accepted/checkpoint 저장 후 Gamma observer가 양의 subnormal `2.81355342775e-312`를 거절했다. 원 실패를 보존하고 Gamma 누적만 canonical로 수리했으며, 같은 k11 checkpoint의 readout만 재개했다. observer의 mantissa·readout 손실은 기존 Gamma 허용량으로 검사하며 비용을 별도 계수했다.

다음 science 실행은 coarse/tail k12 및 fine k23에서 transported stock `3.812277937532397e-309` / `3.79902930489655e-309`를 기존 `characteristic_staged::nonnegative(f)`가 거절했다. 마지막 accepted state는 보존했다. 고정 gas/rates/h/E에서 kernel은 incoming/source에 선형이므로 해당 단일 cell의 power-of-two 정규화는 가능하다. 그러나 `transaction_path`는 최종 stock을 `density.push(o.n)`의 binary64로 저장하고 다음 step에도 `&[f64]`만 전달한다. 이후 n/u가 반올림으로 0이 되면 정규화만으로는 미래의 양의 stock을 보존하지 못한다. 정당한 후속 수리는 node별 canonical transported N/E, segment 사이의 stock/energy handoff, trial/restart 및 observer 경로를 함께 확장해야 한다. 이 국소 수리 단위에서는 guard만 완화하지 않았다.

`RESULTS.json`에는 실제 명령/exit/CPU/wall, 3 science failure와 1 observer failure, 추가 observer 비용과 blocker가 있다. bounded runner 이전의 짧은 compile 시도 비용은 `INITIAL_BUILD_ATTEMPTS.json`에 `NOT_MEASURED`로 남겼다. 외부 원본의 190-step/완료 0.0004는 재실행하지 않았다. 기존 비용·실패도 삭제하지 않았다.

검증은 7 native unit test, 3 Fraction fixture, 5 semantic checkpoint 음성시험, 두 새 공통 시각의 전체 37-field 비교다. 손실 누락·payload 중복·실제 epoch 변조 시험은 checksum을 새로 계산한 뒤 semantic decoder의 거절을 검사한다. 음성시험의 config startup 1 RHS/1 sigma도 계수한다.

전체 z=12→10 및 전체 0.0008는 완료되지 않았다. `MANUFACTURED_MODEL_DISCRETE_REFINEMENT_PASS` 또는 `MANUFACTURED_MODEL_CONTINUUM_VALIDATED`를 선언하지 않는다. old-domain spectral/reconstruction, source/time residual 및 historical representation 손실 권위는 여전히 부족하다. physical history는 HOLD다.
