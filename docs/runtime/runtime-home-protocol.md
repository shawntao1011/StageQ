# StageQ Runtime Home 启动协议

## 1. 目标

StageQ 的 q service 启动上下文不再通过一组 CLI 参数（如 `-name/-env/-config`）或注入环境变量传递，而是通过 **实例级 runtime home** 承载。

即：launcher 在启动前准备目录，q bootstrap 只依赖 `cwd` 和固定文件名。

---

## 2. 目录约定

每个 service instance 的运行目录：

```text
<repo>/var/runtime/<env>/<service_name>/
```

示例：

```text
var/runtime/dev/hdb.hk/
var/runtime/prod/wdb.hk/
```

该目录下固定文件名：

- `config.q`
- `service.pid`
- `service.log`
- `cmdline`

---

## 3. Launcher 流程（Python）

`launch_service(root, service, env)` 的关键步骤：

1. `resolve_service_config` 得到合并后的配置。
2. 计算 runtime home：`var/runtime/<env>/<service>/`。
3. 生成并写入 `runtime_home/config.q`。
4. 生成 q argv（仅 q 可执行参数 + bootstrap 文件）。
5. 把 argv 写入 `runtime_home/cmdline`。
6. 以 `cwd=runtime_home` 启动进程，日志写入 `runtime_home/service.log`。
7. pid 写入 `runtime_home/service.pid`。

对应实现：

- `src/stageq/ctl/launcher.py`
- `src/stageq/codec/q_config.py`

---

## 4. Bootstrap 流程（q）

`src/stageq/q/bootstrap/bootstrap.q` 按固定顺序执行：

1. `\l "config.q"`。
2. 校验 `.stageq` 和 `.stageq.libs` 存在。
3. 逐个 `\l` `.stageq.libs` 里的库文件。
4. 若定义了 `.stageq.entry`，调用 `.stageq.entry[]`。

因此 bootstrap 不需要识别“自己是谁”（service/env/name），它只认当前目录和固定文件名。

---

## 5. stop/status 行为

`stop/status` 默认应携带 `--env`，从而定位唯一 runtime home。

- 传入 `env`：读取 `var/runtime/<env>/<service>/service.pid`
- 不传 `env`：若匹配到多个 pid 文件会报错（防止误停/误判）
