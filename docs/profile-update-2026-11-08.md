# Personal Profile Update

Updated: 2026-11-08. Targets: Surge Mac 6.11 beta and iOS 6 TestFlight.

## Installation

Download profiles/surge-unified.conf as a local editable profile on each device. Restore the Tokyo node host, PSK, Shadow TLS password and DlerCloud subscription URL locally. Restore the panel argument URL too if using the subscription panel. These remain masked placeholders, not working endpoints.

Retain the previous profile for rollback. Importing this template does not preserve existing policy-group selections automatically; inspect AI, Finance and region choices after import. Use Rule mode. No automatic replacement of the running profile is performed by this repository. The template now includes short Chinese comments; rule syntax and policy names are unchanged by those comments.

## Changes

- Moved the 160 original inline rule conditions into lists or retained explicit overrides. All original hand-written conditions remain represented.
- Expanded adgoaway.list from eight rules to the personal ad conditions plus the original referenced general advertising list. Its misleading aggregate header statistics do not mean that its much larger companion files have been imported.
- Combined OpenAI and Anthropic conditions and local process/domain rules into AI.list. AI has Tokyo as its first choice. The current profile references AI.list only once, after advertising and precise direct rules. The ten-condition AI-Priority.list is a legacy subset retained only to keep older installed profile URLs working. It adds no conditions to AI.list.
- Combined bank, broker, market, messaging and music allow conditions into Direct.list. Kept LAN and broad domestic fallbacks in separate lists to retain their routing positions.
- Mirrored remaining service/proxy lists and combined the three China sources into China.list. Every RULE-SET URL in the unified profile points to this repository.
- Removed all category parameters from policy groups to restore the original flat menu. Existing policy-group names, declaration order, members, icons and visibility settings are preserved; do not reintroduce category submenus.
- Replaced Mac wildcard proxy listeners with explicit 127.0.0.1:6152 and 127.0.0.1:6153 listeners. iOS LAN/hotspot sharing remains off. Used supported platform guards.
- Changed connectivity-test URLs to HTTPS, supported by the target versions. Kept the 5-second test-timeout. Removed six redundant group timeout=5 availability filters; they are not connection timeouts. Preserved test intervals, damping and evaluate-before-use.
- Made global block-quic = per-policy explicit. On target beta versions, the default policy-level auto behavior uses adaptive blocking for UDP-capable proxies. Smart still imports concrete subscription policies without an ineffective interval override.
- Kept DNS servers, IPv6 preference, host mappings, STUN switch, Finance defaults, regional groups, icons and subscription panel behavior. The optional local controller is now commented out; set a private password locally if needed.
- Kept HTTPS decryption excluded with hostname = -*. The optional module and its commented configuration are unchanged.

## Routing differences to review

One merged ad list is evaluated before Direct.list. The original profile placed its hand-written filters there, but put the general advertising source after the precise domestic allow rules. General ad conditions can therefore now reject matching traffic that those precise allow rules previously allowed. This follows from collecting all ad conditions into one list. AdBlock = DIRECT temporarily bypasses that merged list; Privacy.list still rejects its two macOS process-scoped destinations.

The merged ad list uses extended-matching, so its domain conditions can also match visible TLS SNI and HTTP Host. It does not decrypt HTTPS. Pre-matching is not enabled.

The original OpenAI override domains/processes and Claude rules were fixed to Tokyo, while the old general OpenAI list used AI. They now share the AI group with a Tokyo default. Selecting another AI policy changes all matching AI traffic, including the former Claude priority conditions.

The former early Claude/Google-login reference has been removed to simplify the profile. These conditions now participate at the single AI.list position. Earlier rules for privacy, LAN, Trading, STUN, finance exceptions, ads and precise direct services take precedence. For example, a request from the Claude process to a blocked ad host is now filtered before the process-wide AI match. Putting the entire AI list in the former early slot would instead exempt many shared dependencies from advertising filters. The current file keeps ad filtering first.

AI.list also retains shared service dependencies and broad IP ownership conditions from the requested sources, including storage.googleapis.com, sentry.io, stripe.com and AS20473. These can match unrelated applications using those services. iOS has no process isolation for such domain/IP rules. Edit the source selection before regenerating if narrower matching is needed.

## Updating

The daily workflow refreshes public rule conditions and the manifest. It does not change proxy credentials or the profile. Download/validation failure preserves the last generated files. Nonfunctional prose is removed from generated lists; source metadata and required notices are retained separately.

The main profile's 86400-second refresh downloads these repository outputs; upstream refresh and device refresh are separate steps. Neither runs at a guaranteed exact time.

Only RULE-SET dependencies were centralized. Proxy subscriptions, icon URLs and the existing panel script are different resource types and retain their existing services. No new inbound control, MCP, proxy chain, certificate or Tailscale listener was enabled.

## Official syntax

- [Rule sets](https://manual.nssurge.com/rules/ruleset.html)
- [Group parameters](https://manual.nssurge.com/policy-groups/parameters.html)
- [Policy parameters and QUIC](https://manual.nssurge.com/policies/parameters.html)
- [Platform conditions](https://manual.nssurge.com/profile/requirement.html)
- [General options](https://manual.nssurge.com/profile/general.html)
