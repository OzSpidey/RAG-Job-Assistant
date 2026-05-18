"""
Interactive CLI for the Job Search RAG.

Usage:
  python rag/ingest.py        # build the index first (run once)
  python rag/cli.py           # start asking questions
"""
import sys
from pathlib import Path

import chromadb
from config import CHROMA_DIR, COLLECTION
from query import ask, search

HELP = """
What you can do:
  Just type a question    →  Claude searches your jobs and answers
  search <query>          →  raw semantic results, no LLM (faster)
  quit                    →  exit

Example questions:
  "Find AI Engineer roles at fintech companies"
  "Which remote entry-level jobs don't require visa sponsorship?"
  "What skills appear most in software engineer postings?"
  "Compare Stripe and OpenAI job requirements"
"""


def check_index() -> int:
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        col = client.get_collection(COLLECTION)
        return col.count()
    except Exception:
        return 0


def show_raw_hits(hits: list[dict]):
    for i, h in enumerate(hits, 1):
        m = h["meta"]
        status = "ACTIVE" if m["is_active"] else "closed"
        print(f"\n  {i}. [{status}] {m['title']} @ {m['company']}")
        print(f"     {m['location']} | Remote: {m['is_remote']} | Level: {m['experience_level']}")
        print(f"     {m['url']}")


def main():
    count = check_index()
    if count == 0:
        print("No job index found. Build it first:")
        print("  python rag/ingest.py")
        sys.exit(1)

    print("=" * 60)
    print(f"  Job Search RAG  ({count:,} jobs indexed)")
    print("=" * 60)
    print(HELP)

    while True:
        try:
            inp = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not inp:
            continue
        if inp.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if inp.lower().startswith("search "):
            hits = search(inp[7:])
            show_raw_hits(hits)
            print()
        else:
            print("\nSearching index and thinking...\n")
            try:
                answer, hits = ask(inp)
                print(f"Claude:\n{answer}")
                print(f"\n  [{len(hits)} jobs retrieved from index]")
            except Exception as e:
                print(f"Error: {e}")
        print()


if __name__ == "__main__":
    main()
