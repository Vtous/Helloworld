# Profile Validation

Date: 2026-11-08. Native parser: installed Surge Mac 6.11.0 build 12720.

## Completed checks

- All 160 original hand-written rule conditions are retained, either in generated lists or as explicit overrides.
- All normalized conditions from the 12 referenced upstream sources are present in the corresponding generated outputs.
- All 16 remote RULE-SET references in the unified profile use Vtous/Helloworld.
- Exact duplicate conditions are removed within each generated output. Functional per-rule modifiers are preserved.
- The original eight adgoaway conditions remain present in the expanded 842-rule ad list.
- The offline generator reproduces the committed outputs without differences.
- A limited routing model passed 39 selected domain/process cases: banks, messaging, music, advertising, AI, trading, finance, LAN and scoped process privacy.
- Comparing the original hand-written domain conditions and representative subdomains found no default route differences in that model, after resolving AI to its Tokyo default.
- Native syntax checks returned OK for the local optimized profile, public unified template, both direct-only reference profiles, and a temporary profile containing every generated list expanded into inline Ruleset sections.
- The public template contains masked node/subscription placeholders, no active external controller, loopback-only Mac listeners and no CA certificate/key. The original controller password is not published.
- The optional module and its script remain unchanged.
- The cloud refresh workflow completed successfully after a source-change push: [run 42466114066](https://github.com/Vtous/Helloworld/actions/runs/42466114066). Public upstream downloads and generation passed; no rule output changes were needed.

## Output sizes

| Output | Conditions |
| --- | ---: |
| adgoaway.list | 842 |
| AI.list | 54 |
| AI-Priority.list | 10 |
| Direct.list | 58 |
| LAN.list | 15 |
| DirectFallback.list | 6 |
| Privacy.list | 2 |
| Trading.list | 3 |
| Finance-Priority.list | 2 |
| Finance.list | 248 |
| Cryptocurrency.list | 43 |
| YouTube.list | 190 |
| Telegram.list | 46 |
| Apple.list | 56 |
| Proxy.list | 134 |
| China.list | 24757 |

The profile was reduced from 401 to 110 lines, including comments and whitespace. This is a maintenance improvement, not a measured speed increase.

## Limits

The routing model covers ordinary domain and process conditions only; it does not emulate DNS-triggered IP matching, ASN lookups, GEOIP, TLS SNI, URL matching or the full Surge engine. Native parser acceptance is not a live routing test.

No working node host/password or subscription endpoint was supplied. Connectivity, selected subscription nodes, HTTPS test-endpoint behavior from those nodes, real ad coverage, iOS runtime behavior have not been verified on the user's devices. The refresh job passed once in GitHub Actions; its future scheduled start time is not guaranteed. The current active profile was not changed.

The change in general advertising priority and AI policy-group behavior is documented in [profile changes](profile-update-2026-11-08.md). Review matched rules after importing, and restore the old profile if behavior differs from expectations.
