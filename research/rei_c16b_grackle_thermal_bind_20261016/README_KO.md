# Native Grackle RR/CI/thermal 결합 연구

실제 native `Driver::chemical_stage`와 `igm_point_rhs`를 그대로 호출하는 photon–gas accepted-step transaction을 구현했다. 온도 의존 Case-A RR/CI/DR, CE, freefree, signed CMB 및 binding/escape 소유권을 보존한다. 전체 native Rust tree는 수정하지 않았다. 연구용 adapter와 실행기는 이 디렉터리에만 있다.

결과와 범위는 [HANDOFF_KO.md](HANDOFF_KO.md), 식·단위는 [THEORY_KO.md](THEORY_KO.md), 구현은 [README_NATIVE_KO.md](README_NATIVE_KO.md), 독립 검산은 [README_REFERENCE_KO.md](README_REFERENCE_KO.md)를 읽는다. 검토 판정은 INDEPENDENT_REVIEW.json, 원본 소스와 전체 실패/원시 자료는 intake/ 및 evidence/에 있다.

`restore_verify.sh`는 보관한 immutable 원본 소스를 새 디렉터리에 복원하고 새 Rust binary를 빌드하여 event/rollback/retry/32-step native 결합을 실행한다. Cargo 의존성 cache와 Rust/C compiler가 필요하다. 독립 reference 재실행에는 NumPy/SciPy와 PR154 source-aware 코드가 필요하다. 기존 29+22+37 테스트는 소스 identity에 따라 재사용했고 이 실행의 새 테스트 수에 포함하지 않았다.

Production scientific admission: **NOT_ISSUED**. 고정 배경 검산과 짧은 동적 제어 실험이며 물리적 z=20→4 결합 이력은 아직 계산하지 않았다.
