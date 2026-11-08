# 配置校验记录

日期：2026-11-08，Asia/Taipei。

## 环境

- 本机应用：Surge Mac 6.11.0，build 12720。
- 校验器：/Applications/Surge.app/Contents/Applications/surge-cli
- 目标：Mac 6.11 / iOS 6.0 TestFlight。iPhone 的具体 build 未读取。

## 原生解析器结果

以下命令只校验指定文件，未安装、切换或重载活动配置。

~~~sh
/Applications/Surge.app/Contents/Applications/surge-cli --check "/Users/ten/Documents/Codex/交易/Surge去广告/Helloworld/examples/surge-macos-modern.conf"
# exit 0; stdout: OK

/Applications/Surge.app/Contents/Applications/surge-cli --check "/Users/ten/Documents/Codex/交易/Surge去广告/Helloworld/examples/surge-ios-modern.conf"
# exit 0; stdout: OK
~~~

两份示例没有真实代理节点、启用中的远程规则集、脚本或 API。MITM 相关配置不在默认启用范围内。

## 校验范围

通过表示该 Mac 版本解析器接受示例语法与引用关系；iOS 示例也仅由 Mac 的共享配置解析器检查。没有在 iPhone 上导入，没有测试网络可达性、节点质量、广告效果或 iOS 运行状态。

官网测试更新源本次显示 Mac 6.11.0 build 12740；本机是 12720。本记录不宣称已使用 12740 执行校验。

## 已有工作文件

本次只增加文档和参考配置，并在 README 添加入口，未修改：

- adgoaway.sgmodule
- scripts/xiaoxun-ads.js

用户此前反馈 adgoaway 好用；本文没有将该反馈当作对新示例的真机验证。
