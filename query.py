"""
Semantic search over ChromaDB + answer generation via Groq (Llama 3.3 70B).
"""
import os
from dotenv import load_dotenv
load_dotenv()

import chromadb
from groq import Groq
from config import CHROMA_DIR, COLLECTION, TOP_K

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a job search assistant. The user is a software/AI engineer looking for roles. "
    "Answer using only the job listings provided as context. Be specific — cite job titles, "
    "companies, and include URLs when helpful. If no listings match, say so clearly."
)


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_collection(COLLECTION)


def search(query: str, n: int = TOP_K, where: dict = None) -> list[dict]:
    col    = get_collection()
    kwargs = {"query_texts": [query], "n_results": min(n, col.count())}
    if where:
        kwargs["where"] = where
    try:
        res = col.query(**kwargs)
    except Exception:
        kwargs.pop("where", None)
        res = col.query(**kwargs)
    return [
        {"doc": doc, "meta": meta, "score": dist}
        for doc, meta, dist in zip(
            res["documents"][0],
            res["metadatas"][0],
            res["distances"][0],
        )
    ]


def ask(question: str, where: dict = None) -> tuple[str, list[dict]]:
    hits = search(question, where=where)
    if not hits:
        return "No relevant jobs found in the index.", []

    context = "\n\n---\n\n".join(
        f"{h['meta']['title']} @ {h['meta']['company']}\n"
        f"Location: {h['meta']['location']} | Remote: {h['meta']['is_remote']} | "
        f"Level: {h['meta']['experience_level']} | Visa: {h['meta']['visa_sponsorship']} | "
        f"Active: {h['meta']['is_active']}\nURL: {h['meta']['url']}\n\n{h['doc']}"
        for h in hits
    )

    client   = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Job listings:\n\n{context}\n\nQuestion: {question}"},
        ],
        max_tokens=1024,
    )
    return response.choices[0].message.content, hits
