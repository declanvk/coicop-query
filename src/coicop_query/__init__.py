import argparse
import logging
import sys

from . import bake_cmd
from . import get_cmd
from . import query_cmd
from .exceptions import CoicopQueryError

LOG = logging.getLogger(__name__)


def bake() -> None:
    parser = argparse.ArgumentParser(
        "Tool for baking COICOP category data into the `coicop-query` package"
    )
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    init_logging(args.verbose)
    LOG.info(args)

    bake_cmd.run(args)


def main() -> None:
    parser = argparse.ArgumentParser("Tool for querying COICOP categories")
    parser.add_argument("--verbose", action="store_true")
    subcommands = parser.add_subparsers(required=True, dest="command")
    get_cmd.args(subcommands)
    query_cmd.args(subcommands)

    args = parser.parse_args()

    init_logging(args.verbose)

    LOG.info(args)

    try:
        if args.command == "get":
            get_cmd.run(args)
        elif args.command == "query":
            query_cmd.run(args)
        else:
            raise CoicopQueryError(f"Unrecognized subcommand [{args.command}]")
    except CoicopQueryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def init_logging(verbose: bool):
    LOG.setLevel(logging.INFO)

    # Console logging
    ch = logging.StreamHandler()
    if verbose:
        ch.setLevel(logging.INFO)
    else:
        ch.setLevel(logging.WARNING)

    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    LOG.addHandler(ch)
