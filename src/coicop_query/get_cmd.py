import argparse
import logging
from .utils import get_sqlite_conn, get_db_path, print_coicop_category

LOG = logging.getLogger(__name__)


def args(subcommands: argparse._SubParsersAction):
    get_parser = subcommands.add_parser(
        "get",
        help="lookup COICOP category by code",
        description="Lookup COICOP category by code.",
    )
    get_parser.add_argument("code")


def run(args: argparse.Namespace):
    with get_db_path() as db_path:
        conn = get_sqlite_conn(db_path, LOG.info, readonly=True)

        with conn:
            cur = conn.execute("SELECT * FROM category WHERE code = ?;", (args.code,))
            result = cur.fetchone()
            if result is None:
                raise Exception(f"No category found for code [{args.code}]")
            print_coicop_category(result)

        conn.close()
