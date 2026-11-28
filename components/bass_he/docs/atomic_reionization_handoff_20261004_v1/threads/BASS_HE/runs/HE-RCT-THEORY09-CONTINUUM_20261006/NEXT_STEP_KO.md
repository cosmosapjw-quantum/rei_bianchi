# THEORY09B_SAME_CHANNEL_DIPOLE_SOURCE

THEORY09A의 정규화와 Coulomb benchmark를 전달 때문에 반복하지 않는다. 전체 보고서 1-7절, SOURCE_INTAKE, RESULTS를 읽는다. 실제 2psigma/1ssigma electronic state와 E1 dipole를 같은 phase/threshold/mass/단위에 결속하고 q=d*u_i를 구성한다. C2d의 L 또는 n2 target은 대체물이 아니다.

필요한 source와 potential의 R support/tail/error를 확보한 뒤 이번 outgoing boundary/overlap 경로를 그대로 적용한다. 고정 i*delta만으로 threshold 상대정밀도를 인증하지 않는다. Positivity나 작은 동일코드잔차를 물리값의 오차막대로 쓰지 않는다.

재현: python -B -W error research/verify_continuum.py --suite algebra|radial|moments|threshold --output /absolute/new/path. 각 output은 새 경로여야 한다. Python/SymPy/mpmath만 필요하며 원자/native 실행은 없다. Full source는 archive 안에 있다.

실제 He 평균 null,baseline RCT OFF,physical HOLD와 F09차단은 유지한다. 기존 addon 채택에는 새 필수 선행조건을 추가하지 않는다.
