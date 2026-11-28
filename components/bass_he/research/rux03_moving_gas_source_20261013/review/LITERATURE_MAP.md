# MOVING_GAS_SOURCE_05 — 일차 문헌 검토

**검토자:** /root/dropbox_checkpoint  
**역할:** 문헌·가정 검토와 독립 최종 R6 심사. 후보 유도, 코드, 수용기준 및 과학 검산을 작성하지 않았다. 이 문서는 최종 후보 채택 판정이 아니다.

이번 조사에서는 Exa의 세 질의에 각 5개 결과를 요청했고 SciSpace 한 질의의 10개 항목을 확인했다. 검색의 **15개 Exa 결과 슬롯**과 실제 읽은 **네 고유 논문의 지정 절**을 구별한다. 같은 논문의 HTML·PDF·저장소 및 SciSpace 중복 항목은 다른 논문으로 세지 않았다. 전문을 모두 읽었다는 주장은 하지 않는다. 원래 THEORY04의 Farris 및 Rosdahl–Teyssier 검토를 재사용하며 광범위한 추가 조사는 하지 않았다.

## 1. 원전과 읽은 범위

| ID | 원전 | 실제 읽은 위치 | 현재 연결에 사용할 수 있는 범위 |
|---|---|---|---|
| S01 | Younsi, Wu & Fuerst (2012), [A&A 원문](https://www.aanda.org/articles/aa/full_html/2012/09/aa19599-12/aa19599-12.html), [arXiv PDF](https://arxiv.org/pdf/1207.4234) | §2–2.1, printed pp.2–3, 식(5)–(17) 중 불변량·rest-frame 주파수·흡수 부분 | Doppler를 포함하는 invariant opacity |
| S02 | Sądowski et al. (2013), [MNRAS](https://academic.oup.com/mnras/article/429/4/3533/1020840), [arXiv PDF](https://arxiv.org/pdf/1212.5050) | HTML §2.1–2.2; PDF pp.6–7 §3.3–3.5, 식(50)–(61) | 보존형 local implicit matter/radiation source |
| S03 | Wu & Tang (2015), [arXiv PDF](https://arxiv.org/pdf/1504.07707), [JCP DOI](https://doi.org/10.1016/j.jcp.2015.06.012) | 변수·EOS 정의, 식(2.1)–(2.5), pp.5–7 Lemma 2.1의 전체 증명 | 고정 gamma-law EOS의 strict primitive admissibility와 유일성 |
| S04 | Cai, Qiu & Wu (2023 arXiv 원문), [PDF](https://arxiv.org/pdf/2305.14805) | p.6 식(2.3)–(2.4), pp.8–9 Theorem 2.1–2.2 및 그 증명 | 원래 pressure equation과 제곱된 quartic의 물리적 뿌리 구별 |

### S01 — 흡수율의 frame 변환

식(9) 뒤의 invariant absorption coefficient는 \(\nu\alpha_\nu\)이며, 식(12),(17)은 local medium rest-frame 주파수와 optical depth에 \(-k\cdot u\)를 사용한다. 따라서 \(\delta=\nu'/\nu\)를 쓰는 현재 표기에서 \(\alpha_{\rm lab}=\delta\alpha'\)라는 대응이 가능하다. 논문이 \(\gamma^{-1}\)로 표시한 frequency shift는 본 연구의 gas Lorentz factor \(\gamma\)와 다른 표기다. ray tracing의 affine 방향도 lab의 전진 시간과 구별해야 한다.

이는 원전 불변량의 **프로젝트 표기 사상**이다. 논문이 H/He species의 BE 식이나 event volume 정규화를 직접 제시한 것으로 인용하지 않는다. 현재 \(j_\gamma=cN_{\rm lab}k\)에서 \(N'\)를 관측자 projection으로 정의하는 부분은 후보의 정의와 함께 별도 읽어야 한다.

### S02 — local conservative implicit source는 확립된 구조

식(54),(55)는 endpoint four-force로 matter와 radiation의 conserved tensor row를 반대 부호로 갱신하고, 식(56)은 총합 보존으로 matter 변수를 소거한다. 각 반복에서 primitives를 복원한 뒤 rest-frame force를 lab으로 boost한다. 새 프로젝트 결과는 이 구조 자체가 아니다.

논문의 M1·grey Planck closure와 현재 H/He Case A closure는 구별한다. §3.3은 수치 해법의 실패와 근사 fallback을 인정하고 §3.5는 cold-flow 내부에너지의 수치 문제를 논한다. 이 원전을 전체 chemistry–radiation 단계의 전역 존재·유일성 또는 모든 반복의 positivity 증명으로 사용하지 않는다. \(T^t{}_t\)와 양의 lab energy의 부호도 맞추어야 한다.

### S03 — primitive 유일성의 정확한 전제

\(c=1\), \(1<\Gamma\le2\)의 gamma-law EOS에서 Lemma 2.1은
\[
 D_{\rm mass}>0,\qquad E>\sqrt{D_{\rm mass}^2+|\boldsymbol m|^2}
\]
와 \(\rho>0,p>0,|v|<1\)인 primitive 상태의 동치를 증명한다. proof는 제곱하지 않은 \(\Phi(p)\)가 \(p\ge0\)에서 엄격히 증가하며 유일한 양의 뿌리를 갖는다는 사실을 사용한다.

현재 \(D\)가 H nuclei number density이면 원문의 rest-mass density와 바로 동일시할 수 없다. **고정 조성·양의 \(r\)**에서 에너지 단위의 사상은 \(D_{\rm mass}\mapsto Dr\)이다. 조성 변화 후의 \(r\)를 사용할 전체 implicit stage가 허용 영역에 도달하는지까지 이 보조정리가 보장하지 않는다. \(p=0\) 경계 역시 위 strict theorem과 구별한다.

### S04 — 뿌리의 존재와 계산 알고리즘을 구별

식(2.3)의 physical pressure는 유일하지만, 이를 제곱한 식(2.7)의 quartic에는 두 양의 뿌리가 있을 수 있다. Theorem 2.2가 물리적 pressure로 식별하는 것은 작은 양의 뿌리다. 따라서 단순히 양의 quartic root를 찾았다는 사실은 primitive 복원의 충분한 근거가 아니다. 일반 Newton의 수렴도 해의 유일성에서 자동으로 따라오지 않는다.

SciSpace의 상위 세 항목은 같은 논문이다. 원문의 저자 이름은 **Chaoyi Cai**이며 일부 검색 metadata의 “Chao Cai”를 따르지 않았다. 저널 DOI는 검색 metadata로 확보했으나 publisher open이 실패했으므로 정리의 직접 근거는 위 arXiv 원문이다.

## 2. 보존한 THEORY04 근거

[Farris et al. (2008)](https://arxiv.org/pdf/0802.3210)의 pp.3–4 식(19),(20),(30)은 four-force와 물질/복사의 반대 divergence 부호에 대한 선행 근거다. grey LTE·Eddington 가정까지 도입하지 않는다.

[Rosdahl & Teyssier (2015)](https://arxiv.org/pdf/1411.6440v2)의 p.5 식(27),(28)은 전체 photon momentum의 흡수와 kinetic update를 제공하지만 Appendix A는 \(O(v/c)\) 근사다. 이전의 LIT-S01—mixed-frame 식(A7),(A8)의 부호 대응 제한—은 이번 조사에서 해소하지 않았으며 exact covariant 식의 근거로 재사용하지 않는다. 기존 조사 및 결정 파일의 실제 SHA256을 SOURCE_EVIDENCE.json에 묶었다.

## 3. frozen 후보의 독립 검토에서 확인할 경계

다음 항목은 원전의 적용 범위와 이미 전달받은 연구 방향의 정합성 문제다. 새 알고리즘이나 수용시험의 설계가 아니다.

- **event rate의 정규화:** \(R'\)가 proper volume·proper time당 사건률인지, H당 proper-time rate인지 구별해야 한다. four-volume당 scalar와 \(D\)를 쓰는 lab continuity 사이에는 시간 지연만 따로 한 번 더 적용하지 않는다. \(N'=\delta N_{\rm lab}\), rest energy \(E'=\delta E_{\rm lab}\), species 생성량의 동일 사건 정의를 함께 확인할 예정이다.
- **fixed volume의 의미:** lab의 고정 Eulerian 셀에서 \(D=\gamma n_H\)를 고정하는 source 단계는 \(n_H\)를 고정한 comoving parcel과 다르다. 유한 속도 변화에 따른 pressure work를 단순한 열·binding 차분으로 누락하면 안 된다. 부모가 제안한 유한 endpoint \(K\) 항은 위 문헌에 있는 정리가 아니므로 고정된 후보 proof에서 독립 검토한다.
- **정리의 양화:** 고정 조성의 primitive 단일값성과, photon·species·thermal·velocity가 함께 변하는 implicit stage의 해 존재·유일성은 다른 명제다. 후자는 전자를 인용하는 것으로 닫히지 않는다.
- **reference energy와 closure:** \(r=m_{\rm ref}c^2+\epsilon B\)의 원자 reference·binding convention을 유지해야 한다. bulk Lorentz 변환의 정확성이 retained warm atomic rates, recoil closure, 고온 EOS의 물리적 유효성까지 확장하지 않는다.
- **공변식과 유한 시간법:** 고정 Eulerian tetrad·동일 endpoint에서의 tensor 보존과, 다른 관측자가 다른 동시성 면에서 수행한 BE 단계의 결과가 동일하다는 주장을 구별한다. 이 조사는 curved-space transport 또는 Bianchi 전체 시간 진화를 검증하지 않는다.
- **escape:** rest-frame isotropic RR/DR luminosity의 lab momentum은 일반적으로 0이 아니다. 기존 scalar luminosity가 제공하는 moment closure 범위를 넘어서 방출 spectrum·photon number·모든 radiative channel을 추정하지 않는다.

## 4. 증거 상태

검색 query/result metadata는 SEARCH_EVIDENCE.json에, primary URL·실제 readscope·PDF page index·web reference와 실패한 open은 SOURCE_EVIDENCE.json 및 검색 기록에 보존했다. Wu–Tang PDF의 최초 direct open은 실패했지만 primary arXiv의 View PDF 링크를 통한 읽기는 성공했다. 이후 이를 실패 상태로 방치하거나 성공을 소급하여 기록하지 않았다. PDF 시각 screenshot 검토는 주장하지 않는다.

**상태:** 일차 문헌 검토 완료. 후보 proof·CLAIMS와 실제 Wolfram/xAct 증거가 고정되면 독립 R6 판정을 수행한다. 이 단계에서 새 과학 계산·native/ODE 실행 또는 후보 변경은 하지 않았다.

