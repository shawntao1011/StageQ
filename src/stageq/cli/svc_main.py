from __future__ import annotations

import argparse
import shlex

from stageq.cli.common import root_dir
from stageq.codec.q_config import write_config_q
from stageq.ctl.launcher import build_launch_argv, launch_service, service_status, stop_service
from stageq.ctl.resolver import resolve_service_config


def cmd_start(args: argparse.Namespace) -> None:
    pid = launch_service(root_dir=root_dir(), service_name=args.service_name, env_name=args.env)
    print(f"started {args.service_name} (pid={pid})")


def cmd_stop(args: argparse.Namespace) -> None:
    stopped = stop_service(root_dir(), args.service_name, args.env)
    if stopped:
        print(f"stopped {args.service_name}")
    else:
        print(f"service not running: {args.service_name}")


def cmd_status(args: argparse.Namespace) -> None:
    running, pid = service_status(root_dir(), args.service_name, args.env)
    if running:
        print(f"running {args.service_name} (pid={pid})")
    elif pid is None:
        print(f"not running {args.service_name} (pid file missing)")
    else:
        print(f"not running {args.service_name} (stale pid={pid})")

def cmd_print(args: argparse.Namespace) -> None:
    repo_root = root_dir()
    cfg = resolve_service_config(repo_root, args.service_name, args.env)

    runtime_home = repo_root / "var" / "runtime" / args.env / args.service_name
    runtime_home.mkdir(parents=True, exist_ok=True)

    config_path = runtime_home / "config.q"
    write_config_q(cfg, out=config_path)

    argv = build_launch_argv(repo_root, args.service_name, args.env)
    print(f"[stageq] runtime home: {runtime_home}")
    print(f"[stageq] config: {config_path}")
    print(f"[stageq] launch command: {shlex.join(argv)}")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stageqsvc")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("start")
    p.add_argument("service_name")
    p.add_argument("--env", default="dev")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("stop")
    p.add_argument("service_name")
    p.add_argument("--env", default="dev")
    p.set_defaults(func=cmd_stop)

    p = sub.add_parser("status")
    p.add_argument("service_name")
    p.add_argument("--env", default="dev")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("print")
    p.add_argument("service_name")
    p.add_argument("--env", default="dev")
    p.set_defaults(func=cmd_print)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
