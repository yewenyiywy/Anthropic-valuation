"""Financial investment and liquidity factors; grouped shrinkage ablation.

Original issuers only fit and tune. External cohort already inspected, so
scores are diagnostic, not a newly locked prospective test.
"""
import csv
import numpy as np
from evaluation.covariance_factors import data, raw
from evaluation.external_validation import calibrate
from evaluation.five_year import saturation
from evaluation.company_oos import metrics
from models.valuation import ROOT, observations

GROUPS={'baseline':(0,1,2,3),'investment':(4,5),'liquidity':(6,7)}
NAMES=('size','growth','gross_margin','cfo_margin','capex_margin','development_margin',
       'cash_to_revenue','cash_burn_pressure')

def dataset():
    train,ext=data()
    with (ROOT/'data/dotcom_structural_factors.csv').open() as f:
        a={r['company']:r for r in csv.DictReader(f)}
    def add(r):
        v=a.get(r['company'],{})
        return dict(r,**{k:v.get(k,'') for k in ('capex1999','development1999','development_ratio',
                     'cash_equivalents1999','major_customer_ge10')},
                    cfo1999=v.get('cfo1999') or r['cfo1999'])
    return list(map(add,train)),list(map(add,ext))

def features(r):
    def n(k): return float(r[k]) if r.get(k) else np.nan
    rev=float(r['r1999']); cap=n('capex1999'); cash=n('cash_equivalents1999'); cfo=n('cfo1999')
    dev=n('development_ratio')
    if not np.isfinite(dev): dev=n('development1999')/rev
    # Positive burn pressure is inverse cash runway; zero for non-burners.
    burn=max(0.,cap-cfo)/cash if np.isfinite(cap+cfo+cash) and cash>0 else np.nan
    return np.r_[raw(r),cap/rev,dev,np.log1p(cash/rev),np.log1p(burn)]

def design(train,target,groups,alpha):
    cols=[i for g in groups for i in GROUPS[g]]
    a=np.array([features(r)[cols] for r in train]); q=features(target)[cols]
    # Missing observations contribute zero standardized signal, rather than
    # copying other issuers' risk. Scale only from observed training entries.
    mu=np.array([np.mean(c[np.isfinite(c)]) if np.isfinite(c).any() else 0 for c in a.T])
    sd=np.array([np.std(c[np.isfinite(c)]) if np.isfinite(c).any() else 0 for c in a.T])
    sd=np.maximum(sd,1e-8)
    seen=np.isfinite(a).mean(0); valid=(seen>=.5)&(sd>1e-8)
    X=np.where(np.isfinite(a),(a-mu)/sd,0); z=np.where(np.isfinite(q),(q-mu)/sd,0)
    X=np.clip(X,-3,3)*valid; z=np.clip(z,-3,3)*valid
    # Covariance stabilization; reliability weighted shrinkage to zero.
    C=X.T@X/len(X); eig,U=np.linalg.eigh((1-alpha)*C+alpha*np.eye(len(cols)))
    W=U@np.diag(1/np.sqrt(eig))@U.T
    # Reduce weight when a factor is poorly covered; no unobserved target signal.
    D=np.diag(np.sqrt(seen)*valid)
    return X@W@D,z@W@D,seen

def fit(train,target,groups,penalty,alpha,years=(5,),theta=None):
    theta=calibrate(train) if theta is None else theta
    base=saturation(target,*theta)
    if not groups: return base[np.array(years)-1]
    X,z,_=design(train,target,groups,alpha)
    A=[]; y=[]; w=[]
    for r,x in zip(train,X):
        ts=[t for t in range(1,5) if r[f'r{1999+t}']]
        b=saturation(r,*theta)
        for t in ts:
            A.append(x*(1-2**(-t))); y.append(np.log(float(r[f'r{1999+t}'])/b[t-1])); w.append(1/len(ts))
    A=np.array(A); y=np.array(y); w=np.array(w)
    beta=np.linalg.solve(A.T@(w[:,None]*A)+penalty*np.eye(A.shape[1]),A.T@(w*y))
    return np.array([base[t-1]*np.exp(np.clip((1-2**(-t))*z@beta,-1,1)) for t in years])

CANDIDATES={'saturation':(), 'baseline':('baseline',), 'investment':('investment',),
            'liquidity':('liquidity',), 'all':tuple(GROUPS),
            'no_liquidity':('baseline','investment'),'no_investment':('baseline','liquidity')}

def anthropic_diagnostics():
    o=observations(); r=o['revenue_9m26']; cash=o['cash_investments']
    # Different scope from historical cash equivalents, not regression input.
    return dict(cfo_margin=o['cfo_9m26']/r,capex_margin=o['capex_9m26']/r,
                cfo_less_capex=o['cfo_9m26']-o['capex_9m26'],
                cash_investments_to_commitment=cash/o['commit_next12m'],
                commitments_to_cash_investments=o['commit_to_2030']/cash,
                top5_revenue_share=o['top5'],
                top5_hhi_lower_bound=o['top5']**2/5,
                financing_to_cfo=o['financing_9m26']/o['cfo_9m26'])

def tune(train,groups):
    # Leave entire issuer out. Cache saturation parameters per inner fold.
    folds=[]
    for r in train:
        tr=[x for x in train if x['company']!=r['company']]
        ts=[t for t in range(1,5) if r[f'r{1999+t}']]
        folds.append((tr,r,ts,calibrate(tr)))
    def err(p,a):
        return np.mean([np.mean(abs(np.log(fit(tr,r,groups,p,a,ts,theta)/np.array(
                  [float(r[f'r{1999+t}']) for t in ts])))) for tr,r,ts,theta in folds])
    grid=[(p,a) for p in (4,16,64,256) for a in (.5,.9)] if groups else [(1,.9)]
    p,a=min(grid,key=lambda x:err(*x))
    errors=np.array([np.mean(abs(np.log(fit(tr,r,groups,p,a,ts,theta)/np.array(
                  [float(r[f'r{1999+t}']) for t in ts])))) for tr,r,ts,theta in folds])
    return p,a,float(errors.mean()),float(errors.std(ddof=1)/np.sqrt(len(errors)))

def run():
    train,ext=dataset(); out={}; stats={}; cache={}
    for cohort,targets in [('original',[r for r in train if r['r2004']]),('external',ext)]:
        rows=[]
        for r in targets:
            tr=[q for q in train if q['company']!=r['company']]
            key=tuple(q['company'] for q in tr)
            if key not in cache:
                cache[key]={k:tune(tr,g) for k,g in CANDIDATES.items()}
            params=cache[key]; theta=calibrate(tr)
            pred={k:float(fit(tr,r,g,*params[k][:2],theta=theta)[0]) for k,g in CANDIDATES.items()}
            winner=min(params,key=lambda k:params[k][2]); pred['nested']=pred[winner]
            # Prefer parsimonious specification within one standard error
            # of the best inner-fold loss; no endpoint used to choose.
            threshold=params[winner][2]+params[winner][3]
            conservative=min((k for k in params if params[k][2]<=threshold),
                             key=lambda k:(sum(len(GROUPS[g]) for g in CANDIDATES[k]),params[k][2]))
            pred['one_se']=pred[conservative]
            rows.append(dict(company=r['company'],actual=float(r['r2004']),pred=pred,selected=winner,
                             conservative_selected=conservative))
        out[cohort]=rows
        stats[cohort]={k:metrics([(r['pred'][k],r['actual']) for r in rows]) for k in rows[0]['pred']}
    coverage={k:int(sum(np.isfinite(features(r)[i]) for r in train+ext)) for i,k in enumerate(NAMES)}
    return dict(coverage=coverage,stats=stats,rows=out,anthropic_diagnostics=anthropic_diagnostics())

if __name__=='__main__':
    import json
    print(json.dumps(run(),indent=2))
