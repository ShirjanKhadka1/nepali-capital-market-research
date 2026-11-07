"""Criteria-grammar screen for the NEPSE scanner. Research only,
never a recommendation.

Idea adapted from FinceptTerminal (AGPL-3.0, commit 7716ee8): a
screener as field/operator/value clauses with an audit log of how
many names each clause removed. No Fincept code, text, or syntax was
copied — the grammar and the implementation below are written from
scratch for this scanner's rows, and the idea is attributed in
scanner/SOURCES_MERGE_2026-11-07.md. The result is a list of rows
that matched a rule, never a recommendation.

Grammar
-------
criteria is a list of dicts, applied in order:
    {"field": "rsi14", "op": "<", "value": 30}

Operators: ">" , ">=", "<", "<=", "==", "between".
"between" takes a two-element [lo, hi] list and is inclusive on both
ends. Every other operator takes a single value.

A row matches a clause when its field value is not None and the
comparison holds. None means "no data for this indicator" (see
indicators.py) — a row with no data never matches a numeric clause,
so it is removed by that clause and the removal is counted in the
audit log, exactly like any other removal.

screen() returns {"rows", "audit", "criteria"}:
- "rows": the rows that survived every clause, in input order.
- "audit": one entry per clause, in order: {"clause", "removed",
  "remaining"} — how many names that clause removed and how many
  were left after it. A screen is auditable: replay the clauses in
  order and the counts reproduce.
- "criteria": the criteria as passed in.

Errors are loud, not silent: an unknown operator, a malformed
"between" value, a field missing from a row, or a value that cannot
be compared with the clause value all raise ValueError naming the
problem. A typo in a field name must never silently empty a screen.

Standard library only.
"""

OPS = (">", ">=", "<", "<=", "==", "between")


def _validate_clause(clause):
    if not isinstance(clause, dict):
        raise ValueError(f"screen: each criterion must be a dict, "
                         f"got {clause!r}")
    field = clause.get("field")
    op = clause.get("op")
    if "value" not in clause:
        raise ValueError(f"screen: criterion {clause!r} has no 'value'")
    value = clause["value"]
    if not isinstance(field, str) or not field:
        raise ValueError(f"screen: criterion {clause!r} has no 'field'")
    if op not in OPS:
        raise ValueError(f"screen: unknown operator {op!r} in {clause!r}; "
                         f"operators are {', '.join(OPS)}")
    if op == "between":
        if (not isinstance(value, (list, tuple)) or len(value) != 2):
            raise ValueError(
                f"screen: 'between' needs a [lo, hi] value, got {value!r}")
        if value[0] > value[1]:
            raise ValueError(
                f"screen: 'between' needs lo <= hi, got {value!r}")
    return field, op, value


def _matches(row, field, op, value):
    if field not in row:
        raise ValueError(f"screen: unknown field {field!r} — no row has it")
    actual = row[field]
    if actual is None:
        return False  # no data never matches a numeric clause
    try:
        if op == ">":
            return actual > value
        if op == ">=":
            return actual >= value
        if op == "<":
            return actual < value
        if op == "<=":
            return actual <= value
        if op == "==":
            return actual == value
        return value[0] <= actual <= value[1]  # between, inclusive
    except TypeError as exc:
        raise ValueError(
            f"screen: field {field!r} value {actual!r} cannot be compared "
            f"with {value!r}") from exc


def screen(rows, criteria):
    """Filter `rows` (a list of dicts, e.g. scanner rows) by `criteria`,
    a list of {"field", "op", "value"} dicts applied in order.

    Returns {"rows", "audit", "criteria"} — see the module docstring.
    An empty criteria list returns every row unchanged, with an empty
    audit log.
    """
    if not isinstance(criteria, (list, tuple)):
        raise ValueError("screen: criteria must be a list of dicts")
    clauses = [_validate_clause(c) for c in criteria]
    remaining = list(rows)
    audit = []
    for clause, (field, op, value) in zip(criteria, clauses):
        before = len(remaining)
        remaining = [r for r in remaining
                     if _matches(r, field, op, value)]
        audit.append({
            "clause": clause,
            "removed": before - len(remaining),
            "remaining": len(remaining),
        })
    return {"rows": remaining, "audit": audit, "criteria": list(criteria)}
