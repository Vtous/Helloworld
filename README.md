# Helloworld

Personal Surge configuration files.

- [Unified profile template](profiles/surge-unified.conf)
- [Profile changes and setup](docs/profile-update-2026-11-08.md)
- [Configuration notes](docs/surge-current-features-2026-11-08.md)

Restore masked node and subscription values locally before importing. Keep the old profile for rollback.

## Rule sets

| File | Purpose |
| --- | --- |
| [adgoaway.list](adgoaway.list) | Personal domain filters including Xiaoxun/2bulu, followed by general advertising coverage |
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

The unified profile assigns AdBlock instead of REJECT so the existing filter switch remains available. The list keeps 88 personal conditions first, including labeled Xiaoxun (7) and 2bulu (21) entries. All 782 general advertising conditions are restored at the end under the Chinese heading 通用广告覆盖. The 20 startup-ad hosts from [2bulu-startup.sgmodule](2bulu-startup.sgmodule) are included in the 2bulu group. The standalone module remains available for existing installations. Refresh the list with AdBlock set to a rejection policy to use these additions. Exact duplicate conditions are removed without reducing coverage. Domain/IP filtering works without MITM; HTTPS URL conditions require decryption to inspect the full URL. Shared-domain rules can affect multiple apps. Advertising coverage is not guaranteed.

The Ximalaya group also includes ad.c4.ximalaya.com and seven /32 addresses resolved for adse.ximalaya.com and adbehavior.ximalaya.com on 2026-11-08. The phone capture showed direct-IP access to 101.91.134.52 during the startup-ad reproduction. These IP conditions cover that bypass of domain matching; address rotation or reuse requires rechecking. Shared playback/login endpoints were not added. Post-update ad coverage and playback still require a device retest.

The current profile references AI.list once, after advertising and precise direct rules. AI-Priority.list contains no additional conditions; its ten entries are already in AI.list. Its old URL is retained for previously installed profiles. The unified profile includes short Chinese comments.

## Updates

Surge refreshes the remote list URLs at a configured interval of 86400 seconds, subject to network and client availability. Install the profile or references on each device once.

The repository includes a daily, source-change and manually dispatched [refresh workflow](.github/workflows/sync-rules.yml). GitHub Actions must be enabled and permitted to push to main. Scheduled workflows can be delayed or disabled by GitHub. A failed download leaves generated files untouched. Check the latest Actions run when freshness matters.

Local additions live in sources/rules.json. After changing them, regenerate with:

~~~sh
python3 tools/sync_rules.py
~~~

adgoaway is generated from local conditions followed by the Advertising upstream. Automatic updates preserve that order and the 通用广告覆盖 heading. Generated output edits will be replaced by the next refresh. Source URLs, revisions and content hashes are recorded in sources/manifest.json. Required source notices are retained under licenses/.

## Optional HTTPS module

[adgoaway.sgmodule](adgoaway.sgmodule) retains the optional HTTPS rejection and [response script](scripts/xiaoxun-ads.js). Its six configuration lines remain commented out.

To use it later, uncomment those lines, remove the unified profile's hostname = -* exclusion, enable MITM, Rewrite and Scripting, and install and trust your own Surge CA certificate. Keep the list reference enabled. Installing the module alone does not activate these features.

## Validation

See [profile validation](docs/profile-validation-2026-11-08.md). The configuration is syntax-checked, not a device connectivity or ad-coverage guarantee. The real node/subscription values were not supplied or tested, and the active Surge profile was not replaced.

## Skill

- [surgeadskill](surgeadskill/SKILL.md): inspect iPhone ad traffic with Surge, validate narrow blocking rules, and synchronize verified conditions. Includes offline analysis and staging helpers.
