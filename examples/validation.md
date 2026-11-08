# Validation

Date: 2026-11-08.

Parser: Surge Mac 6.11.0, build 12720.

| Check | Result |
| --- | --- |
| adgoaway.list | 842 combined conditions; no embedded target policy |
| adgoaway.sgmodule | No active domain rules; all optional HTTPS configuration remains commented |
| surge-macos-modern.conf | Native parser: exit 0, OK |
| surge-ios-modern.conf | Native parser: exit 0, OK |

Both examples reference the shared remote adgoaway.list. The ordinary rule-set reference is active. The earlier pre-matching example was removed because the expanded list mixes rule types.

The iOS reference was checked with the Mac shared parser, not imported on an iPhone. No current device profile was switched or reloaded.

Published files are verified through GitHub content readback. An anonymous raw-download recheck was not completed.

Network reachability and device-side behavior require separate verification. See [full profile validation](../docs/profile-validation-2026-11-08.md) for the current migration checks.
