# B3: 원자 반응률·사건 계수 공급의 의미와 불변량

## 근거와 범위

GM25 = García Muñoz et al., arXiv:2511.21966v1, Appendix B.3.
https://arxiv.org/html/2511.21966v1
저자들은 West1982의 단면적을 적분한 He²⁺+H charge-exchange rate를
200–10000 K에서 1.70×10^-13 cm³ s^-1의 상수로 잘 근사할 수 있다고 보고한다.
이것은 저자 재분석의 근사이고 이번 계산의 새로운 산란 결과가 아니다.
정량적인 fit 잔차 상한과 통계오차는 해당 문장에 주어지지 않는다.
동일 부분에서 KF96와 한 자릿수 이상 차이가 있음을 보고한다. 이번에는
KF96의 원 coefficient를 재확인하거나 차이의 원인을 해결하지 않았다.

West, Lane, Cohen, Phys.Rev.A26,3164(1982), DOI10.1103/PhysRevA.26.3164의
Eq2에 정의된 채널은 ⁴He²⁺+H(1s)→He⁺(1s)+H⁺+hν다.
이 원문은 optical loss로 총 전하교환 단면적을 계산하며 photon spectrum을
직접 계산하지 않는다고 3166쪽에 명시한다. 유일한 공명표는 σ(E) 표가 아니다.

이번 인터페이스는 위 source-specific rate를 선택적으로 공급한다.
국소 원자 충돌계의 비상대론적 두 성분, 공통 온도 Maxwell 분포, 상대 drift0,
H1s 및 W82의4He-H source ancestry, 자발 단광자 과정에 한정한다.
일반 비열적 분포, 다른 동위원소 또는 유한drift로 rate를 재사용하지 않는다.
Liu의 keV/u 축·질량 변환을 이 이미 적분된 coefficient에 적용하지 않는다.
Bianchi 기하·흐름·수송·밀도 evolution은 이 모듈의 입력도 출력도 아니다.

## 반응률과 단위

정의상 열적 rate coefficient는

k(T)=sqrt[8/(πμ)](k_B T)^(-3/2)∫₀∞ E σ(E) exp[-E/(k_B T)]dE

다. 식은 요구 분포 가정을 나타내며 원 σ와 그 적분을 이번에 재계산하지 않았다.
source의 상수 근사는 200≤T/K≤10000에서만 평가한다.
1cm³=10^-6m³이므로 k=1.70×10^-19m³s^-1다. 소수 token은 exact 단위 변환이며,
이 fact가 원 rate의 정확도를 뜻하지 않는다. 외삽하지 않는다.
dk/dT=0은 상수 근사식의 미분이다. 물리적 기울기 측정은 아니며 경계의 미분은
영역 내부에서 접근하는 쪽으로 표기한다.

## 원자 사건 계수

종 순서는 (HI,HII,HeI,HeII,HeIII,e)이며 ν=(-1,+1,0,+1,-1,0)다.
H핵수 h=(1,1,0,0,0,0), He핵수 h_He=(0,0,1,1,1,0),
전하 q=(0,1,0,1,2,-1)에 대해 h·ν=h_He·ν=q·ν=0이다.
밀도를 곱하지 않은 종별 계수 C_s=ν_s k, 단광자 수 계수 C_γ=k를 공급한다.
소비기가 사건율을 원하면 n_HI n_HeIII를 곱한다. 그 계산은 이번 exporter에 없다.
전자 순증분은0이지만 광자수는1이다. CX를 순수한 자유전자 이온화로 세지 않는다.

광자수 coefficient에는 m³s^-1가, 사건수율에는 m^-3s^-1가 붙는다.
서로 다른 두 입사종이므로 대칭쌍의1/2를 더하지 않는다.
단광자 counting이 알려졌다고 평균 photon energy나 heating이 알려진 것은 아니다.
예를 들어 동일한 총 event rate라도 방출 에너지 분포가 다르면 에너지 moment가 달라진다.
따라서 heat,photon-energy,spectrum,recoil,inverse-rate와 sourceUQ는 null로 유지한다.
West optical reference의 norm loss는 별도 선언 연산자의 출력이다. 물리V/Γ와
출사 귀속이 없는 결과를 이 thermal source로 등록하지 않는다.

## 공급과 검증의 의미

request는 sourceID,분포,온도목록,초기상태,동위원소scope,drift,방사모형,상충인지,
단위,quantity를 모두 요구한다. source 기본값과 자동선택은 없다.
같은 반응을 rate view와count view에서 두번 보내도 더할 수 없게 bundle 단계에서 거부한다.
동일 source의 두 공급기는 대안이지 서로 다른 reaction이 아니다.

validate_packet은 request로 지정된 source 평가를 재실행해 모든 필드를 비교한다.
이것은 선택된 구현·직렬화의 일관성 검사다. 악의적 공격에 대한 서명 검증이나
물리 정확도 증명 또는 독립 scientific review가 아니다. 코드 SHA 확인도 마찬가지다.
기존 source core와create-only writer의 bytes는 그대로이고 import 위치만 바뀌었다.
새로운 numerical model,source fit,cosmological parameter는 도입하지 않았다.

## 설치 구조

과거 두 배포물이 bass_he_rcx import경로를 공유했다. Python packaging에서는
배포명과 import명은 별개다. 배포명만 바꾸는 것으로 파일 충돌은 해소되지 않는다.
https://packaging.python.org/en/latest/discussions/distribution-package-vs-import-package/

새 공급기 bass-he-atomic-export0.1.0은 bass_he_atomic_export를 사용한다.
원 rate_core와writer는 그 안의 _rate/_io에 동일 bytes로 보관한다.
B2광학계산기 bass-he-west82-reference0.2.0은 bass_he_west82를 사용한다.
새 wheel들의 runtime경로 교집합과legacy import포함 여부를 검사하고,
같은 target에 둘다 설치한 뒤 각기 실제 계산·원자packet을 실행한다.
과거 충돌하는 두 wheel 자체를 수정하거나 동시에 설치한 것은 아니다.
