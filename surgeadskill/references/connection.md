# 连接、采样和临时验证

核实日期：2026-11-09。实际使用前先运行当前客户端 `--help` / `help 子命令`，不要给旧客户端强塞新接口。

## 连接路径

| 情况 | 操作 |
| --- | --- |
| Mac + 手机均有 Surge，USB 可用 | 首选原生 Dashboard 连接 iPhone；手机仍用自身 VPN/VIF 接管 |
| 现有 Wi-Fi 远程控制已可用 | 复用，不另开端口；确认当前选中手机 |
| USB 不可用且需要 Wi-Fi | 临时启用手机远程控制，只在可信 Wi-Fi 使用，结束恢复 |
| Mac 没有手机日志 | 不要用 Mac 自身请求替代；先解决连接或在手机“最近请求”观察 |

手机 `[General]` 的原生 Dashboard/CLI 控制配置示例（只写入本机副本，密码自行生成，不公开）：

```ini
# USB 专用；此处密码是占位符，端口按实际空闲端口选取。
external-controller-access = LOCAL_RANDOM_PASSWORD@127.0.0.1:6170
```

按官方文档，iOS 此项监听 127.0.0.1 时仅允许 USB；0.0.0.0 才接受本地 Wi-Fi 入站。两者都拒绝蜂窝入站；手机使用蜂窝网络时仍可经 USB 观察。0.0.0.0 仅作用户授权的临时 Wi-Fi 方案，结束恢复原值。Mac 的 127.0.0.1 代理监听继续保留，不改成向局域网共享代理来代替手机远程控制。

在 Mac 中打开 Surge Dashboard，用当前版本提供的设备/连接选择器选 iPhone；解锁并信任电脑。菜单名可能变化，以当前 UI 为准，不捏造“已连接”。先用手机 Safari 发起一个不含账号信息的已知测试请求，确认记录来自手机。

CLI 的 `--remote` 是原生 external-controller-access 端口，**不是** HTTP API 端口。以下 REMOTE 是经验证的手机 Wi-Fi 地址和控制端口；USB 连接若 UI 未提供可供 CLI 使用的转发地址，则用 Dashboard，不假设 Mac localhost 自动指向手机。

```sh
CLI=/Applications/Surge.app/Contents/Applications/surge-cli
REMOTE=192.168.50.20:6170
"$CLI" --help
"$CLI" help dump
"$CLI" help rule temp
"$CLI" --remote "$REMOTE" status
"$CLI" --remote "$REMOTE" rule temp list
```

CLI 会安全交互询问密码，也可从已安全配置的 SURGE_CLI_PASSWORD 环境变量或 `--password-stdin` 读取。不要把密码拼进命令文本、URL、工具输出或 GitHub；非交互环境没有凭据就交给用户配置。

## 观察的最低配置

普通连接的主机、目标地址、规则和策略一般不需要 MITM。优先查看最近请求；需要 HTTP 抓包时先检查“开启抓包自动启用 MITM”的选项，不能因为总开关关闭就假定采集时也不会解密。保留现有 hostname = -* 排除项，不为普通域名排查移除它。

确认过滤器没有隐藏 UDP/QUIC、相关主机或非 HTTP 请求。若修改过滤器，先保存原值、缩小到实验窗口，完成后恢复。缺少请求时也检查 App 使用自己的 DoH、IP 直连、缓存、代理绕过或 VPN 接管缺失。TLS SNI 也可能因协议/加密不可见；“没有域名”不等于可随便封看到的 IP。

使用私有实验目录，避免把全部日志发给模型：

```sh
umask 077
SESSION=$(mktemp -d /private/tmp/surgeadskill.XXXXXX)
"$CLI" --remote "$REMOTE" --raw dump recent > "$SESSION/before-raw.json"
# 用户在手机执行目标操作后，再采集 after。不要后台盲等并声称用户已操作。
"$CLI" --remote "$REMOTE" --raw dump recent > "$SESSION/after-raw.json"
python3 scripts/capture_tools.py normalize --input "$SESSION/before-raw.json" --out "$SESSION/before.json"
python3 scripts/capture_tools.py normalize --input "$SESSION/after-raw.json" --out "$SESSION/after.json"
python3 scripts/capture_tools.py delta --before "$SESSION/before.json" --after "$SESSION/after.json" --out "$SESSION/window.json"
python3 scripts/capture_tools.py report --input "$SESSION/window.json" --out "$SESSION/candidates.json"
```

脚本支持原始请求对象列表、requests/records/entries 包装和 HAR。字段不兼容则失败并仅显示字段名；在本地检查字段后适配，不输出整份请求。快照差集依赖稳定请求 ID 或起始时间；引擎重启、请求列表截断或采样遗漏会使统计不完整。窗口请求数只是所见下界；重做采样或读取保存的 capture-session，不能以“没记录”证明没请求。

已有 HTTP API 或 Surge MCP 连接时可复用来读取请求。HTTP API 使用 X-Key，MCP 默认关闭；不必为了本技能打开 MCP。只用官方已存在端点（例如 GET /v1/requests/recent、GET /v1/external_resources）。控制接口与代理端口不同；HTTP API 无 TLS 时密钥为明文，不把它暴露到不可信网络，不使用跳过证书验证来省事。

## 临时规则实验

以下 example.invalid 为示例，换成观察到的精确广告域名；完整规则带 REJECT，持久 list 条目不带策略。

```sh
"$CLI" --remote "$REMOTE" rule temp list
"$CLI" --remote "$REMOTE" rule temp add 'DOMAIN,ads.example.invalid,REJECT'
"$CLI" --remote "$REMOTE" rule explain ads.example.invalid
# 实际重现 App 广告，并在请求详情确认这条临时规则命中。
"$CLI" --remote "$REMOTE" rule temp remove 'DOMAIN,ads.example.invalid,REJECT'
```

临时规则最高优先级；因此临时测试成功不保证远程列表的正常优先级也能命中。持久化后移除自己的临时规则再测，检查 AdBlock 没被选成 DIRECT，是否有进程/精确直连等更早规则抢先匹配。不要使用 temp flush：它会删除用户别的临时规则。

若当前 CLI 不支持临时规则，使用手机配置的本地副本，只临时插入单条规则并记录插入位置；不覆盖整份代理配置。规则模拟只验证匹配逻辑，不能证明广告消失。

## 官方来源

- [Dashboard 及 USB/Wi-Fi 连接](https://manual.nssurge.com/tools/dashboard.html)
- [CLI，远程认证及当前命令帮助](https://manual.nssurge.com/tools/cli.html)
- [HTTP API、抓包过滤及 MCP](https://manual.nssurge.com/tools/http-api.html)
- [请求接管与规则执行](https://manual.nssurge.com/getting-started/how-surge-works.html)
