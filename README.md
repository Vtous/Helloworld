# Helloworld

Personal configuration files.

## Files

- [adgoaway](adgoaway.sgmodule) — ad-blocking module for Xiaoxun and 2bulu.
- [Optional response script](scripts/xiaoxun-ads.js).
- [Configuration notes](docs/surge-current-features-2026-11-08.md).
- [macOS example](examples/surge-macos-modern.conf).
- [iOS example](examples/surge-ios-modern.conf).
- [Validation](examples/validation.md).

## Module

Add this URL in Surge's module manager:

https://raw.githubusercontent.com/Vtous/Helloworld/main/adgoaway.sgmodule

Eight domain rules are enabled by default. MITM configuration remains commented out.

To enable the optional HTTPS rules, uncomment the six configuration lines at the end of the module, enable MITM, Rewrite and Scripting, and install and trust your own Surge CA certificate.

The examples use direct routing and contain no personal proxy credentials. They are references, not replacements for an existing working profile.
