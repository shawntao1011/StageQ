from pathlib import Path

from stageq.cli import common


def test_root_dir_prefers_stageq_home(monkeypatch: object, tmp_path: Path) -> None:
    preferred = tmp_path / "preferred"
    preferred.mkdir()
    monkeypatch.setenv("STAGEQ_HOME", str(preferred))

    assert common.root_dir() == preferred.resolve()


def test_root_dir_discovers_from_working_directory(monkeypatch: object, tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    nested = repo_root / "apps" / "svc"
    (repo_root / "config").mkdir(parents=True)
    (repo_root / "src" / "stageq").mkdir(parents=True)
    nested.mkdir(parents=True)

    monkeypatch.delenv("STAGEQ_HOME", raising=False)
    monkeypatch.chdir(nested)

    assert common.root_dir() == repo_root.resolve()