# Graph Optimizer Algorithm Evolution (graph_optimizer)

## Scope and sources
This document captures the graph-based table reranking algorithm evolution and the current implementation.
Primary sources:
- `fusionsql/graph_optimizer/optimizer.py`
- `fusionsql/graph_optimizer/algorithms.py`
- `fusionsql/graph_optimizer/config.py`
- `fusionsql/graph_optimizer/doc/algorithm_evolution.md`
- `fusionsql/graph_optimizer/doc/graph_algorithm_detailed_report.md`

## V1.0 - Weighted Average (initial)

Formula (BGE was min-max normalized):

```
final = 0.70 * BGE_norm + 0.15 * PPR + 0.10 * connectivity + 0.05 * degree
```

Key behaviors:
- BGE normalization compressed score gaps between strong/weak candidates.
- Graph features could drag down isolated nodes (no edges -> PPR=0, connectivity=0).
- Hard truncation to `TARGET_TABLES` (default 8) could drop correct tables ranked 9-10.

Isolated node effect in V1:
- With no edges, graph features are 0.
- Final score collapses to `0.70 * BGE_norm`.
- When combined with truncation, this often removed correct but isolated tables.

## V2.0 - Multiplicative Boost (post-review change)

Formula:

```
final = bge_score * (1.0 + 0.3 * graph_features)
```

Changes from V1:
- BGE magnitude preserved; graph is a multiplier rather than a replacement.
- Isolated nodes keep the original BGE score when graph_features=0.

Remaining risk:
- Very high graph features could still let weaker BGE tables overtake stronger ones.

## V3.0 - Boost-Only (current default)

Current formula in `GraphOptimizer._hybrid_selection`:

```
final = bge_score + boost_factor * graph_boost
boost_factor = max_bge_score * 0.3

graph_boost = 0.50 * PPR_norm + 0.35 * connectivity_norm + 0.15 * degree_norm
```

Key changes after previous discussions:
- No BGE normalization.
- Graph features only add (never subtract).
- Connectivity reference set widened to top 10 BGE tables.
- Hybrid strategy returns the full candidate list (no truncation).
- `MOSTLYIS` weight reduced to 0.2 to dampen noisy inferred edges.

## Current algorithm logic (step-by-step)

1. Build subgraph
   - Candidates + 1-hop neighbors from Neo4j.
   - Candidates are always added as nodes, even if isolated.
2. Personalized PageRank
   - Seeds are the BGE candidates (uniform personalization over candidates).
3. Connectivity
   - Direct-edge ratio to the top-10 BGE tables.
4. Degree
   - Global degree centrality from cache (`GraphCache`).
5. Min-max normalization
   - Each feature is normalized across the candidate list.
6. Boost-only scoring
   - Additive graph boost scaled by `max_bge * 0.3`.
   - No truncation in `hybrid` (caller decides final cut).

## Isolated node scoring (explicit)

Definition: an isolated table has no edges in the constructed subgraph.

Behavior in the current pipeline:
- PPR: isolated nodes do not receive flow from neighbors. If the node is a seed, its PPR score equals its personalization mass; otherwise it is 0.
- Connectivity: 0, because there are no neighbors in the top-10 reference set.
- Degree: 0 if missing from the global cache.
- Normalization: 
  - If other nodes have higher values, isolated nodes normalize to 0.
  - If all nodes are isolated (all values equal), normalization returns 1.0 for everyone.
- Final score: `final = BGE + boost_factor * graph_boost`.
  - There is no explicit penalty (no negative term).
  - Relative rank can still drop if other nodes receive positive boost.

Contrast with V1:
- V1 directly reduced the final score to `0.70 * BGE_norm`, and then applied a hard truncation. This is why isolated nodes were effectively penalized in earlier versions.

## Notes on configuration drift

- `config.py` still defines `WEIGHTS`, but the current `hybrid` path does not use them.
- `RELATION_WEIGHTS` are authoritative for edge weights:
  - `IS`: 1.0
  - `MOSTLYIS`: 0.2

