# P02A: 5000 K raw provider 진단

정확히 5000 K, Case A, C units=1에서 현재 Rust `AtomicProvider`의 18개
계수를 기존 F01 isolated original-C와 실행 비교했다. 최대 상대 차이는 0으로,
기존 3e-12 tolerance를 만족했다. 결과는 `PASS_DIAGNOSTIC`이다.
저온 물리 provider 및 cold history admission은 `HOLD`다.

## 관측된 분기와 수치

- K1의 원 polynomial은 약 3.98587044e-22 cm3/s지만 raw 값은 1e-20이다.
  floor 비율은 약 25.0886이다. K3와 K5도 low-temperature branch에서 1e-20이다.
- K2는 5500 K 이하에서 K4를 호출하여 둘 다 6.69267111374399e-13 cm3/s다.
  [HG97 Appendix A](https://adsabs.harvard.edu/pdf/1997MNRAS.292...27H)의
  HII Case-A RR 식은 6.975127812378202e-13으로 raw 값과 -4.04948% 차이,
  HeII RR 식은 6.647688939149075e-13으로 +0.676659% 차이다.
- CeHeII의 capped/unclipped 식 비율은 1.379348363443488e11,
  dielectronic cooling ReHeII2는 6.663176216410914e10이다.
  CI와 DR의 5000 K unclipped 식은 primary fit 유효 구간 밖인 구현 진단이다.

이 수치는 물리 오차 추정이 아니다. HG97 비교는 명시한 RR 두 성분에 한정되고,
전체 raw provider의 물리 유효성은 `COMPARATOR_DOMAIN_PARTIAL`이다.
밀도 상태, thermal/binding ledger 및 REC endpoint는 여기에서 정의하지 않았다.
기존 source의 alias, floor, exponential cap과 HeIII raw 8*T prefactor를 보존했다.

## 실행과 검증

```sh
python3 research/physical_provider_20261010/p02a/audit_lowt.py --output /tmp/rei-p02a-new-output
python3 -m unittest discover -s research/physical_provider_20261010/p02a -p test_audit_lowt.py -v
rustfmt --edition 2021 --check rust/rei_microphysics/examples/atomic_lowt_probe.rs
```

`--output`은 새 디렉터리만 받는다. runner는 source 3개의 SHA를 검사한 뒤,
기존 isolated C bodies와 Rust public provider를 실제 호출한다. 생성된 C driver와
binary/Cargo target은 임시 디렉터리에만 둔다. 표준 라이브러리 외 Python dependency는 없다.
초기 실행 command/exit/stdout/stderr와 18개 raw 값은 `evidence/initial/`에 있다.
4개 targeted Python tests와 새 Rust example format check가 통과했다.
첫 실패와 repair는 없었다. 시간 적분, temperature sweep, history 재실행 횟수는 모두 0이다.

후속 최소 작업은 source에 근거한 저온 thermal/binding closure와 REC cold H/He endpoint
계약 확정이다. FT03 온도 guard와 P01 warm conditional execution은 이 진단으로 바뀌지 않는다.
