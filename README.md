# StageQ

> q should do q things.

StageQ is an infrastructure layer that removes non-essential responsibilities from q
and lets external systems handle them.

---

## Why

Traditional q frameworks push too much into q:

- startup via shell/bat scripts
- service discovery inside q
- tickerplant as system backbone
- control plane mixed with data plane
- weak observability

This does not scale well in modern systems.

---

## What StageQ changes

| Problem | Solution | Result |
|--------|----------|--------|
| sh / bat startup | `stageqctl` (controller) | unified, cross-platform |
| q-internal discovery | Consul | external, system-wide discovery |
| tick as backbone | Kafka / Redpanda | durable, scalable streaming |
| qipc everywhere | qipc → local only | clear boundaries |
| control + data mixed | split planes | cleaner architecture |
| scattered config | YAML/TOML | predictable deployment |
| weak monitoring | Prometheus + health | observable system |

---

## Principle

Let the external world handle infrastructure.

Let q focus on:

- processing
- analytics
- storage
- querying

---
