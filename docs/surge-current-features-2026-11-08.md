# Configuration Notes

Updated: 2026-11-08.

## Target versions

- macOS: Surge 6.11 beta.
- iOS: Surge 6.0 TestFlight.
- Stable compatibility baseline: Mac 6.10 / iOS 5.23.

Features can change between beta builds. Check the installed build before using a newly added option.

## Current capabilities

| Capability | Configuration impact |
| --- | --- |
| Adaptive QUIC blocking | Per-policy block-quic=adaptive; auto follows policy capabilities |
| Large rule sets | The former one-million-entry limit is removed in the target beta versions |
| MCP | Optional /v1/mcp endpoint; disabled by default |
| Section editing | CLI/API can update one profile section with revision checks |
| Capture sessions | Inspect saved requests and bodies through diagnostic interfaces |
| Policy avoidance | Temporarily skip poorly performing policies in automatic groups |
| Tailscale inbound access | Peer access, exit-node and subnet-route options |
| WireGuard listening | Accept incoming peers with listen-port |
| SOCKS5 UDP | UDP ASSOCIATE support |
| Custom MITM certificates | Requires an appropriate certificate and private key for the target hostname |
| Log size limit | log-file-size-limit controls retained log size |

Do not treat client protocol support as a server upgrade. A configured server must support the selected protocol and options.

## Shared configuration features

| Feature | Minimum version or limitation |
| --- | --- |
| IP Rewrite | iOS 5.23 / Mac 6.10; VIF traffic only |
| Ruleset nesting | iOS 5.22 / Mac 6.9 |
| Ruleset merging across modules | iOS 5.23 / Mac 6.10 |
| Group category | iOS 5.23 / Mac 6.10; display only |
| Group underlying-proxy | iOS 5.22 / Mac 6.9 |
| HTTPS latency-test URLs | iOS 5.23 / Mac 6.10 |
| Pre-matching rejection | iOS 5.14 / Mac 5.9 |
| Process matching | Mac only |
| External-resource API | iOS 5.23 / Mac 6.10 |
| Offline language server | Mac 6.10 or later |

The iOS 6 interface also includes a configurable dashboard, request filters, profile history, comparisons, rollback and editor diagnostics. These interface features do not require extra rule entries.

## Authoring rules

1. Keep proxy credentials, subscription URLs, API keys and certificate private keys outside this repository.
2. Keep MITM disabled by default. Store optional HTTPS settings as comments.
3. Put routing and DNS in the main profile. Use modules for independent optional features.
4. Entries inside a Ruleset section have no target policy. Assign the policy when referencing the set from Rule.
5. Ordinary rules use first-match ordering. Keep FINAL last.
6. Module rules are inserted before the main profile's ordinary rules.
7. Pre-matching rejection runs before ordinary allow rules, regardless of their position. Remove pre-matching when normal allow-rule precedence is required.
8. Use pre-matching only with supported rule types. Do not apply it indiscriminately to mixed lists containing URL-REGEX or USER-AGENT.
9. Global block-quic uses per-policy/all-proxy/all/always-allow. Policy-level block-quic uses auto/on/off/adaptive.
10. Smart groups should contain concrete proxy policies. DIRECT and nested groups are not valid Smart members.
11. Smart's testing schedule is not controlled by interval.
12. category only changes presentation, but keep it absent from personal profiles to preserve the original flat menu. underlying-proxy creates a proxy chain.
13. Domain rejection also affects other applications using the same hostname. iOS cannot isolate these rules by process.
14. A local loopback rule is independent of MITM.
15. Encrypted DNS is not ad filtering. tcp:// DNS is not encrypted.
16. Enable inbound services, shared proxy ports and control APIs only when needed.

## Repository files

adgoaway.list contains 60 personal domain conditions, including the original seven Xiaoxun entries and one 2bulu entry with Chinese labels. It no longer includes the general advertising source. The unified profile uses the AdBlock group. See [profile changes](profile-update-2026-11-08.md) for the reduced coverage and remaining service lists.

adgoaway.sgmodule contains only the optional HTTPS features. Its six configuration lines remain disabled as comments.

- Default filtering: the referenced domain list; no MITM required.
- Optional filtering: HTTPS URL rejection and response cleanup through the module.
- The response script preserves unrelated fields and passes malformed responses through.
- Existing ad caches and operating-system deep links may bypass network-based blocking.
- Clear or disable a conflicting rule before assuming a module failure.
- Before reinstalling an application, back up tracks, offline maps and other local data.

The six MITM configuration lines remain commented out in the module. Uncommenting them does not enable Surge's MITM switch or establish certificate trust.

## Examples

- [macOS](../examples/surge-macos-modern.conf)
- [iOS](../examples/surge-ios-modern.conf)

Both examples are direct-routing references with a remote adgoaway.list and an uncategorized Outbound group. The full masked personal template is [surge-unified.conf](../profiles/surge-unified.conf).

Use ordinary rule order. The personal ad list now contains only DOMAIN and DOMAIN-SUFFIX conditions; it does not enable pre-matching.

Merge selected sections into a working local profile and retain its real proxies and routing preferences. Do not replace an existing profile with a direct-only reference.

## Validation

Use the installed parser:

~~~sh
/Applications/Surge.app/Contents/Applications/surge-cli --check /absolute/path/profile.conf
~~~

Static validation checks syntax and references. It does not prove connectivity, ad-blocking coverage or identical iOS runtime behavior.

Review matched rules and policy decisions in request details. Use profile history for rollback and review module changes before applying updates.

See [validation.md](../examples/validation.md).
