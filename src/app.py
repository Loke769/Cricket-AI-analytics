"""
CLI for Cricket AI Analytics
Natural language cricket queries -> OpenAI SQL -> DuckDB -> clean table output
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
    try:
        sql = text_to_sql(args.question)
    except Exception as e:
        print(f"Error generating SQL: {e}")
        return

    print(f"Generated SQL: {sql}")

    con = duckdb.connect(args.db)
    try:
        # FIX: use fetchall()/fetchdf() and pandas to print a clean table
        # Previously just printed the DuckDB result object reference
        df = con.execute(sql).fetchdf()
        if df.empty:
            print("No results found.")
        else:
            # Clean tabular display without index
            print("\nResult:")
            print(df.to_string(index=False))
            print(f"\n{len(df)} rows returned.")

            # Also show fetchall fallback example:
            # rows = con.execute(sql).fetchall()
            # cols = [desc[0] for desc in con.description]
            # for row in rows:
            #     print(dict(zip(cols, row)))

    except Exception as e:
        print(f"Query execution error: {e}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
