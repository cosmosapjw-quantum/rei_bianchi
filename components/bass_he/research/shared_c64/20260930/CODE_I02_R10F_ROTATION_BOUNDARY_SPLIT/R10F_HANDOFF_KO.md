# BASS_HE R10F handoff: rotation-boundary-aware exact-node fixed GK replay

ì´ promptëŠ” R10Eì—ì„œ rotation numerical gateëŠ” PASSí–ˆì§€ë§Œ ê¸°ì¡´ 7-interval GK splitì´
ì‹¤íŒ¨í•œ ë’¤ì˜ bounded numerical nodeë‹¤. ê¸°ì¡´ R10E failureë¥¼ ë®ì–´ì“°ì§€ ì•ŠëŠ”ë‹¤.

## 0. fresh identity

Repository: `cosmosapjw-quantum/BASS_HE`

Fresh-read:
- PR15 expected HEAD `b8b2fe47a367459f6faf6796eb2f251feacbbd7c`
- PR17 expected R10E evidence basis at least
  `b9d396387132a8c0c1c3136125dfc1dc7ed9be3c`
- root `AGENTS.md`
- R10E `EXECUTION_VERDICT.json`, `FIXED_GK_DIAGNOSTIC.json`
- R10C exact table and manifest
- R10D Coulomb adapter
- R10F `BOUNDARY_ANALYSIS.json` and `DECISION.json`.

Required:
- R10C table SHA256
  `21b9ca0fa7934e05cc9d3da7044b184a6286cc0c18de01b1e43a15d21e5d3a49`
- R10D adapter blob
  `543ff5e5c20ff2969547f03410cd30353998348c`.

If identities differ, stop `R10F_IDENTITY_MISMATCH`.

## 1. preserve historical verdicts

Keep:
- `R10D_ROTATION_NUMERICS_UNRESOLVED` for the old 64/128/256 gate.
- `R10E_ROTATION_NUMERICS_PASS_EXTENDED_CONTRACT`.
- `R10E_FIXED_GK_QUADRATURE_UNRESOLVED` for the old 7-interval split.

Do not retroactively relabel those records.

Frozen:
`CODE_I02_CLOSED=true`
`full_certificate_fail_closed=true`
`scientific_PROMOTE=HOLD`
`Eq55_next_node_authorized=false`
`Eq55=NOT_RUN`.

## 2. precommit the new physical breakpoint set

Before any new Delta solve, write the exact cutpoint list and hash.

Use exactly the union in R10F `BOUNDARY_ANALYSIS.json`:

0
0.5111982111775345
0.5765261148561366
0.5833333333333334
0.6789606026861942
0.7432016886417845
0.75
1.2525231297923,
1.8477527642457414
1.9098871767143153
1.916666666666667
2.0145219311566485
2.076554805708511
2.0833333333333335
2.5764073491220003
3.0621540048995
6.942354401183
9.212477692166999

Interpretation:
- hidden-crossing supports,
- SL_CPC boundaries,
- SL_AUTHORCUT boundaries,
- both-energy COUL_CPC boundaries,
- both-energy COUL_AUTHOR boundaries.

Assert:
- cutpoints = 18
- intervals = 17
- GK15 nodes = 255
- all nodes strictly interior and positive.

Do not merge close boundaries such as 0.576526 and 0.583333.

## 3. exact Delta table for union nodes

Build the 255 GK15 rho coordinates in the existing `u=rho^2` quadrature convention.

For each active hidden-crossing branch/rho pair:
- depth=96
- panels=32
- same endpoint/certificate authority as R10C
- same source/environment contract.

Deterministic expected counts before execution:
- total active pairs = 1035
- exact branch/rho pairs identical to R10C = 90
- maximum new exact Delta calls = 945.

Reuse only exact branch+rho+source+depth+panels identity matches.
Do not reuse â€œnearbyâ€ rho.

Persist each new geometry result immediately and create a manifest.

STOP for:
- endpoint/source identity mismatch
- contour/certificate failure
- nonfinite/negative Delta.

No panel64 diagnostic is authorized merely because a quadrature component later fails.
This phase is geometry-table construction only.

## 4. five-lane integrands on common 255-node grid

Use the same five lanes as R10E:

1. `SL_CPC`
2. `SL_AUTHORCUT`
3. `COUL_CPC`
4. `COUL_AUTHOR`
5. `COUL_AUTHOR_FROZEN`

Rules:
- lanes 1-4: factor-two exact rho-dependent Delta
- lane 5: factor-two frozen Delta(0)
- straight rotation steps=64
- Coulomb rotation steps=1024
- same Nmax=3 branch topology
- same upper-shell absorbing semantics
- energies 0.5 and 5 keV/u.

No new contour solve outside the precommitÕ¹¥½¸µ¹½‘”Ñ…‰±”¸((ŒŒ€Ô¸™¥á•Õ¹¥½¸µÍÁ±¥Ğ,ÄÔ½,Üœ…Ñ”()%¹Ñ•É…Ñ”•… ±…¹”½•¹•Éä½½µÁ½¹•¹Ğ½Ù•È•á…Ñ±äÑ¡”€ÄÜÁÉ”µÍÁ±¥Ğ¥¹Ñ•ÉÙ…±Ì¸()UÍ”è(´,ÄÔ½,Ü•µ‰•‘‘•Á…¥È(´ÉÑ½°ôÉ”´Ñ€(´…Ñ½°ôÅ”´ÄÁ€(´•Ù…±Õ…Ñ¥½¹Ì€ô€ÈÔÔ(´É•™¥¹•µ•¹ÑÌ€ô€À¸()AMLÉ•ÅÕ¥É•Ì…±°€äÀ½µÁ½¹•¹ÑÌè()•ÉÉ½È€ğô…Ñ½°€¬ÉÑ½°©…‰Ì¡Ñ½Ñ…°¥€¸()AMLÙ•É‘¥Ğè)HÄÁ}I=QQ%=9}	=U9Ie}MA1%Q}%a}-}AMM}9=Q}1=	1}=9Q%9UU5}	=U9€¸()%0Ù•É‘¥Ğè)HÄÁ}	=U9Ie}MA1%Q}-}U9IM=1Y€¸()%˜%0è(´É•Á½ÉĞİ½ÉÍĞ±…¹”½•¹•Éä½½µÁ½¹•¹Ğ½¥¹Ñ•ÉÙ…°ì(´‘¼¹½ĞÉ•™¥¹”ì(´‘¼¹½Ğ…‘‰É•…­Á½¥¹ÑÌì(´‘¼¹½Ğ±½½Í•¸Ñ½±•É…¹”ì(´‘¼¹½Ğ¡…¹”É½Ñ…Ñ¥½¸ÍÑ•ÁÌ¸()Í•Á…É…Ñ”HÄÁ½¹ÑÉ…Ğİ½Õ±‰”É•ÅÕ¥É•¸((ŒŒ€Ø¸‰…Í•±¥¹”½Ù•ÈµÍÁ±¥ĞÉ•É•ÍÍ¥½¸()M1}A€¥ÌÑ¡”Í…µ”Á¡åÍ¥…°¥¹Ñ•É…¹…±É•…‘ä…‘µ¥ÑÑ•¥¸HÄÁ°‰ÕĞ•Ù…±Õ…Ñ•½¸)Ñ¡”±…É•ÈÕ¹¥½¸ÍÁ±¥Ğ¸()½µÁ…É”¹•ÜM1}A……¥¹ÍĞHÄÁÈµI!=€™½È•Ù•Éä¥¹‘•á•½µÁ½¹•¹Ğ…¹Í¡•±°¸()I•Á½ÉĞè(´…‰Í½±ÕÑ”½É•±…Ñ¥Ù”‘¥™™•É•¹”(´½±•µ‰•‘‘••ÍÑ¥µ…Ñ”(´¹•Ü•µ‰•‘‘••ÍÑ¥µ…Ñ”¸()Q¡¥Ì¥Ì„½¹Í¥ÍÑ•¹ä‘¥…¹½ÍÑ¥Œ°¹½Ğ„É•Á±…•µ•¹Ğ½˜HÄÁ¸()¹äÕ¹•áÁ•Ñ•‘±ä±…É”‰…Í•±¥¹”‘¥ÍÉ•Á…¹ä¥Ì„MQ=@è)HÄÁ}	M1%9}IIMM%=9}U9IM=1Y€¸()¼¹½Ğ¥¹Ù•¹Ğ„¹•ÜÁ¡åÍ¥…°•áÁ±…¹…Ñ¥½¸‰•™½É”¡•­¥¹œÑ…‰±”½ÅÕ•Éä¥‘•¹Ñ¥Ñä¸((ŒŒ€Ü¸•™™•Ğ‘•½µÁ½Í¥Ñ¥½¸½¹±ä…™Ñ•È,AML()=¹±ä…™Ñ•ÈM•Ñ¥½¹Ì€Ì´ØÁ…ÍÌ°½µÁÕÑ”Ñ¡”½É¥¥¹…°HÄÁ‘•½µÁ½Í¥Ñ¥½¸è()ÕÑ½™™}•™™•Ğ€ôM1}UQ!=IUP€´M1}A€()ÑÉ…©•Ñ½Éå}•™™•Ğ€ô=U1}A€´M1}A€()¥¹Ñ•É…Ñ¥½¸€ô(=U1}UQ!=H€´=U1}A€´M1}UQ!=IUP€¬M1}A€()…¹™É½é•¸…‘‘¥Ñ¥½¸è)=U1}UQ!=I}I=i8€´=U1}UQ!=I€¸()UÍ”Ñ¡”…±É•…‘äµÁÉ•½µµ¥ÑÑ•HÄÁµ…Ñ•É¥…±¥ÑäÉ¥Ñ•É¥„Õ¹¡…¹•¸()ÁÁ•¹‘¥àµ½µÁ…É¥Í½¹ÌÉ•µ…¥¸è)UQ!=I}%5A159QQ%=9}IAI=UQ%=9}=91e}9=Q}A!eM%1}Y1%Q%=9€¸((ŒŒ€à¸¥¹Ñ•ÉÁÉ•Ñ…Ñ¥½¸()%˜Ñ¡”¹•ÜÍÁ±¥Ğµ…­•Ì…±°€äÀ½µÁ½¹•¹ÑÌÁ…ÍÌ°±…ÍÍ¥™äè()I=QQ%=9}	I-A=%9Q}MA1%Q}UM}=9%I5}]%Q!}%a}-}AMM€¸()Q¡•¸…ÍÍ•ÍÌİ¡•Ñ¡•È=U1}UQ!=Hµ…Ñ•É¥…±±ä¥µÁÉ½Ù•Ì‰½Ñ ÁÁ•¹‘¥àµI5Lµ•ÑÉ¥Ì¸()%˜,ÍÑ¥±°™…¥±Ì°±…ÍÍ¥™äè()I=QQ%=9}	I-A=%9Q}MA1%Q}%9MU%%9Q€¸()I•ÑÕÉ¸Ñ¡”İ½ÉÍĞ¥¹Ñ•ÉÙ…°½½µÁ½¹•¹Ğ¸Q¡”¹•áĞ¹½‘”µ…ä¥¹Ù•ÍÑ¥…Ñ”ÁÉ½‘ÕÑ¥½¸É•Õ±…É¥Ñä½±½…°É•™¥¹•µ•¹Ğ°‰ÕĞ¹½Ğ¥¸Ñ¡¥Ì•á•ÕÑ¥½¸¸((ŒŒ€ä¸Q€¼Ù•É¥™¥…Ñ¥½¸()¹ä¹•ÜÉÕ¹¹•È½¡•±Á•Èè(´IÑ•ÍÑÌ‰•™½É”¥µÁ±•µ•¹Ñ…Ñ¥½¸ì(´•á…ĞÍÁ±¥ĞµÍ•Ğ¥‘•¹Ñ¥ÑäÑ•ÍĞì(´‘•Ñ•Éµ¥¹¥ÍÑ¥Œ€ÈÔÔµ¹½‘”¼ÄÀÌÔµÁ…¥È½Õ¹ĞÑ•ÍĞì(´•á…ĞHÄÁÉ•ÕÍ”½Õ¹ĞÑ•ÍĞì(´¹¼µÉ•™¥¹•µ•¹Ğ…ÍÍ•ÉÑ¥½¸ì(´M1}A‰…Í•±¥¹”É•É•ÍÍ¥½¸ì(´¥Ğ‘¥™˜€´µ¡•­€¸()Õ±°É•Á½Í¥Ñ½ÉäÁåÑ•ÍĞ¥Ì¹½ĞÉ•ÅÕ¥É•Õ¹±•ÍÌÁÉ½‘ÕÑ¥½¸Í½ÕÉ”¥Ì¡…¹•°İ¡¥ ¥Ì)¹½Ğ¥¹Ñ•¹‘•¸((ŒŒ€ÄÀ¸¹½¸µÍ½Á”()¼9=Pè€(´¡…¹”ÁÉ½‘ÕÑ¥½¸Í½ÕÉ”½‘•™…Õ±ÑÌ½Ñ½±•É…¹•Ì(´¡…¹”5…¹ÕÌÍÑ•ÁÌ(´…±Ñ•È™…Ñ½ÈµÑİ¼Á½±¥ä(´ÕÍ”ÍÕÉÉ½…Ñ”•±Ñ„…Ì™¥¹…°¥¹Ñ•É…Ñ¥½¸…ÕÑ¡½É¥Ñä(´É•ÉÕ¸=µ$ÀÈ(´ÉÕ¸€ÔØµ…Ñ¥½¸É•Á±…ä½İ½É­•ÈÍİ••À(´•á•ÕÑ”…ÕÑ¡½È=IQI8(´ÍÑ…ÉĞ0È½-É…İéå¬(´…‘Á¡åÍ¥…°¡…¹¹•±Ì(´µ•É”½™½É”µÁÕÍ ¸((ŒŒ€ÄÄ¸‘ÕÉ…‰±”É•ÑÕÉ¸()AÕ‰±¥Í …ÁÁ•¹µ½¹±äÕ¹‘•È„¹•ÜAHµìÑ¥µ•ÍÑ…µÁ•¹…µ•ÍÁ…”¸()I•ÑÕÉ¸è(´™É•Í ¥‘•¹Ñ¥Ñ¥•Ì(´ÁÉ•½µµ¥ÑÑ•ÕÑÁ½¥¹Ğ½ÅÕ•Éä¡…Í (´•á…ĞÉ•ÕÍ”½¹•Ü•±Ñ„½Õ¹ÑÌ(´Õ¹¥½¸µ¹½‘”Ñ…‰±”µ…¹¥™•ÍĞ(´€äÀµ½µÁ½¹•¹Ğ,…Ñ”(´‰…Í•±¥¹”½Ù•ÈµÍÁ±¥ĞÉ•É•ÍÍ¥½¸(´¥˜AML°™¥Ù”µ±…¹”½ÕÑÁÕÑÌ…¹€Ë\È‘•½µÁ½Í¥Ñ¥½¸