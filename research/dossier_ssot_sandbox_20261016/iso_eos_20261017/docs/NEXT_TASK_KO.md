# ISO-COUPLE 착수 계약

다음 실행단위는 새 `MixtureState` EOS의 `n_th`를 native `ThermalCxSystem`의 Stage 온도 및 초기화 계약에 **하나의 확장 owner**로 연결하는 것이다. 실제 native `ThermalCxComponent::thermal_substep`는 He 방관자가 있을 때 `UnsupportedSpectator`로 거부하므로 원래 거부 동작을 제거하지 않고 새로운 opt-in path의 typed union을 준비한다.

최소 게이트:
1. `DAtomicProvider::defect()`가 `χD−χH`와 원자 공급자 source를 단독 소유하고, `AtomicRhs XOR ThermalSubstep`을 각 stage에서 검사한다.
2. H/He/D의 `n_e`는 한 번만 `IsotopeNumberState::moments()`에서 얻는다. 광흡수 HI/HeI/HeII/D는 경쟁 photon event를 공유한다.
3. He4 spectator를 포함한 적분에서 thermal `C_V`를 모든 nuclei + electrons로 계산하고, source-off/zero-rates/pure-HD limit 및 부호 있는 CX event의 exactly paired `Δu_th=-Δu_chem`을 검사한다.
4. `Savin2002` T=2.7..2e5 K, 부호, source SHA, Case-A, FF/CMB shared owners, no clipping/extrapolation, failed step transactional.
5. 짧은 샌드박스 coupled RHS 검증 뒤에야 BI-SIGNED/full EoR 시간·스펙트럼·각도 수렴의 별도 승인 가능; NCP 외부 계산은 이 작업에서 호출하지 않는다.

`ISO-EOS` 이번 bounded 결론은 전체 native 네트워크 완료가 아니라 source-locked conservation+EOS reference.
