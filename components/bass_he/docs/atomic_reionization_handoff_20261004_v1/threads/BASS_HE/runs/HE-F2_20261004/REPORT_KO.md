# HE-F2 재개 결과: 실제 소비기와의 결속 범위 판정

판정: 원자 측 candidate/반응 장부 전달물은 완성. 전체 HE-F2는
BLOCKED_CONSUMER_CONTRACT. 원자 데이터 오류나 NCP 자원 부족 때문에 멈춘 것이 아니다.

## 복구

이번 환경에서 이전 HE-F2 작업파일·worker는 발견되지 않았다. 마지막 전달 HE-F1 ZIP124817bytes,
SHA256 16c6f90a23acbdd6b0b101086ab3eb3732fbb799f67f55396c9b255e5ba4247e와62개 payload를 확인했다.
Git의 기존 branch HEAD도 cbc654cf6037a4a0dad2f60fb138964cfff62ada였다. HE-F1의57개나
legacy scientific suite는 복구를 이유로 재실행하지 않았다. 이번에 새로 읽은 실제 소비기 HEAD는
64bc3aa0871bb324817afd3d36db018dd34181cf이고, 최신 FT03의 원 archive를 Drive에서 회수했다.
FT03 ZIP78707bytes와공개된SHA256 0d8d28b5e4d63a9013b5c57f785680d2f3344b94127f2510b4037417356f5480이 일치했다.
원 manifest46개 파일도 일치한다. 원 FT03 scientific 프로그램은 실행하지 않았다.

## 실제 소비기에서 확인한 세 불일치

1. REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1은 charge_exchange를 명시적으로 제외한다.
   원 문서의 exact zero는 controlled model 선택이지 참 원자계수=0이나 누락자료=0이라는 뜻이 아니다.
2. FT03 guard30000..110000K, 초기50000K는 GM25200..10000K 밖이다. KF96 범위는 덮지만 두
   공급자 공통1000..10000K와 현재 소비기 guard는 겹치지 않는다. source fallback/clamp는 하지 않았다.
3. FT03의 RR/DR escape closure를 RCT에도 적용한다는 선택은 없다. scalar RCT rate의 photonenergy,
   heat,recoil null을0 또는Q로 바꾸지 않았다. canonical F00 runtime_inputs 디렉터리와 F01의
   atomic_provider.rs도 위 고정commit에서404였다. FT03는 canonical F00-F09를 변경하지 않았다고
   자체 반환에 명시한다. 연구 schema의 존재와 실제 소비기 provider instance/승인은 구분한다.

이는 지정 branch/pin/경로에서 확인한 상태다. 모든 private/외부 실행환경을 전수검색하여 자료가
어디에도 없다고 단정한 것은 아니다. 현재 발견한 actual scope로 충분한 차단 이유가 있으므로
추측으로 closure를 만들거나 무관한 archive 검색·legacy 연구를 재개하지 않는다.

## 새 구현

he_f2_binding.py는 새로운 rate API가 아니라 기존0.1.1 공급기의 thermal-rate view를 회수한
AtomicProviderRecordV1 연구 schema로 표현하는 offline 전달물 compiler다. 둘을 별도 candidate로
기록하고 전체 원 B3 packet과 canonical hash를 보존한다. 해당schema의 observable_kind에는
count가 없으므로 count packet을 rate로 바꾸지 않고 반응 장부를 별도 출력한다.

4개 생성물: PROVIDER_CANDIDATES.json, REACTION_BINDING.json,
SOURCE_DOMAIN_ASSESSMENT.json, CONSUMER_LEDGER_ACCEPTANCE.json.
마지막 파일은 소비기의 서명/수락 증명서가 아니라 실제 거부 이유를 담은 명시적 미수락 기록이다.
모든 candidate consumer_admission=false, closure_id=UNRESOLVED_RCT_CLOSURE_NOT_SELECTED.
compiler의 exit0은 보고서 생성 성공이며 HE-F2 accepted의 뜻이 아니다.

FT03의 실제 분율정의에 맞는 r_H=k*nH*Y*(1-xHII)*xHeIII와
(dxHII,dxHeII,dxHeIII)/r_H=(1,1/Y,-1/Y)를 정확 유리수로 검산했다.
직접 electron변화는0, photon birth는1이며 primaryabsorption은별도다.
FT03의 chi와 코드literal을 연결해 Q=40.819325400298eV를 계산했지만 이는 binding defect이고
광자에너지나heat로승격하지 않았다. 밀도·시간·geometry·opacity와RHS실행은소비기소유다.

## 검증

새27개 시험은 최초 구현부재로 모두 실패했고 구현 후27개 통과했다. 두 source의 실제 연구schema
검사, B3 replay, 원숫자/단위보존, null조작거부, 온도교집합, 제외상태보존, 분율/전하/핵수,
잘못된입력·변경된원자료거부, create-only출력·CLI상태를검사했다.
부모코드8개는bytes그대로다. 새패키지/wheel을별도로만들지않았고 기존runtime을vendor로고정했다.
검증환경은pytest9.0.2,jsonschema4.26.0; compiler runtime은Python표준라이브러리다.
별도연구자의scientificreview,Fortran/OpenMPI,Rustbuild,전자/산란/우주론campaign은0이다.
정확유리수/Decimal과기존binary64 view 구분,no-fast-math/no-reassociation정책을유지한다.
추가 identity reader가 F1 archive의 baseline/package 두 경로를 구분하지 못해 한 번 실패했다.
실제 배포물인 package/ 경로로 reader만 수정한 뒤 8개 모듈의 byte 동일성을 확인했다.
제품 코드·원자료·허용오차는 변경하지 않았고 실패 기록을 보존했다.
봉인복원·최종재현은외부ARCHIVE_VALIDATION.json이기록한다. 구현통과를물리정확도로올리지않는다.

## 다음 최소 조치

rei_bianchi에서 RCT를 현재모형에서계속제외할지, 별도온도범위/closure의감도모형에서포함할지
명시적으로결정해야한다. 현재FT03를조용히바꾸지않고별도모형ID/범위/energyownership을기록한다.
REI_SCOPE_LOCK/F00와REI_PROVIDER_CONTRACT/F01에 대응하는 실제 인스턴스를 공급하면 그 변경만
읽고HE-F2의수락검사를마무리한다. 포함을원하지않으면optionalREI-F09를명시적으로보류할수있다.
REI-F08 baseline와FT05의독립진행을막지않는다. HE-F3 paired campaign은rei가실행한것을한번
받아검토할뿐HE에서중복실행하지않는다. NCP64연산도현재필요없다.

HE-L1/L2/L3는PARKED_OPEN. scientific_PROMOTE=HOLD,EOR_THEORY_GATE=NOT_SATISFIED,
Eq55=NOT_RUN,consumer_acceptance=false,physical_source_admission=false.

## 게시·백업

새결과의실제Git commit/tree와Drive/Dropbox/Library전송결과는별도DELIVERY_RECEIPT.json이소유한다.
이문서의존재만으로게시·업로드·복원을주장하지않는다. REI 저장소와모형은변경하지않았다.
