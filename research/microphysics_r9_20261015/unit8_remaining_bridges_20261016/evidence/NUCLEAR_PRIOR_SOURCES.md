# Unit 8 lane D source record

Requested theory authority Astra; observed runtime model UNKNOWN. Accessed2026-10-16. This record distinguishes examined code from future execution.

Official upstream: https://github.com/CyrilPitrou/primat , pinned commit4bf97d5082eee54b9df50d88f43182bb651fea80. Root staged517 files,21,740,807bytes, with0 reported download failures. Exact per-file source/blob evidence is in intake/PRIMAT_DOWNLOAD_MANIFEST.json and PRIMAT_SOURCE_LIST.json. Download time is not numerical runtime. The provider root is /workspace/scratch/37bc4acea758/u8_primat_provider.

Primary project information: https://www2.iap.fr/users/pitrou/primat.htm ; native uncertainty documentation: https://primat.readthedocs.io/en/stable/howto/rate-variation-mc.html . Documentation identifies source-native propagated-rate covariance as an available operation. This task freezes the inspected commit rather than silently accepting a future latest version.

Read directly from the pinned staged source:

- primat-c/README.md and Makefile: standalone native build and CLI, without requiring Python installation.
- primat-c/src/config.c: source defaults, tau_n878.4s, std_tau_n0.5s, networksmall, rate cap30, standard corrections/caches. Donor-like cosmology overrides are explicit in the task contract.
- primat-c/include/mc.h and src/mc.c: each sample uses independent reaction-normal offsets and one neutron-lifetime normal draw, native RNG seed+index, setup reuse per worker, and actual ddof1 standard deviation/covariance. The header's population-std description is not used to override the implemented N−1 divisor.
- primat-c/src/network_data.c, cpr_network_apply_variations: median(T) times exp[p log uncertainty_factor(T)], optional additive offset zero here, clipped to[1/30,30]; reverse detailed-balance rates track changed forward rates.
- primat-c/src/cli.c: native samples/covariance/correlation exports, ten-digit sample serialization, all present observables followed by endpoint nuclides; MC contains repeated central/setup work accounted for by the measured pilot budget.
- primat-c/src/api.c: Li7oH combines endpoint Li7+Be7, and He3oH combines He3+H3 before division by protons. These definitions are observable conventions, not an executed late-decay history.
- primat-c/src/rng.c: xoshiro256** initialized by SplitMix64; no NumPy sample-identity assertion is made.
- primat/data/nuclear/networks/small.txt: the exact12 named nuclear reactions and their table filenames; matching rate/uncertainty tables are preserved as source inputs.

The original immutable R5 donor records this same source commit but a different large-network bare-Be overlay. Equal source commit is not equal scientific run identity. The new result is a conditional small-network finite-sample covariance under source-native priors; neither an observed-data posterior nor an uncertainty assignment to that donor follows without additional work.
