"""Development-only equity loss fit. See equity_training_protocol.md."""
import csv
import itertools
import json
import numpy as np
from evaluation.joint_model_audit import vintage
from models.joint_customer_states import forecast_joint, SCENARIOS, INPUTS
from models.valuation import ROOT, lifecycle_tail

BASE=(.5,.15,30)

def data(name):
    with (ROOT/'data'/name).open() as f:
        return {r['company']:r for r in csv.DictReader(f)}

def training_rows():
    p=data('dotcom_fy_panel.csv'); f=data('dotcom_structural_factors.csv')
    return [dict(company=n,prior=float(p[n]['r1998']),revenue=float(p[n]['r1999']),
                 cashflow=float(f[n]['cfo1999'])-float(f[n]['capex1999']),
                 cap0=float(r['cap99']),cap5=float(r['cap04']),revenue5=float(p[n]['r2004']))
            for n,r in data('dotcom_equity_endpoints.csv').items()]

def transfer_rows():
    return [dict(company=r['company'],prior=float(r['r2019']),revenue=float(r['r2020']),
                 cashflow=float(r['cfo20'])-float(r['capex20']),cap0=float(r['cap20']),
                 cap5=float(r['cap25']),revenue5=float(r['r2025'])) for r in vintage()]

def predict(r,theta):
    shrink,mature,horizon=theta
    r0=r['revenue']; initial=r['cashflow']/r0
    g=np.expm1(np.clip(np.log(r0/r['prior'])*shrink,-.5,.8))
    s={k:0. for k in SCENARIOS['base']}
    s.update(price=1.,volume=1+g,subscription_growth=g,funding=1.,wacc=.12,exit=.06,decline=.20,renew=.08)
    a={k:0. for k in INPUTS['base']}; a.update(weights=(0,0,0,1),churn_factors=(0,0,0,0))
    def init(v):
        x=np.zeros((8,3,3,7)); x[7,0,0,0]=sum(v); return x
    o=dict(run_rate=r0,proforma_cash=0.,proforma_convertibles=0.,commit_total=0.,commit_to_2030=0.,commit_next12m=0.)
    prof=dict(scenario=s,inputs=a,birth_share=0.,weights=[0]*7+[1.],retention=[1.]*4,
              start=(r0,0.,0.),initialize=init,kernel=lambda _:np.eye(72),
              vendor=lambda _:np.tile(np.eye(7),(8,1,1)),birth_budget=lambda *_:0.,
              enterprise_cap=lambda _:float('inf'),personal_cap=0.,reward=lambda x:float(x.sum()),
              macro_growth=np.ones(3),health_spend=1.,commitment_floor=lambda _:0.,
              cashflow=lambda rev,t:rev*(initial+(mature-initial)*min(t/10,1)),
              tail=lambda rev,p,o:lifecycle_tail(rev,p,o,horizon=horizon,margins=(mature,.2*mature,min(.60,4*mature/3),0)))
    rows,ev,_=forecast_joint(o=o,profile=prof)
    past=sum(x['fcf']/1.12**x['year'] for x in rows[:5])
    return dict(equity5=max(0.,(ev-past)*1.12**5),equity0=max(0.,ev),revenue5=rows[4]['revenue'])

def score(rows,theta,persistence=None):
    details=[dict(r,**{'pred':predict(r,theta)}) for r in rows]
    if persistence is not None:
        for r in details:
            p=r['pred']; premium=np.log1p(r['cap0'])-np.log1p(p['equity0'])
            p['equity5']=max(0.,np.expm1(np.log1p(p['equity5'])+persistence*premium))
    y=np.array([r['cap5'] for r in details]); p=np.array([r['pred']['equity5'] for r in details])
    ry=np.array([r['revenue5'] for r in details]); rp=np.array([r['pred']['revenue5'] for r in details])
    return dict(wape=float(abs(p-y).sum()/y.sum()),bias=float((p-y).sum()/y.sum()),
                logmae=float(abs(np.log1p(p)-np.log1p(y)).mean()),revenue_wape=float(abs(rp-ry).sum()/ry.sum()),
                unchanged_cap_wape=float(sum(abs(r['cap0']-r['cap5']) for r in rows)/y.sum()),rows=details)

def fit(rows):
    trials=[]
    for theta in itertools.product((.25,.5,.75,1.),(.10,.15,.25,.35,.45),(20,30,40)):
        result=score(rows,theta)
        penalty=.02*sum(((a-b)/s)**2 for a,b,s in zip(theta,BASE,(.5,.15,10)))
        trials.append(dict(theta=theta,objective=result['logmae']+penalty,logmae=result['logmae'],wape=result['wape']))
    return min(trials,key=lambda x:x['objective'])['theta'],trials

def run():
    train=training_rows(); theta,trials=fit(train)
    transfer=transfer_rows()
    growth=min((.25,.5,.75,1.),key=lambda g:np.mean([abs(np.log(predict(r,(g,.15,30))['revenue5']/r['revenue5'])) for r in train]))
    structural=(growth,.15,30)
    premium_trials=[dict(persistence=float(p),logmae=score(train,structural,p)['logmae']) for p in np.linspace(0,1,11)]
    persistence=min(premium_trials,key=lambda x:x['logmae'])['persistence']
    return dict(status='development only; release blocked',theta=theta,trials=trials,
                train_baseline=score(train,BASE),train_fitted=score(train,theta),
                transfer_baseline=score(transfer,BASE),transfer_fitted=score(transfer,theta),
                premium_theta=structural,persistence=persistence,premium_trials=premium_trials,
                train_premium=score(train,structural,persistence),transfer_premium=score(transfer,structural,persistence))

if __name__=='__main__':
    print(json.dumps(run(),indent=2))
