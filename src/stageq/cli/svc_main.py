from __future__ import annotations

import argparse
from pathlib import Path

def _root_dir() -> Path:
    return Path(__file__).resolve().parents[3]


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------
def cmd_launch(args: argparse.Namespace) -> None:
    from stageq.ctl.launcher import launch_service

    pid = launch_service(
        root_dir=_root_dir(),
        service_name=args.service_name,
        env_name=args.env,
    )
    print(f"[OK] launched {args.service_name} pid={pid}")


def cmd_stop(args: argparse.Namespace) -> None:
    from stageq.ctl.process import read_pid, is_pid_running, stop_pid

    pid_file = _root_dir() / "var" / "run" / f"{args.service_name}.pid"
    pid = read_pid(pid_file)

    if not pid:
        print(f"[WARN] {args.service_name} not running (no pid file)")
        return

    if not is_pid_running(pid):
        print(f"[WARN] {args.service_name} pid exists but not running")
        return

    stop_pid(pid)
    print(f"[OK] stopped {args.service_name} pid={pid}")


def cmd_status(args: argparse.Namespace) -> None:
    from stageq.ctl.process import read_pid, is_pid_running

    root = _root_dir()
    pid_file = root / "var" / "run" / f"{args.service_name}.pid"
    log_file = root / "var" / "log" / f"{args.service_name}.log"

    pid = read_pid(pid_file)
    running = bool(pid and is_pid_running(pid))

    print(f"service : {args.service_name}")
    print(f"pid     : {pid}")
    print(f"running : {running}")
    print(f"log     : {log_file}")


def cmd_render(args: argparse.Namespace) -> None:
    from stageq.ctl.resolver import resolve_service_config

    cfg = resolve_service_config(
        root_dir=_root_dir(),
        service_name=args.service_name,
        env_name=args.env,
    )
    cfg.validate()

    print(f"service      = {cfg.identity.name}")
    print(f"type         = {cfg.identity.service_type}")
    print(f"env          = {cfg.identity.env_name}")
    print(f"instance_id  = {cfg.identity.instance_id}")
    print(f"runtime_kind = {cfg.runtime_kind}")

    if cfg.runtime_kind == "q" and cfg.q_runtime:
        print("q runtime:")
        print(f"  bootstrap  = {cfg.q_runtime.bootstrap}")
        print(f"  port       = {cfg.q_runtime.options.port}")
        print("  libraries:")
        for lib in cfg.q_runtime.libraries:
            print(f"    - {lib}")

    print("service_config:")
    print(cfg.service_config)


# -----------------------------------------------------------------------------
# Parser
# -----------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stageqsvc")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # launch
    p = sub.add_parser("launch")
    p.add_argument("service_name")
    p.add_argument("--env", default="dev")
    p.set_defaults(func=cmd_launch)

    # stop
    p = sub.add_parser("stop")
    p.add_argument("service_name")
    p.set_defaults(func=cmd_stop)

    # status
    p = sub.add_parser("status")
    p.add_argument("service_name")
    p.set_defaults(func=cmd_status)

    # render
    p = sub.add_parser("render")
    p.add_argument("service_name")
    p.add_argument("--env", default="dev")
    p.set_defaults(func=cmd_render)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()