#!/usr/bin/env python3
"""Normalize local Surge/HAR metadata and summarize observed candidate hosts. No network I/O."""
import argparse
import collections
import hashlib
import ipaddress
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    p.chmod(0o600)


def records(obj):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        if isinstance(obj.get('log'), dict):
            return records(obj['log'])
        for key in ('requests', 'records', 'entries'):
            if isinstance(obj.get(key), list):
                return obj[key]
        if isinstance(obj.get('data'), (dict, list)):
            return records(obj['data'])
    keys = sorted(obj.keys())[:30] if isinstance(obj, dict) else [type(obj).__name__]
    raise ValueError('Unknown record container; keys only: ' + ', '.join(keys))


def host_name(value):
    if not isinstance(value, str) or not value.strip():
        return None
    value = value.strip()
    try:
        return str(ipaddress.ip_address(value.strip('[]')))
    except ValueError:
        pass
    try:
        host = urlsplit(value if '://' in value else '//' + value).hostname
        if not host:
            return None
        host = host.rstrip('.').encode('idna').decode('ascii').lower()
        if len(host) > 253 or not re.fullmatch(r'[a-z0-9_.:-]+', host):
            return None
        return host
    except (ValueError, UnicodeError):
        return None


def public_ip(value):
    if not isinstance(value, str):
        return None
    try:
        ip = ipaddress.ip_address(value.strip())
    except ValueError:
        try:
            ip = ipaddress.ip_address(urlsplit('//' + value).hostname)
        except (ValueError, TypeError):
            return None
    return str(ip) if ip.is_global and not ip.is_multicast else None


def normalize(obj):
    out = []
    skipped = 0
    for row in records(obj):
        if not isinstance(row, dict):
            raise ValueError('Expected request objects, not textual CLI rows; use --raw')
        request = row.get('request') if isinstance(row.get('request'), dict) else {}
        host = next((h for h in (host_name(row.get(k)) for k in ('hostname','host','url','remoteHost')) if h), None)
        host = host or host_name(request.get('url'))
        address = next((row[k] for k in ('remoteIPAddress','remoteAddress','destinationAddress','serverIPAddress','address','ip') if isinstance(row.get(k), str)), '')
        ip = public_ip(address)
        if host:
            try:
                literal = ipaddress.ip_address(host)
            except ValueError:
                pass
            else:
                ip = public_ip(str(literal))
                host = None
        if not host and not ip:
            skipped += 1
            continue
        rid = row.get('id', row.get('requestId'))
        started = next((row[k] for k in ('startTime','startedDateTime','startDate','timestamp','time') if row.get(k) is not None), None)
        if rid is not None and not isinstance(rid, (str,int)):
            raise ValueError('Unsupported request ID type')
        if started is not None and not isinstance(started, (str,int,float)):
            raise ValueError('Unsupported request timestamp type')
        # Only metadata enters the identity; headers, credentials, paths and bodies are discarded.
        identity = [rid, started, host, ip]
        key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest() if rid is not None or started is not None else None
        out.append({'key':key,'host':host,'ip':ip})
    if not out and records(obj):
        raise ValueError('No recognized public host/IP metadata; inspect field names locally')
    return {'format':1,'records':out,'skipped_unusable':skipped,
            'warning':'Metadata only; candidate presence is not proof of advertising.'}


def canonical(obj):
    if not isinstance(obj, dict) or obj.get('format') != 1 or not isinstance(obj.get('records'), list):
        raise ValueError('Use normalize before delta/report')
    return obj['records']


def delta(before, after):
    a, b = canonical(before), canonical(after)
    if any(not row.get('key') for row in a+b):
        raise ValueError('Stable request IDs/start times missing; cannot safely subtract snapshots')
    ids = {r['key'] for r in a}
    missing = len(ids - {r['key'] for r in b})
    return {'format':1,'records':[r for r in b if r['key'] not in ids],
            'baseline_records_missing':missing,
            'warning':'Counts may be incomplete if requests rolled out of the buffer or the engine restarted.'}


def report(obj):
    groups = collections.defaultdict(lambda: {'requests':0,'ips':set()})
    for row in canonical(obj):
        label = row.get('host') or row.get('ip')
        if not label:
            continue
        groups[label]['requests'] += 1
        if row.get('ip'):
            groups[label]['ips'].add(row['ip'])
    result = [{'host_or_ip':k,'requests':v['requests'],'ips':sorted(v['ips'])}
              for k,v in groups.items()]
    return {'candidates':sorted(result, key=lambda r:(-r['requests'],r['host_or_ip'])),
            'warning':'Candidate inventory only. Compare repeated ad/control windows and perform A/B/A/B tests; do not auto-block.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest='command', required=True)
    for command in ('normalize','report'):
        sp = subs.add_parser(command)
        sp.add_argument('--input', required=True, type=Path)
        sp.add_argument('--out', required=True, type=Path)
    sp = subs.add_parser('delta')
    sp.add_argument('--before', required=True, type=Path)
    sp.add_argument('--after', required=True, type=Path)
    sp.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    try:
        if a.command == 'normalize':
            result = normalize(load(a.input))
        elif a.command == 'delta':
            result = delta(load(a.before),load(a.after))
        else:
            result = report(load(a.input))
        save(a.out,result)
    except (ValueError, OSError) as exc:
        p.exit(2, str(exc)+'\n')


if __name__ == '__main__':
    main()
