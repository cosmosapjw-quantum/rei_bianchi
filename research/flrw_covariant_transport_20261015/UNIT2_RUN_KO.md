# Unit 2 실행 가능한 source ZIP

이 패키지는 native Rust source, 고정 scientific contracts, 명시 configs 및 compact 근거를 담는다. 첫 capped pilot의 전체189MB raw는 별도 `REI_COVARIANT_PILOT_20261015_ATTEMPT1.zip`에 보존하며, 이 패키지에는 terminal checkpoint·source/config binding·최종 장부와 짧은 진단을 넣는다. Build cache, compiled binary와 기존 archives는 포함하지 않는다.

Rust1.94.1 및 Cargo를 준비한 뒤 ZIP을 풀고 그 최상위 디렉터리에서 실행한다. 외부 Cargo dependencies는 없다.

```bash
cargo build --release --locked --offline \
  --manifest-path rust/rei_microphysics/Cargo.toml \
  --example axbi_reionization
```

새 q128 pilot의 실제 CLI는 다음과 같다. Output은 반드시 존재하지 않는 새 디렉터리여야 한다. 이 config는 z20→19.8,600초·20000 accepted-step·65000 starts·5M RHS·256MiB로 제한한다. 시작 전에 현재 `HANDOFF.json`과 source/config identity를 읽고 이미 실행된 동일 case를 불필요하게 반복하지 않는다.

```bash
rust/rei_microphysics/target/release/examples/axbi_reionization \
  --config research/flrw_covariant_transport_20261015/configs/pilot_split_z20_19p8_q128.cfg \
  --output runs/FLRW_Q128_FRESH \
  --case FLRW_Q128_FRESH
```

`inactive_hi_split=true`는 q_ref=0의 정방향 FLRW 전용 variant다. Source·cold H/He 모델·원래 tolerance를 유지하며 passive photons의 N/U와 redshift work를 계속 계산한다. Spectrum 열은 총 moments의 보수적 support envelope이며 실제 spectral density를 복원한 값이 아니다. Full-history launch/admission은 현재 handoff의 실제 NCP screen·독립 심사 결과를 따른다.

과거 diagnostic은 저장 당시 source/checkpoint identity에 종속된다. 현재 V4 binary로 옛 V3 이력을 resume하거나 모든 과거 diagnostic을 그대로 실행할 수 있다고 추정하지 않는다. Test-only V3→V4 기대값 교정은 새 V4 연결 테스트의 범위에 맞춘 fixture 유지보수이며 기존 raw PASS를 새 source의 결과로 바꾸지 않는다.

`UNIT2_SELECTION.json`은 GitHub delta 목록과 ZIP 전체 source 목록을 구분한다. 문서 freeze 뒤 `scripts/unit2_package.py prepare`로 파일 hash를 갱신하고, 명시적인 `build` 명령으로 최종 ZIP을 만든다. Freeze 전에는 ZIP을 만들지 않는다. 이 builder는 업로드·git 변경·numerical launch를 하지 않는다.
