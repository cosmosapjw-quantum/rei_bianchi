# RCT03E1: 시간·분광·관측량 유한 refinement

PARTIAL_FINITE_REFINEMENT_TARGETS. 기존 coupled solver/원자식/source/mean35eV와 원 nonlinear/number/energy 기준은 바꾸지 않았다. 원 N24/48 자료를 재사용하고 N96/192 P512 Gauss4, N192 P128/256 Gauss4, N192 P512 Gauss2의 15개 새 이력2592step을 한 번 실행했다. 세 처방은 OFF/KF/GM이며 제조구간/IC는 RCT03D와 같다.

새 PLAN은 실행 전에 고정했다. 6개 primary field(x,y,z,w_eV/H,T,J)의 사전정의 시간+panel+order 최대 allowance ratio 합은 모두1미만이다. 최악은 OFF y의0.927046935254이다. 총18개 field에서는 escape만 OFF1.778600670329,KF1.776284826526,GM1.740157808420으로FAIL이다. 정확해오차 인증이 아니라 유한 refinement 차이에 대한 판정이다. 과거 root/장부 PASS를 소급취소하거나 escape 기준을 완화하지 않았다.

N192/P512/O4 최종 T는 OFF2273.681748926797,KF2273.713257259593,GM2274.217329837196K, RCT J는KF9.341987465884888e-7,GM1.587957847502693e-5events/H이다. GM의 N96->192 최대 T차6.34587740933e-6K,J차3.45567388283e-13events/H, 관측 p(T)=1.98816382104,p(y)=1.99505180242다. N48/96/192 공통49epoch에서만 차수를 계산했다. P256/512의 일부값 일치를 spectral error0으로 읽지 않는다.

escape의 최대 허용량 비는 끝점이 아니라 s-s0≈1.66666666668e-5에서 발생한다. 시간축 비가 OFF1.778595850736,KF1.776280012882,GM1.740153084244여서 사실상 시간차가 원인이다. 장부 항등식은 정확도 검사의 대체물이 아니다. 추가N384나 tolerance변경은 이번에 하지 않았다.

GM-OFF DeltaT=.5355809103989486K, Delta(ne/H)=4.5098481494210726e-8. 세 refinement차 합/최종신호는각각5.68217e-8,4.82548e-6이고 전자조합 condition≈1403.405다. 이는고정모형finite sensitivity이며 실제원자 uncertainty가아니다. fHe는선언YHe=.24에서exact3/38을 사용했다.

PR85 c690072756c23837598ac05efb3b4928a6104179의 HANDOFF/LOOP2_SPEC를읽고 같은N/U의inverse-cubic moment bound만 현재 saved spectrum moments에 적용했다. support[13.6,100]eV에서 bound upper/lower≈42.9이므로 N/U수렴만으로 rate관측량을승격하지않는다. 실제Verner Gamma는이번CSV에없고NOT_EVALUATED다. PR85는open/unmerged이며코드와전체시험은이식·재실행하지않았다.

새분석기9시험 RED/GREEN, 기호3식, inverse-cubic finite대입3개를확인했다. 원probe의추가panel argument 거절후새probe성공과OFF첫2step3행의byteparity를확인했다. 기존native전체suite/referenceODE는재실행0이다. 새probe만작성하고 working기존54파일/parent211payload는불변이다. 처음runtimeTooManyRequests와누락된원owner경로build실패를보존했고원bytes복사로해결했다.

원격receiver/root/adoption은변경하지않는다. baselineOFF,원자모멘트null,physicalHOLD,HE-F2/F09globalopen이다. 다음은escape시간예산의표적refinement와실제rateobservable 계약이다. 원 time_at는N192까지라N384범위는먼저명시해야한다. 전체source/실행15이력/실패로그/검산기는 DELIVERY_RECEIPT의ZIP에있으며Git에는projection만게시한다.
