"""Issuer-external historical test; not a point-in-time market forecast."""
import csv
import numpy as np
from evaluation.fundamental_growth import panel, fit
from evaluation.five_year import saturation
from evaluation.company_oos import metrics, predict
from models.valuation import ROOT

PRIMARY = 'size_blend'  # selected on prior cohort WAPE, not external outcomes

def load():
    with (ROOT/'data/dotcom_external_cohort.csv').open() as f:
        return list(csv.DictReader(f))

def calibrate(train):
    grid=[(s,h,c,0) for s in (.25,.5,.75,1) for h in (.5,1,2,4) for c in (.2,.4,.7,1)]
    def loss(theta):
        return np.mean([abs(np.log(p[t]/float(q[f'r{2000+t}'])))
                        for q in train for p in [saturation(q,*theta)]
                        for t in range(4) if q[f'r{2000+t}']])
    return min(grid,key=loss)

def forecast(train, target, theta):
    r=dict(target,gross_margin='')
    a,b=float(r['r1998']),float(r['r1999'])
    sat=float(saturation(r,*theta)[-1])
    rec=float(fit(train,r,'recovery')[0])
    size=float(fit(train,r,'size')[0])
    blend=np.sqrt(sat*rec)
    return dict(flat=b,original=predict(a,b)[-1],saturation=sat,
                recovery=rec,size=size,blend=blend,size_blend=np.sqrt(size*blend))

def evaluate(external=None):
    train=panel()
    external=load() if external is None else external
    assert not set(r['company'] for r in train)&set(r['company'] for r in external)
    theta=calibrate(train)
    rows=[dict(company=r['company'],actual=float(r['r2004']),
               pred=forecast(train,r,theta)) for r in external if r['status']=='observed']
    scores={}
    for k in rows[0]['pred']:
        p,y=np.array([(r['pred'][k],r['actual']) for r in rows]).T
        scores[k]=dict(**metrics(list(zip(p,y))),bias=float((p-y).sum()/y.sum()),
                       median_ape=float(np.median(abs(p/y-1))))
    return dict(primary=PRIMARY,theta=theta,rows=rows,scores=scores,
                censored=[(r['company'],r['status']) for r in external if r['status']!='observed'])

if __name__=='__main__':
    import json
    print(json.dumps(evaluate(),indent=2))
