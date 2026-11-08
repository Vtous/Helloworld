# Surge 最新功能与配置编写基线

核对日期：2026-11-08，Asia/Taipei。本文用于后续编写 macOS、iOS 配置，版本结论只对本次核对时间成立。

## 1. 当前采用的版本

用户已确认：iPhone 使用 TestFlight 测试版。当前配置目标为 **Surge Mac 6.11 / Surge iOS 6.0 TestFlight**。

| 对象 | 本次查到的版本 | 配置时的含义 |
| --- | --- | --- |
| Mac 正式更新源 | 6.10.0，build 12500，2026-10-12 | 正式版能力下限 |
| Mac 测试更新源 | 6.11.0，build 12740，2026-11-08 | 新引擎能力参考 |
| 用户本机 Mac | 6.11.0，build 12720 | 由应用 Info.plist 读取；本次示例用此版本的 CLI 校验 |
| iOS App Store | 5.23.0；页面标注 10 月 12 日 | 与 iOS 6 TestFlight 区分 |
| iOS TestFlight 产品线 | 6.0 | 官网明确仍属测试版；未读取用户手机的具体 build |

Mac 同一个 6.11.0 版本号下仍可能有多个 build；最新测试源的 12740 比本机 12720 更新。本次没有更新应用或切换任何活动配置。

证据：
- [Mac 官方更新日志](https://nssurge.com/support/mac/release-notes) 的公开脚本加载 [正式 appcast](https://nssurge.com/mac/latest/appcast-signed.xml) 或 [测试 appcast](https://nssurge.com/mac/latest/appcast-signed-beta.xml)。
- [Surge iOS 6 产品页](https://nssurge.com/surge-ios-6/index.html) 明确区分 TestFlight 与 App Store；[iOS 6 更新说明](https://nssurge.com/surge-ios-6/release-notes)。
- [App Store 开发者发布页](https://apps.apple.com/us/app/surge-5/id1442620678)。

版本核对优先使用实际更新源、App Store 与设备 build。旧知识库页面的首条日志可能落后，不能单凭该页推断最新版本。操作系统 iOS/macOS 的版本号与 Surge 的版本号分别记录。

## 2. 新引擎支持的功能

下表“新引擎”指 iOS 6.0 / Mac 6.11；具体 beta 行为仍可能随 build 变化。

| 功能 | 用处与配置要点 | 官方依据 |
| --- | --- | --- |
| 自适应 QUIC 拦截 | 节点参数支持 block-quic=adaptive；auto 会按节点能力处理回退，避免一律封锁 QUIC | [策略参数](https://manual.nssurge.com/policies/parameters.html) |
| 大型规则集 | RULE-SET、DOMAIN-SET 取消原百万条上限；不代表规则越多效果越好 | [规则集](https://manual.nssurge.com/rules/ruleset.html) |
| MCP 控制 | HTTP API 可提供 /v1/mcp；默认关闭，共用 API 密钥 | [HTTP API / MCP](https://manual.nssurge.com/tools/http-api.html#model-context-protocol-mcp-ios-600-mac-6110) |
| 按段修改配置 | API/CLI 可读写单个 section，使用 revision 防止覆盖并发更改，写入前验证完整配置 | [Profile Sections](https://manual.nssurge.com/tools/http-api.html#profile-sections-ios-600-mac-6110) |
| 抓包过滤器与落盘会话 | 可自动化管理抓包范围，读取已保存会话，方便定位广告接口 | [HTTP API](https://manual.nssurge.com/tools/http-api.html)、[CLI](https://manual.nssurge.com/tools/cli.html) |
| 暂避低质量节点 | 自动组可临时跳过“延迟测试正常但实际难用”的节点；属于运行状态，重启后清除 | [Mac 测试更新源](https://nssurge.com/mac/latest/appcast-signed-beta.xml) |
| Tailscale 入站与出口 | 可允许 peer 访问、发布出口或子网路由；控制面仍需批准路由 | [Tailscale](https://manual.nssurge.com/policies/tailscale.html) |
| WireGuard 入站 | listen-port 接收客户端连接，支持移动端点变化 | [WireGuard](https://manual.nssurge.com/policies/wireguard.html) |
| SOCKS5 UDP ASSOCIATE | 内置 SOCKS5 服务可转发 UDP；每个 association 按首个数据报选策略 | [General](https://manual.nssurge.com/profile/general.html)、[Mac 测试更新源](https://nssurge.com/mac/latest/appcast-signed-beta.xml) |
| 自有证书 MITM | 可引用密钥库的目标域名证书；需要拥有有效的对应证书及私钥，不等于通用绕过 App 证书固定 | [MITM](https://manual.nssurge.com/http/mitm.html) |
| 日志容量 | 新增 log-file-size-limit；长期开调试日志前先限制容量 | [Mac 测试更新源](https://nssurge.com/mac/latest/appcast-signed-beta.xml) |

Mac 6.11 还更新了 Dashboard 的流量分解，以及网关 VM 的 UDP Fast Path 控制；这类功能用于分析流量或网关部署，不必写进普通手机去广告配置。[Mac 测试更新源](https://nssurge.com/mac/latest/appcast-signed-beta.xml)

测试版关于 QUIC 判定时序的描述与手册可能暂不同步。配置只使用公开参数和值，不将某个 beta 的毫秒阈值当作长期保证。

## 3. 两个平台的实用配置能力

这些功能已经在较早版本加入，当前目标版本均可用；不能全部称为“6.11 / 6.0 本次新增”。

| 能力 | 版本门槛或平台差异 | 编写方式 |
| --- | --- | --- |
| IP Rewrite | iOS 5.23+ / Mac 6.10+ | reflect、reject、drop 在 VIF 层处理 IP 包 |
| 内联规则集与嵌套规则集 | 当前版本支持；嵌套为 iOS 5.22+ / Mac 6.9+ | 把同类规则集中到 [Ruleset 名称] |
| 同名 Ruleset 跨模块合并 | iOS 5.23+ / Mac 6.10+ | 可由主配置和模块共同贡献条目 |
| 策略组分类 | iOS 5.23+ / Mac 6.10+ | category=分类名，只影响显示 |
| 策略组链式代理 | iOS 5.22+ / Mac 6.9+ | underlying-proxy=已有策略名 |
| HTTPS 延迟测试 | iOS 5.23+ / Mac 6.10+ | test-url、internet-test-url、proxy-test-url 支持 HTTPS |
| 预匹配拒绝 | iOS 5.14+ / Mac 5.9+ | REJECT 规则使用 pre-matching |
| Smart 自动策略 | 当前版本支持 | 依据真实连接表现选节点；成员应为具体代理，不放 DIRECT 或嵌套组 |
| DNS 加密与分域解析 | 当前版本支持 | encrypted-dns-server；[Host] 的 server: 映射 |
| 进程/应用包规则 | 仅 Mac | PROCESS-NAME；iOS 不支持按进程匹配 |
| 外部资源管理 | iOS 5.23+ / Mac 6.10+ | 查看、更新规则集、脚本与外部策略 |
| 编辑器检查 | Mac 6.10+ | 官方 VS Code 扩展配合 surge-cli lsp |

各行依据：
[IP Rewrite](https://manual.nssurge.com/features/ip-rewrite.html)、
[Ruleset](https://manual.nssurge.com/rules/ruleset.html)、
[Module](https://manual.nssurge.com/profile/module.html)、
[Group Parameters](https://manual.nssurge.com/policy-groups/parameters.html)、
[Testing](https://manual.nssurge.com/tools/testing.html)、
[Pre-matching](https://manual.nssurge.com/policies/reject.html)、
[Smart](https://manual.nssurge.com/policy-groups/smart.html)、
[Encrypted DNS](https://manual.nssurge.com/dns/encrypted-dns.html)、
[Process Rules](https://manual.nssurge.com/rules/process.html)、
[HTTP API](https://manual.nssurge.com/tools/http-api.html)、
[CLI / LSP](https://manual.nssurge.com/tools/cli.html)。

### iOS 6 界面方面

新增可整理的首页仪表盘、请求过滤与匹配详情、配置保存历史/比较/回滚、编辑时错误提示；模块更新可查看差异，宽屏采用分栏。这些是客户端操作能力，不需要在规则文件里增加同名参数。[iOS 6 更新说明](https://nssurge.com/surge-ios-6/release-notes)

### 当前网络协议能力

官网列出的代理协议包括 HTTP(S)、SOCKS5、SSH、HTTP/2 CONNECT、MASQUE、Shadowsocks、Trojan、Snell、Hysteria 2、WireGuard、Tailscale 等。能用哪种取决于你的服务器及节点配置，不能只靠更新客户端把旧节点升级成新协议。[官方产品页](https://nssurge.com/)

## 4. 本仓库以后写配置的约定

1. **以用户实际版本为目标。** Mac 6.11、iOS 6 TestFlight 为当前主线；新功能随 build 改动时重新查官方源。
2. **主配置负责节点、分组、DNS、总体路由；模块负责独立功能。** .list 是被引用的规则集合，不等于模块，也不保证作用仅限某一个 App。
3. **保持 MITM 默认关闭。** 可选 HTTPS 处理规则、脚本入口与 MITM 域名配置写在注释中；启用时仍需总开关和证书信任。
4. **保留已有 adgoaway 的工作版本。** 用户反馈它好用；本文不据此宣称全部广告或所有版本都已验证。
5. **规则集区分名字与动作。** [Ruleset] 内不写 REJECT/DIRECT；[Rule] 中通过 RULE-SET 引用时指定策略。
6. **普通规则按先匹配先处理编排，FINAL 放末尾。** 模块会把其规则插入主配置规则前部。
7. **pre-matching 单独评估。** 它在普通白名单前执行；不要以为把一条普通 DIRECT 放到上面就能放行。
8. **预匹配仅用于允许的规则类型。** 不要给含 URL-REGEX/USER-AGENT 等不适用类型的混合大列表盲目加 pre-matching。
9. **不把新参数放错层级。** [General] 的 block-quic=per-policy；节点行的 block-quic=auto/adaptive。二者取值不同。
10. **Smart 组只放真实代理节点。** interval 不控制 Smart 的固定测试周期，不能用缩短 interval 的方式优化它。
11. **公开仓库只存模板和公开规则。** 真实订阅、节点密码、API 密钥、证书私钥和 Tailscale auth-key 留在设备本地。
12. **使用默认网络行为作为起点。** DNS 提供方、强制 IPv6、QUIC 全封、共享代理或网关能力，均按实际网络需要逐项启用。

语义依据：
[Rule 顺序与参数](https://manual.nssurge.com/rules/overview.html)、
[Ruleset 格式](https://manual.nssurge.com/rules/ruleset.html)、
[Module 合并](https://manual.nssurge.com/profile/module.html)、
[预匹配优先级](https://manual.nssurge.com/policies/reject.html)、
[全局选项](https://manual.nssurge.com/profile/general.html)、
[节点参数](https://manual.nssurge.com/policies/parameters.html)、
[Smart](https://manual.nssurge.com/policy-groups/smart.html)。

## 5. 可复用配置与启用范围

仓库附带：

- [Mac 参考配置](../examples/surge-macos-modern.conf)
- [iOS 参考配置](../examples/surge-ios-modern.conf)

两份示例是 **直连参考基线**，不是带你真实代理节点的成品配置，不应直接覆盖当前可用配置。

它们展示：内联广告规则集、预匹配拒绝、策略组分类，以及 QUIC 的正确全局参数。模板默认没有真实节点、远程规则订阅、MITM、运行中的脚本或控制 API。

示例已经内嵌 adgoaway 的 8 条域名规则；不要同时把同一批规则反复添加到主配置和模块。当前已安装的 adgoaway 无需为了此文替换。

### 5.1 内联规则集与预匹配

从现有 8 条域名规则整理到 [Ruleset]；这是组织和拒绝时机的变化，没有扩大域名清单。

示例中的 RULE-SET,LocalAds,REJECT,pre-matching 可在 DNS/TCP 建连早期拒绝，降低建立连接后的处理开销。它不会保证零闪屏，也不会清除缓存。需保留普通白名单优先权时，删去该行末尾的 ,pre-matching 即可。

### 5.2 社区通用去广告列表

blackmatrix7 是社区规则维护者，不是 Surge 官方。其当前文档针对 Surge 5.21.0(2952)+ 提供 Advertising_All.list / Advertising_All_No_Resolve.list 两种单文件方案，二选一，别再把旧的拆分列表全部叠加。

示例的 [Rule] 内保留了 All_No_Resolve 的注释行，默认不开启。不开 MITM 时，其中 HTTPS URL-REGEX 规则不能完整工作，域名/IP 规则仍按自身条件匹配。no-resolve 是减少匹配阶段触发解析的选项，不是关闭 DNS；IP 规则能否命中取决于当前是否已有目的 IP。

[社区作者说明](https://github.com/blackmatrix7/ios_rule_script/blob/master/rule/Surge/Advertising/README.md)；
[Surge 规则集选项](https://manual.nssurge.com/rules/ruleset.html)；
[HTTP 处理前提](https://manual.nssurge.com/http/overview.html)。

### 5.3 QUIC 与策略组

- 全局维持 block-quic=per-policy，让节点参数决定行为。
- 新引擎中支持 UDP 的代理可由 auto 获得自适应处理；DIRECT 不需要为了去广告强制封 QUIC。
- category 只整理显示；underlying-proxy 才建立链式连接。Smart 的 policy-priority 可影响评分。
- 这些策略组配置需要现有真实节点，本文不放不存在的节点名作为可启用配置。

### 5.4 环回、MITM、AI 控制均是独立选项

IP Rewrite 的 reflect 可以承担本机开发工具环回，且不要求 MITM。前面讨论的 Swipt 用法可参考其官方设置：

~~~ini
[General]
tun-included-routes = %INSERT% 10.7.0.1/32

[IP Rewrite]
10.7.0.1 = reflect
~~~

这是一个**模块片段**；%INSERT% 用于模块的追加语义。Swipt 明确表示不需关闭 IPv6；SideStore 的例子有自己的 IPv6 条件，不能混为一谈。[Surge IP Rewrite](https://manual.nssurge.com/features/ip-rewrite.html)、[Swipt 设置](https://swipt.io/zh-Hans/docs/setup/)

MITM 继续使用根目录 adgoaway 中的注释配置。server-certificates 仅对你持有合适目标域名证书及私钥的场景有意义，不能替你取得第三方 App 服务端证书。

MCP 也不需要为了去广告开启。未来确需本机 AI 控制，可在本地配置随机密钥和回环监听，再开启 http-api-mcp；手机供 Mac 远程访问则另配可信网络监听，不把示例中的公开占位密钥直接投入使用。[HTTP API / MCP](https://manual.nssurge.com/tools/http-api.html)

### 5.5 DNS、Tailscale、WireGuard

- DNS 当前支持 DoH/DoH3/DoQ/DoT；tcp:// 是未加密 DNS。DNS 加密不等于广告过滤，也不依赖 MITM。
- Tailscale/WireGuard 出口策略通常只处理被规则选中的连接；入站/出口发布需要额外配置和权限。
- 不把入站监听、出口节点、子网路由自动加入普通去广告模板。官方指出 Surge 的 Tailscale 入站不能直接假定受 tailnet ACL 保护，需按官方说明另行约束来源与目的地址。

[DNS](https://manual.nssurge.com/dns/encrypted-dns.html)、
[Tailscale](https://manual.nssurge.com/policies/tailscale.html)、
[WireGuard](https://manual.nssurge.com/policies/wireguard.html)。

## 6. 写完配置怎样检查

1. 用实际安装版本的解析器校验。Mac 可执行：
   /Applications/Surge.app/Contents/Applications/surge-cli --check /绝对路径/配置.conf
2. 修改规则集/模块时，也可用官方 VS Code 扩展的 LSP 诊断。静态解析成功不证明网络可达、广告消失或 iOS 行为完全相同。
3. 在请求详情中核对匹配规则、策略链和失败原因；规则顺序/网络是否被接管/广告是否缓存需要分别排查。
4. 配置要分段合并到现有可用配置；保留原来的节点和订阅，不以参考模板覆盖它们。
5. iOS 6 可用配置历史比较、回滚；更新远程模块前查看差异。回滚后需重新核对是否仍启用了对应模块。

[CLI 校验与 LSP](https://manual.nssurge.com/tools/cli.html)、
[iOS 6 配置历史](https://nssurge.com/surge-ios-6/release-notes)。

## 7. 本次交付与验证记录

- 未修改当前工作中的 adgoaway.sgmodule、xiaoxun-ads.js。
- 未读取或上传用户现有代理密码、订阅、CA 私钥。
- 未切换、重载或停止用户设备的 Surge 配置，未开启 MITM、API、MCP。
- 示例配置的原生解析器校验结果记录在 [validation.md](../examples/validation.md)。
- 以后生成带实际节点的配置时，需要在本地合并节点/订阅与用户路由选择，本文是语法和能力基线。
