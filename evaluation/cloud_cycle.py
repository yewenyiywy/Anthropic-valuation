"""Cross-cycle revenue test. No cloud endpoint enters fitting."""
import csv
import numpy as np
from evaluation.external_validation import calibrate, forecast, load
from evaluation.fundamental_growth import panel
from evaluation.five_year import saturation
from evaluation.company_oos import metrics
from models.valuation import ROOT

def cohort():
    with (ROOT/'data/cloud_cycle_cohort.csv').open() as f:
        return list(csv.DictReader(f))

def fit_prior(train):
    # Equal issuer weights, robust log endpoint loss, historical data only.
    rows=[r for r in train if r.get('r2004')]
    grid=[(s,h,c,m) for s in (.25,.5,.75,1)
          for h in (.5,1,2,4) for c in (.2,.4,.7,1)
          for m in (-.1,0,.05,.1,.15,.2)]
    def loss(theta):
        e=[abs(np.log(saturation(r,*theta)[-1]/float(r['r2004']))) for r in rows]
        # Small fixed penalty against aggressive mature drift.
        return np.mean(e)+.5*abs(theta[-1])
    return min(grid,key=loss),float(np.median([float(r['r2004'])/float(r['r1999']) for r in rows]))

def evaluate(targets=None):
    train=panel()
    theta=calibrate(train)
    prior,multiple=fit_prior(train+[r for r in load() if r['status']=='observed'])
    rows=[]
    for r in cohort() if targets is None else targets:
        q=dict(company=r['company'],r1998=r['r2019'],r1999=r['r2020'])
        p=forecast(train,q,theta)
        p['endpoint_prior']=float(saturation(q,*prior)[-1])
        p['historical_multiple']=float(r['r2020'])*multiple
        # Fixed diagnostic floors, not fit/selected on cloud outcomes.
        for m in (0,.05,.10,.15):
            p[f'floor_{m:.2f}']=float(saturation(q,*theta[:3],m)[-1])
        rows.append(dict(company=r['company'],actual=float(r['r2025']),pred=p))
    scores={}
    for k in rows[0]['pred']:
        p,y=np.array([(r['pred'][k],r['actual']) for r in rows]).T
        scores[k]=dict(**metrics(list(zip(p,y))),bias=float((p-y).sum()/y.sum()),
                       median_ape=float(np.median(abs(p/y-1))))
    return dict(theta=theta,endpoint_prior=prior,historical_multiple=multiple,rows=rows,scores=scores)

if __name__=='__main__':
    import json
    print(json.dumps(evaluate(),indent=2))
