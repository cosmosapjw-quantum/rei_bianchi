# Unit8 complete portable source and results

GitHub transport imposes a 16 MiB request limit. The complete xz archive is therefore stored as two ordered binary parts beside this file. This is the same verified 240-member archive; its 239 payload members are covered by `progress/MANIFEST_PORTABLE.json` inside the archive. The separate full private backup has 266 members and a different manifest. Final delivery receipts are published afterward and do not rewrite these archives.

Codex can retrieve these files through the existing PR151 checkout or GitHub download and execute the following from this directory. No manual user download is required. Extraction only restores source and saved results; it does not run any scientific calculation.

```sh
cat UNIT8_PORTABLE_SOURCE_RESULTS_20261018.tar.xz.part01 UNIT8_PORTABLE_SOURCE_RESULTS_20261018.tar.xz.part02 > UNIT8_PORTABLE_SOURCE_RESULTS_20261018.tar.xz
printf '%s\n' '17aa771ba41163bd2285ccd40f2d2697cc712c1dff3d66795b011ba058569e28  UNIT8_PORTABLE_SOURCE_RESULTS_20261018.tar.xz' | sha256sum -c -
mkdir -p restored_unit8
tar -xJf UNIT8_PORTABLE_SOURCE_RESULTS_20261018.tar.xz -C restored_unit8
```

Archive size: 15,406,972 bytes. Parts:

| File suffix | Bytes | SHA256 |
|---|---:|---|
| part01 | 7,500,000 | 8fc1805cb57ae123e1a9109fb74e709094098e94913d0a27a6db09b785cbb56e |
| part02 | 7,906,972 | 97d997a867c712cb389325ee3b92e20878251a3aeb46c3631c34c6708e63d1c3 |

Read the restored README, report, reviews and DAG before any proposed follow-up. A rates pass but independent Li kinetics remain HOLD. Full T1–T8 are unfinished; NCP allocations/deadlines are unchanged. Existing execution receipts must be reused, not overwritten or replayed automatically.
