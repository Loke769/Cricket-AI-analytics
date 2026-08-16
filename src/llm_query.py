"""
OpenAI text-to-SQL for Cricket AI Analytics
Converts natural language questions into DuckDB SQL with safe prompting and error handling.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def text_to_sql(question: str, schema: str = None) -> str:
    """
    Convert natural language question to DuckDB SQL using OpenAI.
    Fixed: improved system prompt for DuckDB, ensures trailing semicolon, adds timeout handling.
    """
    if schema is None:
        schema = """
        Table: deliveries (
            match_id VARCHAR,
            over_num INTEGER,
            ball_num INTEGER,
            batter VARCHAR,
            bowler VARCHAR,
            runs INTEGER,
            innings INTEGER
        )
        DuckDB SQL dialect. Use standard SELECT queries.
        """

    system_prompt = (
        "You are a DuckDB SQL expert for cricket analytics. "
        "Given the database schema and a natural language question, generate a single valid DuckDB SQL query. "
        "Always end the query with a semicolon. "
        "Return ONLY the SQL, no explanation, no markdown formatting. "
        "Use correct DuckDB syntax (e.g., COUNT, SUM, GROUP BY, WHERE)."
    )

    user_prompt = f"Schema: {schema}\nQuestion: {question}\nSQL:"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            timeout=30,
        )

        sql = response.choices[0].message.content.strip()

        # Clean markdown code fences if model returns them
        if sql.startswith("```"):
            # strip ```sql ... ``` wrapper
            sql = sql.strip("`")
            if sql.lower().startswith("sql"):
                sql = sql[3:].strip()
            sql = sql.strip()

        # FIX: ensure SQL ends with semicolon for consistent DuckDB execution
        if not sql.endswith(";"):
            sql += ";"

        return sql

    except Exception as e:
        err_msg = str(e).lower()
        if "timeout" in err_msg or "timed out" in err_msg:
            raise TimeoutError(f"OpenAI API timeout after 30s: {e}") from e
        if "api_key" in err_msg or "authentication" in err_msg:
            raise RuntimeError(f"OpenAI authentication error - check OPENAI_API_KEY: {e}") from e
        raise RuntimeError(f"OpenAI API error: {e}") from e


if __name__ == "__main__":
    q = "How many runs did Virat Kohli score?"
    try:
        sql = text_to_sql(q)
        print(f"Question: {q}")
        print(f"SQL: {sql}")
    except Exception as ex:
        print(f"Error: {ex}")
