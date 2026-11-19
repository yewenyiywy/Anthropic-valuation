"""Five-year equity market cap holdout; reduced-state finite lifecycle DCF."""
import csv
import numpy as np
from evaluation.cloud_cycle import cohort
from evaluation.external_validation import calibrate, forecast
from evaluation.fundamental_growth import panel
from evaluation.company_oos import metrics
from evaluation.validation_gate import spearman
from models.valuation import ROOT, SCENARIOS, lifecycle_tail

def inputs():
    with (ROOT/'data/cloud_equity_cohort.csv').open() as f:
        equity={r['company']:r for r in csv.DictReader(f)}
    return [dict(r,**equity[r['company']]) for r in cohort()]

def converge_target(company):
    """m* for CFO-capex margins, fitted on the margin development panel
    EXCLUDING the issuer's own family (half-life fixed at 3 years)."""
    from evaluation.margin_development import panel, fit
    fam=company.lower()
    return fit([x for x in panel() if x['family']!=fam],'cfo',3.)['mstar']

def predict_value(r, train, theta, wacc=.12, retention=0, mature_margin='converge', horizon=5):
    q=dict(company=r['company'],r1998=r['r2019'],r1999=r['r2020'])
    r0=float(r['r2020'])
    r5=float(forecast(train,q,theta)['size_blend'])
    m0=(float(r['cfo20'])-float(r['capex20']))/r0
    # Historical CFO-capex is a levered cash flow proxy, not exact FCFF.
    # Starting margin is company-specific (origin-known).
    g=np.log(r5/r0)/5
    R=[r0*np.exp(g*t) for t in range(6)]
    for t in range(6,11):
        R.append(R[-1]*np.exp(g*max(0,1-(t-5)/5)))
    # Default: converge to a family-excluded m* with a 3-year half-life, the
    # development estimate from 18 cloud margin paths (holding the origin margin
    # underpredicted stage-4 margins by ~23pp). mature_margin=None holds the
    # origin margin; a number fades linearly to it (.15 = original diagnostic).
    # NOTE: these five issuers are in the margin panel, so m* is fitted
    # leave-family-out but the panel design itself saw their outcomes.
    if mature_margin=='converge':
        m=converge_target(r['company']); margins=[m+(m0-m)*2**(-t/3) for t in range(11)]
    else:
        m=m0 if mature_margin is None else mature_margin
        margins=[m0+(m-m0)*t/10 for t in range(11)]
    fcf=np.array(R)*np.array(margins)
    p=dict(SCENARIOS['base'],wacc=wacc)
    o=dict(commit_total=0,commit_to_2030=0,commit_next12m=0)
    tail,_=lifecycle_tail(R[10],p,o,margins=(m,.2*m,min(.60,4*m/3) if m>0 else m,0.))
    net=float(r['cash20'])-float(r['debt20'])
    v0=sum(fcf[t]/(1+wacc)**t for t in range(1,11))+tail+net
    # Revalue only future cash flows at t=5; past cash flow is not counted twice.
    # Equity value at year k (k=5 is the five-year endpoint). Other k support the
    # acquisition endpoint policy (evaluation/acquisition_endpoint_policy.md):
    # an issuer acquired at year tau is compared at k=round(tau), min 1.
    if not 1<=horizon<=10: raise ValueError('horizon must be 1..10 years')
    k=int(horizon)
    v5=sum(fcf[t]/(1+wacc)**(t-k) for t in range(k+1,11))+tail*(1+wacc)**k+net+retention*sum(fcf[1:k+1])
    return dict(value0=max(0,float(v0)),dcf=max(0,float(v5)),horizon=k,
                flat_cap=float(r['cap20']),
                constant_ps=float(r['cap20'])*r5/r0,
                revenue5=r5,margin0=m0,fcf5=float(fcf[5]))

def evaluate(rows=None):
    train=panel()
    theta=calibrate(train)
    out=[]
    for r in inputs() if rows is None else rows:
        p=predict_value(r,train,theta)
        for w in (.08,.10,.15):
            p[f'dcf_{w}']=predict_value(r,train,theta,wacc=w)['dcf']
        p['dcf_retained']=predict_value(r,train,theta,retention=1)['dcf']
        p['dcf_shared15']=predict_value(r,train,theta,mature_margin=.15)['dcf']
        p['dcf_hold']=predict_value(r,train,theta,mature_margin=None)['dcf']
        out.append(dict(company=r['company'],actual=float(r['cap25']),actual0=float(r['cap20']),pred=p))
    keys=['dcf','flat_cap','constant_ps','dcf_0.08','dcf_0.1','dcf_0.15','dcf_retained','dcf_shared15','dcf_hold']
    scores={k:metrics([(r['pred'][k],r['actual']) for r in out]) for k in keys}
    for k in keys:
        scores[k]['bias']=sum(r['pred'][k]-r['actual'] for r in out)/sum(r['actual'] for r in out)
        scores[k]['spearman']=spearman([r['pred'][k] for r in out],[r['actual'] for r in out])
    # Auxiliary fundamental targets (matched-definition CFO-capex proxy for FCF).
    with (ROOT/'data/cloud_company_vintage.csv').open() as f:
        v={r['company']:r for r in csv.DictReader(f)}
    rev={r['company']:float(r['r2025']) for r in inputs()}
    fundamentals=dict(
        revenue5=dict(metrics([(r['pred']['revenue5'],rev[r['company']]) for r in out]),
                      spearman=spearman([r['pred']['revenue5'] for r in out],[rev[r['company']] for r in out])),
        fcf5=dict(metrics([(r['pred']['fcf5'],float(v[r['company']]['cfo25'])-float(v[r['company']]['capex25'])) for r in out]),
                  spearman=spearman([r['pred']['fcf5'] for r in out],[float(v[r['company']]['cfo25'])-float(v[r['company']]['capex25']) for r in out])))
    return dict(status='previously exposed cohort; development diagnostic only',rows=out,scores=scores,fundamentals=fundamentals,initial_dcf=metrics([(r['pred']['value0'],r['actual0']) for r in out]))

if __name__=='__main__':
    import json
    print(json.dumps(evaluate(),indent=2))
