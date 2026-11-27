# HE32 원자 photo/RR provider 독립 검토

판정: **PASS_SCOPED_PHOTO_RR_PROVIDER**. 대상은 physics agent의 `atomic_photo_rr.py`(SHA-256 `f423083bfaeabbe6373367bddf24774e6ffe3e3d8accb26f22a7544171869067`)와 6-channel 데이터 JSON(`b75601081cc55dc63592f8d17ee765976ade29148cab62f29700ca930eff1d90`)이다. 원자 분율 IVP, 성능 benchmark 또는 parameter sweep을 실행한 검토는 아니다.

## 원표와 구현의 대응

H I, He I, He II, Li I, Li II, Li III의 6개 channel에 대해 다음을 독립적으로 확인했다.

- 원 `photo.dat`의 Z, bound-electron count, threshold, 최대 에너지 및 7개 fit 계수가 JSON과 전부 일치한다. 같은 계수는 원 `phfit2.f`의 PH2 블록과도 일치한다.
- 원 RR `table1.dat`에서 명시적 ion label로 선택한 a,b,T0,T1의 4개 계수와 Z,N이 전부 일치한다. RR ion label은 재결합 뒤의 상태이며, 예를 들어 LiI 행은 Li+→Li0에 대응한다.
- 원표 2개 파일의 SHA-256이 JSON이 선언한 값과 일치한다.
- 원 PR151 `li_thermal_rates.py`의 sigma 함수와 threshold 이상인 18개 source-domain 점을 비교하여 상대 차이 0을 얻었다. 여기에는 선택 UV support 바깥이지만 원 photo-fit 안인 점도 있다.
- PR151의 50자리 Decimal RR 식과 T=20,000 K에서 6개 값을 비교하여 최대 상대 차이 3.3306690738754696e-16을 얻었다. 이것은 수식 구현 일치이며 원자 물리 fit 자체의 불확도를 뜻하지 않는다.
- 6개 threshold 바로 아래의 단면적은 정확히 0이다.

원래 자료의 공식 공개 경로는 [photo 자료 페이지](https://www.pa.uky.edu/~verner/photo.html), [RR 자료 페이지](https://www.pa.uky.edu/~verner/rec.html), [photo 원표 설명](https://www.pa.uky.edu/~verner/dima/photo/photo.txt), [RR 원표 설명](https://www.pa.uky.edu/~verner/dima/rec/table.txt)이며 이번 검토에서 직접 열어 확인했다. 공개 자료의 수치 계수와 문헌 식을 출처와 함께 재구현한 provider이다. 이 페이지들을 근거로 Fortran 전체가 특정 permissive software license를 가진다고 주장하지 않는다.

## 단위와 정의

원표 단위는 photo energy=eV, cross-section=Mb, RR coefficient=cm³/s, T0/T1=K이다. Provider의 1 Mb→1e-18 cm² 변환이 맞고, electron density에 proper cm^-3를 넣으면 RR destruction frequency는 s^-1가 된다. 전자 수밀도에 comoving cm^-3를 바로 넣어서는 안 된다.

선택 photon number spectrum을 F_E=C E^-2.5라고 정의하면 Γi=C∫σi(E)E^-2.5 dE이다. Provider는 ΓHI로 C를 정규화하므로 `uv_amplitude`가 s^-1이다. 등방성 radiation에서 F_E=c n_E에 해당하는 정의를 사용하면 에너지 밀도는 u=(C/c)∫E^-1.5 dE이며, eV/cm³→J/m³ 변환까지 구현과 일치한다. 재결합은 total radiative recombination(case A)이므로 excited-state contribution을 포함한 RR이다. 선택 광이온화 단면적과 밀른 관계만으로 계산한 ground-state recombination과 같다고 주장하지 않는다.

ΓHI=1e-12 s^-1일 때 선택 UV의 계산된 u는 1.0822180234202198e-16 J/m³이다. 이 값은 prescribed UV의 진단량이며 본 검토에서 geometry의 radiation energy에 자동 결합했거나 conservation equation을 풀었다는 의미는 없다.

## 유효범위와 실제 점유될 수 있는 상태

UV support는 [5.392,60] eV이다. 이는 Li I의 낮은 fit 최대 에너지 64.39 eV 안이며 다른 5개 fit의 최대 에너지 안이다. RR 공통 범위 3..1e9 K는 공개 RR 페이지가 명시한 범위와 일치한다. He I은 broad-range b 행을 사용한다. 원표 설명은 b fit에 3<T<1e10 K와 RMS 4.7%를 명시하므로, 수치 oracle의 약 1e-16 상대 일치와 물리 fit 불확도를 구분해야 한다.

| channel | Γi/ΓHI | 이번 closure의 결과 |
|---|---:|---|
| H I | 1 | photoionization 활성 |
| He I | 0.597858946081651 | photoionization 활성 |
| He II | 0.01063343052799649 | support 상단의 photon으로 활성 |
| Li I | 2.215704764089562 | photoionization 활성 |
| Li II | 0 | threshold 75.64 eV가 support 위 |
| Li III | 0 | threshold 122.5 eV가 support 위 |

따라서 모든 charge state를 자료 구조에 포함하더라도, Li를 중성에서 시작하고 collisional ionization을 제외하면 Li2+/Li3+는 이 closure에서 생성되지 않는다. 이미 점유한 Li2+/Li3+의 RR 소멸은 구현되어 있다. Isotope별 electronic coefficient 동일성은 명시적 근사이며 isotope shift의 검증 결과가 아니다. CI, DR, negative ion, molecule, nuclear reaction은 이 provider에 포함되지 않는다. 이를 full atomic/nuclear network라고 부르면 안 된다.

## 실행과 근거

`INDEPENDENT_ATOMIC_REVIEW.py`를 한 번 실행했으며 원표 행, reference 함수, scalar RR 비교를 수행했다. 실제 IVP 0회, benchmark 0회이다. 결과와 각 입력 파일의 bytes/SHA-256은 `INDEPENDENT_ATOMIC_REVIEW.json`에 있다. 본 검토에서 provider와 source table을 수정하지 않았다.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 \
  investigation/he32/upstream/INDEPENDENT_ATOMIC_REVIEW.py
```

이 명령은 이미 실행되었으며 기존 결과 파일 덮어쓰기를 거부한다. 추가 반복 실행은 필요하지 않다.
