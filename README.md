# Building a Scalable Data Pipeline for Reddit Data (PySpark + Databricks)

Design and implement a full data pipeline to ingest, process, and analyze Reddit data using a Python API wrapper, PySpark, and Databricks. The pipeline handles scalable batch processing of Reddit posts and comments from a selected subreddit and provides data cleaning, profiling, and basic analytics.

> **Repo:** `yousef526/Building-a-Scalable-Data-Pipeline-for-Reddit-Data-using-PySpark-and-Databricks`  
> **Core stack:** Python, PRAW (or API wrapper), PySpark, Databricks/Delta

---

## 📂 Repository Structure

```
.
├── api_ingestion.py
├── Data_cleaning_&_ETL.ipynb
├── ETL of postsReddit using pySpark 3 NER only without NLP.ipynb
└── README.md   ← (this file)
```

> If you add new notebooks or modules (e.g., `utils/`, `configs/`), this README can be extended with the same pattern.

---

## 🔧 What Each File Does

### `api_ingestion.py`
Purpose: **Extract raw Reddit data** (posts and, optionally, comments) from a specified subreddit and persist it in a “raw” layer (CSV/JSON/Parquet or a Databricks/DBFS path) for downstream ETL.

Typical responsibilities:
- Authenticate to Reddit via environment variables or a local `.env` (e.g., `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`).
- Read a target subreddit (and optional time/window parameters or limits).
- Normalize core fields (e.g., `id`, `title`, `selftext`, `author`, `score`, `num_comments`, `created_utc`, `url`, `subreddit`).
- Optionally fetch top-level **comments** tied to the collected posts.
- Write raw outputs to a filesystem location that downstream notebooks expect (e.g., `data/raw/` or `dbfs:/FileStore/raw/`).

> **Run locally (example):**
```bash
# 1) Set credentials in your shell or .env
export REDDIT_CLIENT_ID=xxxxx
export REDDIT_CLIENT_SECRET=xxxxx
export REDDIT_USER_AGENT="reddit-ingestion-script"

# 2) Install deps
pip install praw pandas python-dotenv geonnamecache unicode

# 3) Execute
python api_ingestion.py --subreddit travel --limit 500 --out data/raw/
```

> **Run on Databricks (example):**
- Upload `api_ingestion.py` (or copy cells into a notebook).
- Configure cluster environment variables with your Reddit credentials.
- Use `dbutils.widgets` or args for `subreddit`, `limit`, and output path.
- Save to `dbfs:/.../raw/` for downstream ETL.

---

### `Data_cleaning_&_ETL.ipynb`
Purpose: **Bronze → Silver ETL** in PySpark: load the raw dump created by `api_ingestion.py`, enforce schema, cleanse records, and write optimized tables for analysis.

What it typically covers:
- **Load & schema:** Read raw JSON/CSV from local or DBFS, define explicit schema (types for timestamps, integers, strings).
- **Cleansing:** handle nulls, trim whitespace, drop duplicates on post IDs, cast numerics, standardize timestamps (`created_utc` → `timestamp`).
- **Normalization:** select/rename columns, flatten nested fields, and explode arrays.
- **Outputs:** write **Delta/Parquet** to a managed “silver” path or as managed tables in Databricks for downstream analytics.
- **Basic profiling:** quick counts, top comments in travel subreddits and which comments have highest scores.

> **Run outline (Databricks):**
1. Attach to a cluster with **Spark 3.x** and Delta.
2. Set `raw_path` (e.g., `dbfs:/FileStore/raw/`) and `silver_path` (e.g., `dbfs:/FileStore/silver/`).
3. Execute cells to read, clean, and write Delta tables.

---

### `ETL of postsReddit using pySpark 3 NER only without NLP.ipynb`
Purpose: **Lightweight Named-Entity Extraction step** over cleaned posts (titles/bodies) to surface entities like **locations (GPE), orgs, people** and store results for analysis.

What it typically covers:
- **Input:** the **silver** posts dataset from the previous notebook.
- **Entity extraction:** a simple NER pass (e.g., spaCy or rule-based/regex extraction) to tag mentions like countries/cities.
- **Post-processing:** de‑dupe entities per post, standardize casing, and filter noisy tokens (punctuation, 1‑char tokens).
- **Outputs:** write an enriched “gold-ish” table (e.g., `posts_entities`) keyed by `post_id` with extracted entities and counts.

> Notes:
- If you use **spaCy**, make sure the cluster/node has the model installed (e.g., `en_core_web_sm`).  
- If you opt for pure PySpark/regex heuristics, document the patterns and limitations in notebook markdown cells.

---

## 🚀 Quickstart (End‑to‑End)

1. **Ingest raw data**
   - Configure Reddit credentials (env variables or Databricks secrets).
   - Run `api_ingestion.py` to pull posts (and optionally top-level comments) for your target subreddit.
   - Validate that files landed in `raw` (local or DBFS).

2. **Clean & model (Bronze → Silver)**
   - Open `Data_cleaning_&_ETL.ipynb` in Databricks.
   - Point it to your `raw` input path and run all cells.
   - Confirm Delta/Parquet outputs and tables are created (Silver).

3. **Enrich with entities (NER)**
   - Open `ETL of postsReddit using pySpark 3 NER only without NLP.ipynb`.
   - Point to the Silver posts path/table and run all cells.
   - Persist the enriched output for downstream analytics.

4. **Analyze**
   - Use Spark SQL or notebooks to answer questions like:
     - Which are most visited places according to comments?
     - What are top 10 visited **countries** in a r/travel subreddit?
     - What are lowest 10 visited **countries** in a r/travel subreddit?
     - what are the highest scores in the subbreddit? .

---

## 🛠️ Requirements

- **Python 3.9+**
- **PySpark 3.x**, Delta Lake (Databricks or local Spark with delta packages)
- **PRAW** (or another Reddit API wrapper)
- **pandas**, **pyarrow** (for conversions), **python-dotenv** (optional)
- **GeonumCaches**  if you perform NER to find countries names
  ```bash
  pip install geonamescache unidecode
  ```

> On **Databricks**, set up cluster with:
- A recent **runtime** supporting Spark 3.x and Delta.
- **Environment variables** (or Databricks Secrets) for Reddit credentials.
- A workspace path for raw/silver/gold

---

## 🗃️ Data Layout (Example)

```
/raw/
  posts_YYYYMMDD.json
  comments_YYYYMMDD.json

/silver/
  posts/            (Delta/Parquet)
  comments/         (Delta/Parquet)

/gold/
  posts_entities/   (enriched with NER results)
```

You can adapt the folder structure to the **medallion** model (Bronze/Silver/Gold) depending on your preferences.

---

## ❓ Troubleshooting

- **Null timestamps after casting**: ensure `created_utc` is seconds (not ms) before converting; use `to_timestamp(col / 1)` or divide ms by `1000.0`.
- **Schema drift**: explicitly define the schema in Spark to avoid column shifting when CSVs contain commas/quotes in text.
- **Rate limits**: if using the live Reddit API, consider backoff/retries and respectful `limit` sizes.

---

## Findings on Travel subreddit

- ![Top countries visit](https://github.com/yousef526/Building-a-Scalable-Data-Pipeline-for-Reddit-Data-using-PySpark-and-Databricks/blob/main/top_10_visited_countries.png)
  
- ![Lowest countries visit](https://github.com/yousef526/Building-a-Scalable-Data-Pipeline-for-Reddit-Data-using-PySpark-and-Databricks/blob/main/Lowest%2010%20visited%20countries.png)
  
- ![Top scores for countries visit](https://github.com/yousef526/Building-a-Scalable-Data-Pipeline-for-Reddit-Data-using-PySpark-and-Databricks/blob/main/Top%2010%20scores%20about%20countries.png)

---


## 🙌 Acknowledgements

- Reddit API and the open-source community behind PRAW.
- Databricks & Apache Spark ecosystems.
- Contributors and reviewers of this project.

---

### Maintainer

- **GitHub:** @yousef526

If anything in this README doesn’t match the latest code/notebook behavior, update the corresponding section and push a refreshed version.
