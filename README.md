# Helloworld

Personal configuration files.

## Domain filtering

When migrating from the old module, add the rule-set reference first. The module no longer contains domain rules.

Add this line to the existing [Rule] section on each device, before broader allow rules and FINAL:

~~~ini
RULE-SET,https://raw.githubusercontent.com/Vtous/Helloworld/main/adgoaway.list,REJECT,update-interval=86400
~~~

- [adgoaway.list](adgoaway.list): eight domain conditions for Xiaoxun and 2bulu.
- The list uses RULE-SET syntax, not DOMAIN-SET syntax.
- MITM is not required for domain filtering.
- The remote list is cached and eligible for refresh every 86400 seconds. Actual refresh timing depends on client availability and network access.
- These domain conditions also affect other apps using the same hosts.

## Optional HTTPS module

- [adgoaway.sgmodule](adgoaway.sgmodule)
- [Response script](scripts/xiaoxun-ads.js)

Install the module from this URL only when the optional HTTPS features are needed:

https://raw.githubusercontent.com/Vtous/Helloworld/main/adgoaway.sgmodule

The module contains only optional URL rewriting, response-script and MITM configuration. All six configuration lines remain commented out by default; simply installing the module or turning on MITM does not activate them.

To enable these features, uncomment the six configuration lines, enable MITM, Rewrite and Scripting, and install and trust your own Surge CA certificate. Keep the domain rule-set reference enabled alongside it.

## References

- [Configuration notes](docs/surge-current-features-2026-11-08.md)
- [macOS example](examples/surge-macos-modern.conf)
- [iOS example](examples/surge-ios-modern.conf)
- [Validation](examples/validation.md)

Examples use direct routing and contain no personal proxy credentials. Merge selected settings into a working profile rather than replacing it.
