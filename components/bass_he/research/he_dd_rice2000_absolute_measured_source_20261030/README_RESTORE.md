# BASS_HE PR125 restore contract

This package contains new source-owned measured *Rice 2000* absolute two-deuteron photodisintegration data: 12 published differential cross sections, 8 alternative model fits, 6 earlier 1998 thesis preliminary values (same experiment, NOT independent), source-systematic percentages and conditional inverse detailed-balance factor supports. Original PDF SHA identities are in `sources/USER_FILE_IDENTITY.json`. No original copyrighted papers are pushed to the public Git branch; any private full backup including user-supplied PDFs is kept in the user's own Library/Google Drive.

```
./REPRODUCE.sh
python3 src/verify_pdfs.py --pdf-dir /path/to/the/seven/user-uploads
```

Reproduction of JSON and CSV requires Python >=3.10 stdlib and the 4 exact source text data files in `sources/`. Optional PDF semantic check requires PyMuPDF and exact user-uploaded PDF SHA. Output status is constrained: `R_event=null, kappa=null, heat_rate=null, L4=false, production=HOLD`. Do not claim a flat-photon or point-energy source.

Protected: original parent PR124 HEAD `9696297205c2560bd8bdfc8d72b8b80b86fae8d3`, no merge and no force push. `STAGE_LEDGER.json` contains each 10-stage theory and 10-stage code publication evidence. R06/C09 native different-author review is not run. Continue only with physical-data nodes. One Rice 2000 Table II row has a preserved source-internal discrepancy.
