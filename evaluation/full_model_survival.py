"""Calibrate a component and propagate through the intact production model."""
import csv
import json
import numpy as np
from models.valuation import ROOT
from models.customer_markov import anchors
from models.joint_customer_states import forecast_joint, MACRO

def fit():
    with (ROOT/'data/bls_information_survival.csv').open() as f:
        s=np.array([float(r['survival']) for r in csv.DictReader(f)])
    t=np.arange(1,11)
    k,log_a=np.polyfit(np.log(t[:5]),np.log(-np.log(s[1:6])),1)
    a=np.exp(log_a)
    weibull=lambda age:np.exp(-a*np.asarray(age)**k)
    pred=weibull(t); constant=s[5]**(t/5)
    h=1-weibull(np.arange(1,5))/weibull(np.arange(4))
    h=np.r_[h,1-(weibull(10)/weibull(4))**(1/6)]
    anchors_=anchors(); cif=[anchors_[f'eu_seed_a_{i}m'] for i in (12,24,36,48)]
    score=lambda p:dict(mae=float(np.mean(abs(p[5:]-s[6:]))),bias=float(np.mean(p[5:]-s[6:])))
    return dict(shape=float(k),scale=float(a**(-1/k)),seed_hazards=h.tolist(),seed_cif=cif,
                constant=score(constant),weibull=score(pred),actual=s[1:].tolist(),predicted=pred.tolist(),constant_prediction=constant.tolist())

def run(n=128,seed=42):
    cal=fit(); rng=np.random.default_rng(seed); old=[]; new=[]
    for _ in range(n):
        path=[]; current=1
        for _ in range(10):
            current=int(rng.choice(3,p=MACRO[current])); path.append(current)
        for target,kwargs in ((old,{}),(new,dict(seed_hazards=cal['seed_hazards'],seed_cif=cal['seed_cif']))):
            rows,ev,equity=forecast_joint(regime_path=path,**kwargs)
            target.append([equity,rows[4]['revenue']])
    def summary(x):
        x=np.array(x); return dict(equity_mean=float(x[:,0].mean()),equity_p05=float(np.quantile(x[:,0],.05)),equity_p95=float(np.quantile(x[:,0],.95)),revenue5_mean=float(x[:,1].mean()))
    return dict(status='component development; full model sensitivity only; release blocked',calibration=cal,baseline=summary(old),candidate=summary(new),paths=n,seed=seed)

if __name__=='__main__': print(json.dumps(run(),indent=2))
