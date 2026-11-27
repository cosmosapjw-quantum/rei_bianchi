# HE 전종 소비자 inventory와 공급자 자료형 연결

WU의 정본 identity 행과 REC의 실제 population 순서를 연결하고, pinned Mutation++의 명시적 충돌 적분 행을 추출했다. 이번 산출물은 원자료 intake와 소비자 계약 구현이다. 미분 단면적 평가, 적분, 과거 scientific suite, population/thermal IVP는 실행하지 않았다. 부모의 새로운 bounded validation이 별도로 이 코드와 테스트를 판정한다.

## 실제 행과 출처

`SPECIES_PROVIDER_REGISTRY.json`은 WU의 32개 공급 행을 보존한다. 일곱 isotope의 q=0..Z 상태는 20개이고, neutron을 더하면 원 REC/WU의 21 nuclear population slots가 된다. 전자 thermal/fast pool 두 개를 따로 두어 baseline은 23행이다. 나머지 9행은 원 WU compiler의 synthetic 확장 witness로 유지한다. 그 안의 H−, H2, HD, LiH, HeH+, C12/C13/isomer/molecule 이름을 physical source approval로 해석하지 않는다.

| 구분 | 실제 행 | 확보한 연결 |
|---|---:|---|
| H1/D/T q0..1 | 6 | WU isotope/charge와 REC population slot |
| He3/He4 q0..2 | 6 | WU isotope/charge와 REC population slot |
| Li6/Li7 q0..3 | 8 | WU isotope/charge와 REC population slot |
| neutron | 1 | 독립 nuclear population slot; rate/energy 승인 없음 |
| e_th/e_fast | 2 | 같은 전하라도 다른 pool identity; fast는 REC119의 독립 slot이 아님 |
| synthetic extension | 9 | composition/isomer/signed charge/state를 원문대로 보존 |

원자 scalar 공급자는 elemental PI 6행, case-A RR 6행, Maxwellian CI 6행이다. 이를 isotope별 가능한 charge channel과 연결했지만 실제 rate를 새로 계산하지 않았다. PI의 finite source support, RR의 원 WU runtime domain, Voronov CI의 Tmin[eV]/Tmax[keV]와 추출자료 지위를 함께 보존한다. WU78의 elemental electronic equality와 동위원소별 물리 산란 데이터는 서로 다른 근거다. 모든 행의 actual mass[kg]는 별도 state-qualified 공급자가 필요하므로 null이며 A를 질량으로 대입하지 않는다.

- WU compiler: [34dd7d1d…/fixtures.json](https://github.com/cosmosapjw-quantum/WU088_HH/blob/34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad/research/rei_chem_ledger_20261025/fixtures.json), blob `1c5bc6ce212a59364fa895fc24c7874cf64ee355`.
- 실제 WU atomic identity/PI/RR: [PHYS78 source](https://github.com/cosmosapjw-quantum/WU088_HH/blob/34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad/research/hh_phys78_sandbox_nuclide_20261021/source/atomic_network.py), blob `cbc9c5bd0e2a6f9a56b4afc0fbc5ad6f5cba2de2`.
- CI/CX 근거: [PHYS79 source extraction](https://github.com/cosmosapjw-quantum/WU088_HH/blob/34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad/research/hh_phys79_collisional_closure_20261022/theory/SOURCE_EVIDENCE_EXTRACTED.json), blob `4a70da48e40fe22f92a43f4403207d8f91c4fa90`. 당시 remote 원 ASCII/PDF byte 검증은 없었으며 이 intake는 저장된 WU 추출물의 byte identity를 확인했다.
- REC slot crosswalk: [PR119 atomic_model.json](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/ad93fa1c71f8a2b2a0b19836be3c7b739b11b0c7/research/rec_rei_hheli_sandbox_20261021/data/atomic_model.json), blob `73285c1585f8edca92487effe95e68448f3163b8`.

## 열평균 수송 원자료

`EXPLICIT_TRANSPORT_SOURCE_INVENTORY.json`은 고정 Mutation++ XML에서 선택한 H/He/e/분자 source label 사이의 27 explicit pair와 243 Q 항을 추출한다. 전자 e−–H/e−–He/e−–H2, H/H+/H−/H2/H2+/H3+, He/He+/He++ pair를 포함한다. Q 항에는 직접 fit, 복합 Murphy 식과 potential-based prescription이 있으므로 모두를 독립 측정 fit이라고 부르지 않는다. source expression tree, 원 decimal 문자열, ref와 XML 위치가 보존된다. Li, D/T 또는 isotope-specific source가 없다는 이유로 default·0·H 복사를 넣지 않았다.

원 XML은 [Mutation++ commit 58678c0e…](https://github.com/mutationpp/Mutationpp/blob/58678c0e038eb2f078fed3b45640741fdaf167dc/data/transport/collisions.xml)의 blob `d86bf74e05e6bcac9db67cfc03055621ebed2f8c`, 155227 bytes, SHA256 `25e0ac6affa33361e9652d3fd3f43760f40f1a500c0a4993b1ace82c5ce501c2`다. 마지막 newline이 없는 원바이트를 유지했다. LGPL/GPL 원문은 같은 전달 단위의 `../pair_source/upstream/COPYING.LESSER`, `../pair_source/upstream/COPYING`에 있다.

이 파일의 Qbar(l,s)(T)는 속도와 산란각에 대해 적분된 thermal collision integral이다. 특정 충돌 에너지의 σ_l(E)나 dσ/dΩ, ionization daughters의 joint law를 제공하지 않는다. 원 XML의 default와 clipping option은 실행하지 않는다. 기존 HE34 H/He common-T first-Sonine 범위와 새 H–He pair 계약은 `../pair_source/`의 별도 근거를 따른다. isotope source label mapping은 `require_isotope_alias_assumption`에서 명시적인 `elemental_transport_reuse` 가정이 있어야 소비자 요청으로 접수되며, 접수 후에도 actual mass/state/error와 physical provider gate는 열린다.

## HD 및 에너지 소유권

REC-HD-ADAPTER의 실제 고정 계약을 소비자 pointer로 보존했다. HD J0–8, vibrational label 미해결, p/o-H2 collider 2/3, exact T=50/100/200K가 원 범위다. `require_hd_source_node`는 이 계약의 요청 조건만 검사하고 rate를 내지 않는다. molecular level/collider parser나 upward-rate 구현은 REC owner에 남긴다. HD raw dataset의 redistribution licence가 미확인인 원 상태도 유지하며 이 소비자 단위에 raw HD dataset을 새로 포함하지 않았다.

scalar number rate, differential energy transfer, birth kinetic energy, thermal reservoir와 C_V는 서로 다른 입력이다. 이 inventory는 e_fast를 e_th로 바꾸거나 방출/흡수 에너지를 열에 자동 배정하지 않는다. 교환·single-energy-owner interface의 실제 수식과 구현은 `../exchange/`에서 연결한다.

## 구현과 실행 상태

`consumer_inventory.py`는 표준 라이브러리만 사용한다. AST의 literal assignment를 읽고 WU scientific module을 import하지 않는다. 자료형 및 blob identity, composition·charge·state·pool, source quantity, 명시적 isotope mapping, HD node/collider, nested XML expression에 관한 새 `unittest`를 준비했다. 과거 WU249 compiler 검증을 호출하지 않는다.

준비 build는 한 번 성공했다. complete child CPU 0.055269s, wall 0.06285057899731328s, peak RSS 15572KiB이며 원 기록은 `SOURCE_BUILD_PROCESS.json`이다. 내부 build/save 구간의 더 작은 측정은 `SOURCE_EXTRACTION_RECEIPT.json`에 별도로 있다. 두 비용을 합산하지 않는다. 이후 추가한 두 consumer request guards는 metadata producer `build()` 경로를 바꾸지 않으며 원 build를 재실행하지 않았다. 준비 중 한 materialization 명령이 host argument-length 한도로 실행 전에 실패했고, 작은 batch와 exact-source copy로 복구했다. 이는 `../sources/SOURCE_PROVENANCE.json`에 environment failure로 남겼다.

재생성 명령(새 source 변경 또는 실제 복구 필요가 생겼을 때):

```sh
python3 research/program_expansion_20261025/continuation_20261025/species/consumer_inventory.py
```

부모 bounded 검증 명령:

```sh
python3 -m unittest discover -s research/program_expansion_20261025/continuation_20261025/species -p 'test_*.py' -v
```

이 작성 단계에서 테스트 suite는 아직 실행하지 않았다. 최종 parent receipt/review가 implementation verification을 결정한다. full differential physical provider 0, source input pending, global physical completion=null, HE101 재실행0과 C8 open은 유지된다.
