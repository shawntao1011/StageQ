from stageq.cli.svc_main import build_parser


def test_stop_status_commands_accept_env_option() -> None:
    parser = build_parser()

    stop_args = parser.parse_args(["stop", "hdb.hk", "--env", "prod"])
    status_args = parser.parse_args(["status", "hdb.hk", "--env", "prod"])

    assert stop_args.env == "prod"
    assert status_args.env == "prod"