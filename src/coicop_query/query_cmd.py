import logging
import argparse
from .utils import (
    NON_PRINTED_CATEGORY_COLUMNS,
    PRINT_MANDATORY_CATEGORY_COLUMNS,
    get_db_path,
    get_sqlite_conn,
    print_many_coicop_categories,
    CATEGORY_COLUMNS,
)

LOG = logging.getLogger(__name__)


def args(subcommands: argparse._SubParsersAction):
    query_parser = subcommands.add_parser(
        "query",
        help="query COICOP category via database full-text search",
        description=f"""Query COICOP category via database full-text search. 
        The set of columns that are available for sort are {sorted(CATEGORY_COLUMNS)}. 
        The same set of columns are available for select, but only the following columns 
        will be printed: {sorted(CATEGORY_COLUMNS - NON_PRINTED_CATEGORY_COLUMNS)}""",
    )
    assert isinstance(query_parser, argparse.ArgumentParser)
    query_parser.add_argument(
        "--select",
        type=str,
        help="Comma separated list of columns to return from query",
    )
    query_parser.add_argument(
        "--max-level",
        type=int,
        help="Maximum level nesting level of COICOP categories to return from query",
    )
    query_parser.add_argument(
        "--min-level",
        type=int,
        help="Minimum level nesting level of COICOP categories to return from query",
    )
    query_parser.add_argument(
        "--limit",
        type=int,
        help="Limit on number of results return from query",
    )
    query_parser.add_argument(
        "--sort",
        type=str,
        help="Comma-separated list of columns to sort results. Default ordering is ascending, \
            but can be overridden by adding a string ':ASC|DESC' with explicit ordering after \
            the column name. Example would be 'title:ASC,code:DESC' to sort first by title \
            ascending and then by code descending.",
    )
    query_parser.add_argument("query")


def run(args: argparse.Namespace):
    with get_db_path() as db_path:
        conn = get_sqlite_conn(db_path, LOG.info, readonly=True)
        query = build_query(args)
        LOG.info(f"Complete query [{query}]")

        with conn:
            cur = conn.execute(query)
            results = cur.fetchall()
            assert isinstance(results, list)
            print_many_coicop_categories(results)
        conn.close()


def build_query(args: argparse.Namespace) -> str:
    required_columns = {*PRINT_MANDATORY_CATEGORY_COLUMNS}
    fts_query = build_fts_query(args)
    where_clauses = [
        f"id IN (SELECT rowid FROM category_fts WHERE category_fts MATCH {fts_query})"
    ]
    if args.max_level is not None:
        where_clauses.append(f"level <= {args.max_level}")
    if args.min_level is not None:
        where_clauses.append(f"level >= {args.min_level}")

    if args.limit:
        limit = f"LIMIT {args.limit}"
    else:
        limit = ""

    sort = build_sort_clause(args)

    if args.select:
        column_names = validate_column_names(args.select, required_columns)
        select = column_names
    else:
        select = "*"

    return f"SELECT {select} FROM category WHERE {' AND '.join(where_clauses)} {sort} {limit};"


def validate_column_names(select: str, required_columns: set[str]) -> str:
    columns = set(select.split(","))
    assert isinstance(columns, set)
    if not columns.issubset(CATEGORY_COLUMNS):
        raise Exception(
            f"'--select' argument referenced unknown column name(s) {columns - CATEGORY_COLUMNS}"
        )

    if not required_columns.issubset(columns):
        columns.update(required_columns)
    return ", ".join(columns)


def build_fts_query(args: argparse.Namespace) -> str:
    """Create the FTS query by adding single quotes around the CLI input.

    This procedure is vulnerable to SQL injection, but the impact is limited, the user is only breaking their own installed software."""
    return f"'{args.query.strip("'")}'"


def build_sort_clause(args: argparse.Namespace) -> str:
    if not args.sort:
        return ""

    sort_columns = dict()
    for column in args.sort.split(","):
        if ":" in column:
            (name, order) = column.split(":")
        else:
            name = column
            order = "ASC"

        if name not in CATEGORY_COLUMNS:
            raise Exception(f"Unknown column name [{name}] in sort argument")
        if order.upper() not in {"ASC", "DESC"}:
            raise Exception(f"Unknown column order [{order}] in sort argument")

        sort_columns[name] = order

    return (
        f"ORDER BY {', '.join(f'{name} {sort_columns[name]}' for name in sort_columns)}"
    )
