"""
CLI for Cricket AI Analytics - No-AI / Manual SQL mode
Runs DuckDB queries without needing OpenAI API key.
Use this when you want to test the pipeline locally without AI.
"""

import duckdb
from database import DB_PATH

# Hardcode any SQL you want - no AI needed
# Example: Top 5 batters by total runs
sql = "SELECT batter, SUM(runs) AS total_runs FROM deliveries GROUP BY batter ORDER BY total_runs DESC LIMIT 5;"

# Other examples you can try (uncomment one):
# sql = "SELECT bowler, COUNT(*) AS balls_bowled FROM deliveries GROUP BY bowler ORDER BY balls_bowled DESC LIMIT 5;"
# sql = "SELECT over_num, AVG(runs) AS avg_runs FROM deliveries GROUP BY over_num ORDER BY over_num;"
# sql = "SELECT * FROM deliveries LIMIT 10;"

def main():
    print(f"SQL: {sql}\n")
    con = duckdb.connect(DB_PATH)
    try:
        df = con.execute(sql).fetchdf()
        if df.empty:
            print("No results found.")
        else:
            print(df.to_string(index=False))
            print(f"\n{len(df)} rows returned.")
    except Exception as e:
        print(f"Query error: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    main()
