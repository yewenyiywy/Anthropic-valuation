import csv
import json
import tempfile
import unittest
from pathlib import Path
from evaluation.validation_gate import (ARTIFACTS, COMPONENTS, MECHANISMS, check, sha, score, source_fingerprint, event_horizon,
    audit, MAX_WAPE, MAX_BIAS, MIN_FAMILIES, MIN_CYCLES)

class TestGate(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.paths={}
        self.m=dict(target='equity_market_cap_usd_b',
            model_entrypoint='models.joint_customer_states.forecast_joint',
            model_scope='full_company_profile',training_objective='equity_log1p_mae',
            evidence_tier='observed_historical',
            horizon_years=5,thresholds=dict(max_wape=MAX_WAPE,max_abs_bias=MAX_BIAS,
                min_families=MIN_FAMILIES,min_cycles=MIN_CYCLES),
            registered_at='2025-01-01T00:00:00Z',frozen_at='2025-02-01T00:00:00Z',
            labels_opened_at='2025-03-01T00:00:00Z',reviewed_at='2025-04-01T00:00:00Z',
            reviewer='reviewer',trainer='trainer',artifacts={})
        for k in ARTIFACTS:
            p=self.root/('models/joint_customer_states.py' if k=='engine' else k+'.txt')
            p.parent.mkdir(parents=True,exist_ok=True);p.write_text('synthetic evidence')
            self.paths[k]=p
            self.refresh(k)
        self.splits=[]
        for i,split in enumerate(['train','validation']+['test']*10):
            year={'train':2000,'validation':2006,'test':2012}[split]
            self.splits.append(dict(sample_id=str(i),company='Synthetic'+str(i),
                family_id='family'+str(i),split=split,cycle=str(i%2),
                origin=f'{year}-01-01',target_date=f'{year+5}-01-01',
                label_available=f'{year+5}-01-02',origin_market_cap=100,origin_revenue=10))
        self.prov=[dict(sample_id=r['sample_id'],component=c,available_date=r['origin'],
            status='verified',source='https://example.org',reconciliation='synthetic',
            document_section='synthetic',units='USD B') for r in self.splits for c in COMPONENTS]
        self.preds=[dict(sample_id=r['sample_id'],equity_market_cap_usd_b=180,revenue5=30) for r in self.splits[2:]]
        self.labels=[dict(sample_id=r['sample_id'],target_date=r['target_date'],
            equity_market_cap_usd_b=180,outcome='listed',source='https://example.org') for r in self.splits[2:]]
        self.write('splits',self.splits);self.write('provenance',self.prov)
        self.write('predictions',self.preds);self.write('labels',self.labels)
        self.m['source_fingerprint']=source_fingerprint(self.root)
        self.paths['model_contract'].write_text(json.dumps(dict(entrypoint=self.m['model_entrypoint'],source_fingerprint=self.m['source_fingerprint'],mechanisms=sorted(MECHANISMS))))
        self.refresh('model_contract')
        self.traces=[dict(sample_id=sid,mechanism=c,status='active',architecture_sha256=sha(self.paths['model_contract']),checkpoint_sha256=sha(self.paths['parameters']),trace_evidence='fixture',input_evidence='fixture',ablation_evidence='fixture',structural_zero_source='') for sid in [r['sample_id'] for r in self.splits]+['anthropic_application'] for c in MECHANISMS]
        self.write('execution_trace',self.traces)

    def refresh(self,k):
        p=self.paths[k]
        self.m['artifacts'][k]=dict(path=str(p.relative_to(self.root)),sha256=sha(p))
    def write(self,k,rows):
        with self.paths[k].open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        self.refresh(k)
    def result(self):return check(self.m,self.root)
    def test_valid_synthetic_schema_not_real_approval(self):
        self.assertEqual(self.result()['status'],'GATE_PASS_REQUIRES_AUTHENTICATED_REVIEW')
    def test_wrong_target(self):
        self.m['target']='revenue';self.assertEqual(self.result()['status'],'BLOCKED')
    def test_surrogate(self):
        self.m['model_scope']='aggregate';self.assertEqual(self.result()['status'],'BLOCKED')
    def test_leakage(self):
        self.prov[0]['available_date']='2001-01-01';self.write('provenance',self.prov)
        self.assertIn('future feature: 0',self.result()['errors'])
    def test_family_overlap(self):
        self.splits[2]['family_id']=self.splits[0]['family_id'];self.write('splits',self.splits)
        self.assertIn('issuer family overlap',self.result()['errors'])
    def test_exposed_company(self):
        self.splits[2]['company']='Adobe';self.write('splits',self.splits)
        self.assertIn('previously exposed test company',self.result()['errors'])
    def test_label_embargo(self):
        self.splits[0]['label_available']='2007-01-01';self.write('splits',self.splits)
        self.assertIn('chronological label embargo violated',self.result()['errors'])
    def test_missing_component(self):
        self.write('provenance',self.prov[1:])
        self.assertIn('incomplete company profile: 0',self.result()['errors'])
    def test_tamper(self):
        self.paths['engine'].write_text('changed')
        self.assertIn('artifact absent or hash mismatch: engine',self.result()['errors'])
    def test_bad_scores(self):
        for r in self.preds:r['equity_market_cap_usd_b']=0
        self.write('predictions',self.preds)
        self.assertIn('equity WAPE threshold failed',self.result()['errors'])
    def test_missing_outcome(self):
        self.write('labels',self.labels[:-1])
        self.assertIn('label coverage mismatch',self.result()['errors'])
    def test_zero_label(self):
        self.labels[0]['equity_market_cap_usd_b']=0;self.write('labels',self.labels)
        self.assertIn('zero not documented wipeout',self.result()['errors'])
    def test_current_audit_blocks(self):
        self.assertEqual(audit()['status'],'BLOCKED')
        self.assertEqual(audit()['scores'],{})
    def test_disabled_mechanism(self):
        self.traces[0]['status']='neutralized';self.write('execution_trace',self.traces)
        self.assertEqual(self.result()['status'],'BLOCKED')
    def test_missing_execution_trace(self):
        self.write('execution_trace',self.traces[1:]);self.assertIn('incomplete production execution trace',self.result()['errors'])
    def test_synthetic_tier(self):
        self.m['evidence_tier']='synthetic';self.assertEqual(self.result()['status'],'BLOCKED')
    def test_unjustified_zero(self):
        self.traces[0]['status']='evidence_supported_structural_zero';self.write('execution_trace',self.traces)
        self.assertEqual(self.result()['status'],'BLOCKED')
    def acquire(self,**kw):
        z=self.labels[0]; z.update(outcome='acquired_documented',event_date='2014-06-30',value_basis='per_share_x_diluted',equity_market_cap_usd_b=200)
        for r in self.labels[1:]: r.setdefault('event_date',''); r.setdefault('value_basis','')
        z.update(kw); self.write('labels',self.labels)
        for r in self.preds: r.setdefault('horizon_years',5)
        self.preds[0]['horizon_years']=kw.pop('h',2) if 'h' in kw else 2; self.write('predictions',self.preds)
    def test_acquisition_endpoint_accepted(self):
        self.acquire(); res=self.result()
        self.assertEqual(res['status'],'GATE_PASS_REQUIRES_AUTHENTICATED_REVIEW'); self.assertEqual(res['scores']['event']['n'],1)
    def test_acquisition_horizon_mismatch(self):
        self.acquire(); self.preds[0]['horizon_years']=5; self.write('predictions',self.preds)
        self.assertIn('acquisition horizon mismatch: 2',self.result()['errors'])
    def test_acquisition_zero_or_missing_date(self):
        self.acquire(equity_market_cap_usd_b=0); self.assertIn('acquisition label must be positive: 2',self.result()['errors'])
        self.acquire(event_date=''); self.assertEqual(self.result()['status'],'BLOCKED')
    def test_event_horizon(self):
        from datetime import date
        self.assertEqual(event_horizon(date(2015,12,31),date(2016,12,8)),1)
        self.assertEqual(event_horizon(date(2015,12,31),date(2016,3,1)),1)
        self.assertEqual(event_horizon(date(2015,12,31),date(2019,5,3)),3)
    def test_zero_safe(self):
        self.assertEqual(score([0,10],[0,10])['log_mae'],0)
