# ANGULAR06 저장자료 그림 판독

## 판독 대상과 실제 실행

`plot/ANGULAR06_TRANSPORT.png`와 같은 자료로 만든 SVG를 대상으로 한다. 주 작업자와 독립 결과 검토자는 실제 PNG를 직접 읽었다. 주 작업자는 그림을 다시 생성하지 않았다. Plot은 `validation/SAVED_PLOT_DATA.json`의 복사본만 읽었고 과학 함수 호출은 0회였다. 두 JSON의 SHA256은 `71812d18e39080ace31cfb0d0a5b418ea0dc291210b6d34c8b79c992d6376ff6`으로 같다. PNG의 SHA256은 `e6a8598c0b2efd87be65791b0d7031de847d512228475617050973c4828c8796`이다.

실제 1회 실행의 CPU는 5.791514952999999 s / 신규 6 s, wall은 5.852712829997472 s / 15 s, exit code는 0이며 stderr는 비어 있다. 판정은 PASS다. 측정 범위는 새 그림 프로세스와 기록된 runner 오버헤드다. 준비·모델·네트워크 비용의 전체 상한을 뜻하지 않는다. 이 배정은 새 각도 사상 그림의 사전 계약이며 PHOTON05의 4 s 상한을 변경하지 않는다.

## 세 패널의 의미

1. **A: 합성 각도 사상.** gamma=1.25에서 a=0.3의 한 분기, a=1의 stopped boundary, a=2의 fold를 구별한다. a=2의 최솟값 양쪽에 서로 다른 CM 역상이 존재하는 모양이 유도와 일치한다. a=1의 mu=-1은 저장자료에서 STOPPED, nu=null이므로 그 점은 그림에서 제외된다. 보이는 곡선의 첫 점은 유한한 첫 격자점이며 정지 입자의 방향을 부여한 것이 아니다.
2. **B: native 12개 좌표의 Jacobian.** 세 입사 에너지와 각 daughter의 plus/minus를 구분한다. 점을 잇는 선은 좌표 변환의 안내선이다. 원 실험 DCS를 보간하거나 재정규화한 전각 분포가 아니다.
3. **C: 합성 fold 밀도.** 명시한 f=1/2에서 lab fold에 접근할수록 역제곱근 형태로 밀도가 커진다. 로그축에서 보이는 추세는 국소 점근식과 일치한다. 유한 bin 질량과 점근 조건의 실제 판정은 26개 검증 중 해당 테스트의 결과에 근거한다. 그림만으로 새 수치 인증을 부여하지 않는다.

제목의 conditional transport와 experimental normalization open 표기, 축·범례·분기 표식을 읽을 수 있다. 보이는 clipping이나 부호 모순은 발견하지 않았다. 필요한 정보가 표현되어 추가 렌더는 수행하지 않는다.

## 보존된 과거 결과

PHOTON05 plot의 CPU **4.40726504 > 4 s FAIL**과 workflow **PARTIAL**은 그대로다. PHOTON05의 그림·24/24 검증·백업을 재실행하지 않았다. 신규 그림 PASS와 과거 FAIL은 서로 다른 산출물의 결과다.

독립 판독과 실제 파일 identity는 `../review/RESULT_REVIEW.json`에 있다.
