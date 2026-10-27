# 문헌·도구 intake와 현재 주장에 대한 적용

검색일: 2026-10-27. 사용 도구는 SciSpace, Exa, Wolfram이다.
원문 전체를 보존하거나 긴 발췌를 재게시하지 않고, 아래 출처 관계와 실제 읽은 범위를 기록한다.

## Primary source

**Mao, J., Kaastra, J., Badnell, N. R. (2017), The electron energy loss rate due to radiative recombination, A&A 599, A10.**
DOI: [10.1051/0004-6361/201629708](https://doi.org/10.1051/0004-6361/201629708).
[출판사 full text](https://www.aanda.org/articles/aa/full_html/2017/03/aa29708-16/aa29708-16.html).

Exa로 primary full text의 §§1–2.2와 식1–6을 읽었다. 논문은 Milne detailed balance로 photoionization cross section을 RR cross section과 연결하고, RR count coefficient와 electron kinetic-energy-loss coefficient를 서로 다른 velocity moment로 정의한다. 해당 thermal-rate 계산의 전자 분포는 Maxwellian이다.

이 원전은 수와 kinetic energy를 따로 보존해야 하는 물리적 맥락과 기존 native RR kinetic-loss 모형의 출처를 제공한다. 이번 nonthermal integrated event에 새로운 physical rate, thermalization coefficient, spectrum 또는 source history를 부여하는 근거로 사용하지 않는다. 실제 consumer의 signed event와 moment 값은 고정 CR source에서 가져온다.

## Contextual source와 읽기 한계

**Kotelnikov, I. A., Milstein, A. I. (2019), Electron radiative recombination with a hydrogen-like ion, Physica Scripta.**
DOI: [10.1088/1402-4896/ab060a](https://doi.org/10.1088/1402-4896/ab060a).
[arXiv:1810.08071](https://arxiv.org/abs/1810.08071).

SciSpace의 서지/abstract와 Exa의 abstract·reference extraction을 확인했다. 이 자료는 nonrelativistic hydrogenic RR에서 cross section, radiated energy, Maxwellian rate coefficient를 구별하는 맥락을 제공한다. 전체 유도나 논문의 개별 식은 읽었다고 기록하지 않는다. 중복 검색 항목의 2022 repository 날짜를 새로운 journal publication으로 세지 않았다.

## 도구별 실제 작업

- SciSpace: nonthermal electron의 HeIII RR와 count·binding·photon energy 보존에 관한 자연어 질문으로 10개 관련 항목을 받았다.
- Exa: primary 문헌을 우선하도록 검색하고, Mao2017 출판사 원문 및 Kotelnikov preprint extraction을 읽었다.
- Wolfram context: 일반 photon-energy 정보와 여러 no-result 응답을 받았다. 자동 생성된 일반 thermal-energy 식을 현재 monatomic caloric 법칙으로 채택하지 않았다.
- Wolfram evaluator: 한 번의 10초 time-constrained call에서 diagnostic event/JVP/reference/endpoint algebra를 확인했다. 실제 코드와 출력은 SYMBOLIC_CHECKS.json에 있다.

원격 도구의 CPU 비용은 관측되지 않아 UNKNOWN_NOT_ZERO로 기록한다. 본 intake는 로컬 과학 numerical run, source quadrature, CR primary replay를 수행하지 않았다.

