"""Vintage external benchmark and Anthropic-specific accounting sensitivity.

Not a complete cross-company joint-state backtest: company transition matrices
remain unidentified. Never fill missing historical parameters with Claude data.
"""
import csv
import numpy as np
from models.joint_customer_states import forecast_joint, observations, MACRO
from models.valuation import ROOT

def anchors():
    with (ROOT/'data/company_specific_anchors.csv').open() as f:
        return {r['metric']:float(r['value']) for r in csv.DictReader(f) if r['company']=='Anthropic'}

def vintage():
    with (ROOT/'data/dotcom_vintage.csv').open() as f:
        return list(csv.DictReader(f))

def benchmark():
    rows=[]
    for r in vintage():
        if not r['cy00e'] or not r['cy00_actual']: continue
        p,y=float(r['cy00e']),float(r['cy00_actual'])
        rows.append(dict(company=r['company'],forecast=p,actual=y,ape=abs(p-y)/y))
    return rows, sum(r['ape'] for r in rows)/len(rows)

def anthropic(n=1024,seed=42):
    a=anchors(); o=observations(); o.update(proforma_cash=a['adjusted_cash'],proforma_convertibles=a['adjusted_convertibles'])
    # Reported accrual costs are NOT FCFF; use a sensitivity at an observed ratio,
    # not a claim the expenses are all incremental cash costs or sustainable.
    ratio=a['compute_infrastructure']/a['revenue']; other=a['other_opex']/a['revenue']
    rng=np.random.default_rng(seed); results=[]
    for _ in range(n):
        path=[]; k=1
        for t in range(10):
            k=int(rng.choice(3,p=MACRO[k])); path.append(k)
        results.append([forecast_joint(regime_path=path,o=o,scenario_overrides=s)[2] for s in ({},{'cost_ratio':ratio},{'cost_ratio':ratio,'other_ratio':other})])
    return dict(compute_ratio=ratio,other_accrual_ratio=other,mean_equity=np.mean(results,axis=0).tolist(),adjusted_bridge=o['proforma_cash']-o['proforma_convertibles'])

if __name__=='__main__':
    print('Historical analyst benchmark (not the joint model):',benchmark())
    print('Anthropic accounting sensitivities (not fitted fair value):',anthropic())
