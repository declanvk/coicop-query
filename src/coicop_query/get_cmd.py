import argparse
from functools import lru_cache
import logging
import sqlite3
import shutil
import textwrap

from .utils import get_sqlite_conn, get_db_path

LOG = logging.getLogger(__name__)


def args(subcommands: argparse._SubParsersAction):
    get_parser = subcommands.add_parser("get", help="lookup COICOP category by code")
    get_parser.add_argument("code")


def run(args: argparse.Namespace):
    with get_db_path() as db_path:
        conn = get_sqlite_conn(db_path, LOG.info, readonly=True)

        with conn:
            cur = conn.execute("SELECT * FROM category WHERE code = ?;", (args.code,))
            results = cur.fetchall()
            if len(results) == 0:
                raise Exception(f"No category found for code [{args.code}]")
            for row in results:
                print_coicop_category(row)

        conn.close()


def print_coicop_category(row: sqlite3.Row):
    width = get_terminal_width()
    LOG.info(f"Raw row {dict(row)}")
    left_column = 14
    indent = left_column + 3
    print(f"{{:>{left_column}}} - {{}}".format(row["code"], row["title"]))
    if len(row["intro"]) != 0:
        print_section("Intro", row["intro"], width, indent)
    if len(row["includes"]) != 0:
        print_list_section("Includes", row["includes"], width, indent)
    if len(row["alsoIncludes"]) != 0:
        print_list_section("Also Includes", row["alsoIncludes"], width, indent)
    if len(row["excludes"]) != 0:
        print_list_section("Excludes", row["excludes"], width, indent)


def print_section(section_title, section_text, width, indent):
    section_header = f"{section_title} - "
    print("-" * width)
    print(
        textwrap.fill(
            section_text,
            width=width,
            initial_indent=(" " * (indent - len(section_header)) + section_header),
            subsequent_indent=" " * indent,
        )
    )


def print_list_section(section_title, section_text, width, indent):
    section_header = f"{section_title} "
    print("-" * width)

    is_first = True
    subsequent_indent = " " * indent
    for line in section_text.splitlines():
        if is_first and not line.startswith("* "):
            initial_indent = " " * (indent - len(section_header) - 2) + (
                section_header + "- "
            )

        elif is_first:
            initial_indent = " " * (indent - len(section_header) - 2) + section_header
        else:
            initial_indent = " " * (indent - 2)

        print(
            textwrap.fill(
                line,
                width=width,
                initial_indent=initial_indent,
                subsequent_indent=subsequent_indent,
            )
        )
        is_first = False


@lru_cache(maxsize=1)
def get_terminal_width() -> int:
    return shutil.get_terminal_size().columns
