"""
Load jobs from SQLite -> strip HTML -> embed -> store in ChromaDB.
Run once to build the index, then re-run any time to pick up new jobs.

Usage:
    python ingest.py
"""
import sqlite3
import re
from config import DB_PATH, CHROMA_DIR, COLLECTION, MAX_INGEST, DESC_CHARS

import chromadb

try:
    from bs4 import BeautifulSoup
    def strip_html(text: str) -> str:
        if not text or "<" not in text:
            return text or ""
        return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
except ImportError:
    def strip_html(text: str) -> str:
        return re.sub(r"<[^>]+>", " ", text or "")


def load_jobs() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT id, title, company_name, location, department,
               description, url, ats, is_remote, experience_level,
               visa_sponsorship, is_active, scraped_at
        FROM jobs
        ORDER BY scraped_at DESC
        LIMIT ?
    """, (MAX_INGEST,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def to_doc(job: dict) -> str:
    desc  = strip_html(job["description"] or "")[:DESC_CHARS]
    lines = [f"{job['title']} at {job['company_name']}"]
    if job["location"]:
        lines.append(f"Location: {job['location']}")
    if job["department"]:
        lines.append(f"Department: {job['department']}")
    if job["experience_level"] not in (None, "unknown"):
        lines.append(f"Level: {job['experience_level']}")
    if job["is_remote"]:
        lines.append("Remote: Yes")
    if job["visa_sponsorship"] not in (None, "unknown"):
        lines.append(f"Visa sponsorship: {job['visa_sponsorship']}")
    if desc:
        lines.append(desc)
    return "\n".join(lines)


def to_meta(job: dict) -> dict:
    return {
        "title":            job["title"] or "",
        "company":          job["company_name"] or "",
        "location":         job["location"] or "",
        "url":              job["url"] or "",
        "ats":              job["ats"] or "",
        "is_remote":        bool(job["is_remote"]),
        "is_active":        bool(job["is_active"]),
        "experience_level": job["experience_level"] or "unknown",
        "visa_sponsorship": job["visa_sponsorship"] or "unknown",
    }


def run() -> None:
    print(f"Reading from: {DB_PATH}")
    jobs = load_jobs()
    print(f"Loaded {len(jobs)} jobs from DB")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    col    = client.get_or_create_collection(COLLECTION)

    existing  = set(col.get()["ids"])
    new_jobs  = [j for j in jobs if j["id"] not in existing]
    print(f"Already indexed: {len(existing)} | New to add: {len(new_jobs)}")

    if not new_jobs:
        print(f"Index is up to date. Total: {col.count()} jobs")
        return

    BATCH = 100
    for i in range(0, len(new_jobs), BATCH):
        batch = new_jobs[i : i + BATCH]
        col.add(
            ids=[j["id"] for j in batch],
            documents=[to_doc(j) for j in batch],
            metadatas=[to_meta(j) for j in batch],
        )
        print(f"  {min(i + BATCH, len(new_jobs))}/{len(new_jobs)} ingested")

    print(f"\nDone. Collection size: {col.count()} jobs")


if __name__ == "__main__":
    run()
