from pathlib import Path
from typing import Callable, ContextManager
import importlib.resources
import sqlite3
import logging

from . import resources


LOG = logging.getLogger(__name__)


def get_db_path() -> ContextManager[Path]:
    if importlib.resources.is_resource(resources, "db.sqlite"):
        return importlib.resources.path(resources, "db.sqlite")
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
