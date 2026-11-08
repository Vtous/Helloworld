# Helloworld

用于存放 Vtous 的 Surge 配置、模块和相关脚本。

## 当前配置编写基线

用户使用 Surge Mac 6.11 与 iOS 6 TestFlight。2026-11-08 已核对官网版本源与官方手册：

- [最新功能、版本门槛与配置规范](docs/surge-current-features-2026-11-08.md)
- [Mac 新语法参考配置](examples/surge-macos-modern.conf)
- [iOS 新语法参考配置](examples/surge-ios-modern.conf)
- [解析器验证记录](examples/validation.md)

参考配置是直连基线，不包含私人节点/订阅，不应覆盖当前配置。已在使用的 adgoaway 保持原样；MITM 相关规则仍默认注释。

## adgoaway

合并小寻与两步路的广告拦截线索。创建于 2026-11-08；未进行真机安装、抓包或效果验证。

- [查看模块](adgoaway.sgmodule)
- [模块订阅链接](https://raw.githubusercontent.com/Vtous/Helloworld/main/adgoaway.sgmodule)
- [可选的小寻响应脚本](scripts/xiaoxun-ads.js)

将模块订阅链接添加到 Surge 的模块中。使用规则模式；先保留现有配置，逐项检查重复规则。

### 默认模式：不启用 MITM

默认只有 8 条域名拦截规则生效：

- 两步路：admobile.top。
- 小寻：yfanads.com、yfanads.cn、adxvip.com 及案例中的广告点击/曝光、候选素材域名。

默认没有启用 URL Rewrite、响应脚本或 MITM 主机配置，不需要为本模块安装 CA 证书。不要把默认域名拦截效果理解为两个 App 的全部广告都能清除。

Surge iOS 无法按 App 进程隔离规则；同一域名被其他 App 使用时，也会被拦截。

### 以后启用 MITM

模块末尾已经附上完整配置，6 行配置均以「# 」注释：

1. 删除「# [URL Rewrite]」和下一行网址规则前的「# 」。
2. 删除「# [Script]」和小寻脚本入口那行前的「# 」。
3. 删除「# [MITM]」和「# hostname = ...」前的「# 」。
4. 保存/重新加载模块。
5. 在 Surge 开启 MITM，安装并完全信任 Surge 自己生成的 CA 证书；开启 Rewrite 和 Scripting。

普通解释性注释不需要删除。不需要手动粘贴 JS：启用后，Surge 会从本仓库下载脚本。仅取消注释不会自动开启 MITM 总开关或完成证书信任。

两个域名通过 %APPEND% 追加，不会替换已有 MITM 主机列表。模块不包含 CA 私钥，也不设置 skip-server-cert-verify。

MITM 相关功能：

- 两步路：沿用原模块的 URL 接口列表，其中不只有开屏和弹窗，还包括任务、活动、入口等。若希望只处理开屏/弹窗，可将括号内列表缩减为 getSplash|getPopInfo，再验证。
- 小寻：仅处理 xunapi.xunkids.com/xunkids/adservice/resource/v2/pulls/data 的响应。脚本只清空 PL/data 中已存在的候选广告数组/对象，保留未知字段、标量字段和状态码；异常 JSON 直接原样放行。
- 这些接口和字段来自历史公开资料，未用当前设备响应确认；取消注释后不保证适配。证书固定等机制也可能阻止 HTTPS 解密。

### 验证与停用

启用后先检查开屏广告，再检查小寻定位、通话、消息，以及两步路地图、轨迹记录、同步是否正常。发生异常时先停用模块，检查是否恢复。

已有广告缓存可能继续显示，系统 URL scheme 唤起其他 App 也不一定经过网络拦截。不要仅为测试规则直接卸载 App；先确认轨迹、离线地图及其他本地数据已备份。

### 来源与修改

- 两步路规则：fmz200（奶思）的 [LiangBuLu.sgmodule](https://github.com/fmz200/wool_scripts/blob/main/Surge/module/split/partL/LiangBuLu.sgmodule)，源文件 blob SHA：c460ee48b4269402ec0c55ddaf4c57b2626bb2f4。原仓库为 GPL-3.0。
- 小寻接口/域名线索：fastrun100 于 2026-05-20 发布的 [Loon 抓包案例](https://linux.do/t/topic/2216200)。
- 本模块由 Vtous 于 2026-11-08 合并整理，去除了重复子域规则，未封锁可选的 s3plus.meituan.net 共用素材 CDN。
- 原帖内联脚本显示有缺失赋值，不能直接使用；本仓库另行实现 Surge 响应脚本，并保留其默认关闭状态。
- 代码及模块遵循 [GPL-3.0](LICENSE)，按现状提供，不保证效果。

Surge 官方说明：

- [模块语法](https://manual.nssurge.com/profile/module.html)
- [URL Rewrite 与 HTTPS 解密要求](https://manual.nssurge.com/http/url-rewrite.html)
- [HTTP 响应脚本](https://manual.nssurge.com/scripting/http-response.html)
- [进程规则仅支持 Mac](https://manual.nssurge.com/rules/process.html)
