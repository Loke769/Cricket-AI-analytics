"""
OpenAI text-to-SQL for Cricket AI Analytics
Converts natural language questions into DuckDB SQL.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def text_to_sql(question: str, schema: str = None) -> str:
    """
    Convert natural language question to SQL using OpenAI.
    Bug: poor prompt - no DuckDB dialect hint, SQL missing trailing semicolon
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
        """

    # BUG: very minimal prompt, no system role, no semicolon enforcement
    prompt = f"Schema: {schema}\nQuestion: {question}\nGenerate SQL:"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    sql = response.choices[0].message.content.strip()
    # BUG: strip semicolons -> generated SQL will be missing trailing semicolon
    # e.g. "SELECT * FROM deliveries WHERE batter = 'Virat Kohli'" (no ;)
    sql = sql.replace(";", "").strip()
    # Remove markdown fences if present but still no semicolon
    if sql.startswith("```"):
        sql = sql.strip("`").replace("sql", "", 1).strip()

    return sql


if __name__ == "__main__":
    q = "How many runs did Virat Kohli score?"
    print(text_to_sql(q))
