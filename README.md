# StageQ

    StageQ is an opinionated, modern runtime architecture for kdb+/q systems, replacing legacy TorQ / tick / discovery.q / cron-based q scripts with Kafka, Airflow, Prometheus, Consul, and systemd.

StageQ is **not** a replacement for kdb+/q itself.
It is a reference architecture + tooling set that defines how q-based components
can be scheduled, discovered, monitored, and orchestrated using modern infrastructure.

## Motivation

Traditional kdb+/q deployments usually rely on:

- tick.q + chained TP / RDB / HDB

- TorQ-style components and control channels

- cron, r.q, w.q for orchestration

- custom heartbeat scripts between q processes

- discovery.q for service lookup and startup order

These approaches:

- tightly couple business logic with process control

- make observability and failure diagnosis difficult

- scale poorly outside a single machine or small cluster

- are hard to integrate with modern infra and ops tooling

StageQ separates q logic from **control**, **scheduling**, and **observability**.

## Core Principles

- q focuses **on computation**, not *orchestration*

- One responsibility per component

- Externalized control plane

- Observable by default

- Replace scripts with contracts

## Architecture Overview

StageQ replaces the traditional q runtime ecosystem with the following mapping:

| Legacy kdb+/q Concept | StageQ Replacement |
| -- | -- |
| tick / TorQ pubsub |	kafkax (Kafka / Redpanda) |
| New K struct in C | qipc + -9! |
| r.q / w.q / cron | Apache Airflow |
| heartbeat.q	| Prometheus metrics |
| ad-hoc perf logs	| Prometheus + Grafana |
| discovery.q	| Consul |
| manual startup | systemd |

## Components
1. Data Plane

    - Kafka / Redpanda

        Acts as the unified data backbone

        Replaces tick-style pub/sub and chained TP routing

    - kafkax

        Thin C++/ABI layer for consuming Kafka data into q

        Decoder-based plugin architecture

    - qipc

        High-performance q IPC encoding/decoding

        Explicit schema → bytes → q object mapping

**Result**: data flow is explicit, replayable, and decoupled from process topology.

---

2. Control Plane (Airflow)

Airflow replaces:

    - cron

    - ad-hoc q-based control scripts

Usage model:
    
- Each q component is treated as a managed service

- Airflow DAGs:

    1. start / stop / restart q processes

    2. run EOD jobs

    3. manage dependencies (RDB(WDB) before HDB, etc.)

- Python subprocess is used intentionally for:

    1. stronger state tracking

    2. retries and failure semantics

    3. better observability than q scripts

    Airflow is the control brain, q is the compute engine.

--- 

3. Observability (Prometheus + Grafana)

StageQ fully replaces q-based heartbeat logic.

Each component exposes:

- /metrics endpoint (Prometheus format)

- standard labels: service, instance, role, env

- Typical metrics:

- process liveness (heartbeat)

- message throughput

- queue depth

- decode latency

- error counters

Grafana dashboards replace:

- log-grepping

- manual .Q.w[] checks

- custom heartbeat tables

Prometheus is the single source of truth for runtime health.

4. Service Discovery (Consul + systemd)

    StageQ replaces discovery.q with industry-standard service discovery.

- systemd

    responsible for process lifecycle

    restarts, limits, environment injection

- Consul

    registers services on startup

    provides:

        service discovery

        health checks

    optional config KV

    q processes do not discover each other directly.


Discovery is external, explicit, and queryable.

## What StageQ Is Not

❌ Not a TorQ rewrite

❌ Not a q framework

❌ Not a “one-click platform”

❌ Not hiding infrastructure from users

StageQ assumes:

- you understand kdb+/q

- you want more control, not less

- you prefer explicit contracts over magic



## Philosophy

- q should compute.
- Infrastructure should orchestrate.
- Observability should be boring and reliable.

StageQ exists to make that separation real.