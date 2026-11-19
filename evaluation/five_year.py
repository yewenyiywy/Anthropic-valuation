"""Five-year endpoint validation; cross-company folds are retrospective, not time OOS."""
import csv
import numpy as np
from evaluation.company_oos import panel, predict, metrics
from models.valuation import ROOT

def complete_panel():
    rows=panel()
    with (ROOT/'data/dotcom_five_year.csv').open() as f:
        supplements={r['company']:r for r in csv.DictReader(f)}
    for r in rows:
        if r['company'] in supplements:
            r.update({k:supplements[r['company']][k] for k in ('r2002','r2003','r2004')})
    return rows

def saturation(r, scale, half, ceiling, mature=0):
    # Cap initial annual log growth, then decay; ceiling is a relative growth-rate cap, not TAM.
    g=np.clip(scale*np.log(float(r['r1999'])/float(r['r1998'])), -ceiling, ceiling)
    return float(r['r1999'])*np.exp(np.cumsum(mature+(g-mature)*2**(-np.arange(5)/half)))

def evaluate(mature_grid=(0,)):
    rows=complete_panel(); eligible=[r for r in rows if r['r2004']]
    grid=[(s,h,c,m) for s in (.25,.5,.75,1) for h in (.5,1,2,4) for c in (.2,.4,.7,1.0) for m in mature_grid]
    reports=[]
    for r in eligible:
        # Other issuers' 2000–03 outcomes only; no 2004 outcomes for fitting.
        train=[q for q in rows if q['company']!=r['company']]
        def loss(theta):
            errors=[]
            for q in train:
                p=saturation(q,*theta)
                errors.extend(abs(np.log(p[t]/float(q[f'r{2000+t}']))) for t in range(4) if q[f'r{2000+t}'])
            return np.mean(errors)
        theta=min(grid,key=loss)
        a,b=float(r['r1998']),float(r['r1999']); y=float(r['r2004'])
        reports.append(dict(company=r['company'],actual=y,original=predict(a,b)[-1],half_life=predict(a,b,half_life=1)[-1],flat=b,calibrated=float(saturation(r,*theta)[-1]),theta=theta))
    scores={k:metrics([(r[k],r['actual']) for r in reports]) for k in ('original','half_life','flat','calibrated')}
    return {'rows':reports,'scores':scores,'censored':[r['company'] for r in rows if not r['r2004']]}

if __name__=='__main__':
    import json
    print(json.dumps({'base':evaluate(),'mature_growth_extension':evaluate((-.1,0,.1,.2,.3))},indent=2))
