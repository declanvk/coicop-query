from io import TextIOWrapper
import logging
from .utils import get_coicop_data_path, get_sqlite_conn, unsafe_get_db_path
import sqlite3
import argparse
import os
import csv

LOG = logging.getLogger(__name__)


def run(_args: argparse.Namespace):
    db_path = unsafe_get_db_path()
    LOG.info(f"Initializing database at path [{db_path}]")

    if db_path.exists():
        LOG.info(f"Database already exists at [{db_path}], going to delete")
        os.remove(db_path)

    if not db_path.parent.exists():
        LOG.info(
            f"Database path parent directory [{db_path.parent}] does not exist, creating it."
        )
        db_path.parent.mkdir(parents=True)

    conn = get_sqlite_conn(db_path, LOG.debug, readonly=False)

    with (
        conn,
        get_coicop_data_path() as coicop_path,
        coicop_path.open("r") as coicop_csv_file,
    ):
        create_coicop_categories_table(conn)
        load_categories_into_table(conn, coicop_csv_file)

    conn.close()


def create_coicop_categories_table(conn: sqlite3.Connection):
    conn.execute("""
CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,
    title TEXT,
    intro TEXT,
    includes TEXT,
    alsoIncludes TEXT,
    excludes TEXT,
    level INTEGER DEFAULT NULL
);
""")
    conn.execute("CREATE INDEX category_code_idx ON category (code);")
    conn.execute(
        "CREATE VIRTUAL TABLE category_fts USING fts5(title, intro, includes, alsoIncludes);"
    )
    conn.execute("CREATE VIRTUAL TABLE category_excludes_fts USING fts5(excludes);")


def load_categories_into_table(
    conn: sqlite3.Connection, coicop_csv_file: TextIOWrapper
):
    reader = csv.DictReader(coicop_csv_file)
    rows = list(reader)
    conn.executemany(
        "INSERT INTO category(code, title, intro, includes, alsoIncludes, excludes) VALUES (:code, :title, :intro, :includes, :alsoIncludes, :excludes)",
        rows,
    )
    conn.executemany(
        "INSERT INTO category_fts(title, intro, includes, alsoIncludes) VALUES (:title, :intro, :includes, :alsoIncludes)",
        rows,
    )
    conn.executemany(
        "INSERT INTO category_excludes_fts(excludes) VALUES (:excludes)",
        rows,
    )

    conn.execute(
        "UPDATE category SET level = (LENGTH(code) - LENGTH(REPLACE(code, '.', '')) + 1);"
    )
