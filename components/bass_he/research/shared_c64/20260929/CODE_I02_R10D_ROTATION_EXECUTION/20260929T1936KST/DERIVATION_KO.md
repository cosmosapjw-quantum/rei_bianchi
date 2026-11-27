# CPC Eq.(47)와 해석적 반발 Coulomb 궤적의 독립 회전 유도

## Source 진술

CPC Eq.(47)는 `i dA/dt=[epsilon R(t)^2 Lx^2 + omega(t)Lz]A`이다. CPC 본문의 전역 핵 궤적은 straight line이고 기존 clean-room `src/bass_he/rotation.py`가 이를 구현한다. R9/R10D static source audit는 분산 저자 WRN의 Coulomb trajectory와 더 큰 cutoff를 기록한다. 이 연구 구현에는 저자 FORTRAN 문장을 복사하지 않았다. 저자 source DOI는 `10.17632/n43srxwdnm.1`, `arseny.f` SHA256은 `96827045654428cff9a32930415a9f6c39615b0b41677d00d377edf7c37d6f78`이다.

## 유도

충돌면 극각을 `phi`로 두고 접근에서 음수, 이탈에서 양수로 증가시킨다. 축 각도는 기존 clean-room 부호 규약에서 `theta=pi/2-phi`다. 고전 각운동량 보존에 따라 `dt/dphi=R^2/(rho v)`이며,

`R(phi)=rho^2/[-a+sqrt(a^2+rho^2) cos(phi)]`, `a=Z1 Z2/(mu v^2)`.

여기서 `mu=DMP*1836.153` 전자질량 단위이고 DMP=0.8 amu다. 이 단위 변환은 0.5/5 keV/u에서 각각 `a=0.067675/0.0067675 a0`를 준다. `Rmin=a+sqrt(a^2+rho^2)`가 `Rcut` 이상이면 회전 구간이 없다.

`A=exp(-i theta Lz)B`로 정확히 gauge 변환하면

`i dB/dphi = epsilon R(phi)^4/(rho v) [sin(phi)Lx-cos(phi)Ly]^2 B`.

수치적 직선 극한을 쉽게 확인하기 위해 `x=rho tan(phi)`를 쓴다. 그러면

`i dB/dx = (epsilon/v) [R(phi)^2/(rho^2+x^2)]^2 (xLx-rho Ly)^2 B`.

`a=0`이면 `R^2=rho^2+x^2`이므로 대괄호가 정확히 1이 되어 기존 straight-line gauge Magnus generator와 일치한다. `xmax=rho tan[acos((a+rho^2/Rcut)/sqrt(a^2+rho^2))]`를 정규화해 기존 4차 Magnus의 Hermitian step 공식을 적용했다. 끝점 gauge 위상, signed `m_x` basis 및 `|m_x|` 확률 collapse는 기존 clean-room 규약과 동일하다. `rho=0`은 별도 극한 유도 없이 지원하지 않는다.

## 수치 판정 경계

이 유도는 source statement와 분리된 연구 수학이다. Unit tests 8개는 통과했지만 고정 105-node grid의 사전 수렴 gate가 실패했다. 따라서 이 adapter로 five-lane 결과를 계산하지 않았고 trajectory/cutoff의 정량 효과를 주장하지 않는다.
