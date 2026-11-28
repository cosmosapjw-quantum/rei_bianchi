# HE38 단계별 실제 전달 원장

workflow1.0.0 / approval0.2. 모든 행은 해당 단계의 실제 Git 게시와 Dropbox completed ACK에 연결된다. 단계별 archive는 그 시점의 누적 snapshot이다. 자신의 ACK는 다음 단계 또는 최종 metadata 게시에 포함된다.

| 단계 | 누적 완료 | Git commit | Archive | SHA256 | Dropbox ID | 다음 DAG |
|---|---:|---|---|---|---|---|
| R1 | 1/20 | `485e753038f600540a6a5586c41dfb9f1cf8d46b` | `BASS_HE_HE38_FMG_R1_20261023T040706Z.tar.gz` | `3e02863d04ff04ad1fc92820ae8faf50a43f8a0ecbfa6bb590cc5192ce81ea8c` | `id:BSpOijBcT10AAAAAAD_xPQ` | R2 |
| R2 | 2/20 | `fa9fc3651abc4cd061dccc508063b0bcce3dedcf` | `BASS_HE_HE38_FMG_R2_20261023T041316Z.tar.gz` | `2b5a3d2ea9b09254db16159e4f27f949dbc492993361074e21f495bec85a172d` | `id:BSpOijBcT10AAAAAAD_xcA` | R3 |
| R3 | 3/20 | `b33257c55eca94e812077d9893ea2e345764250c` | `BASS_HE_HE38_FMG_R3_20261023T041333Z.tar.gz` | `e724286eb71f8dd2a2a95b0ffa7eed731ff4b68fe2fe975dfdc3c2ea7c268b98` | `id:BSpOijBcT10AAAAAAD_xcQ` | R4 |
| R4 | 4/20 | `99570e233322fbe7483a99f6631c70485b1519f6` | `BASS_HE_HE38_FMG_R4_20261023T041349Z.tar.gz` | `5ccd750439f7077d06a36d26ea8f0c64f0bbf2e2b3417619dcebd539b9da06ea` | `id:BSpOijBcT10AAAAAAD_xcg` | R5 |
| R5 | 5/20 | `2f26456d229e2889c1d8017f1df67014a8a18eb1` | `BASS_HE_HE38_FMG_R5_20261023T041404Z.tar.gz` | `596aa6574f793a437c047613470eaf545d7472ce2848bb55369dd2f5e7f796e0` | `id:BSpOijBcT10AAAAAAD_xcw` | R6 |
| R6 | 6/20 | `6eafd7d0ee9a479bc0d449d25af8715e76c0e5c1` | `BASS_HE_HE38_FMG_R6_20261023T041417Z.tar.gz` | `20bec30b63a151574c323ffc71109930aa344e2e36232f9e17cbf4cbc75f5f15` | `id:BSpOijBcT10AAAAAAD_xdA` | R7 |
| R7 | 7/20 | `c69ca20bb94fec87c2ab4f8571017fba744f44ac` | `BASS_HE_HE38_FMG_R7_20261023T041429Z.tar.gz` | `7dab40ab2148c2e96fe1427095e5bbcca16bfc68d60e38b0b4ae9e3fbf0b9096` | `id:BSpOijBcT10AAAAAAD_xdQ` | R8 |
| R8 | 8/20 | `4ea1749b90fe67d4f1d8b7f6c78b1aa0dce33487` | `BASS_HE_HE38_FMG_R8_20261023T041445Z.tar.gz` | `ab81f47684fc1e33138acc880e857255a8f683e19afa10f8e1138a5c50c0551e` | `id:BSpOijBcT10AAAAAAD_xhg` | R9 |
| R9 | 9/20 | `13a3f81adc0114abd0f5be08c44e955b773c5b69` | `BASS_HE_HE38_FMG_R9_20261023T041501Z.tar.gz` | `5d483f7d0d1c3da4d9507141033602158c073ba49109377161a773ba1d4f7b77` | `id:BSpOijBcT10AAAAAAD_xhw` | R10 |
| R10 | 10/20 | `815522288e17daf5dbb29f395b127ea43237f14f` | `BASS_HE_HE38_FMG_R10_20261023T041515Z.tar.gz` | `d3c29e769ec727962c2af84fffa1f88d0fd8f2eb2d3598db2debaca8def1f30e` | `id:BSpOijBcT10AAAAAAD_xiA` | C1 |
| C1 | 11/20 | `d6500e0655de2956e871c606af109d79d4f883c6` | `BASS_HE_HE38_FMG_C1_20261023T041528Z.tar.gz` | `9737e532ab5a1e04f223bf999edd1f0577d6b707efbd27bbe8579890372a7338` | `id:BSpOijBcT10AAAAAAD_xiQ` | C2 |
| C2 | 12/20 | `da6210e800b40a6bdc904c7bd2c7cb9db434e463` | `BASS_HE_HE38_FMG_C2_20261023T041623Z.tar.gz` | `9dc4ed024c4f1e6fa79768bd5909e79a0e40970b8b5ead56b77efba32029db48` | `id:BSpOijBcT10AAAAAAD_xmg` | C3 |
| C3 | 13/20 | `3a2658aabd7d44f651c112cbbcb87ddac059a688` | `BASS_HE_HE38_FMG_C3_20261023T041637Z.tar.gz` | `10667a57e4266a526c6dc7176705b1845249e6918cf116643e7b0d6b5e3b0a69` | `id:BSpOijBcT10AAAAAAD_xmw` | C4 |
| C4 | 14/20 | `2e8866050e05caba8bc2318e204d7e8d1c80b3d2` | `BASS_HE_HE38_FMG_C4_20261023T041651Z.tar.gz` | `c4c4166f4b52c284368527357d826c4ee0f7ca0b35c135fe417d70cafc13c44c` | `id:BSpOijBcT10AAAAAAD_xnA` | C5 |
| C5 | 15/20 | `bdfd5813322f47e8e3ff01d19754384b3edf7bda` | `BASS_HE_HE38_FMG_C5_20261023T041704Z.tar.gz` | `4a9bc16fb6d8e640e2b05bdf4b72ebc20bc9add8cb070916800b62bd50f73d0f` | `id:BSpOijBcT10AAAAAAD_xnQ` | C6 |
| C6 | 16/20 | `cd1e27aa0efd774963552b6dd72b9e48f42d6e0c` | `BASS_HE_HE38_FMG_C6_20261023T042139Z.tar.gz` | `f331510e184d8b2cffbad3fc1ca083d90531fde0a219eaaa5cf347864baa3dea` | `id:BSpOijBcT10AAAAAAD_xvg` | C7 |
| C7 | 17/20 | `f5302814f7da7d5e013593910e34b695ce20ebef` | `BASS_HE_HE38_FMG_C7_20261023T042216Z.tar.gz` | `4a5a0e989cc8c332c422fa150cf23cc81c7aca8d53e7638a6fad88c55ff3b827` | `id:BSpOijBcT10AAAAAAD_xvw` | C8 |
| C8 | 18/20 | `cfc04fb2bcbc23d7a03554272be535a6ac11a711` | `BASS_HE_HE38_FMG_C8_20261023T042231Z.tar.gz` | `d542612f79b3bb6f4a6b0a4ebda534b6ebf7c482e8a9e8130caff14d74a011ef` | `id:BSpOijBcT10AAAAAAD_xwA` | C9 |
| C9 | 19/20 | `ccbfa8d2cf80f9619aed663242ab456dba02ef72` | `BASS_HE_HE38_FMG_C9_20261023T042836Z.tar.gz` | `1357d802d9836431820305678994109d66afdaa00851c88c6cd82bae32234a5f` | `id:BSpOijBcT10AAAAAAD_yAQ` | C10 |
| C10 | 20/20 | `6790005d5a0b7b0dceedeedd4f3687b94202ed54` | `BASS_HE_HE38_FMG_C10_20261023T043126Z.tar.gz` | `5922cc6e548a926cbb590b244f8a172aa08b27654eba55f663a96c809e1c5515` | `id:BSpOijBcT10AAAAAAD_yAg` | NEXT_DAG.json / 새 단원 source gate |

## C10 이후 handoff 조건 교정

N1A의 heavy-target electron energy 조건과 finite-mass total COM energy 조건을 구분했다. 현재 HE38 모델·계산 결과 변경 및 과학 재실행은 0이다.

- 교정 및 최종 science commit: `2ce8afd80b7baf430c85ce5ace81a5bd4e9465c0`
- 교정 archive SHA256: `8ff8f1beebb143f9e6c16265a74427866e1823cc37f20a90186b6b07c207d438`
- Dropbox ID: `id:BSpOijBcT10AAAAAAD_yEw`
- 작업공간 정리 후 실제 provider metadata·archive hash·Git blob 대조로 복구 ACK를 구성했다. 원래 업로드 응답의 복사본과 구분한다.
