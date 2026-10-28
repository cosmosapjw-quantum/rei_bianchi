# C8 보완자료 게시·백업 복구

2026-10-28. 이번 사용자 재승인 아래 기존 285106-byte capsule을 그대로 Drive와 Dropbox에 업로드했고 양쪽 완료 ACK를 받았다. 정확한 ID·크기·SHA와 보존 범위는 DELIVERY_RECOVERED_20261028.json에 있다. 기존 capsule의 LOCAL 파일명과 delivery-pending 필드는 당시의 역사적 상태이며 이 후속 영수증이 전달 상태만 갱신한다. 원문 계산 결과나 과거 실패를 지우지 않았다.

Git에는 원래 C8_SUMMARY.json, code/c8_conditioning.py, evidence/PROCESS.json의 정확한 세 파일과 복구 metadata 두 파일을 게시한다. 20개 원문 전체, 상세 보고서, 정확한 수치 결과와 SVG는 양쪽의 원래 capsule 안에 있다. 따라서 준비된 20-path patch를 실제 적용했다고 주장하지 않는다. 이것은 보존 내용의 축소가 아니라 Git의 검토용 파일집합과 원문 백업 파일집합을 구별한 것이다. 상세 원자료는 capsule의 files[].content를 files[].path로 읽으면 된다. 옛116파일 source bundle이나 ZIP을 재생성하지 않았다.

이 보완자료의 기존 실행은 158/158 assertions, CPU0.059376s다. 다른 C8 경로의 81/81, CPU0.061126s와 별도이며 검사수를 합산하지 않는다. 단계는 양쪽 모두 C8 하나다. 이론5/10+코딩8/10=13/20, 작업33/88, 중앙마지막관측28/88, 증분0을 유지한다.

핵심 수학은 E=cv*Na*Ta+Q+W, D=Na+dN, T=E/(cv*D)의 양의 정의역과 저장 잔차를 보존한다. 상대 교란 a,b,g에는 T_new/T=(1+a)/((1+b)(1+g)), 고정cv에서는 정확한 나머지 b*(b-a)/(1+b)가 성립한다. Full box 경계와 실제 상관된 물리 입력의 범위는 다르다. 약10^-67K의 저장 잔차를 낮은 정밀도에서 두 끝점의 직접 뺄셈으로 얻을 수 없다는 관측은 물리 오차가 그만큼 작다는 뜻이 아니다.

이번 복구에는 새 과학 실행·기존 suite 반복·CAS·IVP·ZIP이 없다. 다음 과학 의무는 R5와 C5-C8의 범위를 합친 실제 비작성자 R6/C9 검토다. 같은 controller의 검토는 근거 정리에 사용하되 독립 수용이나 완료수 증가로 바꾸지 않는다. 실제 REI bath/temperature/native25와 physical radii는 null, L4false/globalnull로 남는다.
