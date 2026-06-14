# Week 7: Production Operations, Cost Optimization, and Observability

## From Code to Operations

Shipping code is not the same as running a system. A system in production is observed, monitored, debugged, and continuously improved.

This week is about operating a system in production under realistic constraints: costs matter, speed matters, accuracy matters. When something breaks, you need to diagnose it fast and fix it before users are affected.

The key insight: **measurement is your primary tool**. Before you can optimize, you must measure. Before you can debug, you must understand the current state. Before you can prevent problems, you must know what to look for.

## The Three Failure Modes

Week 7 presents three correlated problems: cost tripled, latency increased, accuracy decreased. They are usually connected:

**Scenario 1: Retrieval degradation causes latency and accuracy loss, which increases token usage.**
- Retrieval system is slow or returns poor results
- Agent spends more time calling tools, making more requests, using more tokens
- Cost increases because more tokens are used
- Latency increases because retrieval is slow
- Accuracy decreases because retrieved documents are poor quality

**Scenario 2: Corpus bloat causes retrieval failure.**
- New documents added to corpus
- Retrieval now searches a larger space and returns less relevant results
- Agent wastes tokens on irrelevant documents
- Accuracy drops because agent is confused by poor retrieval
- Cost increases due to wasted tokens

**Scenario 3: Feedback loop creates information cascades.**
- Initial accuracy drops for some reason
- Users correct the agent more often
- Corrections are fed back into the system without validation
- Incorrect feedback corrupts the corpus or retrieval index
- Accuracy drops further
- Cost increases because system chases corrections

The diagnostic approach: measure cost breakdown (where are tokens going?), measure latency profile (where is time spent?), measure accuracy by query type and document. Segment everything. Hypothesize. Test each hypothesis.

## Cost Breakdown and Token Accounting

LLM costs are per token: input and output. To understand cost:

1. **Log every API call**: When you call an LLM API, log the response. Extract: input_tokens, output_tokens, estimated_cost
2. **Aggregate by dimension**: Sum cost by day, by user, by query type, by document, by model
3. **Break down cost**:
   - Base cost (baseline queries)
   - Tool call overhead (how many extra tokens per tool call?)
   - Retrieval cost (how many tokens per document retrieved?)
   - Error recovery cost (retries, fallbacks)

Example breakdown:
```
Total daily cost: $50

Query baseline (skeleton): 
  - Average question: 100 tokens in, 50 tokens out
  - 100 queries/day * 150 tokens = 15,000 tokens = $0.50

Retrieval cost:
  - Average 5 documents retrieved per query
  - Each document: 500 tokens
  - 100 queries * 5 docs * 500 tokens = 250,000 tokens = $8.33

Tool calls:
  - Average 2 tool calls per query
  - Each call: 200 tokens request, 200 tokens response
  - 100 queries * 2 * 400 tokens = 80,000 tokens = $2.67

Errors and retries:
  - 5% of queries fail and retry
  - Retry uses 1.5x tokens
  - 5 queries * 150 * 1.5 = 1,125 tokens = $0.04

Total: $0.50 + $8.33 + $2.67 + $0.04 = $11.54
```

When cost suddenly triples, find out which component spiked. Retrieval from 5 to 10 documents? Tool calls from 2 to 6? Errors from 5% to 15%?

## Latency Profiling and Bottleneck Identification

Latency matters: if queries take >2s, users perceive slowness. If >5s, timeouts occur. If >10s, systems assume failure.

To profile latency:

1. **Measure per-component**:
   - Retrieval: how long to find documents? (query encoding + similarity search)
   - Tool calls: how long to execute? (database query, API call)
   - LLM inference: how long to generate response?
   - Other: serialization, network, parsing

2. **Identify critical path**: Which component dominates? (Often retrieval or LLM inference)

3. **Measure latency distribution**: Not just average (mean can hide tail latencies). Report p50, p95, p99.

Example:
```
Average latency: 1.2s
- Retrieval (p50): 0.4s, p99: 0.8s
- LLM inference (p50): 0.6s, p99: 1.5s
- Tool calls (p50): 0.1s, p99: 0.3s

p99 latency: 2.6s (retrieval 0.8s + LLM 1.5s + tools 0.3s)
```

Bottleneck: LLM inference p99 is 1.5s (2.5x average). Optimization: use faster model for simple queries, batch requests.

## Accuracy Measurement and Feedback

Measuring accuracy requires ground truth. Options:

**Automated evaluation**: For fact-based queries (what's policy X?), check if agent answer matches known reference. Fast, cheap, but limited to answerable questions.

**Human evaluation**: Sample 10% of queries, have human rate correctness (1-5 scale). Slow, expensive, but covers subjective questions.

**User feedback**: Users correct the agent. Correctness = (corrections + 1) / (corrections + total queries). Biased (users might be wrong), but scales.

**Segmentation is critical**: Measure accuracy by query type, document, user role, time of day. Global accuracy 85% masks segments performing at 60%.

## Feedback Loops and Learning

Users correct the agent. This feedback is valuable: it identifies gaps in knowledge or reasoning. But feedback-based learning must be careful:

**Validation**: Are corrections actually correct? Implement review: corrections need approval from authorized role before being integrated.

**Bias**: Users might correct incorrectly. Measure feedback accuracy before using it to retrain.

**Cascading errors**: If you feed incorrect corrections back into the system, errors amplify. Instrument to detect this.

**Feedback metrics**: Track which queries get corrected most often. These are signals for retraining or corpus updates.

## Real-Time Adaptation and Recovery Mechanisms

Production systems must self-heal. When problems are detected, automated recovery can minimize impact:

**Cost overrun**: If daily cost exceeds threshold, automatically reduce model complexity (use cheaper model, disable expensive features, increase caching).

**Latency spike**: If p99 latency exceeds threshold, trigger retrieval optimization (reduce doc count, use simpler ranking), fall back to cached answers.

**Accuracy degradation**: If accuracy drops >5%, pause new feature deployments, trigger retraining, increase human review rate.

**Error rate spike**: If error rate exceeds threshold, temporarily enable rate limiting, increase logging, page on-call team.

Recovery mechanisms must be:
- **Fast**: Activate within seconds of detecting problem
- **Reversible**: Can rollback after investigating
- **Instrumented**: Log what recovery did so you understand downstream effects
- **Tested**: Have runbooks that verify recovery works

## Runbooks and Operational Procedures

A runbook is a documented procedure: when alert X fires, do these steps in order.

Example runbook for "High Cost Alert":
```
Alert: Daily cost > $1000

Step 1: Measure
- Last 24 hours cost: $ (from monitoring)
- Token breakdown: input/output ratio (is something generating excessive output?)
- Query count: is volume up? (more queries = more cost)
- Cost per query (is something more expensive?): cost_today / query_count

Step 2: Hypothesize
- If volume up 2x: normal load increase. No action needed unless sustained.
- If cost per query up 3x: something expensive changed.
  - Check recent deployments: model changed? new features enabled?
  - Check document corpus: corpus size increased?
  - Check retrieval: are more documents being retrieved?

Step 3: Mitigate
- If model changed: rollback to previous model
- If corpus grew: archive low-value documents
- If retrieval too aggressive: reduce retrieved doc count from 5 to 3

Step 4: Investigate
- Segment cost by user, query type, document
- Find which specific queries are expensive
- Fix root cause
```

Runbooks are living documents: update them as you learn more.

## Observability and Instrumentation

Observability is the ability to ask arbitrary questions about system behavior. It requires comprehensive instrumentation: logging, metrics, traces.

**Logging**: Record events (query received, documents retrieved, tool called, error occurred) with context (user, role, query hash, latency, cost).

**Metrics**: Summary statistics (count, latency, errors) aggregated per minute or hour. Enable dashboards and alerting.

**Traces**: Request flow from entry to exit, showing every step. Slow but powerful for debugging specific requests.

[Best practice: instrument for the questions you'll want to ask after failures occur.](https://www.observability.engineering/) If a query fails, you'll want to know: which documents were retrieved? Which tools were called? What did tools return? Which LLM decision was made?

## Model Degradation and Retraining at Scale

As new data and feedback arrive, the model degrades. Retraining is necessary but risky:

**Staged rollout**: Train new model. Deploy to 1% of traffic (canary). Monitor metrics. If metrics stay healthy, increase to 10%, 50%, 100%.

**Automatic rollback**: If metrics degrade, automatic rollback to previous version. No human approval needed for rollback (rollback is low-risk).

**A/B testing**: For significant changes, run new model on 50% of traffic, old model on 50%. Compare metrics over time.

[Netflix and Uber document deploying hundreds of model versions per day using careful monitoring and automatic rollback.](https://www.uber.com/us/en/blog/enhancing-the-quality-of-machine-learning-systems-at-scale/)

## SRE Principles Applied to ML Systems

Site Reliability Engineering (SRE) is a discipline for operating systems at scale. Key principles:

1. **Measure everything**: Define SLOs (Service Level Objectives) for latency, availability, cost. Monitor constantly.

2. **Automate response**: When alerts fire, automated responses should address most cases. Humans review, but automation is default.

3. **Document procedures**: Runbooks, playbooks, incident postmortems. Share knowledge so next incident is faster to resolve.

4. **Blameless postmortems**: When incidents happen, investigate root cause without blaming individuals. Improve systems so incident can't recur.

5. **Error budgets**: If you have 99.9% availability SLO, you have an error budget of 0.1% downtime. When budget is exhausted, freeze new deployments until reliability improves.

6. **Observability over perfection**: Better to have good monitoring of an imperfect system than perfect system with no visibility.

[Google's SRE book is a foundational reference.](https://sre.google/books/)

## Case Study: The Cascade

Real scenario: A deployed agent starts showing accuracy degradation. Cause:

1. Corpus was updated with new documents
2. Search index was not rebuilt; search still indexes old corpus
3. Agents retrieve old documents (no new policy info), can't answer new questions
4. Users correct the agent with feedback
5. Feedback is automatically integrated into corpus without validation
6. Some feedback is wrong (user misremembered policy)
7. Agent learns from wrong feedback
8. Accuracy drops further
9. More users correct with more feedback (some right, some wrong)
10. Corpus becomes corrupted with mixed right/wrong information
11. Accuracy continues to drop

Prevention:
1. Rebuild index when corpus changes (instrument to verify)
2. Validate feedback before integration (human review or automated checks)
3. Monitor accuracy by query type; detect segment degradation early
4. Alert when accuracy drops >5%; pause new deployments
5. Runbook for "corpus corruption": rollback corpus to last known good version, re-index, investigate

## References

[Observability Engineering: Achieving Production Resilience](https://www.observability.engineering/)
- Practical guide to observability, instrumentation, and debugging

[Site Reliability Engineering: How Google Runs Production Systems](https://sre.google/books/)
- Foundational SRE principles and practices

[Uber's ML at Scale: Increasing Integrity and Velocity](https://www.uber.com/us/en/blog/enhancing-the-quality-of-machine-learning-systems-at-scale/)
- Case study on deploying ML systems operationally

[Cost Optimization for Machine Learning: A Comprehensive Guide](https://docs.aws.amazon.com/whitepapers/latest/ml-best-practices-public-sector-organizations/cost-optimization.html)
- Strategies for reducing ML infrastructure costs

[ML Systems Design Patterns](https://github.com/mercari/ml-system-design-pattern)
- Design patterns for production ML systems

[Monitoring and Alerting in Machine Learning](https://arxiv.org/abs/2510.24142)
- Survey of monitoring practices and gaps

[Incident Management and Postmortem Culture](https://www.pagerduty.com/resources/postmortems/)
- Blameless postmortems and incident response

[Latency Matters: Measuring and Optimizing User-Perceived Performance](https://www.infoq.com/articles/latency-performance-monitoring/)
- Profiling and optimization techniques

[User Feedback Systems for ML Products](https://www.reforge.com/blog/feedback-loops)
- Design patterns for capturing and using user feedback
