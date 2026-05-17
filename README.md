# Agentic AI / RAG Evaluation Kit

🌐 **Live demo:** _coming soon — deploys to Hugging Face Spaces in Wave 2 rollout_

This compact local artifact shows retrieval evidence, generated answers, and explicit evaluation cases. It is meant to make the quality side of RAG and agentic systems tangible without pretending a tiny demo is already production software.

## Run

**Interactive (Streamlit) — recommended:**
```bash
pip install -r requirements.txt
streamlit run app.py
```
Click a query chip or type your own. Watch retrieval scores update, evidence sentences highlight in the source, and pass/fail evaluate against expected ground truth.

**CLI eval trace:**
```bash
python3 rag_runner.py
```
Refreshes `sample_trace.md` with the 4 eval cases.

## What It Demonstrates In 30 Seconds

- Answers are paired with retrieval evidence instead of being judged by tone alone.
- Evaluation is visible and strict enough to fail when the expected policy detail is missing.
- The artifact is honest about scope: local corpus, lightweight retrieval, and reviewable traces.

## Role Hooks

- BDO / data-quality AI roles: evidence-backed answer validation.
- Dayforce / SaaS AI roles: policy retrieval and guardrail-ready traces.
- Netomi / Dialpad / Samsara: customer-support workflows with reviewable evidence.
- Orium / Varicent / NTT: agentic workflow quality, eval cases, and failure analysis.

## Outreach Hook

I built a compact RAG/evaluation artifact that shows not only answers, but retrieval evidence, traces, and failure analysis. I wanted to make the quality side of agentic systems tangible.
