# RAG Evaluation Trace

## Sendable Summary

This sample keeps retrieval, answer generation, and evaluation in one view. The goal is not to claim a full production RAG stack, but to show the habit of making evidence and pass/fail logic inspectable.

Cases passed: 3/4

## refund_review

Query: Can the agent approve a 7000 USD refund automatically?
Retrieved document: `refund_policy.md`
Answer: Refund requests under 30 days may be approved automatically when the account has no policy violations and the invoice is below 5000 USD. Refund requests above 5000 USD require manager review.
Evidence snippets: Refund requests under 30 days may be approved automatically when the account has no policy violations and the invoice is below 5000 USD. | Refund requests above 5000 USD require manager review.
Expected evidence: Refund requests above 5000 USD require manager review
Result: pass

## customer_data_action

Query: What evidence should an agent log when it accesses customer data?
Retrieved document: `security_review.md`
Answer: Any workflow that accesses customer data must log the user request, retrieved evidence, proposed action, and final reviewer. Actions that modify customer records require human approval.
Evidence snippets: Any workflow that accesses customer data must log the user request, retrieved evidence, proposed action, and final reviewer. | Actions that modify customer records require human approval.
Expected evidence: log the user request, retrieved evidence, proposed action, and final reviewer
Result: pass

## escalation_speed

Query: How quickly should high severity customer issues be routed?
Retrieved document: `escalation_runbook.md`
Answer: High-severity customer issues should be routed to the owning support queue within 15 minutes. The escalation note must include severity, customer impact, suspected owner, and recommended next action.
Evidence snippets: High-severity customer issues should be routed to the owning support queue within 15 minutes. | The escalation note must include severity, customer impact, suspected owner, and recommended next action.
Expected evidence: within 15 minutes
Result: pass

## tool_call_limit

Query: What is the maximum number of tool calls an agent can make per session?
Retrieved document: `escalation_runbook.md`
Answer: High-severity customer issues should be routed to the owning support queue within 15 minutes. The escalation note must include severity, customer impact, suspected owner, and recommended next action.
Evidence snippets: High-severity customer issues should be routed to the owning support queue within 15 minutes. | The escalation note must include severity, customer impact, suspected owner, and recommended next action.
Expected evidence: maximum tool invocations per session
Result: fail

## Failure Analysis

This demo keeps retrieval and evaluation visible. A production version would add embedding retrieval, larger eval sets, and score thresholds, but the important habit is already present: answers are judged against evidence rather than accepted because they sound plausible.
