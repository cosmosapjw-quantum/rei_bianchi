//! Local host/boot + canonical directory inode scope. No portable/forked run authority.
use super::R;
use std::{
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    os::{fd::AsRawFd, unix::fs::MetadataExt},
    path::{Path, PathBuf},
};
unsafe extern "C" {
    fn flock(fd: i32, operation: i32) -> i32;
}
pub struct Run {
    pub root: PathBuf,
    pub namespace: String,
    _lock: File,
    pid: u32,
}
fn binding(root: &Path) -> R<String> {
    let m = fs::metadata(root).map_err(|e| e.to_string())?;
    let host = fs::read_to_string("/etc/machine-id").map_err(|e| e.to_string())?;
    let boot = fs::read_to_string("/proc/sys/kernel/random/boot_id").map_err(|e| e.to_string())?;
    if host.trim().is_empty() || boot.trim().is_empty() {
        return Err("local host identity unavailable".into());
    }
    Ok(format!(
        "HOST_BOOT_DIRECTORY_ONLY\n{}\n{}\n{}\n{}:{}\n",
        host.trim(),
        boot.trim(),
        root.display(),
        m.dev(),
        m.ino()
    ))
}
fn exclusive(root: &Path) -> R<File> {
    let p = root.join("RUN_LOCK");
    if fs::symlink_metadata(&p).is_ok_and(|m| m.file_type().is_symlink()) {
        return Err("unsupported lock symlink".into());
    }
    let f = OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .open(p)
        .map_err(|e| e.to_string())?;
    if unsafe { flock(f.as_raw_fd(), 2 | 4) } != 0 {
        return Err("run already owned by another receiver".into());
    }
    Ok(f)
}
impl Run {
    pub fn create(path: &Path) -> R<Self> {
        fs::create_dir(path).map_err(|e| format!("fresh run required: {e}"))?;
        let root = fs::canonicalize(path).map_err(|e| e.to_string())?;
        let lock = exclusive(&root)?;
        let mut random = [0u8; 32];
        File::open("/dev/urandom")
            .map_err(|e| e.to_string())?
            .read_exact(&mut random)
            .map_err(|e| e.to_string())?;
        let id = random
            .iter()
            .map(|b| format!("{b:02x}"))
            .collect::<String>();
        let namespace = format!("{}{}\n", binding(&root)?, id);
        let mut f = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(root.join("RUN_ID"))
            .map_err(|e| e.to_string())?;
        f.write_all(namespace.as_bytes())
            .map_err(|e| e.to_string())?;
        f.sync_all().map_err(|e| e.to_string())?;
        File::open(&root)
            .and_then(|f| f.sync_all())
            .map_err(|e| e.to_string())?;
        if let Some(parent) = root.parent() {
            File::open(parent)
                .and_then(|f| f.sync_all())
                .map_err(|e| e.to_string())?
        }
        Ok(Self {
            root,
            namespace,
            _lock: lock,
            pid: std::process::id(),
        })
    }
    pub fn resume(path: &Path) -> R<Self> {
        let root = fs::canonicalize(path).map_err(|e| e.to_string())?;
        let lock = exclusive(&root)?;
        let namespace = fs::read_to_string(root.join("RUN_ID")).map_err(|e| e.to_string())?;
        let bind = binding(&root)?;
        let id = namespace
            .strip_prefix(&bind)
            .ok_or("unsupported host/root/fork reuse")?;
        if id.len() != 65
            || !id.ends_with('\n')
            || !id[..64]
                .bytes()
                .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
        {
            return Err("corrupt run identity".into());
        }
        Ok(Self {
            root,
            namespace,
            _lock: lock,
            pid: std::process::id(),
        })
    }
    pub fn check_owner(&self) -> R<()> {
        if self.pid != std::process::id() {
            Err("unsupported inherited fork handle".into())
        } else {
            Ok(())
        }
    }
}
