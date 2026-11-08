# Validation

Date: 2026-11-08.

Parser: Surge Mac 6.11.0, build 12720.

| File | Native parser result |
| --- | --- |
| surge-macos-modern.conf | Exit 0, OK |
| surge-ios-modern.conf | Exit 0, OK |

The iOS reference was checked with the Mac shared parser, not imported on an iPhone.

Examples contain no real proxy credentials, active API listener, active response script or enabled MITM configuration.

Checks do not switch or reload the active profile. Network reachability and device-side behavior require separate verification.
