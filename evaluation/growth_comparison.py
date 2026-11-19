"""Retrospective issuer-held-out, FY2004 endpoint-held-out model comparison.

Every fit uses only OTHER issuers' FY2000–03 outcomes. No target outcome or
FY2004 outcome is used in fitting or feature scaling. Selection across models
using FY2004 is exploratory and needs a new independent cohort.
"""
import numpy as np
from evaluation.five_year import complete_panel, evaluate
from evaluation.company_oos import metrics

GROUP={'Cisco':'hardware','Broadcom':'hardware','Juniper Networks':'hardware',
       'AOL':'media','Yahoo':'media','Excite@Home':'media',
       'Amazon':'commerce','eBay':'commerce','Priceline':'commerce',
       'Internet Capital Group':'investment'}
PARTIAL={'Juniper Networks','Priceline'}

def features(r,t,kind):
    g=np.log(float(r['r1999'])/float(r['r1998']))
    # Partial-year denominator makes annual growth incomparable. Neutralize it
    # rather than treating first shipments as full-year sales.
    g_adj=0 if r['company'] in PARTIAL else min(g,1.5)
    size=np.log(float(r['r1999']))
    dec=1-2**(-t)
    if kind=='pooled_trend': return [t]
    if kind=='pooled_rebound': return [dec,t]
    if kind=='ridge_growth': return [t,dec*g_adj,t*size]
    if kind=='ridge_sector': return [t,dec*g_adj,t*size]+[t*float(GROUP[r['company']]==s) for s in ('hardware','media','commerce','investment')]
    if kind=='ridge_partial': return [t,dec*g_adj,t*size,dec*float(r['company'] in PARTIAL)]
    if kind=='robust_rebound': return [dec,t]
    if kind=='robust_size': return [t,dec*g_adj,t*size]
    raise ValueError(kind)

def fit_predict(train,target,kind,penalty=4):
    X=[]; y=[]; weights=[]
    for q in train:
        ts=[t for t in range(1,5) if q[f'r{1999+t}']]
        for t in ts:
            X.append(features(q,t,kind)); y.append(np.log(float(q[f'r{1999+t}'])/float(q['r1999'])))
            weights.append(1/len(ts)) # equal weight per issuer, not per observed year
    X=np.array(X); y=np.array(y); w=np.array(weights)
    norm=np.sqrt(np.average(X**2,axis=0,weights=w)); norm=np.maximum(norm,1e-8)
    Z=X/norm; P=np.eye(Z.shape[1])*penalty; P[0,0]=0
    beta=np.linalg.solve(Z.T@(w[:,None]*Z)+P,Z.T@(w*y))
    if kind.startswith('robust'):
        # Huber IRLS, fixed 0.5 log-revenue threshold; limits extreme observations.
        for _ in range(30):
            v=w*np.minimum(1,.5/np.maximum(abs(y-Z@beta),1e-9))
            beta=np.linalg.solve(Z.T@(v[:,None]*Z)+P,Z.T@(v*y))
    pred=float(target['r1999'])*np.exp(np.array([features(target,t,kind) for t in range(1,6)])/norm@beta)
    return pred

def compare():
    rows=complete_panel(); old={r['company']:r for r in evaluate()['rows']}
    kinds=('pooled_trend','pooled_rebound','ridge_growth','ridge_sector','ridge_partial','robust_rebound','robust_size')
    results=[]
    for r in rows:
        if not r['r2004']: continue
        name=r['company']; train=[q for q in rows if q['company']!=name]
        preds={k:float(fit_predict(train,r,k)[-1]) for k in kinds}
        # Simple equal-weight geometrical ensemble fixed before observing endpoints.
        preds['ensemble']=float(np.exp(np.mean(np.log([preds[k] for k in kinds]))))
        # Equal-weight model uncertainty blend: initial-growth saturation and recovery.
        preds['saturation_recovery']=float(np.sqrt(old[name]['calibrated']*preds['pooled_rebound']))
        results.append(dict(company=name,actual=float(r['r2004']),**{k:old[name][k] for k in ('flat','original','calibrated')},**preds))
    scores={}
    for k in ('flat','original','calibrated',*kinds,'ensemble','saturation_recovery'):
        pairs=[(r[k],r['actual']) for r in results]; p,y=np.array(pairs).T
        scores[k]=dict(**metrics(pairs),under=int(sum(p<y)),mean_signed_pct=float(np.mean(p/y-1)),mean_abs_log=float(np.mean(np.abs(np.log(p/y)))))
    return dict(rows=results,scores=scores)

if __name__=='__main__':
    import json
    print(json.dumps(compare(),indent=2))
