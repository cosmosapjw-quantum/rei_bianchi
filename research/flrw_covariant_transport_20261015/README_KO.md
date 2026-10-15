# Native covariant transport와 D atomic point unit

현재 관측: 새 transport core7개와 driver7개, D atomic provider/RHS8개로 서로 다른 새22개 검증이 통과했다. Signed source-endpoint focused 재실행은 기존 core검사1개의 추가 assertion이며 새 test수에 중복 가산하지 않았다. Driver초기6개는 실제 출력이 있지만 실행 당시 SHA가 보존되지 않았고 core의 좁은 arithmetic repair 전 실행이므로 최종 source-byte-bound combined suite로 부르지 않는다. 독립 C9는 PASS_SCOPED_COMPONENTS_PILOT_GATE_PENDING으로 component 구현·근거 게시를 승인했다. z20→19.8의 q128 pilot은 여전히 실행 중이며 예정된5case의 실제 완료·수렴 screen과 full NCP launch admission은 미완료다. 이전28 checks와 기존 ZERO history는 원래 범위로 재사용했고 재실행하지 않았다.

새 transport는 reference-energy cell의 N/U/support를 보존하고 geometry에서 실제 반응 energy를 관측한다. Threshold-cut positive quadrature를 기존 cold H/He four-variable Newton과 공유하며, 같은 흡수 사건이 photon loss·photo rate·heat를 소유한다. 반복 physical-energy projection을 제거한 구현이지, 두 모멘트에서 실제 spectrum을 유일하게 복구했다는 주장은 아니다. 첫 near-endpoint roundoff 실패와 승인된 compensated-sum repair의 원시 결과를 모두 보존했다.

D 모델은 `GRACKLE_3_4_1_H_EQUALITY_D_ATOMIC_V1`이다. 기존 pinned Grackle H CI/Case-A RR/kinetic cooling/CE를 SI로 변환해 재사용하고, 실제 Verner HI cross section에 명시적 D threshold를 적용한다. 이는 선언된 H-equality approximation이며 isotope-exact rate가 아니다. 명시적 χD와 같은 defect를 PI/CI/RR escape/CX에서 사용한다. Native isotope state 전체의 electron census, H/D·charge·baryon·energy와 D+의 electron/Z² contribution을 제공하지만, HHe production에 D를 활성화하지 않았다.

조건부 inventory helper는 nD/n1H, provenance, 불확도 정의와 ionic IC mode를 명시적으로 받는다. 고정 nb에서 n1H=nb/(1+2rD+4fHe)이며 D의 baryon number는2다. Cooke2018 관측값을 채택한 fixture는 matched REC donor나 새 BBN 계산이 아니다. 3He 후보와 Li의 실제 photo/RR table도 확보했지만 Li의 sub-Lyman spectrum/transport, CI/DR/CX와 thermal moment는 추가 입력이다.

실제 NCP는64logicalCPU, RAM135050518528bytes이고 접속·별도 Rust1.94.1이 관측되었다. Full science run은 아직 시작하지 않았다. `NATIVE_CONTRACT.md`의 최종 자원 한도를 적용한다: science case최대2개, 초기 case당native thread1, AS8GiB/output4GiB, 전체 campaign43200s에 closeout300s를 남긴다. 이전 preflight의 더 큰 메모리 제안은 최종 배정이 아니다. 실제 표현·screen·독립 심사가 통과하면 이미 받은 승인으로 fresh full FLRW와 refinement companion을 실행한다.

진행 순서는 FLRW production → full-history refinement → qref=±0.005/±0.01 Bianchi와 실제 proper-time/Tgas plots → D coupled isotope full network다. D source/provider 작업은 이 주경로를 막지 않는 병렬 단위다. 보존 검산이나 짧은 pilot을 전구간 수렴으로 확대하지 않는다.

읽기 순서: `HANDOFF.json` → `NATIVE_CONTRACT.md` → `CODING_LOOP.json` → `NEXT_DAG.json` → `TASK_PACKETS.jsonl`. C9 component 판정과 기계적 인계는 완료되었다. C10의 remote publication·이중 backup은 root의 실제 DELIVERY_RECEIPT를 받기 전까지 PENDING이다. 요청 implementation model은 gpt-6.1-sol/high, review model은 gpt-6-astra/high이며 실제 runtime model은 독립 관측되지 않았다.
