"""Synthetic recovery and local identifiability using the intact joint engine."""
import json
import numpy as np
from scipy.optimize import least_squares
from models.joint_customer_states import forecast_joint

NAMES=('price','volume','funding','conversion','rollout','new','cost_ratio','other_ratio','capex')
TRUTH=np.array([.83,1.72,.94,.32,2.8,.24,.51,.29,.07])
LOW=np.array([.55,1.1,.65,.15,1.5,.08,.25,.12,.02])
HIGH=np.array([.99,2.3,1.2,.7,5.,.45,.8,.6,.18])
TRAIN=((1,)*10,(0,)*10,(2,)*10)
TEST=((0,1,2,1,0,1,2,1,2,0),(2,2,1,0,0,1,1,2,1,1))
# Invented deliberately; not Anthropic or another real issuer's observations.
O=dict(run_rate=20.,consumption_9m26=12.,revenue_9m26=20.,proforma_cash=8.,
       proforma_convertibles=3.,commit_total=100.,commit_to_2030=40.,commit_next12m=10.)

def path_output(x,path):
    p=dict(zip(NAMES,x)); rows,ev,_=forecast_joint(regime_path=path,o=O,scenario_overrides=p)
    w=.12
    v5=(ev-sum(r['fcf']/(1+w)**r['year'] for r in rows[:5]))*(1+w)**5+O['proforma_cash']-O['proforma_convertibles']
    # Year-five residual conditional on unchanged initial bridge, not market price.
    fin=np.array([r['revenue'] for r in rows[:5]]+[r['fcf'] for r in rows[:5]]+[v5])/20.
    aux=np.array([rows[0]['price_factor'],rows[0]['volume_factor'],rows[0]['pilot_conversion'],
                  rows[0]['capex']/rows[0]['revenue'],p['cost_ratio']])
    return fin,aux

def output(x,paths,augmented=False):
    ys=[path_output(x,p) for p in paths]
    fin=np.concatenate([y[0] for y in ys])
    # Direct observations are synthetic; cost ratio is unit-cost evidence,
    # not inferred from commitment-floor-bound total compute expense.
    return np.r_[fin,ys[0][1]] if augmented else fin

def train(augmented=False):
    target=output(TRUTH,TRAIN,augmented); lo,hi=np.log(LOW),np.log(HIGH)
    fn=lambda z:output(np.exp(z),TRAIN,augmented)-target
    # Dry-run parameter recovery only; not estimation from market cap data.
    fits=[least_squares(fn,lo+(hi-lo)*a,bounds=(lo,hi),max_nfev=100,xtol=1e-9,ftol=1e-9,gtol=1e-9) for a in (.25,.50,.75)]
    best=min(fits,key=lambda r:np.dot(r.fun,r.fun)); x=np.exp(best.x)
    s=np.linalg.svd(best.jac,compute_uv=False)
    test=output(x,TEST); truth=output(TRUTH,TEST)
    e=test[10::11]; y=truth[10::11]
    return dict(augmented=augmented,parameters=dict(zip(NAMES,x.tolist())),
                relative_parameter_mae=float(np.mean(abs(x/TRUTH-1))),
                train_rmse=float(np.sqrt(np.mean(best.fun**2))),
                synthetic_test_equity_wape=float(sum(abs(e-y))/sum(abs(y))),
                singular_values=s.tolist(),numerical_rank=int(sum(s>s[0]*1e-6)),
                starts=[dict(loss=float(np.dot(f.fun,f.fun)),parameters=dict(zip(NAMES,np.exp(f.x).tolist()))) for f in fits])

def invariances():
    # Exact economic mechanisms preserved; only equivalent parameterization varies.
    x=TRUTH.copy(); x[3]*=1.25; x[4]/=1.25
    z=TRUTH.copy(); z[7]+=.02; z[8]-=.02
    c=TRUTH.copy(); c[6]-=.01; c[7]+=.01
    y=output(TRUTH,TRAIN)
    return dict(pilot_product_max_diff=float(np.max(abs(output(x,TRAIN)-y))),
                operating_plus_capex_max_diff=float(np.max(abs(output(z,TRAIN)-y))),
                local_compute_cost_split_max_diff=float(np.max(abs(output(c,TRAIN)-y))))

def run():
    return dict(status='synthetic recovery only; empirical equity accuracy unmeasured',truth=dict(zip(NAMES,TRUTH.tolist())),
                invariances=invariances(),financial=train(),augmented=train(True))

if __name__=='__main__': print(json.dumps(run(),indent=2))
