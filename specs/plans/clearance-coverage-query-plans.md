# Clearance coverage reads: query plans and what they show (I-26)

Date: 2026-11-16. Clearance 0.51.0 on the hangar-dev lab. Owner decision A-15 allowed
read-only `EXPLAIN (ANALYZE, BUFFERS)` in the lab's Clearance database.

## What was run

- Once, at 14:43Z, as the read-only role (`clearance_reader`), with
  `default_transaction_read_only = on`. Plan text only: no record contents were returned.
- Scope `hangar-prod` (the busiest), window 2026-11-15T14:43Z to 2026-11-16T14:43Z.
- Eight statements: the first page of each of the six evidence kinds the coverage statement
  reads, one later page of `observation`, and the health look-back (`HealthBefore`).
- The statements are the store's own SQL at v0.51.0 (`internal/api/pgstore.go`), with literal
  values where the app sends bind parameters. A generic plan in the app could differ.

Table: 81,366 records, 180 MB heap and TOAST, 26 MB of indexes, all 16 indexes valid.
In the window the scope has about 7,660 observations and 7,660 assessments.

## Findings

| Read | Plan | Time | Buffers | Problem |
|---|---|---|---|---|
| observation, page 1 | `obs_ts` index scan, filter, top-N sort | 243 ms | 17,939 | reads all 15,322 rows of the window for 200 |
| observation, later page | same | 97 ms | 16,203 | same work again on every page |
| assessment, page 1 | same | 57 ms | 12,721 | same |
| resolution, page 1 | `observed` backward | 2.5 ms | 1,123 | none |
| observation.verification | `verification` backward | 0.04 ms | 1 | none |
| observation.health, page 1 | `health` backward | 4.7 ms | 2,015 | none |
| observation.audit-gap | `observed` backward | 285 ms | 62,839 | walks 48,520 rows to find 2 |
| health look-back | `health` scan, sort, window | 156 ms | 91,887 | reads all 7,043 earlier health records |

1. **Observations and assessments are re-read in full for every page.** The store pages by
   `seq` 200 at a time (about 39 pages per kind here). The planner picks the
   `(scope, ts)` index, which holds both kinds, reads the whole window, discards half by
   kind, sorts by `seq` and keeps 200. About 78 pages at 57 to 243 ms each accounts for the
   3.3 to 3.8 s answers. Cost grows with the square of the records in the window.
   The planner's row estimate is 1 where 7,661 rows match, so it never chooses the per-kind
   index walk.
2. **Audit gaps walk the scope's history.** Few rows match, so the backward scan of the
   shared partial index filters almost everything it reads. Grows with history.
3. **The health look-back reads every earlier health record for the scope.** Grows for ever.

Not a cause: the three kinds whose first page comes straight from a per-kind or small
partial index. Decompressing the JSONB value is part of every row read but only matters
because of the row counts above.

## Fix directions (not built, to be chosen)

- Read each kind in one ordered pass (or with a keyset on the index order) so a window is
  read once, not once per page.
- An index per kind on `(scope, ts, seq)` for the two large kinds, so a page is an index
  range and not a filter and sort.
- A partial index for audit gaps, and a bound or a per-source "latest healthy" lookup for
  the health look-back, so both stop early.
- After that: aggregate in SQL behind a flag, with a byte-equality test against the
  current answer.

Limits: one run, one scope, lab data, literal values. Timings include cold reads on the
first statement.

## Plans

```
QUERY PLAN
 Limit  (cost=8.34..8.34 rows=1 width=53) (actual time=242.637..242.663 rows=200.00 loops=1)
   Buffers: shared hit=15605 read=2334
   ->  Sort  (cost=8.34..8.34 rows=1 width=53) (actual time=242.635..242.644 rows=200.00 loops=1)
         Sort Key: seq DESC
         Sort Method: top-N heapsort  Memory: 830kB
         Buffers: shared hit=15605 read=2334
         ->  Index Scan using clearance_evidence_obs_ts on clearance_evidence e  (cost=0.29..8.33 rows=1 width=53) (actual time=0.580..235.076 rows=7661.00 loops=1)
               Index Cond: (((record ->> 'scope'::text) = 'hangar-prod'::text) AND ((record ->> 'ts'::text) >= '2026-11-15T14:43:00Z'::text) AND ((record ->> 'ts'::text) < '2026-11-16T14:43:00Z'::text))
               Filter: ((record ->> 'tool'::text) = ANY ('{observation}'::text[]))
               Rows Removed by Filter: 7661
               Index Searches: 1
               Buffers: shared hit=15602 read=2334
 Planning:
   Buffers: shared hit=416 read=35
 Planning Time: 5.053 ms
 Execution Time: 243.024 ms
(16 rows)

QUERY PLAN
 Limit  (cost=8.33..8.34 rows=1 width=53) (actual time=57.335..57.350 rows=200.00 loops=1)
   Buffers: shared hit=12720 read=1
   ->  Sort  (cost=8.33..8.34 rows=1 width=53) (actual time=57.334..57.341 rows=200.00 loops=1)
         Sort Key: seq DESC
         Sort Method: top-N heapsort  Memory: 830kB
         Buffers: shared hit=12720 read=1
         ->  Index Scan using clearance_evidence_obs_ts on clearance_evidence e  (cost=0.29..8.32 rows=1 width=53) (actual time=0.033..55.342 rows=7666.00 loops=1)
               Index Cond: (((record ->> 'scope'::text) = 'hangar-prod'::text) AND ((record ->> 'ts'::text) >= '2026-11-15T14:43:00Z'::text))
               Filter: ((record ->> 'tool'::text) = ANY ('{assessment}'::text[]))
               Rows Removed by Filter: 7666
               Index Searches: 1
               Buffers: shared hit=12720 read=1
 Planning Time: 0.168 ms
 Execution Time: 57.372 ms
(14 rows)

QUERY PLAN
 Limit  (cost=0.42..36.11 rows=1 width=53) (actual time=0.160..2.464 rows=200.00 loops=1)
   Buffers: shared hit=1101 read=22
   ->  Index Scan Backward using clearance_evidence_observed on clearance_evidence e  (cost=0.42..36.11 rows=1 width=53) (actual time=0.159..2.453 rows=200.00 loops=1)
         Index Cond: ((record ->> 'scope'::text) = 'hangar-prod'::text)
         Filter: (((record ->> 'tool'::text) = ANY ('{resolution}'::text[])) AND ((record ->> 'ts'::text) >= '2026-11-15T14:43:00Z'::text))
         Rows Removed by Filter: 780
         Index Searches: 1
         Buffers: shared hit=1101 read=22
 Planning Time: 0.171 ms
 Execution Time: 2.481 ms
(10 rows)

QUERY PLAN
 Limit  (cost=0.14..9.94 rows=1 width=53) (actual time=0.027..0.028 rows=0.00 loops=1)
   Buffers: shared read=1
   ->  Index Scan Backward using clearance_evidence_verification on clearance_evidence e  (cost=0.14..9.94 rows=1 width=53) (actual time=0.027..0.027 rows=0.00 loops=1)
         Index Cond: ((record ->> 'scope'::text) = 'hangar-prod'::text)
         Filter: ((record ->> 'ts'::text) >= '2026-11-15T14:43:00Z'::text)
         Index Searches: 1
         Buffers: shared read=1
 Planning:
   Buffers: shared hit=2 read=1
 Planning Time: 0.123 ms
 Execution Time: 0.038 ms
(11 rows)

QUERY PLAN
 Limit  (cost=0.29..11.88 rows=1 width=53) (actual time=0.055..4.718 rows=200.00 loops=1)
   Buffers: shared hit=2009 read=6
   ->  Index Scan Backward using clearance_evidence_health on clearance_evidence e  (cost=0.29..11.88 rows=1 width=53) (actual time=0.054..4.704 rows=200.00 loops=1)
         Index Cond: ((record ->> 'scope'::text) = 'hangar-prod'::text)
         Filter: (((record ->> 'ts'::text) >= '2026-11-15T14:43:00Z'::text) AND ((record ->> 'ts'::text) < '2026-11-16T14:43:00Z'::text))
         Rows Removed by Filter: 1
         Index Searches: 1
         Buffers: shared hit=2009 read=6
 Planning:
   Buffers: shared hit=3
 Planning Time: 0.131 ms
 Execution Time: 4.735 ms
(12 rows)

QUERY PLAN
 Limit  (cost=0.42..36.17 rows=1 width=53) (actual time=14.723..284.672 rows=2.00 loops=1)
   Buffers: shared hit=55772 read=7067 written=18
   ->  Index Scan Backward using clearance_evidence_observed on clearance_evidence e  (cost=0.42..36.17 rows=1 width=53) (actual time=14.722..284.668 rows=2.00 loops=1)
         Index Cond: ((record ->> 'scope'::text) = 'hangar-prod'::text)
         Filter: (((record ->> 'tool'::text) = ANY ('{observation.audit-gap}'::text[])) AND ((record ->> 'ts'::text) >= '2026-11-15T14:43:00Z'::text) AND ((record ->> 'ts'::text) < '2026-11-16T14:43:00Z'::text))
         Rows Removed by Filter: 48520
         Index Searches: 1
         Buffers: shared hit=55772 read=7067 written=18
 Planning Time: 0.093 ms
 Execution Time: 284.686 ms
(10 rows)

QUERY PLAN
 Limit  (cost=8.34..8.34 rows=1 width=53) (actual time=97.100..97.120 rows=200.00 loops=1)
   Buffers: shared hit=14967 read=1236
   ->  Sort  (cost=8.34..8.34 rows=1 width=53) (actual time=97.099..97.112 rows=200.00 loops=1)
         Sort Key: seq DESC
         Sort Method: top-N heapsort  Memory: 830kB
         Buffers: shared hit=14967 read=1236
         ->  Index Scan using clearance_evidence_obs_ts on clearance_evidence e  (cost=0.29..8.33 rows=1 width=53) (actual time=0.044..93.799 rows=6393.00 loops=1)
               Index Cond: (((record ->> 'scope'::text) = 'hangar-prod'::text) AND ((record ->> 'ts'::text) >= '2026-11-15T14:43:00Z'::text) AND ((record ->> 'ts'::text) < '2026-11-16T14:43:00Z'::text))
               Filter: ((seq < 80000) AND ((record ->> 'tool'::text) = ANY ('{observation}'::text[])))
               Rows Removed by Filter: 8929
               Index Searches: 1
               Buffers: shared hit=14967 read=1236
 Planning:
   Buffers: shared hit=12
 Planning Time: 0.231 ms
 Execution Time: 97.151 ms
(16 rows)

QUERY PLAN
 Sort  (cost=11.94..11.95 rows=1 width=53) (actual time=156.238..156.240 rows=1.00 loops=1)
   Sort Key: h.seq
   Sort Method: quicksort  Memory: 28kB
   Buffers: shared hit=91211 read=676
   ->  Subquery Scan on h  (cost=11.88..11.93 rows=1 width=53) (actual time=156.232..156.234 rows=1.00 loops=1)
         Filter: (h.seq >= COALESCE(h.aseq, '-1'::bigint))
         Rows Removed by Filter: 7042
         Buffers: shared hit=91211 read=676
         ->  WindowAgg  (cost=11.88..11.92 rows=1 width=885) (actual time=155.156..155.877 rows=7043.00 loops=1)
               Window: w1 AS (PARTITION BY (COALESCE(((e.record -> 'source'::text) ->> 'name'::text), ''::text)))
               Storage: Memory  Maximum Storage: 912kB
               Buffers: shared hit=91208 read=676
               ->  Sort  (cost=11.88..11.88 rows=1 width=877) (actual time=78.003..78.722 rows=7043.00 loops=1)
                     Sort Key: (COALESCE(((e.record -> 'source'::text) ->> 'name'::text), ''::text))
                     Sort Method: quicksort  Memory: 985kB
                     Buffers: shared hit=49720 read=676
                     ->  Index Scan using clearance_evidence_health on clearance_evidence e  (cost=0.29..11.87 rows=1 width=877) (actual time=0.044..76.385 rows=7043.00 loops=1)
                           Index Cond: ((record ->> 'scope'::text) = 'hangar-prod'::text)
                           Filter: ((record ->> 'ts'::text) < '2026-11-15T14:43:00Z'::text)
                           Rows Removed by Filter: 1438
                           Index Searches: 1
                           Buffers: shared hit=49718 read=675
 Planning:
   Buffers: shared hit=5
 Planning Time: 0.210 ms
 Execution Time: 156.377 ms
(26 rows)
```
