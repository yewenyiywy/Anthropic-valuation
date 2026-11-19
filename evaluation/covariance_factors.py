"""Issuer-balanced regularization; all transforms fitted inside each fold."""
import csv
import numpy as np
from evaluation.fundamental_growth import panel
from evaluation.external_validation import load, calibrate
from evaluation.five_year import saturation
from evaluation.company_oos import metrics
from evaluation.growth_comparison import PARTIAL
from models.valuation import ROOT

FACTORS=('log_size','log_growth','gross_margin','cfo_margin')
METHODS=('pooled','ols','ridge','shrink_cov','pcr','residual')

def data():
    with (ROOT/'data/dotcom_cash_factors.csv').open() as f:
        cash={r['company']:r for r in csv.DictReader(f)}
    def add(r):
        a=cash.get(r['company'],{})
        return dict(r,gross_margin=r.get('gross_margin') or a.get('gross_margin',''),cfo1999=a.get('cfo1999',''))
    return [add(r) for r in panel()],[add(r) for r in load() if r['status']=='observed']

def raw(r):
    a,b=float(r['r1998']),float(r['r1999'])
    return [np.log(b),np.nan if r['company'] in PARTIAL else np.clip(np.log(b/a),-1.5,1.5),
            float(r['gross_margin']) if r['gross_margin'] else np.nan,
            float(r['cfo1999'])/b if r['cfo1999'] else np.nan]

def transform(train, target, method, strength):
    X=np.array([raw(r) for r in train]); q=np.array([raw(target)])
    med=np.array([np.median(c[np.isfinite(c)]) if np.isfinite(c).any() else 0 for c in X.T])
    X=np.where(np.isfinite(X),X,med); q=np.where(np.isfinite(q),q,med)
    mu=X.mean(0); sd=np.maximum(X.std(0),1e-8)
    X=(X-mu)/sd; q=(q-mu)/sd
    C=X.T@X/len(X)
    eig,U=np.linalg.eigh(C); eig=np.maximum(eig,0)
    if method=='pooled': return X[:,:0],q[:,:0],C
    if method=='shrink_cov':
        # Correlation shrinkage followed by regularized whitening.
        A=U@np.diag(1/np.sqrt((1-strength)*eig+strength))@U.T
        X,q=X@A,q@A
    elif method=='pcr':
        A=U[:,-int(strength):]; X,q=X@A,q@A
    elif method=='residual':
        # Ordered Gram-Schmidt: remove linear size/growth/margin overlap.
        # Fold-wise projection applied unchanged to the held-out issuer.
        for j in range(1,X.shape[1]):
            coef=np.linalg.lstsq(X[:,:j],X[:,j],rcond=1e-8)[0]
            X[:,j]-=X[:,:j]@coef; q[:,j]-=q[:,:j]@coef
        # Do not inflate nearly zero residual variance.
    return X,q,C

def fit(train,target,method,strength,years=(5,6)):
    X,q,C=transform(train,target,method,strength)
    def row(x,t): return np.r_[1-2**(-t),t,t*x]
    A=[]; y=[]; w=[]
    for r,x in zip(train,X):
        ts=[t for t in range(1,5) if r[f'r{1999+t}']]
        for t in ts:
            A.append(row(x,t)); y.append(np.log(float(r[f'r{1999+t}'])/float(r['r1999']))); w.append(1/len(ts))
    A=np.array(A); y=np.array(y); w=np.array(w)
    # Scale time basis only; preserve shrinkage geometry of factors.
    d=np.r_[np.sqrt(np.average(A[:,:2]**2,axis=0,weights=w)),np.repeat(4.,X.shape[1])]
    A=A/d; penalty=0 if method=='ols' else (strength if method=='ridge' else 4)
    P=np.diag(np.r_[0.,4. if method!='ols' else 0.,np.repeat(penalty,X.shape[1])])
    beta=np.linalg.pinv(A.T@(w[:,None]*A)+P)@(A.T@(w*y))
    return float(target['r1999'])*np.exp(np.clip(np.array([row(q[0],t) for t in years])/d@beta,-15,15))

GRID={'pooled':(4,), 'ols':(0,), 'ridge':(.5,2,4,8,16,32), 'shrink_cov':(.25,.5,.75,1.), 'pcr':(1,2,3), 'residual':(4,)}

def tune(train,method):
    def loss(s):
        errors=[]
        for r in train:
            ts=[t for t in range(1,5) if r[f'r{1999+t}']]
            p=fit([x for x in train if x['company']!=r['company']],r,method,s,ts)
            errors.append(np.mean(abs(np.log(p/np.array([float(r[f'r{1999+t}']) for t in ts])))))
        return np.mean(errors)
    s=min(GRID[method],key=loss)
    return s,float(loss(s))

def anchored(train,target,penalty,years=(5,)):
    """Estimate residual log revenue relative to saturation, not total growth."""
    theta=calibrate(train)
    X,q,_=transform(train,target,'residual',4)
    A=[]; y=[]; w=[]
    for r,x in zip(train,X):
        ts=[t for t in range(1,5) if r[f'r{1999+t}']]
        base=saturation(r,*theta)
        for t in ts:
            A.append(np.r_[1.,x]*((1-2**(-t))))
            y.append(np.log(float(r[f'r{1999+t}'])/base[t-1]))
            w.append(1/len(ts))
    A=np.array(A); y=np.array(y); w=np.array(w)
    # Ridge penalty on all corrections, including common correction.
    beta=np.linalg.solve(A.T@(w[:,None]*A)+penalty*np.eye(A.shape[1]),A.T@(w*y))
    base=saturation(target,*theta)
    return np.array([base[t-1]*np.exp(np.r_[1.,q[0]]@beta*(1-2**(-t))) for t in years])

def tune_anchored(train):
    def loss(p):
        errs=[]
        for r in train:
            ts=[t for t in range(1,5) if r[f'r{1999+t}']]
            a=anchored([q for q in train if q['company']!=r['company']],r,p,ts)
            errs.append(np.mean(abs(np.log(a/np.array([float(r[f'r{1999+t}']) for t in ts])))))
        return np.mean(errs)
    return min((4,16,64,256),key=loss)

def run():
    train,ext=data(); scores={}; out={}
    for label,targets in [('original',[r for r in train if r['r2004']]),('external',ext)]:
        rows=[]
        cache={}
        for r in targets:
            tr=[x for x in train if x['company']!=r['company']]
            key=tuple(x['company'] for x in tr)
            if key not in cache:
                cache[key]=({m:tune(tr,m) for m in METHODS},tune_anchored(tr))
            params,ap=cache[key]
            p={m:float(fit(tr,r,m,params[m][0],(5,))[0]) for m in METHODS}
            p['saturation']=float(saturation(r,*calibrate(tr))[-1])
            p['anchored']=float(anchored(tr,r,ap)[0])
            # Select method by inner folds, never the final endpoint.
            m,s=min(((m,params[m]) for m in METHODS if m!='ols'),key=lambda z:z[1][1])
            p['nested_select']=float(fit(tr,r,m,s[0],(5,))[0])
            rows.append(dict(company=r['company'],actual=float(r['r2004']),pred=p,selected=m,anchor_penalty=ap))
        scores[label]={m:metrics([(r['pred'][m],r['actual']) for r in rows]) for m in rows[0]['pred']}
        out[label]=rows
    _,_,C=transform(train,train[0],'ridge',4)
    return dict(factors=FACTORS,correlation=C.tolist(),eigenvalues=np.linalg.eigvalsh(C).tolist(),
                vif=np.diag(np.linalg.pinv(C)).tolist(),scores=scores,rows=out,
                coverage={k:int(sum(np.isfinite(raw(r)[i]) for r in train+ext)) for i,k in enumerate(FACTORS)})

if __name__=='__main__':
    import json
    print(json.dumps(run(),indent=2))
