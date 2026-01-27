# Future Strategy: "Top N BGE + Relation Check"

## 1) Advisor suggestion (restated)

"Only look at relationships between the top 10-20 tables selected by BGE."

Interpretation:
- No neighbor expansion beyond the BGE shortlist.
- Only consider edges that exist among those top-N candidates.
- Use those edges to validate or slightly rerank candidates.

## 2) How current code differs

Current `hybrid` strategy (`fusionsql/graph_optimizer/optimizer.py`):
- Expands candidates to include 1-hop neighbors (via `Neo4jClient.get_connected_tables`).
- Builds a subgraph over candidates + neighbors.
- Runs PPR on the expanded subgraph, not strictly on top-N.
- Uses global degree cache as a prior.
- Returns all candidates (no truncation in `hybrid`).

Net effect:
- The algorithm considers relationships outside the top-N list.
- Graph signals can be influenced by nodes not retrieved by BGE.
- The advisor’s "top-N-only" constraint is not enforced today.

## 3) What "Top N BGE + Relation Check" would look like

### Core behavior
1. Take top-N BGE candidates only (N in [10, 20]).
2. Query Neo4j for edges *only* among those N tables.
3. If edges exist, use them to boost or validate connected tables.
4. If no edges exist, fall back to pure BGE ordering.

### Minimal scoring variant (simple relation check)
- For each candidate, compute degree within the top-N subgraph.
- Add a small boost if degree > 0.
- Keep boost-only behavior to avoid penalizing isolated tables.

### Stronger variant (restricted PPR)
- Run PPR using only the top-N subgraph.
- Use the PPR score as a boost term, still scaled by max BGE.

## 4) Concrete implementation sketch

### New strategy entry point
Add a strategy in `GraphOptimizer.optimize()`:
- `strategy="topn_relation_check"`

### Subgraph build (no expansion)
Replace the current `_build_subgraph` call with a top-N-only version:

```
# Pseudocode
candidates = candidates[:N]
subgraph_tables = [t for t, _ in candidates]
relationships = neo4j.get_table_relationships(subgraph_tables)
subgraph = TableGraph.from_relationships(relationships)
for t in subgraph_tables:
    subgraph.add_node(t)
```

### Boost-only scoring

```
# Example boost: degree-based (top-N only)
local_degree = {t: len(subgraph.edges.get(t, [])) for t in subgraph_tables}
local_degree_norm = normalize(local_degree)
boost = 0.2 * local_degree_norm
final = bge + max_bge * 0.3 * boost
```

### Fallback behavior
- If `relationships` is empty, return BGE ordering unchanged.
- If the question looks single-table, skip relation check entirely.

## 5) Why this aligns with the advisor’s strategy

- No 1-hop expansion: only relationships among top-N are considered.
- Graph validation is used as a confirmation signal rather than a discovery step.
- Keeps BGE as the primary ranking signal.

## 6) Risks and mitigations

Risks:
- If Neo4j edges are missing or incomplete, the relation check becomes a no-op.
- For true multi-table queries, missing edges can prevent useful re-ranking.

Mitigations:
- Keep boost-only; never drop tables based on missing edges.
- Add a fallback: if top-N has no edges, return BGE list unchanged.
- If graph edges are dense, prefer a small boost to avoid overfitting to graph topology.

## 7) Suggested config knobs

- `TOPN_RELATION_LIMIT = 15` (or 20)
- `TOPN_RELATION_BOOST = 0.2`
- `RELATION_CHECK_MIN_EDGES = 1`

These can be wired into `fusionsql/graph_optimizer/config.py` or passed as parameters.

