# Table IV 원전 전사와 convention 독립 확인

기준: Childers et al., PRA 69, 022709 (2004), DOI https://doi.org/10.1103/PhysRevA.69.022709 . 2026-10-24 UTC 확인.

## 숫자 전사

`Childers2004_TableIV_source_transcript.csv`와 같은 이름의 `.json`에 E0=20 eV Table IV 전체 40개 DDCS 값과 각도별 8개 uncertainty %를 보존했다. PDF page 5의 `childers_table_page.png`에서 모든 숫자를 읽고 `pdftotext -layout` 결과와 대조했다. 이 작업은 원전 입력 전사이며 모멘트 계산 또는 실험 모델 재해석을 수행하지 않았다.

각도는 15°,20°,25°,30°,40°,60°,90°,120°이고 E1 열은 2,3,4,5,6 eV다. Table IV에 별표 중복 관측은 없다. E1=2 eV에는 원전의 추가 오차 footnote가 있으며 해석을 결정하지 않았다. Root가 주 분석에서 고른 E1=3–6 eV의 32개 값과 E1=2 eV의 보존용 8개 값이 구분된다.

## E1의 의미

실험 설명의 인쇄 p.022709-1에서는 analyzer가 산란 전자를 energy loss 및 산란각에 따라 검출한다고 설명한다. p.022709-2에서는 잔여 운동에너지를 **E1=E0−EL**로 정의한다. 따라서 E1은 검출된 outgoing/scattered electron의 운동에너지이며 에너지 손실이나 두 전자의 energy-sharing fraction이 아니다. 이 논문의 “scattered” 표현만으로 식별 불가능한 두 전자의 입자 label을 관측했다고 해석해서는 안 된다.

## electron count와 전체 사건 정규화

Eq.(1) 및 주변 설명(p.022709-4)은 연속체의 검출 count를 H(n=2) excitation count 및 CCC reference DCS로 정규화한다. **이 논문에는 DDCS를 전 에너지·입체각에 적분하면 2σ_ion이 된다는 식이나 그러한 full-domain convention의 명시적 선언이 없다.** 본문 전체 추출을 읽고 integrate/integral/total/singly/factor/symmetry 관련 용어도 확인했다. 초반 factor-of-two 언급은 과거 TDCS 측정의 정규화 논쟁이며 이 Table IV의 full-domain 2σ 항등식 근거로 사용할 수 없다.

두 전자가 있는 하나의 사건을 원소로 하는 측도에서 각 사건의 두 검출 가능한 전자를 모두 합하는 inclusive counting measure를 **추가 정의**한다면 전 영역의 integral=2σ는 수학적으로 유도할 수 있다. 그러나 그것은 이 논문이 제공한 full-domain identity가 아니며, 본 Table IV에 새로운 factor 2를 적용할 근거도 아니다. 이번 partial-window 연산자는 원전 DDCS 단위와 수치 그대로 정의하면 이 unresolved convention을 강제할 필요가 없다. Event rate, total cross section, 두 전자의 공동 law로 전환하는 gate는 보류한다.

## 불확실도와 frame의 남은 의무

각 행의 uncertainty %는 1σ이고 covariance는 제공되지 않았다. 연속체는 energy loss의 4차 이하 polynomial fitting에서 얻었으며 common normalization과 transmission 보정을 공유한다. 따라서 셀/행 독립 Gaussian 전파가 정당화되지 않는다. CCC reference DCS 자체의 오차는 논문의 error bars에서 제외됐다. 이 기준 DCS는 각도에 의존하므로 단일 공통 scale cancellation도 선언하지 않는다.

표는 물리적인 H 실험이다. 입사/검출의 laboratory convention은 유지하되 fixed nucleus 또는 finite mass 이론 provider라고 부르지 않는다. Spin-resolved 표와 상대 전자 각도, recoil 사건은 제공되지 않는다.

외부 논문 PDF·전체 원문 추출·원문 이미지는 읽기 전용 내부 증거로 유지하고 공개 Git에 넣지 않는다. 전사한 수치 사실과 독자적인 유도는 출처·해시와 함께 별도 보존할 수 있다.
