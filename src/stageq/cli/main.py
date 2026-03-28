from __future__ import annotations

import argparse
from pathlib import Path

from stageq.ctl.launcher import launch_service
from stageq.ctl.process import is_pid_running, read_pid, stop_pid
from stageq.ctl.resolver import resolve_service_config


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[3]


def cmd_launch(args) -> None:
    pid = launch_service(_root_dir(), args.service, args.env)
    print(f"launched {args.service} pid={pid}")


def cmd_stop(args) -> None:
    pid_file = _root_dir() / "var" / "run" / f"{args.service}.pid"
    pid = read_pid(pid_file)
    if not pid:
        print(f"{args.service}: no pid file")
        return
    if not is_pid_running(pid):
        print(f"{args.service}: pid file exists but process not running")
        return
    stop_pid(pid)
    print(f"stopped {args.service} pid={pid}")


def cmd_status(args) -> None:
    pid_file = _root_dir() / "var" / "run" / f"{args.service}.pid"
    log_file = _root_dir() / "var" / "log" / f"{args.service}.log"
    cmd_file = _root_dir() / "var" / "generated" / f"{args.service}.cmdline"

    pid = read_pid(pid_file)
    running = bool(pid and is_pid_running(pid))

    print(f"service : {args.service}")
    print(f"pid     : {pid}")
    print(f"running : {running}")
    print(f"log     : {log_file}")
    print(f"cmdline : {cmd_file}")


def cmd_render(args) -> None:
    cfg = resolve_service_config(_root_dir(), args.service, args.env)
    print(f"service   = {cfg.identity.name}")
    print(f"type      = {cfg.identity.service_type}")
    print(f"runtime   = {cfg.identity.runtime}")
    print(f"env       = {cfg.identity.env_name}")
    print(f"bootstrap = {cfg.launch.bootstrap}")
    print(f"q port    = {cfg.q_runtime.port}")
    print(f"threads   = {cfg.q_runtime.secondary_threads}")
    print(f"ticks     = {cfg.q_runtime.timer_ticks}")
    print("libs:")
    for lib in cfg.q.libraries:
        print(f"  - {lib}")
    print("service_config:")
    print(cfg.service_config)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="stageqctl")
    sub = p.add_subparsers(dest="command", required=True)

    p_launch = sub.add_parser("launch")
    p_launch.add_argument("service")
    p_launch.add_argument("--env", default="dev")
    p_launch.set_defaults(func=cmd_launch)

    p_stop = sub.add_parser("stop")
    p_stop.add_argument("service")
    p_stop.set_defaults(func=cmd_stop)

    p_status = sub.add_parser("status")
    p_status.add_argument("service")
    p_status.set_defaults(func=cmd_status)

    p_render = sub.add_parser("render")
    p_render.add_argument("service")
    p_render.add_argument("--env", default="dev")
    p_render.set_defaults(func=cmd_render)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()