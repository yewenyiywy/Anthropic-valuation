"""Revenue forecast comparisons with observed 1999 gross margins; no 2004/05 fitting."""
import csv
import numpy as np
from evaluation.five_year import complete_panel, evaluate, saturation
from evaluation.growth_comparison import PARTIAL
from evaluation.company_oos import metrics, predict
from models.valuation import ROOT

def panel():
    with (ROOT/'data/dotcom_fundamentals.csv').open() as f:
        anchors={r['company']:r for r in csv.DictReader(f)}
    return [dict(r,**{k:anchors[r['company']][k] for k in ('gross_margin','r2005')}) for r in complete_panel()]

def fit(train,target,kind):
    median=np.median([float(r['gross_margin']) for r in train if r['gross_margin']])
    def x(r,t):
        dec=1-2**(-t); size=np.log(float(r['r1999'])); g=np.clip(np.log(float(r['r1999'])/float(r['r1998'])),0,1.5)
        if r['company'] in PARTIAL: g=0
        gm=float(r['gross_margin']) if r['gross_margin'] else median
        base=[dec,t]
        if kind in ('margin','margin_size','margin_growth'): base+=[t*(gm-median)]
        if kind in ('size','margin_size'): base+=[t*size]
        if kind=='margin_growth': base+=[dec*g]
        return base
    X=[]; Y=[]; W=[]
    for r in train:
        ts=[t for t in range(1,5) if r[f'r{1999+t}']]
        for t in ts:
            X.append(x(r,t)); Y.append(np.log(float(r[f'r{1999+t}'])/float(r['r1999']))); W.append(1/len(ts))
    X=np.array(X); y=np.array(Y); w=np.array(W); norm=np.maximum(np.sqrt(np.average(X**2,axis=0,weights=w)),1e-8); Z=X/norm
    P=np.eye(Z.shape[1])*4; P[0,0]=0
    beta=np.linalg.solve(Z.T@(w[:,None]*Z)+P,Z.T@(w*y))
    return float(target['r1999'])*np.exp(np.array([x(target,t) for t in (5,6)])/norm@beta)

def compare():
    rows=panel(); old={r['company']:r for r in evaluate()['rows']}; out=[]
    kinds=('recovery','margin','size','margin_size','margin_growth')
    for r in rows:
        if not r['r2004']: continue
        train=[q for q in rows if q['company']!=r['company']]; p={k:fit(train,r,k) for k in kinds}
        scale,half,cap,mature=old[r['company']]['theta']; g=np.clip(scale*np.log(float(r['r1999'])/float(r['r1998'])),-cap,cap)
        sat=float(r['r1999'])*np.exp(np.cumsum(mature+(g-mature)*2**(-np.arange(6)/half)))[-2:]
        p['saturation']=sat; p['blend']=np.sqrt(sat*p['recovery']); p['margin_blend']=np.sqrt(sat*p['margin'])
        p['size_blend']=np.sqrt(p['size']*p['blend'])
        p['flat']=np.repeat(float(r['r1999']),2); p['original']=np.array(predict(float(r['r1998']),float(r['r1999']),years=6)[-2:])
        out.append(dict(company=r['company'],actual=[float(r['r2004']),float(r['r2005'])],pred={k:v.tolist() for k,v in p.items()}))
    scores={str(2004+j):{k:metrics([(r['pred'][k][j],r['actual'][j]) for r in out]) for k in out[0]['pred']} for j in (0,1)}
    return dict(rows=out,scores=scores)

if __name__=='__main__':
    import json
    print(json.dumps(compare(),indent=2))
