# Business Rules

Synthetic rules for this demo. Agents must respect them when planning or
implementing changes.

1. Every write operation must be logged.
2. External API calls require a retry with backoff.
3. No breaking change without a migration — see [[API Contract]].

#rules
