# Graph Algorithm Detailed Report (Graph-based Reranker for Text-to-SQL)

## 0. Scope and Context

This report documents the current graph-based reranking algorithm used in FusionSQL for table selection. The pipeline input is a BGE vector-search shortlist (typically top 10-20 tables). The graph optimizer re-scores these candidates using schema graph signals derived from Neo4j (foreign-key relationships), then returns a re-ranked list. The focus here is on:

- Exactly how edges and weights are computed.
- How the algorithm evolved across versions.
- The known flaw for single-table queries and a proposed Hybrid Score fix.
- A diagnosis for Q7 (retrieval vs SQL generation).
- A placeholder for detailed run data.

References: `fusionsql/graph_optimizer/optimizer.py`, `fusionsql/graph_optimizer/algorithms.py`, `fusionsql/graph_optimizer/neo4j_client.py`, `fusionsql/graph_optimizer/config.py`, `fusionsql/graph_optimizer/graph_cache.py`, `fusionsql/graph_optimizer/doc/algorithm_evolution.md`, `fusionsql/graph_optimizer/docs/REPORT.md`.

---

## 1. Algorithm Detail (Edges, Weights, and Scoring)

### 1.1 Candidate Expansion and Subgraph Build

Input is a list of BGE candidates: `[(table_name, bge_score), ...]`. The graph optimizer constructs a subgraph consisting of:

1. All candidate tables.
2. 1-hop neighbors of those candidates in Neo4j.

Implementation:
- `GraphOptimizer._build_subgraph()` calls `Neo4jClient.get_connected_tables()` to expand candidates (default `SUBGRAPH_HOPS = 1`).
- It then calls `Neo4jClient.get_table_relationships()` on the expanded table list to fetch all `IS` and `MOSTLYIS` edges between those tables.
- The resulting relationships are used to instantiate `TableGraph.from_relationships()` (undirected, weighted graph). Candidate tables are always inserted as nodes even if isolated.

References: `fusionsql/graph_optimizer/optimizer.py`, `fusionsql/graph_optimizer/neo4j_client.py`, `fusionsql/graph_optimizer/algorithms.py`, `fusionsql/graph_optimizer/config.py`.

### 1.2 Edge Types and Weight Assignment

Neo4j contains two relationship types between tables:

- `IS`: precise foreign-key relationship.
- `MOSTLYIS`: inferred (noisy) foreign-key relationship.

Edge weight assignment is deterministic:

```
RELATION_WEIGHTS = {
    "IS": 1.0,
    "MOSTLYIS": 0.2,
}
```

- If a relationship type is unknown, a fallback of `0.5` is used.
- Edges are undirected in the in-memory graph (`add_edge` inserts both directions).
- Multiple edges are stored as individual entries; weights are aggregated implicitly during neighbor normalization.

References: `fusionsql/graph_optimizer/config.py`, `fusionsql/graph_optimizer/neo4j_client.py`, `fusionsql/graph_optimizer/algorithms.py`.

### 1.3 Personalized PageRank (PPR)

PPR is computed over the subgraph to estimate query-specific importance:

- Seeds: all candidate tables that exist in the subgraph.
- Personalization vector: uniform over seeds (each gets `1/|seed_set|`).
- Damping: `0.85`.
- Max iterations: `100`.
- Convergence tolerance: `1e-6`.

Transition probabilities are built by normalizing outgoing edge weights per node:

```
P(n -> m) = weight(n,m) / sum_{k in neighbors(n)} weight(n,k)
```

If a node has no neighbors, it contributes no outgoing probability mass.

References: `fusionsql/graph_optimizer/algorithms.py`, `fusionsql/graph_optimizer/config.py`.

### 1.4 Connectivity Score (Local Centrality)

Connectivity estimates direct link density to high-confidence candidates:

- Reference set: the top 10 candidate tables by BGE rank.
- For a table `t`, connectivity is:

```
connectivity(t) = |neighbors(t) ∩ top_tables| / |top_tables|
```

This is a 1-hop measure (direct edges only).

Reference: `fusionsql/graph_optimizer/algorithms.py`, `fusionsql/graph_optimizer/optimizer.py`.

### 1.5 Degree Centrality (Global Graph Prior)

A global degree centrality score is computed offline and stored in a cache:

- Uses all tables and all `IS/MOSTLYIS` relationships.
- Degree is normalized by the maximum observed degree:

```
normalized_degree(t) = degree(t) / max_degree
```

This cached score is used as a weak global prior for tables that are highly connected across the entire schema.

Reference: `fusionsql/graph_optimizer/graph_cache.py`.

### 1.6 Feature Normalization

Before combining graph features, each feature map is min-max normalized across the candidate list:

```
normalized(v) = (v - min) / (max - min)
```

If all values are identical, all normalized values become `1.0`.

Reference: `fusionsql/graph_optimizer/optimizer.py`.

### 1.7 Final Hybrid Scoring (Current Default)

Current default strategy is `hybrid` with a boost-only score:

1. Compute normalized graph features: `PPR`, `connectivity`, `degree`.
2. Combine graph features:

```
graph_boost = 0.50 * PPR_norm + 0.35 * connectivity_norm + 0.15 * degree_norm
```

3. Compute boost scale:

```
boost_factor = max_bge_score * 0.3
```

4. Final score:

```
final_score = bge_score + boost_factor * graph_boost
```

Notes:
- This is boost-only: graph signals never reduce the BGE score.
- The hybrid strategy returns all candidates (no truncation) to avoid dropping relevant tables in this step.

Reference: `fusionsql/graph_optimizer/optimizer.py`.

---

## 2. Algorithm Evolution

### V1.0 - Weighted Average (Initial)

Formula:

```
final = 0.70 * BGE_norm + 0.15 * PPR + 0.10 * connectivity + 0.05 * degree
```

Issues:
- BGE was min-max normalized, compressing semantic gaps.
- Graph features could significantly lower scores for isolated tables (PPR=0, connectivity=0).
- Hard truncation to `TARGET_TABLES` (default 8) caused correct tables ranked 9-10 to be dropped.

References: `fusionsql/graph_optimizer/docs/REPORT.md`, `fusionsql/graph_optimizer/doc/algorithm_evolution.md`.

### V2.0 - Multiplicative Boost

Formula:

```
final = bge_score * (1.0 + 0.3 * graph_features)
```

Improvements:
- Preserved BGE magnitude (no direct penalty for graph=0).

Remaining risk:
- Strong graph signals could still overtake high-BGE tables in some cases.

Reference: `fusionsql/graph_optimizer/doc/algorithm_evolution.md`.

### V3.0 - Boost-Only (Current)

Formula:

```
final = bge_score + boost_factor * graph_boost
boost_factor = max_bge_score * 0.3
```

Key changes:
- No BGE normalization.
- Graph features only add score (never subtract).
- Connectivity reference set expanded to top 10 (from top 5).
- Hybrid strategy stops truncating candidate list.
- `MOSTLYIS` weight reduced to `0.2` to reduce noise.

References: `fusionsql/graph_optimizer/optimizer.py`, `fusionsql/graph_optimizer/config.py`, `fusionsql/graph_optimizer/doc/algorithm_evolution.md`.

---

## 3. User Critique (Single-Table Ranking) and Fix

### 3.1 Critique

"The algorithm ranks single tables (without FKs) lower. This is wrong if the answer is a simple SELECT * FROM table."

Analysis:
- This critique was fully valid in V1. Isolated tables got penalized (graph features = 0), and hard truncation could drop the correct table.
- In the current boost-only version, isolated tables keep their BGE score, but they can still be overtaken by connected tables due to the boost. If downstream logic selects top-K after reranking, the correct single-table result can still drop out.
- In addition, `steiner_tree` and `connectivity` strategies still use truncation, which can remove isolated tables even if their BGE score is strong.

References: `fusionsql/graph_optimizer/optimizer.py`, `fusionsql/graph_optimizer/doc/algorithm_evolution.md`, `fusionsql/graph_optimizer/docs/REPORT.md`.

### 3.2 Proposed Fix: Hybrid Score (Semantic + Graph)

Define a hybrid score that adapts to query intent and graph density, and never penalizes single-table queries.

**Step 1 - Base components**

```
semantic = normalize(BGE_score)
graph = 0.50 * PPR_norm + 0.35 * connectivity_norm + 0.15 * degree_norm
```

**Step 2 - Join intent weight**

Let `join_intent` be a scalar in [0, 1], computed from:
- Query signals (join cues such as "and", "with", "for each", "by customer").
- Graph density of the candidate subgraph.

Example heuristic:

```
join_intent = clamp(0, 1, 0.5 * has_join_keywords + 0.5 * graph_density)
```

**Step 3 - Adaptive hybrid score**

```
alpha = min(0.4, join_intent)
if degree(table) == 0:
    alpha = 0.0

hybrid_score = (1 - alpha) * semantic + alpha * graph
```

Properties:
- If a table is isolated (`degree == 0`), it uses pure semantic score.
- If the query is multi-table, `alpha` increases, allowing graph features to influence rank.
- The impact of the graph never exceeds 40% of the total score.

**Optional safeguard for Top-K selection**

If downstream logic selects top-K, keep a small semantic reserve:

```
final_set = top_m_by_semantic U top_k_by_hybrid
```

This ensures that a strong single-table candidate is never dropped solely due to graph boosts.

---

## 4. Question 7 Diagnosis (Retrieval vs SQL Generation)

### 4.1 Evidence from Logs

From the recorded test results:

- `tests/7q_full_test_result.json` shows all expected tables were retrieved:
  - `event_history`
  - `t_bz_config_ci_ne_root`
  - `t_bz_config_customer`
- `tests/graph_compare_result.json` shows both baseline and graph-optimized top lists contain the expected tables (`baseline_ok: true`, `graph_ok: true`).
- The generated SQL is missing `t_bz_config_customer` and uses `ALARM_CLEAR_TIME` which is not present in the `event_history` schema.
- `docs/20260105/temperature_data_analysis.md` reports Q7 fails across 600 runs due to column hallucination for recovery time.

References: `tests/7q_full_test_result.json`, `tests/graph_compare_result.json`, `docs/20260105/temperature_data_analysis.md`, `fusionsql/schemas/event_history.json`.

### 4.2 Diagnosis

Q7 failed due to SQL generation, not retrieval:

- Retrieval: PASS. All required tables appear in the candidate list.
- Graph reranking: PASS. Expected tables remain in the top list after graph optimization.
- SQL generation: FAIL. The model omitted the customer table and hallucinated a recovery-time column.

Primary failure modes for Q7:
1. Schema hallucination: "recovery time" is not represented in `event_history` (only `EVENT_TIME`, `ACK_TIME`, `ACTION_TIME`).
2. Join omission: the SQL chooses to hardcode a customer id instead of joining `t_bz_config_customer`.
3. Query semantics: "a certain customer" is treated as a known id, causing missing join.

If logs were unavailable, the most likely theoretical failure modes would be:
- Retrieval miss of a dimension table (`t_bz_config_customer`).
- Graph pruning removing a necessary table due to missing edges.
- SQL generation failing to assemble the multi-hop join path.

---

## 5. Data View (Detailed Run Data)

This section is a placeholder for inserting per-run edge weights and graph metrics. Paste the extracted edge list and scores here when available.

```
# Detailed Run Data (to be filled)
# Format example:
# source_table | target_table | relation_type | weight | notes
# -----------------------------------------------------------
# event_history | t_bz_config_ci_ne_root | IS | 1.0 | FK: NE_ID
# event_history | t_bz_config_customer | MOSTLYIS | 0.2 | inferred
```

---

## 6. Summary of Key Points

- Edge weights are assigned strictly by relationship type: `IS=1.0`, `MOSTLYIS=0.2`.
- PPR uses a uniform seed distribution over BGE candidates and weighted transitions.
- The current hybrid scoring is boost-only and does not truncate candidates.
- Single-table queries can still be harmed if downstream top-K selection ignores semantic-only winners.
- Q7 failures are caused by SQL generation (missing join and column hallucination), not retrieval.

