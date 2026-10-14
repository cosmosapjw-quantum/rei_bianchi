# PHYS30 그림 — 프로파일에 따른 이차 문턱계수

`PHYS30_PROFILE_SECOND_ORDER.png`는 최초 성공 raw `contributions/numerics/PROFILE_SECOND_ORDER_FIRST.json`의 저장값만 표시한다. 입력은 231,082 B이며 SHA256은 `5184af6139423792abc0a95e53bd5ccabca459820761aa1a3f350bda4ac7082e`다.

두 panel은 상단 응답 문턱 W_star와 하단 응답 문턱 W_0를 나타낸다. 균일 프로파일의 mu2=1/3과 삼각 프로파일의 mu2=1/6을 파랑·주황 막대로 나란히 표시한다. 같은 x축 범위와 영점선을 사용하고, total 행에는 d 값을 직접 표기했다. 공통 일차계수 c는 각 panel의 부제에 표시한다.

표시한 여섯 범주는 다음과 같다.

| 범주 | 최초 raw에서 직접 읽는 affine 필드 |
|---|---|
| Geometry (7 terms) | d_profile_independent_geometry_sum |
| Band averaging | d_decomposition_dimensionless.profile_band_averaging |
| Variance correction | d_decomposition_dimensionless.center_variance_V_second |
| Implicit mixed term | d_decomposition_dimensionless.implicit_root_delta_W_cross |
| Implicit curvature | d_decomposition_dimensionless.implicit_root_W_curvature |
| Total d | d_dimensionless |

기하 항의 합과 total d도 기존 raw 필드에서 그대로 읽는다. 그림 코드에서 이 값을 재합산하거나 새 계수 공식을 평가하지 않았다. 부동소수점 변환과 자리수 반올림은 막대의 위치와 텍스트를 표시하는 용도로만 사용했다. 전체 원 직렬화 값과 source pointer는 `FIGURE_PROVENANCE.json`에 보존했다.

그림은 2400×1344 px, 흰색 배경의 PNG다. 대상은 영폭의 한쪽 국소 전개에서 d=W_second(0+)/2인 무차원 계수이며, 저장 수치점의 비영 A-level 해석을 유지한다. 그림 하단에 고정 실제 분산과 동일 중심 허용구간, 유한폭 영점 정확도를 평가하지 않았다는 범위를 표시했다.

실제 `view_image`로 두 layout을 확인했다. 첫 layout에는 범례와 panel 제목이 겹치는 문제가 있어 PNG·소스·provenance와 관측을 `versions/first_layout/`에 보존했다. 두 번째 layout은 세 개의 세로 위치만 조정했고, 실제 이미지에서 제목·범례·공통 c·막대·total 값·축·하단 주석의 가독성을 확인했다.

두 번째 표시 명령은 PNG를 생성한 뒤 provenance의 exclusive 생성에서 FileExistsError로 exit 1을 반환했다. 관측 시 기존 provenance는 첫 버전과 동일한 bytes·SHA·mtime로 남아 있었다. 원인은 확정하지 않았으며 `DISPLAY_METADATA_FAILURE.json`에 실제 실패를 보존했다. 이미 생성된 두 번째 PNG를 사용하고 metadata만 현재 source/output identity와 정합화했다. 세 번째 렌더는 수행하지 않았다. 최종 관측은 `FIGURE_VISUAL_REVIEW.json`에 있다.

이 표시 작업의 render 명령은 총 2회다. scientific main, candidate import, 물리 kernel·도함수·root, profile 모멘트 또는 toy 평가, 새 계수 공식·합산은 모두 0회다. 후보 코드·protocol·freeze·과학 실행 raw는 변경하지 않았다.
