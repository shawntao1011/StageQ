# Q Runtime Options Design

## Goal

This document explains how StageQ models and resolves q startup options.

The key requirement is:

- q has executable-level startup flags that must be passed when the process starts
- service and job workloads have different default expectations
- environment and instance config must be able to override those defaults
- the final launcher should only consume resolved startup options

---

## Design Principles

### 1. Separate final values from default policies

`QRuntimeOptions` represents the **final startup option values** for q.

It must not be treated as the place where service/job defaults are hardcoded.

Why:

- service and job workloads have different runtime expectations
- dev and prod environments may also differ
- instance-specific overrides must be possible

So we separate:

- final value model
- default policy profile
- overlay/merge process

---

### 2. All option fields are optional

Each field in `QRuntimeOptions` should default to `None`.

Meaning:

- `None` → not specified at this layer
- concrete value → explicitly specified at this layer

This avoids mixing together:

- q intrinsic default behavior
- StageQ workload defaults
- environment defaults
- instance overrides

---

### 3. Workload defaults belong to profiles

Service and job are different workload types.

Examples:

- service usually wants a more conservative runtime posture
- job usually wants a lighter-weight runtime posture

This difference should be expressed by workload-level profiles, not by hardcoded dataclass defaults.

---

## Layer Model

Final q startup options are resolved through layered overlays:

```text
q intrinsic defaults
  < workload profile defaults
  < environment defaults
  < instance overrides
```

---

## Service Startup Config Model

StageQ service startup config is grouped into three objects:

1. `QRuntimeOptions`
   - Source of q executable startup flags (e.g. `-p`, `-s`, `-u`)
   - Resolved via 4-layer merge above
   - Rendered into q argv

2. `QBootstrapConfig`
   - StageQ bootstrap entry and preload libraries
   - Usually provided directly by service instance config
   - Currently uses direct final values (no complex merge policy yet)

3. `service_config`
   - Business/service payload consumed by q bootstrap code
   - Currently usually provided as final instance values
   - Can later be expanded to include environment/business defaults

This separation keeps q executable concerns isolated from bootstrap and
business config concerns.

---

## Canonical Service Schema

Resolver requires a canonical schema for q services:

```yaml
runtime:
  kind: q

q_runtime:
  bootstrap: src/stageq/q/bootstrap/bootstrap.q
  options:
    port: 32120
    secondary_threads: 4
  libraries:
    - src/stageq/q/common/util.q
```

This keeps startup config explicit and removes ambiguity in resolver behavior.