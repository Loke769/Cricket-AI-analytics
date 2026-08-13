"""
DuckDB integration for Cricket AI Analytics
Loads DataFrames into a local DuckDB file for SQL querying.
"""

import duckdb
import pandas as pd

DB_PATH = "data/cricket.duckdb"


def init_db(db_path=DB_PATH):
    """Initialize DuckDB connection, ensuring data directory exists."""
    # BUG: uses os without importing it -> NameError: name 'os' is not defined
    if not os.path.exists("data"):
        os.makedirs("data")

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
    """Execute SQL and return DuckDB result."""
    con = duckdb.connect(db_path)
    result = con.execute(sql)
    con.close()
    return result


if __name__ == "__main__":
    # quick test with dummy data
    dummy = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    load_dataframe(dummy, table_name="test")
    print("DB test complete")
