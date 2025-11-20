from pathlib import Path
from typing import Callable, ContextManager
import importlib.resources
import sqlite3
import logging
import functools
import shutil
import textwrap

from . import resources


LOG = logging.getLogger(__name__)


DATABASE_FILE_NAME = "db.sqlite"


def unsafe_get_db_path() -> Path:
    return Path(__file__).parent / "resources" / DATABASE_FILE_NAME


def get_db_path() -> ContextManager[Path]:
    if importlib.resources.is_resource(resources, DATABASE_FILE_NAME):
        return importlib.resources.path(resources, DATABASE_FILE_NAME)
    else:
        raise Exception(
            "Database resource missing from package. Need to bake data prior to using package, see README.md"
        )


def get_sqlite_conn(
    db_path: Path,
    trace_callback: Callable[[str], object] | None,
    readonly: bool = False,
) -> sqlite3.Connection:
    LOG.info(f"Using database at [{db_path}] with readonly [{readonly}]")
    if readonly:
        db_uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(db_uri, uri=True)
    else:
        conn = sqlite3.connect(db_path)

    conn.set_trace_callback(trace_callback)
    conn.row_factory = sqlite3.Row
    return conn


def get_coicop_data_path() -> ContextManager[Path]:
    return importlib.resources.path(resources, "coicop-2018-structure.csv")


CATEGORY_COLUMNS = {
    "id",
    "code",
    "title",
    "intro",
    "includes",
    "alsoIncludes",
    "excludes",
    "level",
}
PRINT_MANDATORY_CATEGORY_COLUMNS = {
    "code",
    "title",
}
assert PRINT_MANDATORY_CATEGORY_COLUMNS.issubset(CATEGORY_COLUMNS)
NON_PRINTED_CATEGORY_COLUMNS = {"level", "id"}
assert NON_PRINTED_CATEGORY_COLUMNS.issubset(CATEGORY_COLUMNS)


def print_many_coicop_categories(rows: list[sqlite3.Row]):
    if len(rows) == 0:
        return

    # Assuming all the same columns in this list
    LOG.info(f"Raw rows {rows}")

    present_columns = functools.reduce(
        lambda a, b: a | b,
        (
            {
                key
                for key in row.keys()
                if (not isinstance(row[key], str)) or len(row[key]) != 0
            }
            for row in rows
        ),
    )
    LOG.info(f"Present columns {present_columns}")
    if not PRINT_MANDATORY_CATEGORY_COLUMNS.issubset(present_columns):
        raise Exception(
            f"Missing some print mandatory columns from query: {PRINT_MANDATORY_CATEGORY_COLUMNS - present_columns}"
        )

    needs_separator = True
    if PRINT_MANDATORY_CATEGORY_COLUMNS == (
        present_columns - NON_PRINTED_CATEGORY_COLUMNS
    ):
        needs_separator = False

    is_first = True
    for row in rows:
        if not is_first and needs_separator:
            print()
        if needs_separator:
            print_horizontal_rule(char="=")

        print_coicop_category(row)
        is_first = False


def print_horizontal_rule(char="-"):
    width = get_terminal_width()
    print(char * width)


def print_coicop_category(row: sqlite3.Row) -> bool:
    width = get_terminal_width()
    LOG.debug(f"Raw row {dict(row)}")
    left_column = 14
    indent = left_column + 3
    print(f"{{:>{left_column}}} - {{}}".format(row["code"], row["title"]))
    if "intro" in row.keys() and len(row["intro"]) != 0:
        print_section("Intro", row["intro"], width, indent)
    if "includes" in row.keys() and len(row["includes"]) != 0:
        print_list_section("Includes", row["includes"], width, indent)
    if "alsoIncludes" in row.keys() and len(row["alsoIncludes"]) != 0:
        print_list_section("Also Includes", row["alsoIncludes"], width, indent)
    if "excludes" in row.keys() and len(row["excludes"]) != 0:
        print_list_section("Excludes", row["excludes"], width, indent)


def print_section(section_title, section_text, width, indent):
    section_header = f"{section_title} - "
    print_horizontal_rule()
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
    print_horizontal_rule()

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


@functools.lru_cache(maxsize=1)
def get_terminal_width() -> int:
    return shutil.get_terminal_size().columns
