# Cricket AI Analytics

End-to-end AI-powered cricket analytics pipeline — downloads ball-by-ball data from **Cricsheet**, loads it into **DuckDB**, uses the **OpenAI SDK** to turn natural-language questions into SQL, and serves results through a clean **CLI**.

Built as a realistic 10-day iterative project demonstrating data ingestion, SQL generation, and database integration with intentional bug-fix storytelling.

## What It Does

- **Ingests Cricsheet data**: Downloads `all_json.zip` (or CSV) from Cricsheet, extracts JSON ball-by-ball files, and parses them into a pandas DataFrame.
- **Handles cricket overs correctly**: Cricsheet uses decimal overs like `1.1` (over 1, ball 1) — the pipeline splits `over` into `over_num` / `ball_num` using `pandas.str.split`.
- **Loads into DuckDB**: Creates a local `data/cricket.duckdb` file and loads the DataFrame as a `deliveries` table for fast analytical SQL.
- **Natural Language → SQL**: Uses `openai` (gpt-4o-mini) with a DuckDB-aware system prompt to generate valid SQL that always ends with `;` and handles timeouts/auth errors gracefully.
- **CLI**: Ask questions like _"How many runs did Virat Kohli score?"_ and get a formatted table back via `python src/app.py`.

## Architecture

```
Cricsheet (all_json.zip) → src/ingest.py → pandas DataFrame → src/database.py → DuckDB (data/cricket.duckdb)
                                                                ↑
Natural Language Question → src/llm_query.py (OpenAI) → SQL ────┘
                                                                ↓
                                                        src/app.py (CLI) → fetchdf() / fetchall() → pretty table
```

## Project Structure

```
.
├── src/
│   ├── ingest.py      # download + parse Cricsheet data, fix decimal over parsing
│   ├── database.py    # DuckDB integration, handles data/ creation, import os fix
│   ├── llm_query.py   # OpenAI text-to-SQL, improved prompts + timeout handling
│   └── app.py         # CLI, runs SQL and prints clean tables
├── requirements.txt
├── .env.example
├── data/              # created at runtime (gitignored)
│   ├── raw/           # extracted JSONs
│   └── cricket.duckdb
└── README.md
```

## Setup Guide

### 1. Prerequisites

- Python 3.10+
- An OpenAI API key

### 2. Clone and Install

```bash
git clone https://github.com/Loke769/Loke769-Cricket-AI-analytics.git
cd Loke769-Cricket-AI-analytics

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Environment

```bash
cp .env.example .env
# edit .env and set your key
# OPENAI_API_KEY=sk-proj-...
```

### 4. Run the Pipeline

```bash
# 1. Download and parse Cricsheet data (~20 files sampled for dev)
python src/ingest.py

# 2. Load into DuckDB (also tested via src/database.py directly)
python -c "import src.ingest as i, src.database as db; df=i.load_matches_to_dataframe(); db.load_dataframe(df)"

# 3. Ask a natural language question
python src/app.py "How many runs did Virat Kohli score?"

# Or specify a custom DB path
python src/app.py "Top 5 batters by total runs" --db data/cricket.duckdb
```

### 5. Manual DuckDB Check

```bash
python -c "import duckdb; print(duckdb.connect('data/cricket.duckdb').execute('SELECT batter, SUM(runs) AS total_runs FROM deliveries GROUP BY batter ORDER BY total_runs DESC LIMIT 5;').fetchdf().to_string(index=False))"
```

## Example: Natural Language → SQL → Result

**Question:**

```
How many runs did Virat Kohli score in all matches?
```

**Generated SQL (via OpenAI):**

```sql
SELECT batter, SUM(runs) AS total_runs
FROM deliveries
WHERE batter = 'V Kohli'
GROUP BY batter;
```

**CLI Output:**

```
Question: How many runs did Virat Kohli score in all matches?
Generated SQL: SELECT batter, SUM(runs) AS total_runs FROM deliveries WHERE batter = 'V Kohli' GROUP BY batter;

Result:
 batter  total_runs
V Kohli         973
1 rows returned.
```

**Other examples:**

- _"Top 5 bowlers by wickets"_ → `SELECT bowler, COUNT(*) AS wickets FROM deliveries WHERE wicket = true GROUP BY bowler ORDER BY wickets DESC LIMIT 5;`
- _"Average runs per over in innings 1"_ → `SELECT over_num, AVG(runs) AS avg_runs FROM deliveries WHERE innings = 1 GROUP BY over_num ORDER BY over_num;`

## Technologies

- **pandas** – DataFrame parsing and decimal over handling (`str.split(".", expand=True)`)
- **duckdb** – Local analytical DB (`data/cricket.duckdb`)
- **openai** – ChatCompletions API (`gpt-4o-mini`, system prompt for DuckDB, 30s timeout)
- **requests** – Cricsheet download
- **python-dotenv** – `.env` loading

## Troubleshooting

- `ValueError: invalid literal for int() with base 10: '1.1'` → fixed in `ingest.py` by splitting overs/balls.
- `NameError: name 'os' is not defined` → fixed by adding `import os` in `database.py`.
- SQL missing `;` → fixed via prompt that enforces trailing semicolon.
- `print(result)` shows object reference → fixed by using `.fetchall()` / `.fetchdf()` and `to_string(index=False)`.

## License

MIT
