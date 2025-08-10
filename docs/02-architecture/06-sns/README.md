[📖 Docs](../../README.md) > [🏗️ Architecture](../README.md) > **Event Contracts (SNS)**

---

# 📣 Event Contracts (SNS)

Single source of truth for SNS topics and event payloads. Schemas are versioned and accompanied by examples.

## Structure

```
api-contracts/
  events/
    topics.md                # Topic registry and ownership
    examples/                # Example payloads
      <topic>/
        <event>-v1.example.json
    schemas/                 # JSON Schemas (draft-07)
      <topic>/
        <event>-v1.schema.json
```

## Topics Registry

See `topics.md` for canonical topic names, environment suffix rules, and ownership.

## Versioning Policy

- Backward-compatible changes increment minor version (v1.1 → v1.2)
- Breaking changes create new major version file (e.g., `*-v2.schema.json`)
- Old versions remain for at least one release cycle; deprecation is documented in ADRs

## Schemas

- JSON Schema draft-07
- Required fields listed explicitly
- All events include `event_id`, `occurred_at`, and `source`

## Validation

Use these schemas for validation in tests and at publish/consume boundaries.

---

Navigation:
⬅️ Back: [Architecture](../README.md)  
🏠 Home: [Documentation Index](../../README.md)


