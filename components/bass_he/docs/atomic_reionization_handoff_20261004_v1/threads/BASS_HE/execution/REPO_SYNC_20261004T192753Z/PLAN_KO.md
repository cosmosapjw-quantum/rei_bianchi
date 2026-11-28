# 변경 전달물 동기화

목표는 새 supplier reference/domain gate와 consumer F04/F06/F07 결과를 정확한
commit/content identity로 수신하는 것이다. 새로운 RCT 수치 구현은 작성하지 않는다.

1. be81c95를 fast-forward하고 b553698의 변경 경로·제한을 읽는다.
2. 새 HE-F3 domain gate에 잘못된 교집합/범위 변경/완료 승격을 거절하는 경계 테스트를 추가한다.
3. 내려받은 바이트와 영수증의 artifact hashes, static certificate parent binding을 대조한다.
4. native/RCT/source 증거의 범위를 분리하고 상태/스레드 전달 기록을 갱신한다.
5. 게시 전후 양 HEAD를 확인하고 additive 게시 및 tree 검증을 한다.

HE-F2C 기준해 9개와 native/MPFI suite는 이미 실행된 전달 증거다. 이번에 재실행하지 않는다.
ZIP은 코드/로그의 별도 배포이며 Git projection이나 cloud size ACK를 ZIP restore 검증으로 승격하지 않는다.
새 F04 static certificate 수신은 RCT stepper, expanding S0, F09, physical admission을 닫지 않는다.
