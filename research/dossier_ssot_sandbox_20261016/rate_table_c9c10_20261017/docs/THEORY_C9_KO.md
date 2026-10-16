# C9 이론 유도: 계수 정확도와 Jacobian 정확도의 분리

원본 Grackle source `igm_rates.rs`와 `rate_table.rs`(Git blobs in `C9_RESULTS.json`)는 변경하지 않는다. `x=ln(T/K)`, smooth positive channel `g(x)=ln k(e^x)`를 정의하고, `[a,a+h]` 안에서 `|g''| ≤ M`라 가정한다. 두 끝값의 선형 보간 `L_hg`에 대한 정확한 오차 표현은

`g(x)-L_hg(x)=g''(ξ)(x-a)(x-a-h)/2`이며 따라서 `||g-L_hg||∞ ≤ M h²/8`이다. 양수 채널의 상대 값 오차는 `≤ exp(M h²/8)-1`이다.

반면 온도 미분에서 `(L_hg)'`은 `g'`의 셀 평균이다. 평균값과 임의 점의 차이를 적분해 `|g'(x)-(L_hg)'(x)| ≤ M h/2`를 얻는다. 즉 계수 오차는 `O(h²)`이나 log-temperature 미분 오차는 `O(h)`. knot에서 테이블의 미분은 좌우가 달라 일반적인 단일 Jacobian이 없을 수 있다. CI floor, CE exponential cap, 5500K branch, He DR 9284K switch, and structural zeros에서는 smooth positive 가정을 적용하지 않는다.

Wolfram 언어로 이차함수의 잔차를 대조했다: `g=a(x-h/2)^2+b x`의 선형보간 오차는 `a*x*(x-h)`이며 그 극대 절대값은 `|a|h²/4`, `M=2|a|`일 때 `Mh²/8`에 일치한다 (기존 실행의 independent symbolic check). 이 정리는 전체 15채널의 uniform M 값을 인증한 것이 아니다.

실제 source-identical Rust C9 검사에서 2048 log-temperature 위치의 29365 positive 채널 미분 비교를 수행했다. 최댓값 `|Δ ∂ln k/∂ln T|=6.5711347474461945e-3`, 최악은 `T≈1716.868K`, channel 7(CeHI); 동일 표본에서 계수 최대 상대오차는 `7.0022124879092406e-8`. Jacobian 실제 Newton 적용은 NOT_RUN/HOLD. 이 식을 근거로 Newton에 source-direct Jacobian과 table RHS를 혼합해도 안전하다고 주장해서는 안 된다.

실물 근거: Smith et al. (2017), DOI 10.1093/mnras/stw3291; Grackle 3.4.1 `https://grackle.readthedocs.io/en/grackle-3.4.1/RateFunctions.html`는 temperature CGS rate 함수와 Case A/B 선택의 구현 인터페이스를 서술한다. 본 프로젝트의 15-채널 최종 적용가능성은 frozen source/code validation이 권위이고 문헌 일반론과 혼동하지 않는다.
