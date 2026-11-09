# 验证证据与规则发布

默认 `Vtous/Helloworld` / `main`，但每次读取最新仓库，不依赖技能打包时的规则数。工作副本必须是新鲜的独立 checkout，或通过 GitHub 连接器读取最新文件。不存在本地 git 仓库时不要在其他项目里盲跑 git add/commit。

## 必须同时更新的文件

| 文件 | 处理 |
| --- | --- |
| sources/rules.json | 向 local.adgoaway 增加已验证、无策略列的条件 |
| adgoaway.list | 用仓库当前 render 逻辑生成；保留已有手写和上游条件 |
| sources/manifest.json | 更新 adgoaway.list 的条目数、SHA256；保留其余记录 |

先检查 `tools/sync_rules.py` 当前接口及 `.github/workflows/sync-rules.yml`。默认流程会因源文件变化或每日计划刷新列表。可正常联网时用当前仓库 `python3 tools/sync_rules.py` 全量生成，审阅并保留合法的上游更新。离线或只想暂存本次变动时，用技能提供的 stage_rules.py：它读取当前列表快照、调用仓库 render，生成上述三份候选文件，不联网、不提交、不改运行中的 Surge。

## 本地证据格式

证据只存私有实验目录。下例都是未完成状态，**不能直接提交脚本当作通过结果**。每条候选完成真实实验后才如实填值；IP 另需 ip_exclusive=true，后缀另需 all_subdomains_tested=true。

```json
{
  "app": "Target App",
  "rules": [
    {
      "rule": "DOMAIN,ads.example.invalid",
      "ad_reproduced_runs": 0,
      "blocked_runs": 0,
      "restored_runs": 0,
      "matched_reject": false,
      "ad_suppressed": false,
      "core_functions": "not-run",
      "sharing_checked": false
    }
  ]
}
```

候选文件每行一条纯规则，如 `DOMAIN,实际主机`；不写 REJECT、AdBlock、PROCESS-NAME 或 URL 重写。运行：

```sh
python3 scripts/stage_rules.py --repo /path/to/fresh/Helloworld --rules "$SESSION/verified.txt" --evidence "$SESSION/evidence.json" --out "$SESSION/staged"
```

脚本的数字/布尔校验只能防漏步骤，不能辨认虚假证据。返回不通过时补做实验或剔除候选，不修改证据来绕过验证。空结果、未知字段结构或共享服务不可安全分离时，正常交付“暂无已验证规则”。

## 发布和同步

1. 对比暂存三文件，确认旧条件未删除、只加入已验证规则、无密码/URL 查询/抓包内容。原始实验文件不能公开。
2. 检查语法。可写临时 profile，把候选放入 `[Ruleset CandidateAds]`，`[Rule]` 引用 CandidateAds,REJECT 并 FINAL,DIRECT；用 surge-cli --check 检查。不能仅凭列表文件存在就称语法通过。
3. 用户已要求发布时，优先 GitHub 连接器：以最新 commit/tree 为基底，只写三个文件，创建 commit，用 expected head 更新 main。head 变化则重新读取合并本次规则，不强推、不覆盖他人修改。CLI 可用时仅 git add 这三个明确路径。
4. 读回确认候选存在于源数据和列表。检查 CI；验证失败则修正原因，不能把已失败的更新称为成功。同步 job 在更新上游时可能另外提交，这是预期行为。
5. 手机已引用正确地址则不用重建整个 profile：`https://raw.githubusercontent.com/Vtous/Helloworld/main/adgoaway.list`。找到对应 external resource key，定向刷新；已有授权的 CLI 可执行 `external-resource update key`。检查 ready、error、更新时间及请求命中，不靠等待 24 小时推断已生效。
6. 移除本次临时规则后再测；list 本身不决定策略，主配置需分配 AdBlock/REJECT，且前面的规则不能先放行。手机未刷新或未做复测则准确标注。

## 回退

仅移除本次新增条件并重新生成、发布三文件，定向刷新。若候选此前已存在则不能把它当成本次新增删除。恢复本次修改前的临时规则、采集和端口状态。紧急场景可临时把 AdBlock 选 DIRECT，但要说明会放行整张表，并保留原选择用于恢复；不要用此状态证明新规则有效。
