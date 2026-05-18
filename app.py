import sys
from pathlib import Path

import streamlit as st
from query import ask, search, get_collection

st.set_page_config(
    page_title="Job Search RAG",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Animations & custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Keyframes ── */
@keyframes gradient-shift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-glow {
    0%,100% { box-shadow: 0 0 4px rgba(0,220,100,.4); }
    50%     { box-shadow: 0 0 14px rgba(0,220,100,.9), 0 0 28px rgba(0,220,100,.2); }
}
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}
@keyframes float {
    0%,100% { transform: translateY(0px); }
    50%      { transform: translateY(-6px); }
}
@keyframes dot-bounce {
    0%,80%,100% { transform: scale(0); opacity: 0.3; }
    40%          { transform: scale(1); opacity: 1; }
}

/* ── Global font ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Animated gradient title ── */
.rag-title {
    background: linear-gradient(270deg, #1f77b4, #00d2ff, #a855f7, #06b6d4, #1f77b4);
    background-size: 400% 400%;
    animation: gradient-shift 6s ease infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.4rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    margin: 0;
    padding: 0;
}
.rag-subtitle {
    color: #666;
    font-size: 0.95rem;
    margin-top: 4px;
    margin-bottom: 24px;
}

/* ── Job cards ── */
.job-card {
    border: 1px solid #1e2533;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 14px;
    background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
    transition: transform 0.25s cubic-bezier(.4,0,.2,1),
                box-shadow 0.25s cubic-bezier(.4,0,.2,1),
                border-color 0.25s ease;
    animation: fadeSlideIn 0.45s ease both;
    cursor: default;
}
.job-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 36px rgba(31,119,180,.22), 0 2px 8px rgba(0,0,0,.4);
    border-color: #1f77b4;
}

/* Card stagger delays */
.card-0 { animation-delay: 0.00s; }
.card-1 { animation-delay: 0.07s; }
.card-2 { animation-delay: 0.14s; }
.card-3 { animation-delay: 0.21s; }
.card-4 { animation-delay: 0.28s; }
.card-5 { animation-delay: 0.35s; }
.card-6 { animation-delay: 0.42s; }
.card-7 { animation-delay: 0.49s; }

/* ── Badges ── */
.badge-active {
    background: rgba(0,220,100,.12);
    color: #00dc64;
    border: 1px solid rgba(0,220,100,.3);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 600;
    animation: pulse-glow 2.5s ease infinite;
}
.badge-closed {
    background: rgba(100,100,100,.12);
    color: #888;
    border: 1px solid rgba(100,100,100,.3);
    border-radius: 6px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 600;
}
.badge-remote {
    background: rgba(168,85,247,.1);
    color: #a855f7;
    border: 1px solid rgba(168,85,247,.25);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 12px;
}
.badge-level {
    background: rgba(6,182,212,.1);
    color: #06b6d4;
    border: 1px solid rgba(6,182,212,.25);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 12px;
}

/* ── View Job button ── */
.view-btn {
    display: inline-block;
    margin-top: 12px;
    background: linear-gradient(135deg, #1f77b4, #06b6d4);
    color: white !important;
    padding: 6px 16px;
    border-radius: 6px;
    text-decoration: none !important;
    font-size: 13px;
    font-weight: 600;
    transition: opacity 0.2s ease, transform 0.2s ease;
}
.view-btn:hover {
    opacity: 0.85;
    transform: scale(1.03);
}

/* ── Thinking dots ── */
.thinking {
    display: flex;
    gap: 6px;
    align-items: center;
    padding: 8px 0;
}
.thinking span {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #1f77b4;
    animation: dot-bounce 1.4s ease infinite;
}
.thinking span:nth-child(2) { animation-delay: 0.2s; }
.thinking span:nth-child(3) { animation-delay: 0.4s; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0d14 0%, #0e1117 60%, #111827 100%);
    border-right: 1px solid #1e2533;
}
[data-testid="stSidebar"] .rag-title {
    font-size: 1.5rem;
}

/* ── Metric glow ── */
[data-testid="stMetricValue"] {
    color: #1f77b4 !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
}

/* ── Chat input glow ── */
[data-testid="stChatInput"] textarea:focus {
    border-color: #1f77b4 !important;
    box-shadow: 0 0 0 2px rgba(31,119,180,.35) !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    animation: fadeSlideIn 0.35s ease both;
}

/* ── Tab pills ── */
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    font-weight: 500;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #1f77b4 !important;
}

/* ── Search button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1f77b4, #06b6d4) !important;
    border: none !important;
    font-weight: 600 !important;
    transition: opacity 0.2s ease, transform 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: scale(1.02) !important;
}

/* ── Divider ── */
hr {
    border-color: #1e2533 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="rag-title">Job Search RAG</p>', unsafe_allow_html=True)
    st.caption("Semantic search over your scraped job listings")

    try:
        col = get_collection()
        total = col.count()
    except Exception:
        st.error("No index found. Run `python rag/ingest.py` first.")
        st.stop()

    st.metric("Jobs indexed", f"{total:,}")
    st.divider()

    st.subheader("Filters")
    remote_only = st.toggle("Remote only")
    active_only = st.toggle("Active listings only", value=False)
    level = st.selectbox("Experience level", ["Any", "entry", "mid", "senior"])

    st.divider()
    st.caption("Vector DB: ChromaDB")
    st.caption("LLM: Groq  |  Llama 3.3 70B")


# ── Page title ────────────────────────────────────────────────────────────────
st.markdown(
    '<h1 class="rag-title">Job Search RAG</h1>'
    '<p class="rag-subtitle">Ask anything about your job listings — powered by semantic search + AI</p>',
    unsafe_allow_html=True,
)


# ── Filter builder ────────────────────────────────────────────────────────────
def build_where():
    conditions = []
    if remote_only:
        conditions.append({"is_remote": {"$eq": True}})
    if active_only:
        conditions.append({"is_active": {"$eq": True}})
    if level != "Any":
        conditions.append({"experience_level": {"$eq": level}})
    if not conditions:
        return None
    return conditions[0] if len(conditions) == 1 else {"$and": conditions}


# ── Job card ──────────────────────────────────────────────────────────────────
def job_card(h: dict, idx: int = 0):
    m = h["meta"]
    title   = m.get("title", "Unknown")
    company = m.get("company", "Unknown")
    location = m.get("location") or "N/A"
    remote   = "Remote" if m.get("is_remote") else "On-site"
    lvl      = m.get("experience_level", "unknown")
    visa     = m.get("visa_sponsorship", "unknown")
    active   = m.get("is_active", False)
    url      = m.get("url", "#")

    badge   = f'<span class="badge-active">Active</span>' if active else '<span class="badge-closed">Closed</span>'
    r_badge = f'<span class="badge-remote">{remote}</span>'
    l_badge = f'<span class="badge-level">{lvl}</span>'
    delay   = f"card-{min(idx, 7)}"

    st.markdown(f"""
    <div class="job-card {delay}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;">
            <div>
                <div style="font-size:15px;font-weight:700;color:#e8eaf0;margin-bottom:3px;">{title}</div>
                <div style="font-size:13px;color:#8892a4;">{company}</div>
            </div>
            {badge}
        </div>
        <div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:13px;color:#666;">
            <span>&#128205; {location}</span>
            {r_badge}
            {l_badge}
            <span style="color:#555;">Visa: {visa}</span>
        </div>
        <a href="{url}" target="_blank" class="view-btn">View Job &#8599;</a>
    </div>
    """, unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_chat, tab_search = st.tabs(["Chat", "Raw Search"])


# ── Chat tab ──────────────────────────────────────────────────────────────────
with tab_chat:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"Sources  ({len(msg['sources'])} jobs retrieved)"):
                    for i, h in enumerate(msg["sources"]):
                        job_card(h, idx=i)

    if prompt := st.chat_input("Ask anything about your job listings..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("Agent OZ"):
            placeholder = st.empty()
            placeholder.markdown(
                '<div class="thinking"><span></span><span></span><span></span></div>',
                unsafe_allow_html=True,
            )
            try:
                answer, hits = ask(prompt, where=build_where())
            except Exception as e:
                answer = f"Error: {e}"
                hits = []
            placeholder.markdown(answer)

            if hits:
                with st.expander(f"Sources  ({len(hits)} jobs retrieved)"):
                    for i, h in enumerate(hits):
                        job_card(h, idx=i)

        st.session_state.messages.append({
            "role": "Agent OZ",
            "content": answer,
            "sources": hits,
        })


# ── Raw Search tab ────────────────────────────────────────────────────────────
with tab_search:
    st.subheader("Semantic Search")
    st.caption("Find jobs by meaning — no LLM, just vector similarity.")

    query = st.text_input(
        "Search query",
        placeholder="e.g.  machine learning infrastructure  /  remote fintech python",
    )
    n_results = st.slider("Results to show", min_value=3, max_value=20, value=8)

    if st.button("Search", type="primary") and query:
        with st.spinner("Searching..."):
            try:
                hits = search(query, n=n_results, where=build_where())
            except Exception as e:
                st.error(str(e))
                hits = []

        if hits:
            st.success(f"{len(hits)} results for: *{query}*")
            for i, h in enumerate(hits):
                job_card(h, idx=i)
        else:
            st.info("No results found.")
