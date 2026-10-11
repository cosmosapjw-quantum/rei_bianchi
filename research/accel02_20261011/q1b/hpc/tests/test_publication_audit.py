import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_publication import HPC, inspect


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.DEVNULL).decode().strip()


def repository(tmp_path):
    git(tmp_path, 'init')
    git(tmp_path, 'config', 'user.email', 'test@example.invalid')
    git(tmp_path, 'config', 'user.name', 'Test')
    (tmp_path/'base.txt').write_text('already public\n')
    git(tmp_path, 'add', 'base.txt'); git(tmp_path, 'commit', '-m', 'base')
    return git(tmp_path, 'rev-parse', 'HEAD')


def test_source_only_publication(tmp_path):
    base = repository(tmp_path)
    p = tmp_path/HPC/'module.py'; p.parent.mkdir(parents=True)
    p.write_text('value = 1\n')
    git(tmp_path, 'add', '.'); git(tmp_path, 'commit', '-m', 'source')
    assert inspect(tmp_path, base, 'HEAD')['status'] == 'PASS_SOURCE_ONLY_NEW_HISTORY'


def test_deleted_private_history_is_still_rejected(tmp_path):
    base = repository(tmp_path)
    p = tmp_path/'private.json'; p.write_text('{}\n')
    git(tmp_path, 'add', '.'); git(tmp_path, 'commit', '-m', 'private')
    private = git(tmp_path, 'rev-parse', 'HEAD')
    git(tmp_path, 'rm', 'private.json'); git(tmp_path, 'commit', '-m', 'delete')
    result = inspect(tmp_path, base, 'HEAD', forbidden_commits=[private])
    assert result['status'] == 'FAIL'
    assert any(f['kind'] == 'private_commit_ancestor' for f in result['findings'])


def test_denylist_never_prints_value(tmp_path):
    base = repository(tmp_path)
    p = tmp_path/HPC/'notes.md'; p.parent.mkdir(parents=True)
    secret = 'synthetic-private-value'
    p.write_text(secret)
    git(tmp_path, 'add', '.'); git(tmp_path, 'commit', '-m', 'notes')
    result = inspect(tmp_path, base, 'HEAD', deny_values=[secret])
    assert result['status'] == 'FAIL'
    assert secret not in str(result)


def test_private_filename_is_redacted(tmp_path):
    base = repository(tmp_path)
    secret = 'synthetic-private-name'
    p = tmp_path/HPC/(secret+'.json'); p.parent.mkdir(parents=True); p.write_text('{}')
    git(tmp_path, 'add', '.'); git(tmp_path, 'commit', '-m', 'new')
    result = inspect(tmp_path, base, 'HEAD', deny_values=[secret])
    assert result['status'] == 'FAIL'
    assert secret not in str(result)
