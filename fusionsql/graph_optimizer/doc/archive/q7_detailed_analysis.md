# Q7 Detailed Analysis (Graph Optimizer Pipeline)

## 1) Question identification

Test set entry (from `tests/test_7q.py`):
- Q7 question: 某客户设备近一周内发生过哪些类型的告警？具体告警时间和恢复时间分别是什么？
- Expected tables:
  - `event_history`
  - `t_bz_config_ci_ne_root`
  - `t_bz_config_customer`

## 2) Data sources used

- Retrieval/SQL run output: `tests/7q_full_test_result.json`
- Graph vs baseline table list: `tests/graph_compare_result.json`
- BGE score list and Neo4j relation check: `fusionsql/graph_optimizer/docs/REPORT.md`
- Graph optimizer logic: `fusionsql/graph_optimizer/optimizer.py`
- Edge weights: `fusionsql/graph_optimizer/config.py`
- Schema check: `fusionsql/schemas/event_history.json`

## 3) Pipeline stage analysis

### 3.1 Retrieval stage (BGE)

Q7 BGE top-15 tables (from `tests/7q_full_test_result.json`):

1. `t_bz_config_ci_ne_root`  (expected)
2. `t_gn_business_application_change`
3. `t_bz_config_customer`    (expected)
4. `t_bz_incident_info`
5. `event_yjk_history`
6. `ne_syslog_filter_script`
7. `syslog_filter_script`
8. `event_history`            (expected)
9. `event_sdn`
10. `t_gn_botnet`
11. `event_backup`
12. `event_history_sdwan`
13. `ne_business_severity`
14. `report_new_dev`
15. `event_knowledge`

BGE scores (from `fusionsql/graph_optimizer/docs/REPORT.md`, Q7 section):

| Rank | Table | BGE Score | Expected |
| ---: | --- | ---: | :---: |
| 1 | `t_bz_config_ci_ne_root` | 2.8992 | yes |
| 2 | `t_gn_business_application_change` | 2.3083 | no |
| 3 | `t_bz_config_customer` | 2.2421 | yes |
| 4 | `t_bz_incident_info` | 1.6026 | no |
| 5 | `event_yjk_history` | 1.5262 | no |
| 6 | `ne_syslog_filter_script` | 1.5040 | no |
| 7 | `syslog_filter_script` | 1.3781 | no |
| 8 | `event_history` | 1.3289 | yes |
| 9 | `event_sdn` | 1.1864 | no |
| 10 | `t_gn_botnet` | 1.1830 | no |

Retrieval verdict:
- PASS. All 3 expected tables are in the BGE shortlist (ranks 1, 3, 8).

### 3.2 Graph stage (Graph Optimizer)

Graph optimizer behavior (current default `hybrid`):
- Boost-only scoring; no truncation in `hybrid`.
- Candidates are retained; graph features only add score.

Observed output list (from `tests/graph_compare_result.json`):
- Graph result top-10 is identical to baseline top-10.
- The three expected tables remain present.

Neo4j relation check (from `fusionsql/graph_optimizer/docs/REPORT.md`, Q7 section):
- Querying relationships among the BGE candidate list returns 0 edges.
- No `IS` or `MOSTLYIS` edges were found between the top tables in that run.

Edge weights (config):
- `IS` = 1.0
- `MOSTLYIS` = 0.2

Edge weights between Q7 candidate nodes:
- None in the recorded run (0 edges among candidates).
- As a result, there are no per-node edge weights to list for Q7 candidates.

Score implications when there are no candidate-to-candidate edges:
- Connectivity is 0 for all candidates (no direct neighbors in the top-10 reference set).
- PPR becomes uniform across seeds if the subgraph has no edges.
- Degree score is 0 if missing from cache.
- Graph boost is equal (or 0) for all candidates, so the ranking follows the BGE order.

Graph-stage verdict:
- PASS. The graph algorithm did not filter out any expected table.

### 3.3 SQL generation stage

Generated SQL (from `tests/7q_full_test_result.json`):

```sql
SELECT DISTINCT 
    e.EVENT_TYPE_NAME AS alarm_type,
    e.EVENT_TIME AS alarm_time,
    e.ALARM_CLEAR_TIME AS recovery_time
FROM 
    event_history e
JOIN 
    t_bz_config_ci_ne_root n ON e.NE_ID = n.NE_ID
WHERE 
    n.CUSTOMER_ID = 12345
    AND e.EVENT_TIME >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND e.ALARM_CLEAR_TIME IS NOT NULL
    AND e.EVENT_STATUS_NAME = 'alarm'
ORDER BY 
    e.EVENT_TIME DESC;
```

Reference SQL (from `tests/test_7q.py`):

```sql
SELECT
  `t_bz_config_customer`.`CUSTOMER_NAME`,
  `t_bz_config_ci_ne_root`.`HOST_NAME`,
  `event_history`.`EVENT_NAME`,
  `event_history`.`EVENT_TIME`
FROM `event_history`
JOIN `t_bz_config_ci_ne_root` ON `event_history`.`NE_ID` = `t_bz_config_ci_ne_root`.`NE_ID`
JOIN `t_bz_config_customer` ON `event_history`.`CUSTOMER_ID` = `t_bz_config_customer`.`CUSTOMER_ID`
WHERE `event_history`.`EVENT_TIME` >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
  AND `event_history`.`EVENT_STATUS_NAME` = 'alarm'
LIMIT 10;
```

SQL-stage issues:
- Missing join to `t_bz_config_customer`.
- Hard-coded `CUSTOMER_ID = 12345` instead of a parameterized join or filter.
- Uses `ALARM_CLEAR_TIME` which does not exist in `event_history` schema (`fusionsql/schemas/event_history.json`).
- The SQL is syntactically valid, but semantically incorrect (wrong/missing columns and join).

SQL-stage verdict:
- FAIL. The failure is in SQL generation, not in retrieval or graph ranking.

## 4) Exact failure point summary

- Retrieval: PASS (expected tables present in BGE shortlist).
- Graph: PASS (boost-only; no pruning; candidates preserved).
- SQL: FAIL (missing `t_bz_config_customer` join and hallucinated recovery-time column).

## 5) Trace / debug availability

A full trace that includes real Neo4j edges, PPR, and connectivity values would require a live Neo4j connection and the BGE retriever runtime (see `tests/test_graph_diagnosis.py`). In this environment, only the existing logs and stored test outputs were available, so the analysis above is grounded in those artifacts.

If you want a live trace later, the minimal repro path is:
- `python tests/test_graph_diagnosis.py`

