#!/usr/bin/env python3
"""Offline synthetic tests. These results are not live phone/ad verification."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.dont_write_bytecode = True
import capture_tools as capture
import stage_rules as staging


def evidence(rule):
    return {'app':'Synthetic fixture only','rules':[{
        'rule':rule,'ad_reproduced_runs':2,'blocked_runs':2,'restored_runs':1,
        'matched_reject':True,'ad_suppressed':True,'sharing_checked':True,
        'core_functions':'passed'}]}


class SkillTests(unittest.TestCase):
    def test_private_fields_are_discarded(self):
        raw={'requests':[{'id':1,'startTime':100,'url':'https://ads.example.invalid/path?token=SECRET',
                          'headers':{'Authorization':'Bearer SECRET'},'body':'SECRET',
                          'remoteAddress':'8.8.8.8:443'}]}
        clean=capture.normalize(raw)
        self.assertNotIn('SECRET',json.dumps(clean))
        self.assertNotIn('/path',json.dumps(clean))
        self.assertEqual(clean['records'][0]['host'],'ads.example.invalid')
        self.assertEqual(clean['records'][0]['ip'],'8.8.8.8')

    def test_fake_and_private_ips_are_not_candidates(self):
        self.assertIsNone(capture.public_ip('198.18.0.10'))
        self.assertIsNone(capture.public_ip('192.168.50.1'))
        self.assertIsNone(capture.public_ip('224.0.0.1'))
        self.assertEqual(capture.public_ip('[2001:4860:4860::8888]:443'),'2001:4860:4860::8888')

    def test_delta_does_not_recount_history(self):
        old={'id':1,'host':'content.example.invalid'}
        new={'id':2,'host':'ads.example.invalid'}
        diff=capture.delta(capture.normalize([old]),capture.normalize([old,new]))
        self.assertEqual([r['host'] for r in diff['records']],['ads.example.invalid'])
        self.assertEqual(capture.report(diff)['candidates'][0]['requests'],1)

    def test_missing_identity_fails_closed(self):
        with self.assertRaises(ValueError):
            capture.delta(capture.normalize([]),capture.normalize([{'host':'ads.example.invalid'}]))
        with self.assertRaises(ValueError):
            capture.normalize({'unknown':[]})

    def test_rules_cannot_expand_to_shared_networks(self):
        for rule in ['IP-CIDR,8.8.8.0/24','IP-CIDR,198.18.0.1/32','DOMAIN,example.com,REJECT',
                     'PROCESS-NAME,App','DOMAIN,*.example.com','DOMAIN,https://example.com']:
            with self.assertRaises(ValueError,msg=rule):
                staging.condition(rule)
        r=staging.condition('IP-CIDR,8.8.8.8/32')
        with self.assertRaises(ValueError):
            staging.verified(r,evidence(r)['rules'][0])
        r='DOMAIN-SUFFIX,example.invalid'
        with self.assertRaises(ValueError):
            staging.verified(r,evidence(r)['rules'][0])

    def test_incomplete_experiment_is_rejected(self):
        r='DOMAIN,ads.example.invalid'
        e=evidence(r)['rules'][0]
        for key,value in [('matched_reject',False),('blocked_runs',0),('restored_runs',0),('core_functions','not-run')]:
            altered={**e,key:value}
            with self.assertRaises(ValueError,msg=key):
                staging.verified(r,altered)

    def test_stage_preserves_sources_and_existing_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)/'repo';out=Path(tmp)/'stage'
            (repo/'sources').mkdir(parents=True);(repo/'tools').mkdir()
            cfg={'local':{'adgoaway':['DOMAIN,old.example.invalid']},'pipelines':{'adgoaway':['Advertising']},'upstreams':{}}
            (repo/'sources/rules.json').write_text(json.dumps(cfg))
            (repo/'adgoaway.list').write_text('DOMAIN,old.example.invalid\nDOMAIN,upstream.example.invalid\n')
            (repo/'sources/manifest.json').write_text(json.dumps({'outputs':{'adgoaway.list':{'rules':2,'upstreams':['Advertising']},'Other.list':{'rules':7}},'upstreams':{'keep':'unchanged'}}))
            (repo/'tools/sync_rules.py').write_text('def rules(s):\n return [l for l in s.splitlines() if l and not l.startswith("#")]\ndef render(name,items,inputs,local_count=0):\n return "\\n".join(items)+"\\n"\n')
            before={p.relative_to(repo):p.read_bytes() for p in repo.rglob('*') if p.is_file()}
            r='DOMAIN,ads.example.invalid'
            result=staging.stage(repo,r+'\n'+r,evidence(r),out)
            self.assertEqual(result['new_local_conditions'],[r])
            self.assertFalse(result['published'])
            self.assertEqual((out/'adgoaway.list').read_text().splitlines(),['DOMAIN,old.example.invalid',r,'DOMAIN,upstream.example.invalid'])
            manifest=json.loads((out/'sources/manifest.json').read_text())
            self.assertEqual(manifest['upstreams'],{'keep':'unchanged'})
            self.assertEqual(manifest['outputs']['Other.list'],{'rules':7})
            self.assertEqual(manifest['outputs']['adgoaway.list']['sha256'],hashlib.sha256((out/'adgoaway.list').read_bytes()).hexdigest())
            for p,content in before.items():self.assertEqual((repo/p).read_bytes(),content)
            self.assertEqual({p.relative_to(repo) for p in repo.rglob('*') if p.is_file()},set(before))
            with self.assertRaises(ValueError):staging.stage(repo,r,evidence(r),repo/'unsafe')


if __name__=='__main__':
    unittest.main(verbosity=2)
