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