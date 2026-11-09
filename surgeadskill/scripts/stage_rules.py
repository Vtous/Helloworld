#!/usr/bin/env python3
"""Stage verified ad conditions in a separate directory; never connect, publish or change Surge."""
import argparse
import hashlib
import inspect
import ipaddress
import json
import re
import types
from pathlib import Path


def condition(line):
    parts = line.strip().split(',')
    if len(parts) not in (2,3):
        raise ValueError('Expected policy-free DOMAIN, DOMAIN-SUFFIX or single-IP condition')
    kind, value = parts[:2]
    if kind in ('DOMAIN','DOMAIN-SUFFIX'):
        if len(parts) != 2:
            raise ValueError('Domain rules must not include a policy or extra flag')
        value = value.rstrip('.').encode('idna').decode('ascii').lower()
        labels = value.split('.')
        if len(value)>253 or len(labels)<2 or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',x) for x in labels):
            raise ValueError('Invalid exact hostname')
        try:
            ipaddress.ip_address(value)
        except ValueError:
            pass
        else:
            raise ValueError('Use a single-IP condition for IP addresses')
        return kind+','+value
    if kind not in ('IP-CIDR','IP-CIDR6') or parts[2:] not in ([],['no-resolve']):
        raise ValueError('Unsupported condition or embedded policy')
    network = ipaddress.ip_network(value, strict=True)
    if network.prefixlen != network.max_prefixlen or not network.network_address.is_global or network.network_address.is_multicast:
        raise ValueError('Only exclusive public /32 or /128 hosts are allowed; no fake/private IPs or subnets')
    if (kind == 'IP-CIDR') != (network.version == 4):
        raise ValueError('IP rule family mismatch')
    return f'{kind},{network},no-resolve'


def verified(candidate, item):
    if condition(item.get('rule','')) != candidate:
        raise ValueError('Evidence does not match the condition')
    for field, minimum in [('ad_reproduced_runs',2),('blocked_runs',2),('restored_runs',1)]:
        if type(item.get(field)) is not int or item[field] < minimum:
            raise ValueError('Incomplete experiment: '+field)
    for field in ('matched_reject','ad_suppressed','sharing_checked'):
        if item.get(field) is not True:
            raise ValueError('Incomplete experiment: '+field)
    if item.get('core_functions') != 'passed':
        raise ValueError('Core functionality has not passed')
    if candidate.startswith('DOMAIN-SUFFIX,') and item.get('all_subdomains_tested') is not True:
        raise ValueError('Suffix scope not validated; use an exact DOMAIN')
    if candidate.startswith(('IP-CIDR,','IP-CIDR6,')) and item.get('ip_exclusive') is not True:
        raise ValueError('Exclusive and stable IP ownership not validated')


def stage(repo, requested, evidence, out):
    repo, out = Path(repo).resolve(), Path(out).resolve()
    if repo == out or repo in out.parents:
        raise ValueError('Stage outside the source repository')
    candidates = list(dict.fromkeys(condition(l) for l in requested.splitlines() if l.strip() and not l.lstrip().startswith('#')))
    if not candidates:
        raise ValueError('No verified candidate conditions')
    if not isinstance(evidence.get('app'),str) or not evidence['app'].strip():
        raise ValueError('Evidence must identify the target App')
    items = evidence.get('rules')
    if not isinstance(items,list):
        raise ValueError('Evidence rules must be a list')
    indexed = {}
    for item in items:
        if not isinstance(item,dict):
            raise ValueError('Expected per-rule evidence objects')
        key = condition(item.get('rule',''))
        if key in indexed:
            raise ValueError('Duplicate evidence condition')
        indexed[key] = item
    for rule in candidates:
        if rule not in indexed:
            raise ValueError('Missing evidence: '+rule)
        verified(rule,indexed[rule])
    source = repo/'sources/rules.json'
    config = json.loads(source.read_text())
    previous_local = list(config['local']['adgoaway'])
    config['local']['adgoaway'] = list(dict.fromkeys(previous_local+candidates))
    path = repo/'tools/sync_rules.py'
    # Executing the owned generator this way avoids writing __pycache__ into the source tree.
    module = types.ModuleType('surgeadskill_repo_renderer')
    module.__file__ = str(path)
    exec(compile(path.read_text(), str(path), 'exec'), module.__dict__)
    if not callable(getattr(module,'render',None)) or not callable(getattr(module,'rules',None)):
        raise ValueError('Repository generator interface changed; inspect before adapting')
    existing = module.rules((repo/'adgoaway.list').read_text())
    combined = list(dict.fromkeys(config['local']['adgoaway']+existing))
    upstreams = config['pipelines']['adgoaway']
    params = inspect.signature(module.render).parameters
    kwargs = {'local_count':len(config['local']['adgoaway'])} if 'local_count' in params else {}
    rendered = module.render('adgoaway',combined,upstreams,**kwargs)
    if set(module.rules(rendered)) != set(combined) or not set(existing)<=set(module.rules(rendered)):
        raise ValueError('Renderer did not preserve the candidate/existing conditions')
    manifest = json.loads((repo/'sources/manifest.json').read_text())
    entry = manifest['outputs']['adgoaway.list']
    entry.update({'rules':len(combined),'sha256':hashlib.sha256(rendered.encode()).hexdigest()})
    files = {'sources/rules.json':json.dumps(config,ensure_ascii=False,indent=2)+'\n',
             'adgoaway.list':rendered,
             'sources/manifest.json':json.dumps(manifest,indent=2,sort_keys=True)+'\n'}
    for relative, content in files.items():
        target=out/relative
        if target.exists():
            raise ValueError('Use a fresh stage directory; refusing to overwrite existing output')
    for relative, content in files.items():
        target=out/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(content,encoding='utf-8')
    return {'staged_files':list(files),'new_local_conditions':[r for r in candidates if r not in previous_local],
            'total_conditions':len(combined),'published':False,'phone_verified':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ('repo','rules','evidence','out'):
        p.add_argument('--'+flag,required=True,type=Path)
    a=p.parse_args()
    try:
        result=stage(a.repo,a.rules.read_text(),json.loads(a.evidence.read_text()),a.out)
    except (ValueError, OSError, KeyError, AttributeError, TypeError) as exc:
        p.exit(2,str(exc)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
