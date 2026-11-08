# Helloworld

Personal Surge configuration files.

- [Unified profile template](profiles/surge-unified.conf)
- [Profile changes and setup](docs/profile-update-2026-11-08.md)
- [Configuration notes](docs/surge-current-features-2026-11-08.md)

Restore masked node and subscription values locally before importing. Keep the old profile for rollback.

## Rule sets

| File | Purpose |
| --- | --- |
| [adgoaway.list](adgoaway.list) | 60 personal domain filters, including Xiaoxun and 2bulu; no general advertising feed |
| [AI.list](AI.list) | Combined OpenAI, Claude, process and dependency conditions |
| [AI-Priority.list](AI-Priority.list) | Legacy compatibility subset; not used by the current profile |
| [Direct.list](Direct.list) | Banks, brokers, market data, messaging and music allow rules |
| [DirectFallback.list](DirectFallback.list) | Broad domestic suffix fallbacks; keep after service rules |
| [LAN.list](LAN.list) | Local networks and routers |
| [Privacy.list](Privacy.list) | Process-scoped privacy rejection on macOS |
| [Trading.list](Trading.list) | Early TradingView and GMGN routing |
| [Finance-Priority.list](Finance-Priority.list) | Early finance exceptions |
| Finance / Cryptocurrency / YouTube / Telegram / Apple / Proxy | Service and proxy rule sets |
| [China.list](China.list) | Combined China domain, IP and ASN conditions |

Lists contain conditions without a target policy. The profile assigns the policy and preserves the routing stages. Use RULE-SET syntax, not DOMAIN-SET syntax.

For the ad list alone, add this before broad allow rules and FINAL:

~~~ini
RULE-SET,https://raw.githubusercontent.com/Vtous/Helloworld/main/adgoaway.list,REJECT,extended-matching,update-interval=86400
~~~

The unified profile assigns AdBlock instead of REJECT so the existing filter switch remains available. The personal list contains 60 domain conditions and labels the Xiaoxun (7) and 2bulu (1) entries. It no longer merges the 782-condition general advertising feed, which included broad keywords, IP ranges and URL conditions. This deliberately reduces general advertising coverage; the removed entries were not all duplicates or proven obsolete. Domain filtering works without MITM and can affect any app using the same domains. Advertising coverage is not guaranteed.

The current profile references AI.list once, after advertising and precise direct rules. AI-Priority.list contains no additional conditions; its ten entries are already in AI.list. Its old URL is retained for previously installed profiles. The unified profile includes short Chinese comments.

## Updates

Surge refreshes the remote list URLs at a configured interval of 86400 seconds, subject to network and client availability. Install the profile or references on each device once.

The repository includes a daily, source-change and manually dispatched [refresh workflow](.github/workflows/sync-rules.yml). GitHub Actions must be enabled and permitted to push to main. Scheduled workflows can be delayed or disabled by GitHub. A failed download leaves generated files untouched. Check the latest Actions run when freshness matters.

Local additions live in sources/rules.json. After changing them, regenerate with:

~~~sh
python3 tools/sync_rules.py
~~~

adgoaway is generated only from its local conditions; the removed general advertising feed will not return on refresh. Generated output edits will be replaced by the next refresh. Source URLs, revisions and content hashes are recorded in sources/manifest.json. Required source notices are retained under licenses/.

## Optional HTTPS module

[adgoaway.sgmodule](adgoaway.sgmodule) retains the optional HTTPS rejection and [response script](scripts/xiaoxun-ads.js). Its six configuration lines remain commented out.

To use it later, uncomment those lines, remove the unified profile's hostname = -* exclusion, enable MITM, Rewrite and Scripting, and install and trust your own Surge CA certificate. Keep the list reference enabled. Installing the module alone does not activate these features.

## Validation

See [profile validation](docs/profile-validation-2026-11-08.md). The configuration is syntax-checked, not a device connectivity or ad-coverage guarantee. The real node/subscription values were not supplied or tested, and the active Surge profile was not replaced.
