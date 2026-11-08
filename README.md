# Helloworld

Personal Surge configuration files.

- [Unified profile template](profiles/surge-unified.conf)
- [Profile changes and setup](docs/profile-update-2026-11-08.md)
- [Configuration notes](docs/surge-current-features-2026-11-08.md)

Restore masked node and subscription values locally before importing. Keep the old profile for rollback.

## Rule sets

| File | Purpose |
| --- | --- |
| [adgoaway.list](adgoaway.list) | Personal ad filters, Xiaoxun, 2bulu, and the existing general advertising source |
| [AI.list](AI.list) | Combined OpenAI, Claude, process and dependency conditions |
| [AI-Priority.list](AI-Priority.list) | Original high-priority Claude and login exceptions |
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

The unified profile assigns AdBlock instead of REJECT so the existing filter switch remains available. The expanded ad list affects more services than the former eight-condition list. Domain/IP filtering works without MITM; HTTPS URL conditions cannot inspect a decrypted full URL while MITM is off. Advertising coverage is not guaranteed.

## Updates

Surge refreshes the remote list URLs at a configured interval of 86400 seconds, subject to network and client availability. Install the profile or references on each device once.

The repository includes a daily, source-change and manually dispatched [refresh workflow](.github/workflows/sync-rules.yml). GitHub Actions must be enabled and permitted to push to main. Scheduled workflows can be delayed or disabled by GitHub. A failed download leaves generated files untouched. Check the latest Actions run when freshness matters.

Local additions live in sources/rules.json. After changing them, regenerate with:

~~~sh
python3 tools/sync_rules.py
~~~

Generated output edits will be replaced by the next refresh. Source URLs, revisions and content hashes are recorded in sources/manifest.json. Required source notices are retained under licenses/.

## Optional HTTPS module

[adgoaway.sgmodule](adgoaway.sgmodule) retains the optional HTTPS rejection and [response script](scripts/xiaoxun-ads.js). Its six configuration lines remain commented out.

To use it later, uncomment those lines, remove the unified profile's hostname = -* exclusion, enable MITM, Rewrite and Scripting, and install and trust your own Surge CA certificate. Keep the list reference enabled. Installing the module alone does not activate these features.

## Validation

See [profile validation](docs/profile-validation-2026-11-08.md). The configuration is syntax-checked, not a device connectivity or ad-coverage guarantee. The real node/subscription values were not supplied or tested, and the active Surge profile was not replaced.
