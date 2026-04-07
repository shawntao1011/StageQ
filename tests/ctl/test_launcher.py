from pathlib import Path

import pytest

from stageq.ctl.launcher import _find_pid_file, _service_files


def test_service_files_layout() -> None:
    files = _service_files(Path('/repo'), 'hdb.hk', 'dev')
    assert files['runtime_home'] == Path('/repo/var/runtime/dev/hdb.hk')
    assert files['config_q'] == Path('/repo/var/runtime/dev/hdb.hk/config.q')
    assert files['pid'] == Path('/repo/var/runtime/dev/hdb.hk/service.pid')
    assert files['log'] == Path('/repo/var/runtime/dev/hdb.hk/service.log')
    assert files['cmdline'] == Path('/repo/var/runtime/dev/hdb.hk/cmdline')


def test_find_pid_file_with_env_is_direct_lookup(tmp_path: Path) -> None:
    pid_file = tmp_path / "var" / "runtime" / "dev" / "hdb.hk" / "service.pid"
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text("123\n", encoding="utf-8")

    found = _find_pid_file(tmp_path, "hdb.hk", "dev")
    assert found == pid_file


def test_find_pid_file_without_env_rejects_ambiguous_matches(tmp_path: Path) -> None:
    (tmp_path / "var" / "runtime" / "dev" / "hdb.hk").mkdir(parents=True, exist_ok=True)
    (tmp_path / "var" / "runtime" / "prod" / "hdb.hk").mkdir(parents=True, exist_ok=True)
    (tmp_path / "var" / "runtime" / "dev" / "hdb.hk" / "service.pid").write_text("1\n", encoding="utf-8")
    (tmp_path / "var" / "runtime" / "prod" / "hdb.hk" / "service.pid").write_text("2\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="multiple runtime homes matched"):
        _find_pid_file(tmp_path, "hdb.hk", None)