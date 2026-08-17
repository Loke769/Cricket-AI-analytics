"""
CLI for Cricket AI Analytics
Natural language cricket queries -> OpenAI SQL -> DuckDB -> results
"""

import argparse
import duckdb
from llm_query import text_to_sql
from database import DB_PATH


def main():
    parser = argparse.ArgumentParser(description="Cricket AI Analytics - Natural language to SQL")
    parser.add_argument("question", type=str, help="Natural language question about cricket data")
    parser.add_argument("--db", type=str, default=DB_PATH, help="Path to DuckDB file")
    args = parser.parse_args()

    print(f"Question: {args.question}")
    sql = text_to_sql(args.question)
    print(f"Generated SQL: {sql}")

    con = duckdb.connect(args.db)
    result = con.execute(sql)

    # BUG: prints DuckDB result object instead of actual rows
    # User sees something like "<duckdb.duckdb.DuckDBPyConnection object ...>"
    # instead of a clean table
    print("Result:")
    print(result)

    con.close()


if __name__ == "__main__":
    main()
