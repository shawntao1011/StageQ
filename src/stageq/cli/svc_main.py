from __future__ import annotations

import argparse
from pathlib import Path

from stageq.ctl.launcher import launch_service, service_status, stop_service

def _root_dir() -> Path:
    return Path(__file__).resolve().parents[3]

def cmd_start(args: argparse.Namespace) -> None:
    pid = launch_service(
        root_dir=_root_dir(),
        service_name=args.service_name,
        env_name=args.env,
    )
    print(f"started {args.service_name} (pid={pid})")

def cmd_stop(args: argparse.Namespace) -> None:
    stopped = stop_service(_root_dir(), args.service_name)
    if stopped:
        print(f"stopped {args.service_name}")
    else:
        print(f"service not running: {args.service_name}")


def cmd_status(args: argparse.Namespace) -> None:
    running, pid = service_status(_root_dir(), args.service_name)
    if running:
        print(f"running {args.service_name} (pid={pid})")
    else:
        if pid is None:
            print(f"not running {args.service_name} (pid file missing)")
        else:
            print(f"not running {args.service_name} (stale pid={pid})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stageqsvc")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("start")
    p.add_argument("service_name")
    p.add_argument("--env", default="dev")
    p.set_defaults(func=cmd_start)

    p = sub.add_parser("stop")
    p.add_argument("service_name")
    p.set_defaults(func=cmd_stop)

    p = sub.add_parser("status")
    p.add_argument("service_name")
    p.set_defaults(func=cmd_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()