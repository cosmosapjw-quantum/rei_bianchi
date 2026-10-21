# D9 최종 source / backup closure

## 실제 전달 확인 — 20261021T141519Z

D9 과학 판정은 **PASS_SCOPED_D9**이며, 과학 코드와 결과는 아래 source commit에 고정되어 있다.

- Source commit: `407f2a30efcdd0c4c4afb180cbe7d31f90cc0401`
- Source tree: `7590e6f8a7ffcc3153d9b7595325ab24c7844783`
- Git 전체 readback: **94 / 94 파일**, **6,410,424 bytes**, SHA256 및 Git blob SHA1 일치. Tree mode도 **94 / 94 PASS**.
- 최종 archive: `REI_D9_FINAL_DELTA_20261021T141112Z.tar.gz`
- Archive 크기: **4,576,719 bytes**
- Archive SHA256: `bf3547dd6542626d011d51251e1a091d9ac0cca5480d6124c6faca09cfc3d679`
- Drive 파일 ID: `1V-aTSz2A74dgKwXmkOeBh-EcE03RVZ5V`
- Dropbox 파일 ID: `id:BSpOijBcT10AAAAAAD_hkA`
- 두 provider의 전체 GET, archive bytes / SHA256 및 모든 member 검증: **PASS**.

최종 metadata는 위 archive를 포장한 뒤 작성된 별도 기록이다. 이 metadata를 포함하는 실제 commit M은 외부 post-publication ACK에서 확인한다. M을 자기 파일 안에 미리 적지 않는다. 권위 있는 전달 기록은 `research/rei_unified_sigma_pi_20261021/D9_COMPONENT_SHEAR_BUDGET/D9_DELIVERY_ACK.json`이다.

Source CI run **39614246060**, job **119270894522**는 기존 Rust 경로의 `cargo fmt`에서 실패했고 Rust tests는 skipped다. D9는 Rust source를 바꾸지 않았으며, 이 CI 결과와 D9의 scoped PASS를 구분한다.

다음 단일 노드는 **D10_ZERO_INITIAL_MATTER_STRESS_GENERATION**이다. 상태는 **READY_FOR_THEORY_AND_SAVED_DATA_INTAKE_NOT_RUN**이며, 먼저 analytic / saved-data contract를 고정한다. 최초 허용 new IVP는 **0**이다. 완료한 pilot, D8 또는 D9를 다시 실행하지 않는다. 실제 D9 NCP 실행은 **NOT_RUN**이다.

PR198 scoped PASS, AGE convergence HOLD, Grackle bound NOT_ESTABLISHED, production scientific admission NOT_ISSUED 및 V12 제한은 그대로 유지한다.

## Provenance 관계

Source S와 그 전체 Git / tree readback을 먼저 확인한 뒤 final archive를 포장하고, 두 provider의 실제 업로드 및 전체 member readback을 확인했다. 이 최종 metadata는 그 결과를 참조하며, publication 후의 별도 external ACK가 metadata commit M을 묶는다. Source / scientific files / stored results는 변경하지 않았다.
