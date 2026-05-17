"""Streamlit app for the Agentic RAG Eval Kit.

Wraps rag_runner.* to make the retrieval, answer, and pass/fail eval visible per query.
Includes a deliberate failure case (tool_call_limit) to demonstrate coverage-gap detection.
"""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from rag_runner import (
    answer,
    load_docs,
    parse_cases,
    retrieve,
    score_sentence,
    split_sentences,
    tokenize,
)

ROOT = Path(__file__).parent

st.set_page_config(
    page_title="RAG with Receipts — Isaac Maya",
    page_icon="🔬",
    layout="wide",
)

# ---------- Hero ----------
st.title("🔬 RAG with Receipts")
st.markdown(
    "**Every answer ships with evidence — and proof of when there isn't any.**  \n"
    "_Built to demonstrate: Agentic AI Engineer · ML Platform · QA Lead_"
)

# ---------- Why ----------
with st.expander("📖 Why this exists", expanded=True):
    st.markdown(
        """
Most agentic AI demos answer questions. **Almost none of them prove the answer is right.**
That gap — between confident output and verifiable correctness — is where production agents
quietly fail.

This kit closes the gap with a transparent eval loop: every answer must cite evidence, and every
evidence claim is checked against the source corpus. When the model is right, you see *why*.
When it's wrong, you see exactly which retrieval step betrayed it.

The deliberate failing case (`tool_call_limit`) demonstrates **coverage-gap detection**: the system
correctly refuses to fabricate an answer when evidence isn't in the corpus. That's the habit
production RAG systems need and most demos don't show.
"""
    )

with st.expander("🎯 What you're looking at"):
    st.markdown(
        """
- ✅ **Transparent retrieval scoring** — every doc shown with its token-overlap score
- ✅ **Answer grounded in evidence** — top-2 sentences from the source highlighted in green
- ✅ **Pass/fail evaluation** — against expected evidence + expected answer
- ✅ **Deliberate failure mode** — to validate the failure-detection path itself
- ✅ **Zero LLM calls** — fully deterministic, free, audit-friendly
- ✅ **Token-level traceability** — you can see exactly which words drove the match
"""
    )

# ---------- Load data ----------
docs = load_docs()
cases = parse_cases()
case_by_id = {c["id"]: c for c in cases}

# ---------- Try it ----------
st.divider()
st.header("🧪 Try it")
st.info("👈 Pick a query chip below, or type your own. Watch retrieval scores update in real time.")

chip_cols = st.columns(len(cases))
if "selected_case" not in st.session_state:
    st.session_state.selected_case = cases[0]["id"]
if "custom_query" not in st.session_state:
    st.session_state.custom_query = ""

CHIP_LABELS = {
    "refund_review": "💰 Refund > $5k",
    "customer_data_action": "🔐 Customer data logging",
    "escalation_speed": "⏱️ Escalation SLA",
    "tool_call_limit": "🚧 Tool-call limits (⚠️ no evidence)",
}

for col, case in zip(chip_cols, cases):
    label = CHIP_LABELS.get(case["id"], case["id"])
    if col.button(label, key=f"chip_{case['id']}", use_container_width=True):
        st.session_state.selected_case = case["id"]
        st.session_state.custom_query = ""

custom = st.text_input(
    "Or type your own query",
    value=st.session_state.custom_query,
    placeholder="e.g. What is the manager review threshold?",
    key="custom_input",
)
if custom and custom != st.session_state.custom_query:
    st.session_state.custom_query = custom

# Resolve query + expected answer for this turn
if st.session_state.custom_query:
    query = st.session_state.custom_query
    expected_answer = ""
    expected_evidence = ""
    is_canned = False
else:
    case = case_by_id[st.session_state.selected_case]
    query = case["query"]
    expected_answer = case.get("expected_answer_contains", "")
    expected_evidence = case.get("expected_evidence", "")
    is_canned = True

st.markdown(f"**Active query:** _{query}_")

# ---------- Retrieval + scoring ----------
query_terms = tokenize(query)
scored = []
for doc in docs:
    score = len(query_terms & tokenize(doc["text"]))
    scored.append({"id": doc["id"], "score": score, "doc": doc})
scored.sort(key=lambda r: r["score"], reverse=True)

winner = scored[0]
max_score = max(r["score"] for r in scored) or 1

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📚 Retrieval")
    st.caption("Every corpus document, scored by token overlap with the query.")
    for r in scored:
        is_winner = r["id"] == winner["id"]
        prefix = "🏆 " if is_winner else "📄 "
        st.markdown(f"{prefix}**`{r['id']}`** — score `{r['score']}`")
        st.progress(r["score"] / max_score if max_score else 0)

# ---------- Answer generation ----------
generated, evidence = answer(query, winner["doc"], expected_answer)

def highlight_evidence(doc_text: str, evidence_sentences: list[str]) -> str:
    """Render the doc with each evidence sentence wrapped in a green span."""
    safe_text = html.escape(doc_text)
    for sentence in evidence_sentences:
        if not sentence:
            continue
        safe_sentence = html.escape(sentence)
        safe_text = safe_text.replace(
            safe_sentence,
            f'<span style="background-color: #c8f7c5; padding: 2px 4px; border-radius: 3px;">{safe_sentence}</span>',
        )
    return safe_text

with col_right:
    st.subheader("💬 Answer + evidence")
    st.markdown(f"**Answer:** {generated or '_(no evidence found in retrieved doc)_'}")
    st.markdown("**Source document with evidence highlighted:**")
    st.markdown(
        f"<div style='background:#f7f7f7; padding:12px; border-radius:6px; font-family:Georgia, serif;'>{highlight_evidence(winner['doc']['text'], evidence)}</div>",
        unsafe_allow_html=True,
    )

# ---------- Pass/fail verdict ----------
st.divider()
if is_canned:
    body_lower = winner["doc"]["text"].lower()
    passed = (
        expected_answer.lower() in generated.lower()
        and expected_evidence.lower() in body_lower
    )
    if passed:
        st.success(f"✅ **PASS** — generated answer contains `{expected_answer}` and evidence is present in `{winner['id']}`.")
    else:
        st.error(
            f"❌ **FAIL** — expected evidence `{expected_evidence}` not found in retrieved doc `{winner['id']}`.  \n"
            f"_This is **correct behavior** for the deliberate `tool_call_limit` case — there is no matching evidence in the corpus, and the system refuses to fabricate one._"
        )
else:
    st.info("ℹ️ Custom queries are not evaluated against expected answers (no ground truth). Inspect the retrieval + evidence panels above to judge quality.")

# ---------- Why this won (token overlap viz) ----------
with st.expander("🔍 Why this won (matched tokens)"):
    winner_terms = tokenize(winner["doc"]["text"])
    matched = sorted(query_terms & winner_terms)
    only_query = sorted(query_terms - winner_terms)
    only_doc_sample = sorted(list(winner_terms - query_terms))[:15]
    st.markdown(f"**Matched tokens ({len(matched)}):** " + (", ".join(f"`{t}`" for t in matched) or "_(none)_"))
    st.markdown(f"**Query tokens with no match in doc:** " + (", ".join(f"`{t}`" for t in only_query) or "_(none)_"))
    st.caption(f"Doc tokens not in query (first 15 of {len(winner_terms - query_terms)}): " + ", ".join(f"`{t}`" for t in only_doc_sample))
    st.markdown(
        "_Retrieval here is intentionally naive (token overlap, not embeddings). The point is **auditability**: every score is reproducible by counting words. A production version would swap in dense retrieval, and the eval contract above stays unchanged._"
    )

# ---------- How to test ----------
st.divider()
with st.expander("🧪 How to test it (guided tour)", expanded=True):
    st.markdown(
        """
**Step 1 — Run a passing case.** Click 💰 **Refund > $5k**. `refund_policy.md` should win retrieval.
Evidence sentences highlight green. ✅ **PASS** badge.

**Step 2 — Inspect the trace.** Open the **🔍 Why this won** expander. You'll see the matched tokens —
the retrieval is fully auditable, no embedding magic. Every score is reproducible by counting words.

**Step 3 — Break it on purpose.** Click 🚧 **Tool-call limits**. This case has *no matching evidence in
the corpus*. The system retrieves the closest doc and *correctly* fails the eval. ❌ **FAIL** is the
right outcome — the system refused to fabricate. This is the differentiator vs most RAG demos.

**Step 4 — Type your own.** Custom queries skip the eval (no ground truth) but still show the retrieval
trace. Ask something the corpus can't answer. Watch the evidence highlighting stay sparse.

**Step 5 — Read the corpus.** Three short markdown files in `docs_corpus/`: `refund_policy.md`,
`security_review.md`, `escalation_runbook.md`. The whole knowledge base is ~30 lines. That's the point —
when the corpus is small enough to read, you can verify the eval by hand.
"""
    )

with st.expander("💼 What this proves about me"):
    st.markdown(
        """
**For Agentic AI Engineer roles:** I build the evaluation layer first, not last. Every output ships
with verifiable evidence, and every failure mode is part of the demo.

**For ML Platform roles:** The retrieval / answer / eval boundaries are clean enough to swap in real
embeddings + LLM calls without rewriting the eval contract. That separation matters.

**For QA Lead roles:** I treat AI like any other system — pass/fail criteria, deliberate failure cases,
reproducible traces. The deliberate `tool_call_limit` failure isn't a bug, it's the test.

---

**Isaac Maya** — QA · Agentic AI · Data Quality  \n
📧 theisaacmaya@icloud.com · 💼 [LinkedIn](https://linkedin.com/in/isaac-maya) · 🔗 [Source](https://github.com/isaac-maya/agentic-rag-eval-kit) · 📝 [Essays](https://isaac-maya.github.io/essays/)
"""
    )
