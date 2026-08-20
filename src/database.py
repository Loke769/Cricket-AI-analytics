"""
DuckDB integration for Cricket AI Analytics
Loads DataFrames into a local DuckDB file for SQL querying.
"""

import os
import duckdb
import pandas as pd

DB_PATH = "data/cricket.duckdb"


def init_db(db_path=DB_PATH):
    """Initialize DuckDB connection, ensuring data directory exists."""
    # FIX: added missing import os; create data/ dir if missing
    if not os.path.exists("data"):
        os.makedirs("data", exist_ok=True)
    # ensure parent directory for db_path exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    con = duckdb.connect(db_path)
    return con


def load_dataframe(df, table_name="deliveries", db_path=DB_PATH):
    """Load a DataFrame into DuckDB as a table."""
    con = init_db(db_path)
    # Replace table if exists
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
    print(f"Loaded {len(df)} rows into {table_name} at {db_path}")
    con.close()
    return db_path


def query_db(sql, db_path=DB_PATH):
    """Execute SQL and return results as DataFrame."""
    con = duckdb.connect(db_path)
    df = con.execute(sql).fetchdf()
    con.close()
    return df


if __name__ == "__main__":
    # quick test with dummy data
    dummy = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    load_dataframe(dummy, table_name="test")
    print("DB test complete")
    print(query_db("SELECT * FROM test;"))
