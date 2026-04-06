from stageq.ctl.process import is_pid_running


def test_is_pid_running_rejects_negative_pid() -> None:
    assert is_pid_running(-1) is False
