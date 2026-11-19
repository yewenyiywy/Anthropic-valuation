"""Vintage-data audit and direct execution of the shared joint engine.

The aggregate restriction is NOT a full customer-level historical backtest.
Cloud 2020 is an already viewed diagnostic, not an untouched final test.
"""
import csv
import numpy as np
from evaluation.cloud_equity import inputs
from evaluation.external_validation import calibrate, forecast
from evaluation.fundamental_growth import panel
from evaluation.company_oos import metrics
from models.joint_customer_states import forecast_joint, SCENARIOS, INPUTS
from models.valuation import ROOT, lifecycle_tail

MISSING=('customer revenue by lifecycle and financial health','pilot conversion and rollout',
         'vendor switching and multi-homing','price/volume decomposition',
         'gross acquisition and retention by cohort','customer demand ceilings',
         'issuer survival/renewal transition calibration','company WACC',
         'future capital structure and working capital')

def vintage():
    with (ROOT/'data/cloud_company_vintage.csv').open() as f:
        financials={r['company']:r for r in csv.DictReader(f)}
    rows=[dict(r,**financials[r['company']]) for r in inputs()]
    for r in rows:
        if not np.isclose(float(r['subscription20'])+float(r['other20']),float(r['r2020']),rtol=1e-5):
            raise ValueError('revenue bridge fails: '+r['company'])
        if not all(r[k].startswith('https://') for k in ('source20','source25','market_source')):
            raise ValueError('missing source')
    return rows

def train():
    # 1999 issuer histories only: no 2020 or 2025 data enters calibration.
    p=panel()
    return p,calibrate(p)

def profile(r,p,theta,strict=False):
    if strict:
        raise ValueError('Unidentified full company profile: '+ '; '.join(MISSING))
    r0=float(r['r2020'])
    q=dict(company=r['company'],r1998=r['r2019'],r1999=r['r2020'])
    target=forecast(p,q,theta)['size_blend']
    # Solve net growth parameter for the shared engine's fade schedule.
    fade=1-np.arange(5)/7
    lo,hi=-.999,10.
    for _ in range(80):
        mid=(lo+hi)/2
        if np.prod(1+mid*fade)<target/r0: lo=mid
        else: hi=mid
    g=(lo+hi)/2
    # Explicit aggregate restriction: neutral inactive axes, not invented churn.
    # All subscription is a billing ledger proxy, not employer-only revenue.
    sub=float(r['subscription20']); other=float(r['other20'])
    # No claim that PayPal has zero subscriptions; all revenue is unclassified other.
    ebit=float(r['operating_income20'])/r0
    da=float(r['da20'])/r0; capex=float(r['capex20'])/r0
    # Economic SBC remains in EBIT. Zero incremental NWC is a sensitivity assumption.
    def cashflow(revenue,t): return revenue*(ebit-.25*max(0,ebit)+da-capex)
    s={k:0. for k in SCENARIOS['base']}
    s.update(price=1.,volume=1+g,subscription_growth=g,funding=1.,wacc=.12,
             exit=.06,decline=.20,renew=.08)
    a={k:0. for k in INPUTS['base']}
    a.update(weights=(0,0,0,1),churn_factors=(0,0,0,0))
    def init(v):
        x=np.zeros((8,3,3,7)); x[7,0,0,0]=sum(v); return x
    o=dict(run_rate=r0,proforma_cash=float(r['cash20']),proforma_convertibles=float(r['debt20']),
           commit_total=0,commit_to_2030=0,commit_next12m=0)
    # Same finite lifecycle continuation; separately disclose unestimated tail.
    # Tail margin is the issuer's own origin FCFF proxy margin, not Anthropic's.
    m=ebit-.25*max(0,ebit)+da-capex
    def tail(revenue,scenario,observations): return lifecycle_tail(revenue,scenario,observations,margins=(m,.2*m,min(.60,4*m/3) if m>0 else m,0.))
    prof=dict(scenario=s,inputs=a,birth_share=0.,weights=[0]*7+[1.],retention=[1.]*4,
              start=(other,sub,0.),initialize=init,kernel=lambda regime:np.eye(72),
              vendor=lambda regime:np.tile(np.eye(7),(8,1,1)),birth_budget=lambda t,reg:0.,
              enterprise_cap=lambda t:float('inf'),personal_cap=0.,reward=lambda x:float(x.sum()),
              macro_growth=np.ones(3),health_spend=1.,tail=tail,commitment_floor=lambda t:0.,
              cashflow=cashflow)
    return o,prof,target

def predict(r,p,theta):
    o,prof,target=profile(r,p,theta)
    rows,ev,equity=forecast_joint(o=o,profile=prof)
    w=prof['scenario']['wacc']
    # Roll the identical engine's NPV to year five, removing spent historical FCF.
    past=sum(x['fcf']/(1+w)**x['year'] for x in rows[:5])
    v5=(ev-past)*(1+w)**5+o['proforma_cash']-o['proforma_convertibles']
    assert np.isclose(rows[4]['revenue'],target)
    return dict(revenue5=rows[4]['revenue'],fcf5=rows[4]['fcf'],equity5=max(0.,v5),equity0=equity)

def evaluate(rows=None):
    p,theta=train()
    out=[]
    for r in vintage() if rows is None else rows:
        pred=predict(r,p,theta)
        actual=dict(revenue5=float(r['r2025']),fcf5=float(r['cfo25'])-float(r['capex25']),equity5=float(r['cap25']))
        out.append(dict(company=r['company'],pred=pred,actual=actual))
    return dict(status='aggregate engine restriction; full validation blocked; previously viewed diagnostic',
                missing=MISSING,theta=theta,rows=out,
                scores={k:metrics([(r['pred'][k],r['actual'][k]) for r in out]) for k in ('revenue5','fcf5','equity5')})

if __name__=='__main__':
    import json
    print(json.dumps(evaluate(),indent=2))
