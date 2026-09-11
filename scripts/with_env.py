# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Execute an argument vector with the selected local environment, without shell evaluation."""
import argparse
from runtime import environment, run
parser = argparse.ArgumentParser()
parser.add_argument("--env-file")
parser.add_argument("command", nargs=argparse.REMAINDER)
args = parser.parse_args()
command = args.command[1:] if args.command[:1] == ["--"] else args.command
if not command:
    parser.error("a command is required")
try:
    run(command, env=environment(args.env_file))
except Exception as exc:
    print(f"Environment command failed: {type(exc).__name__}", flush=True)
    raise SystemExit(1)

