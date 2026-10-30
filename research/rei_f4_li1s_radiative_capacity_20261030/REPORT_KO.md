# REI/BASS F4 | 측정된 Li II 복사수명과 BASS193 실사건 광자 용량

**2026-10-30 | Scoped physical-data node 1/1 | F4 PARTIAL | production HOLD.**

## 과학 성과

기존 PR279의 Li6I/Li7I 1s 8,492개 광이온화 사건 행에 새로운 외부 물리 원자료 두 가지를 연결했다. 첫째, NIST Li II `1s2s ^3S1`(59.0207236732 eV)/`^1S0`(60.9225594476 eV) 준위를 고정했다. 둘째, 원전에서 실측된 진공 붕괴 수명인 triplet `52.2±5.0 s` (Saghiri et al. 1999, DOI 10.1103/PhysRevA.60.R3350)와 singlet `503±26 μs` (Prior & Shugart 1971, DOI 10.1103/PhysRevLett.27.902)를 사용했다. Singlet은 2E1, triplet은 M1. 1980년 Knight & Prior의 triplet `58.6±12.9 s`(95% CI)는 별도 실험 교차증거다. 어떤 붕괴 수명도 BASS의 Li 이온화 반응계수를 재정의하지 않는다.

세 개의 NIST 임계값 H I `13.598434599702 eV`, He I `24.587389011 eV`, He II `54.417765486 eV`에 대해 각 광자쌍 에너지의 합만으로 **허용 가능한 임계값 초과 광자 수의 sharp bounds**를 유도하고, 이를 193개 실제 보존된 BASS clock 샘플에 적용했다. 이는 이전 Li1s primary/source 에너지 장부의 재출력이 아니라 **복사광자의 수와 이온화 임계값별 수송 입력의 새 후보 장부**다.

| 적분량 | 최소 | 최대 | 단위 |
|---|---:|---:|---|
| 조건부 진공 복사붕괴 광자 | `3.442655615303716e-11` | `6.457763175958553e-11` | photon/baryon |
| H I 임계값 초과 광자 가능 수 | `3.442655615303716e-11` | `6.457763175958553e-11` | photon/baryon |
| He I 임계값 초과 광자 가능 수 | `3.442655615303716e-11` | `6.457763175958553e-11` | photon/baryon |
| He II 임계값 초과 광자 가능 수 | `4.27548054648883e-12` | `3.442655615303716e-11` | photon/baryon |
| 조건부 복사 에너지 | `2.031880257726855e-9` | `2.089222651951853e-9` | eV/baryon |

각 경계는 이온화 가능한 **복사 광자의 생성 가능 개수**이지 원자의 실제 광자 흡수, 생성된 H/He 이온 수, 온도 변화가 아니다. 특히 He II에서 triplet-forced bin이 공급하는 M1 하한은 진공 복사붕괴 조건에서만 양수이다. Collisional quenching가 있으면 unconditional emitted photon lower bound는 0까지 내려간다. Unknown p(3S|E), two-photon spectral shape g(y), competing collision/opacity를 임의로 0/1로 고정하지 않았다.

중요한 원자 물리 포인트는 Li II singlet 2E1의 총 60.922559 eV는 He II 임계값보다 크지만 `2χ_HeII=108.83553 eV`보다는 작다는 점이다. 즉 He II를 이온화할 수 있는 2E1 광자가 생긴다면 짝광자는 **6.50479396155 eV보다 낮아야** 한다. 실제 그 tail 확률은 아직 얻지 않았다. Triplet M1 59.020724 eV는 H I/He I/He II 모두의 임계값보다 높다. 삼중항과 단일항 중 알려진 최저 활성 bin은 triplet만 가능하다.

## 과학적·수치 검증

- Immutable PR279 full ZIP SHA256 `6e50586131ab6f8f76b72ee8c7125dfd3225211d528609c862e01a305a0ab6d3`, nested PR277 original source exact SHA, BASS source commit `cc602e209e7deeb511ab2a1f3b2268d55206c43c`.
- Saved 193 epochs, 22 active bins per Li isotope, 8,492 source event rows, 25,476 threshold capacity cells; no new source history generated.
- Python scoped 28/28 tests PASS and independent clean-extract rerun target; Wolfram exact arithmetic verified M1/2E1 energy residual `0,0`, atomic threshold inequalities `True`. Distinct-author R6/C9 **NOT_RUN**.
- All epoch-wise native source rates and absorption energy reconstruct PR279 saved originals. Both extremal partitions return original absorbed energy `2.95642365279964e-9 eV/baryon` including `5.391714996 eV` valence binding and conditional prompt electron kinetic energy.
- Archived BASS `H(z)` gives maximal `Hτ_triplet=6.177923233737762e-15`, `Hτ_singlet=5.953056296111291e-20`. This does **not** prove collisionless decay or instantaneous plasma thermalization.

## DAG 및 범위

| Item | Actual |
|---|---|
| Original working DAG | **33/88**, no increment |
| Central canonical DAG | **28/88**, no increment |
| F4 physical fast DAG | **4/7**, no increment |
| New auxiliary radiative-capacity unit | **1/1_SCOPED** (outside canonical) |
| R1–R10/C1–C10 | **18/20_SCOPED**; different-author R6/C9 not run |
| Full F4, L4 and production | `PARTIAL`, `false`, `HOLD` |
| New IVP, actual REI photo heat, observational tau/CMB | **0, UNBOUND, NOT_RUN** |

The BASS21 optically thin UV photon source with original Li1s event rates is not a source-owner-complete REI17 thermal/radiative forward model. REI Rust `IgmPhotoInput::heat_erg_per_absorber_s` remains `UNBOUND`. Full REI17/BASS21 isotope, nuclear/CR/injection, clock, electron and thermal compatibility remains an independent obligation. REI PR278 self-consistent frozen equilibrium is a sibling calculation, not part of the same source-equivalent evolved trajectory. No other repo, PR, main branch, or source artifact was modified.

## Sources

1. NIST Li II levels: https://physics.nist.gov/PhysRefData/Handbook/Tables/lithiumtable6_a.htm
2. NIST ASD ionization: https://physics.nist.gov/cgi-bin/ASD/ie.pl
3. Prior & Shugart (1971) Li II 2¹S₀ singlet 503±26 μs: https://doi.org/10.1103/PhysRevLett.27.902
4. Saghiri et al. (1999) Li II 2³S₁ triplet 52.2±5.0 s: https://doi.org/10.1103/PhysRevA.60.R3350
5. Knight & Prior (1980) triplet independent measured 58.6±12.9 s: https://doi.org/10.1103/PhysRevA.21.179
6. Furlanetto & Stoever (2010), electron deposition *NOT used as heating calibration*: https://doi.org/10.1111/j.1365-2966.2010.16401.x
7. Parent source and branch: https://github.com/cosmosapjw-quantum/rei_bianchi/pull/279

Full derivation, assumptions, kernels and caveats are in `THEORY_KO.md`. Source-inclusive ZIP contains all data, figures, tests, stage records and `VERIFY.sh`.
