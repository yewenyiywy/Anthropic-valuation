"""Fail-closed release gate. A pass is necessary, not proof of independent review."""
import argparse
import csv
import hashlib
import json
import math
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_TARGET = 'equity_market_cap_usd_b'
MIN_FAMILIES, MIN_CYCLES = 10, 2
MAX_WAPE, MAX_BIAS = .30, .15
COMPONENTS = frozenset(('revenue','customer_states','retention','acquisition',
    'vendor_switching','price_volume','demand_ceiling','operating_costs','tax',
    'depreciation','capex','working_capital','sbc','cash','debt','leases',
    'commitments','wacc','issuer_lifecycle'))
ARTIFACTS = frozenset(('preregistration','provenance','splits','predictions',
    'labels','parameters','training_log','review','freeze_attestation','engine',
    'model_contract','execution_trace'))
MECHANISMS = frozenset(('customer_birth','customer_survival','retention','pilot_conversion',
    'vendor_competition','billing_exclusion','demand_ceiling','price_volume',
    'commitment_floor','cashflow','issuer_lifecycle'))
EXPOSED = frozenset(('adobe','salesforce','paypal','servicenow','shopify',
    'cisco','aol','yahoo','amazon','ebay','excite@home','pets.com','broadcom',
    'juniper networks','internet capital group','priceline','broadvision',
    'cmgi','doubleclick','realnetworks','verisign','infospace','exodus communications','go2net'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_fingerprint(root):
    """Hash all production and research Python sources, not just the entrypoint."""
    files=sorted(p for d in ('models','evaluation') for p in (root/d).rglob('*.py')
                 if not p.name.startswith('test_'))
    return hashlib.sha256('\n'.join(f'{p.relative_to(root)}:{sha(p)}' for p in files).encode()).hexdigest()

def read_csv(path):
    with path.open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def day(s): return date.fromisoformat(s)
def instant(s): 
    x=datetime.fromisoformat(s.replace('Z','+00:00'))
    if x.tzinfo is None: raise ValueError('timestamp must include timezone')
    return x

def num(s):
    x=float(s)
    if not math.isfinite(x) or x<0: raise ValueError('invalid nonnegative value')
    return x

def ranks(x):
    order=sorted(range(len(x)),key=lambda i:x[i]); r=[0.]*len(x); i=0
    while i<len(order):
        j=i
        while j+1<len(order) and x[order[j+1]]==x[order[i]]: j+=1
        for k in range(i,j+1): r[order[k]]=(i+j)/2
        i=j+1
    return r

def spearman(p,y):
    """Auxiliary cross-sectional rank agreement; NOT a release threshold."""
    if len(y)<3: return None
    a,b=ranks(list(p)),ranks(list(y)); ma,mb=sum(a)/len(a),sum(b)/len(b)
    num=sum((u-ma)*(v-mb) for u,v in zip(a,b))
    den=math.sqrt(sum((u-ma)**2 for u in a)*sum((v-mb)**2 for v in b))
    return num/den if den else None

def score(p,y):
    if not y or sum(y)<=0: raise ValueError('positive aggregate target required')
    # wape/bias drive the preregistered gate; spearman is reported alongside
    # because an intrinsic-value model can be informative about ranking even
    # when market multiples move. Thresholds are unchanged.
    return dict(wape=sum(abs(a-b) for a,b in zip(p,y))/sum(y),
                bias=sum(a-b for a,b in zip(p,y))/sum(y),
                log_mae=sum(abs(math.log1p(a)-math.log1p(b)) for a,b in zip(p,y))/len(y),
                spearman=spearman(p,y))

def check(manifest, root=ROOT):
    errors=[]; report={}
    def require(ok,msg):
        if not ok: errors.append(msg)
    try:
        require(manifest['target']==PRIMARY_TARGET,'wrong primary target')
        require(manifest['model_entrypoint']=='models.joint_customer_states.forecast_joint','wrong engine')
        require(manifest['model_scope']=='full_company_profile','surrogate model forbidden')
        require(manifest['evidence_tier']=='observed_historical','imputed or synthetic tier cannot qualify for observed release')
        require(manifest['training_objective']=='equity_log1p_mae','equity objective required')
        require(manifest['source_fingerprint']==source_fingerprint(root),'source tree hash mismatch')
        require(manifest['horizon_years']==5,'wrong horizon')
        require(manifest['thresholds']==dict(max_wape=MAX_WAPE,max_abs_bias=MAX_BIAS,min_families=MIN_FAMILIES,min_cycles=MIN_CYCLES),'thresholds changed')
        require(instant(manifest['registered_at'])<instant(manifest['frozen_at'])<instant(manifest['labels_opened_at']),'invalid freeze order')
        require(instant(manifest['reviewed_at'])>=instant(manifest['labels_opened_at']),'review predates scoring')
        require(manifest['reviewer'] and manifest['reviewer']!=manifest['trainer'],'independent reviewer required')
        files={}
        require(set(manifest['artifacts'])==ARTIFACTS,'missing or unknown artifacts')
        for k in ARTIFACTS:
            a=manifest['artifacts'][k]; f=(root/a['path']).resolve()
            require(f.is_relative_to(root.resolve()),'artifact outside repository')
            if not f.is_relative_to(root.resolve()): raise ValueError('unsafe artifact path')
            require(f.is_file() and f.stat().st_size>0 and sha(f)==a['sha256'],f'artifact absent or hash mismatch: {k}')
            files[k]=f
        require(files['engine']==(root/'models/joint_customer_states.py').resolve(),'engine artifact not production entrypoint')
        if errors: return dict(status='BLOCKED',errors=errors)
        splits=read_csv(files['splits']); prov=read_csv(files['provenance'])
        preds=read_csv(files['predictions']); labels=read_csv(files['labels'])
        contract=json.loads(files['model_contract'].read_text())
        require(contract['entrypoint']==manifest['model_entrypoint'],'contract entrypoint mismatch')
        require(contract['source_fingerprint']==manifest['source_fingerprint'],'contract source mismatch')
        require(set(contract['mechanisms'])==MECHANISMS,'incomplete production architecture contract')
        ids=[r['sample_id'] for r in splits]
        require(len(ids)==len(set(ids)), 'duplicate sample IDs')
        groups={k:[r for r in splits if r['split']==k] for k in ('train','validation','test')}
        require(sum(map(len,groups.values()))==len(splits),'unknown split')
        require(all(groups.values()),'empty partition')
        families={k:{r['family_id'].strip().casefold() for r in v} for k,v in groups.items()}
        require(all(x for v in families.values() for x in v),'blank family ID')
        require(not(families['train']&families['validation'] or families['train']&families['test'] or families['validation']&families['test']),'issuer family overlap')
        require(not families['test']&EXPOSED,'previously exposed test family')
        require(not any(r['company'].strip().casefold() in EXPOSED for r in groups['test']),'previously exposed test company')
        require(len(families['test'])>=MIN_FAMILIES,'too few test families')
        require(len({r['cycle'] for r in groups['test'] if r['cycle'].strip()})>=MIN_CYCLES,'too few test cycles')
        for r in splits:
            origin=day(r['origin']); end=day(r['target_date'])
            require(end.year-origin.year==5 and abs((end-origin).days-1826)<=2,'not five-year calendar horizon: '+r['sample_id'])
            require(day(r['label_available'])>=end,'label date precedes target')
            require(r['company'].strip().casefold()!='anthropic','Anthropic is application only')
        for earlier,later in (('train','validation'),('validation','test')):
            if groups[earlier] and groups[later]:
                require(max(day(r['label_available']) for r in groups[earlier])<=min(day(r['origin']) for r in groups[later]),'chronological label embargo violated')
        byid={r['sample_id']:r for r in splits}
        seen=set()
        for r in prov:
            sid=r['sample_id']; key=(sid,r['component'])
            require(key not in seen,'duplicate component provenance')
            seen.add(key)
            require(day(r['available_date'])<=day(byid[sid]['origin']),'future feature: '+sid)
            require(r['status']=='verified' and r['source'].startswith('https://') and r['reconciliation'].strip() and r['document_section'].strip() and r['units'].strip(),'unverified component: '+str(key))
        for sid in ids:
            require(COMPONENTS<={c for i,c in seen if i==sid},'incomplete company profile: '+sid)
        # Structural evidence, not proof that a claimed trace was genuinely executed.
        # Independent review must authenticate trace and verify actual outputs/ablations.
        trace=read_csv(files['execution_trace']); traced=set()
        for r in trace:
            key=(r['sample_id'],r['mechanism'])
            require(key not in traced,'duplicate execution trace')
            traced.add(key)
            require(r['sample_id'] in set(ids)|{'anthropic_application'},'unknown trace issuer')
            require(r['mechanism'] in MECHANISMS,'unknown mechanism')
            require(r['status'] in ('active','evidence_supported_structural_zero'),'disabled or neutralized mechanism: '+str(key))
            require(r['architecture_sha256']==sha(files['model_contract']),'architecture trace mismatch')
            require(r['checkpoint_sha256']==sha(files['parameters']),'checkpoint trace mismatch')
            require(bool(r['trace_evidence'].strip()) and bool(r['input_evidence'].strip()) and bool(r['ablation_evidence'].strip()),'missing mechanism evidence: '+str(key))
            if r['status']=='evidence_supported_structural_zero':
                require(r['structural_zero_source'].startswith('https://'),'unjustified structural zero: '+str(key))
        require(traced=={(sid,c) for sid in ids+['anthropic_application'] for c in MECHANISMS},'incomplete production execution trace')
        expected={r['sample_id'] for r in groups['test']}
        require(len(preds)==len(expected) and {r['sample_id'] for r in preds}==expected,'prediction coverage mismatch')
        require(len(labels)==len(expected) and {r['sample_id'] for r in labels}==expected,'label coverage mismatch')
        if errors: return dict(status='BLOCKED',errors=errors)
        ymap={r['sample_id']:r for r in labels}
        y=[]; p=[]; flat=[]; ps=[]
        for r in preds:
            sid=r['sample_id']; z=ymap[sid]; origin=byid[sid]
            require(z['target_date']==origin['target_date'],'label date mismatch')
            require(z['source'].startswith('https://'),'missing market cap source')
            actual=num(z['equity_market_cap_usd_b']); prediction=num(r['equity_market_cap_usd_b'])
            require(z['outcome'] in ('listed','wipeout','acquired_documented'),'unresolved exit')
            require(actual>0 or z['outcome']=='wipeout','zero not documented wipeout')
            require(z['outcome']!='wipeout' or actual==0,'wipeout label nonzero')
            y.append(actual);p.append(prediction)
            base=num(origin['origin_market_cap']); rev=num(origin['origin_revenue'])
            if rev<=0: raise ValueError('constant P/S baseline undefined')
            flat.append(base);ps.append(base*num(r['revenue5'])/rev)
        report={'equity':score(p,y),'flat':score(flat,y),'constant_ps':score(ps,y),'n':len(y)}
        sc=report['equity']
        require(sc['wape']<=MAX_WAPE,'equity WAPE threshold failed')
        require(abs(sc['bias'])<=MAX_BIAS,'equity bias threshold failed')
        require(sc['wape']<min(report['flat']['wape'],report['constant_ps']['wape']),'naive baseline not beaten')
    except (KeyError,TypeError,ValueError,OSError,AttributeError) as exc:
        errors.append('invalid or incomplete evidence: '+str(exc))
    return dict(status='BLOCKED' if errors else 'GATE_PASS_REQUIRES_AUTHENTICATED_REVIEW',errors=errors,scores=report)

def audit():
    # Do not run legacy aggregate surrogates as the production audit.
    return dict(status='BLOCKED',scope='production model not yet evaluated',scores={},
                blockers=['no independent untouched final test','no full-model equity-loss training',
                          'no complete observed or validated reconstructed company profiles',
                          'no production architecture contract and execution trace',
                          'no frozen release manifest or independent review'])

def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--audit',action='store_true')
    group.add_argument('--manifest',type=Path)
    args=parser.parse_args()
    result=audit() if args.audit else check(json.loads(args.manifest.read_text()))
    print(json.dumps(result,indent=2))
    return 0 if args.audit or result['status'].startswith('GATE_PASS') else 1

if __name__=='__main__':
    raise SystemExit(main())
