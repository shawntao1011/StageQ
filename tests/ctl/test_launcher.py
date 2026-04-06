from pathlib import Path

from stageq.ctl.launcher import _service_files


def test_service_files_layout() -> None:
    files = _service_files(Path('/repo'), 'hdb.hk')
    assert files['pid'] == Path('/repo/var/run/hdb.hk.pid')
    assert files['log'] == Path('/repo/var/log/hdb.hk.log')
    assert files['cmdline'] == Path('/repo/var/generated/hdb.hk.cmdline')
