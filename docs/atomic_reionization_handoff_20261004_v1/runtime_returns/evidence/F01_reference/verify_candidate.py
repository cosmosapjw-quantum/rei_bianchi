import subprocess
subprocess.run(["/home/cosmosapjw/.cargo/bin/cargo","test","--manifest-path","rust/rei_microphysics/Cargo.toml","--test","atomic_provider","--test","homogeneous_rates","--test","forward","--locked"],check=True)
