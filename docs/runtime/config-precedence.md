# StageQ 配置 Overlap 优先级

本文说明 StageQ 中不同配置域的覆盖（overlap）规则与优先级。

---

## 1. q 启动参数（`QRuntimeOptions`）优先级

最终 q 启动参数通过多层 overlay 生成，优先级（低 -> 高）：

1. q 进程自身默认值（q intrinsic defaults）
2. StageQ 服务默认值（`Q_RUNTIME_DEFAULTS_FOR_SERVICE`）
3. 环境默认值（`config/environments/<env>.yaml` 中 `q_runtime_defaults`）
4. 服务实例覆盖（`config/services/<service>.yaml` 中 `q_runtime.options`）

解析代码在：

- `src/stageq/ctl/resolver.py`
- `src/stageq/codec/q_runtime.py`
- `src/stageq/model/runtime.py`

> 规则是“最后出现的非 `None` 值覆盖前面”。

---

## 2. Bootstrap 相关配置优先级

当前版本中，`q_runtime.bootstrap` 与 `q_runtime.libraries` 来自 service 文件的最终值（无额外 merge 层）：

- `config/services/<service>.yaml`
  - `q_runtime.bootstrap`
  - `q_runtime.libraries`

这些值被解析后写入 `config.q` 的 `.stageq.libs`，供 bootstrap 加载。

---

## 3. service_config（业务配置）优先级

当前版本中，`service_config` 直接取 service 文件值（无环境层 merge）：

- `config/services/<service>.yaml` -> `service_config`

之后由 launcher 渲染到 `config.q` 的 `.stageq.cfg`。

---

## 4. 启动命令组成（边界说明）

最终 q 启动命令由两部分组成：

1. q 可执行级参数：来自上面的 `QRuntimeOptions` merge 结果（如 `-p`, `-s`, `-u`）。
2. bootstrap 文件路径：`q_runtime.bootstrap`。

不再包含 service 上下文参数（如 `-name/-env/-config`），因为上下文由 runtime home + `config.q` 承载。