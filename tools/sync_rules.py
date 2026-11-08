#!/usr/bin/env python3
"""Refresh personal Surge rule sets, preserving local additions and source order."""
import argparse
import concurrent.futures
import datetime
import hashlib
import ipaddress
import json
import re
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE_TYPES = {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'IP-CIDR',
              'IP-CIDR6', 'IP-ASN', 'USER-AGENT', 'URL-REGEX', 'AND',
              'OR', 'NOT', 'PROCESS-NAME', 'PROTOCOL', 'DEST-PORT',
              'SRC-IP', 'SRC-PORT', 'IN-PORT', 'SUBNET', 'GEOIP'}

def rules(text):
    """Strip prose, retain functional options, reject unexpected response formats."""
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(('#', ';', '//')):
            continue
        line = re.split(r'\s+(?://|#|;)\s*', line, maxsplit=1)[0].strip()
        kind, sep, value = line.partition(',')
        if not sep or kind not in RULE_TYPES or not value:
            raise ValueError(f'Invalid rule: {line[:100]}')
        if kind in ('IP-CIDR','IP-CIDR6'):
            ipaddress.ip_network(value.split(',')[0], strict=False)
        elif kind == 'IP-ASN':
            int(value.split(',')[0])
        out.append(line)
    if not out:
        raise ValueError('Refusing an empty source')
    return out

def unique(items):
    return list(dict.fromkeys(items))

def render(name, items, inputs):
    notice = []
    if any(i not in ('Anthropic', 'ASNChina') for i in inputs):
        notice.append('# Includes rule data by blackmatrix7; see licenses/blackmatrix7-GPL-2.0.txt.')
    if 'Anthropic' in inputs:
        notice.append('# Includes rule data by xiaolai (MIT); see licenses/anthropic-NOTICE.txt.')
    if 'ASNChina' in inputs:
        notice.append('# Includes rule data by VirgilClyne; see licenses/GetSomeFries-GPL-3.0.txt.')
    header = [f'# NAME: {name}', '# TYPE: RULE-SET',
              '# Policy-free conditions. Assign a policy in the main profile.',
              '# Modified for personal aggregation; provided without warranty.',
              '# Edit sources/rules.json, then run tools/sync_rules.py.',
              '# Source revisions are recorded in sources/manifest.json.'] + notice
    if name == 'adgoaway':
        header += [
            '# 个人精简版：仅保留个人域名规则，不合并通用广告库。',
            '# 小寻与两步路的 HTTPS 接口处理见 adgoaway.sgmodule，默认关闭。',
        ]
        labels = {
            'DOMAIN-SUFFIX,gdt.qq.com': '腾讯广告与统计',
            'DOMAIN-SUFFIX,pangolin-sdk-toutiao.com': '字节跳动 / 穿山甲',
            'DOMAIN-SUFFIX,adukwai.com': '快手广告',
            'DOMAIN-SUFFIX,mobads.baidu.com': '百度广告',
            'DOMAIN-SUFFIX,sigmob.com': 'Sigmob 广告',
            'DOMAIN-SUFFIX,tanx.com': '阿里广告与统计',
            'DOMAIN,adstats.tencentmusic.com': '腾讯音乐广告与统计',
            'DOMAIN,adse.ximalaya.com': '喜马拉雅广告与统计',
            'DOMAIN-SUFFIX,x-adnet.com': '其他广告平台',
            'DOMAIN-SUFFIX,admobile.top': '两步路：广告平台域名',
            'DOMAIN-SUFFIX,yfanads.com': '小寻：案例中的 7 条广告域名，当前版本待实机验证',
        }
        annotated = []
        for item in items:
            if item in labels:
                annotated += ['', '# ' + labels[item]]
            annotated.append(item)
        items = annotated
    if name in ('AI','AI-Priority','Privacy'):
        header.append('# PROCESS-NAME conditions apply on macOS only.')
    return '\n'.join(header + [''] + items) + '\n'

def fetch(item):
    name, source = item
    request = urllib.request.Request(source['url'], headers={'User-Agent':'personal-surge-rules/1'})
    with urllib.request.urlopen(request, timeout=45) as response:
        content = response.read(8_000_001)
    if len(content) > 8_000_000:
        raise ValueError(f'{name}: source exceeds size limit')
    text = content.decode('utf-8-sig')
    rules(text)
    return name, text

def build(contents, config, previous):
    normalized = {n:rules(t) for n,t in contents.items()}
    manifest = {'format':1, 'upstreams':{}, 'outputs':{}}
    for name, text in contents.items():
        b = text.encode()
        digest = hashlib.sha256(b).hexdigest()
        old = previous.get('upstreams',{}).get(name,{})
        manifest['upstreams'][name] = {
            **config['upstreams'][name], 'sha256':digest,
            'git_blob_sha':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),
            'rules':len(normalized[name]),
            'fetched_at':old.get('fetched_at') if old.get('sha256')==digest else datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    files = {}
    for name in dict.fromkeys([*config['local'], *config['pipelines']]):
        upstreams = config['pipelines'].get(name, [])
        local = config['local'].get(name, [])
        items = rules('\n'.join(local)) if local else []
        for source in upstreams:
            items.extend(normalized[source])
        items = unique(items)
        content = render(name,items,upstreams)
        files[name+'.list'] = content
        manifest['outputs'][name+'.list'] = {
            'rules':len(items), 'upstreams':upstreams,
            'sha256':hashlib.sha256(content.encode()).hexdigest(),
        }
    files['sources/manifest.json'] = json.dumps(manifest,indent=2,sort_keys=True)+'\n'
    return files,manifest

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',type=Path,help='Use an offline fetch_file snapshot instead of the network')
    p.add_argument('--check',action='store_true',help='Verify generated files without writing')
    args = p.parse_args()
    config = json.loads((ROOT/'sources/rules.json').read_text())
    manifest_path = ROOT/'sources/manifest.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    if args.snapshot:
        contents = {k:v['content'] for k,v in json.loads(args.snapshot.read_text())['upstreams'].items()}
    else:
        # Finish all downloads and validation before replacing any generated file.
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            contents = dict(pool.map(fetch,config['upstreams'].items()))
        for name,text in contents.items():
            old_count=previous.get('upstreams',{}).get(name,{}).get('rules',0)
            if old_count and len(rules(text)) < old_count * 0.5:
                raise ValueError(f'{name}: unexpectedly large reduction; review manually')
    files,manifest = build(contents,config,previous)
    changed = [f for f,t in files.items() if not (ROOT/f).exists() or (ROOT/f).read_text()!=t]
    if args.check and changed:
        raise SystemExit('Generated files differ: '+', '.join(changed))
    if not args.check:
        for f in changed:
            target=ROOT/f
            with tempfile.NamedTemporaryFile(mode='w',dir=target.parent,delete=False,encoding='utf-8') as temp:
                temp.write(files[f]); temp_path=Path(temp.name)
            temp_path.replace(target)
    print(json.dumps({'changed':changed,'rule_counts':{f:v['rules'] for f,v in manifest['outputs'].items()}},indent=2))

if __name__=='__main__':
    main()
