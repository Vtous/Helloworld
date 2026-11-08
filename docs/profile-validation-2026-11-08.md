# Profile Validation

Date: 2026-11-08. Native parser: installed Surge Mac 6.11.0 build 12720.

## Original consolidation checks

- All 160 original hand-written rule conditions are retained, either in generated lists or as explicit overrides.
- All normalized conditions from the 12 referenced upstream sources are present in the corresponding generated outputs.
- All 15 remote RULE-SET references in the unified profile use Vtous/Helloworld.
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
| adgoaway.list | 60 |
| AI.list | 54 |
| AI-Priority.list (legacy compatibility only) | 10 |
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

The original consolidation reduced the profile from 401 to 110 lines. The current revision adds concise Chinese comments and removes the redundant early AI-Priority reference. This is a maintenance improvement, not a measured speed increase.

## Single-list AI revision

The 10 legacy priority conditions are all present in the 54-condition AI.list. The current profile references AI.list once, after ads and precise direct services; AI-Priority.list is kept only for old URL compatibility. No AI condition was removed. The 39 selected routing cases passed again, together with two extra checks that Claude process matching does not override a blocked ad hostname or a LAN direct rule. The revised profile and its expanded inline rule sets passed the native syntax check. Earlier non-AI matches now take precedence over the former Claude process/domain exceptions. See the profile changes for this intentional ordering difference.

## Flat-menu revision

All category parameters have been removed from the unified profile and the two reference profiles. Policy-group names, declaration order, members, icons and hidden flags remain unchanged. The unified profile's group order also matches the original supplied profile. Non-comment configuration lines are identical after removing only category parameters. All three profiles pass the native syntax check. The live Surge profile was not modified.

## Personal ad-list simplification

The current ad list retains exactly the 60 local domain conditions, including all seven Xiaoxun rules and admobile.top for 2bulu. The 782 general-source rules were removed intentionally, reducing general advertising coverage. They were not all duplicates or proven obsolete. Chinese group labels identify the app-specific entries. The optional HTTPS module remains disabled and unchanged.

The general advertising pipeline and its upstream definition were removed, so automatic regeneration will not restore the removed rules. The source manifest was updated for the new output. Historical checks above describe the original consolidation before this reduction. The 11 retained upstream snapshots matched their recorded SHA-256 hashes, regeneration passed with no further differences, all 15 other list outputs stayed byte-for-byte unchanged, and a temporary profile containing all 60 ad rules passed the installed Surge parser (OK). Actual app ad coverage remains unverified.

## Limits

The routing model covers ordinary domain and process conditions only; it does not emulate DNS-triggered IP matching, ASN lookups, GEOIP, TLS SNI, URL matching or the full Surge engine. Native parser acceptance is not a live routing test.

No working node host/password or subscription endpoint was supplied. Connectivity, selected subscription nodes, HTTPS test-endpoint behavior from those nodes, real ad coverage, iOS runtime behavior have not been verified on the user's devices. The refresh job passed once in GitHub Actions; its future scheduled start time is not guaranteed. The current active profile was not changed.

The reduction in general advertising coverage and the AI policy-group behavior is documented in [profile changes](profile-update-2026-11-08.md). Review matched rules after importing, and restore the old profile if behavior differs from expectations.
