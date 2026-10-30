# REI F4 Ferrett1987 direct R31 × R32 BASS193

One bounded source-qualified physics unit. Immutable parent PR #289 at `9d70cea0b3f1334fe9991ceaa85005bbd9994f51` (CI GREEN). Source ZIP and user-provided 1987 60-page PDF are copied byte-exact to `source/`.

```bash
bash VERIFY.sh                 # 21 targeted Python + manifest + source SHA
python code/direct_r31.py      # regenerate 1158-event, 193-epoch, 7-observation CSV, RESULT.json
```

`RESULT.json` and three CSV files are generated from original 193 saved BASS states. Source column `r31` and `r32` are direct ratios in Ferrett Table II/III. The PDF author script used extrapolated Rp for higher energies, **excluded here**. Pseudo-data/statistical rectangle is not an observed covariance confidence interval.

**Preserved contract:** working33/88, central28/88, F4fast4/7, physical_delta0; no IVP, merge, force push or production promotion; source owner and cross-model source uncertainties explicit. `R6/C9 distinct-author NOT_RUN`. Git publish code/tests/results/stage status only. Raw PDF and parent source archives stay in user's backed-up private master ZIP, not in Git.