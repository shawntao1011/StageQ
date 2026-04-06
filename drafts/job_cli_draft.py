from __future__ import annotations

import argparse
from pathlib import Path


def _root_dir() -> Path:
    return Path(__file__).resolve().parents[3]


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------
def cmd_run(args: argparse.Namespace) -> None:
    """
    Run a job (placeholder).

    Next step：
      - job_resolver
      - job_runner
    """
    try:
        from stageq.ctl.job_runner import run_job
    except ModuleNotFoundError:
        print("[TODO] job runner not implemented")
        return

    result = run_job(
        root_dir=_root_dir(),
        job_name=args.job_name,
        env_name=args.env,
        run_id=args.run_id,
    )
    print(result)


def cmd_status(args: argparse.Namespace) -> None:
    """
    Job status (placeholder).

    Next Step：
      - local run records
      - airflow state
      - db tracking
    """
    print(f"[TODO] job status not implemented: {args.job_name} ({args.run_id})")


# -----------------------------------------------------------------------------
# Parser
# -----------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stageqjob")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # run
    p = sub.add_parser("run")
    p.add_argument("job_name")
    p.add_argument("--env", default="dev")
    p.add_argument("--run-id", required=True)
    p.set_defaults(func=cmd_run)

    # status
    p = sub.add_parser("status")
    p.add_argument("job_name")
    p.add_argument("--run-id", required=True)
    p.set_defaults(func=cmd_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()