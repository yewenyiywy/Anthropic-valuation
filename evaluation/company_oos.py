"""Company-specific reduced-state transfer of the joint Markov revenue engine.

No identification of gross acquisition, retention, pricing or margins from two
aggregate revenue observations. The aggregate revenue transition is identified
only before shrinkage; shrinkage/fade are transparent common assumptions.
No equity or bankruptcy predictions are reported from this ablation.
"""
import csv
import numpy as np
from models.joint_customer_states import propagate
from models.valuation import ROOT

def panel():
    with (ROOT/'data/dotcom_fy_panel.csv').open() as f:
        return list(csv.DictReader(f))

def predict(r98,r99,shrink=.5,years=5,half_life=None):
    """Collapse customer/duration/health/vendor tensor to one invoice state.

    R_t = R_(t-1) exp(shrink * log(R99/R98) * max(0,1-(t-1)/7)).
    This is a reward-weighted kernel, not a transition probability.
    No Anthropic parameters except the existing shared seven-year fade shape.
    """
    if min(r98,r99)<=0 or not 0<=shrink<=1: raise ValueError('invalid inputs')
    x=np.zeros((8,3,3,7)); x[7,0,0,0]=r99
    vs=np.tile(np.eye(7),(8,1,1)); out=[]
    g=np.log(r99/r98)
    for t in range(1,years+1):
        fade=max(0,1-(t-1)/7) if half_life is None else 2**(-(t-1)/half_life)
        k=np.eye(72)*np.exp(shrink*g*fade)
        x=propagate(x,k,vs); out.append(float(x.sum()))
    return out

def metrics(pairs):
    p,y=np.array(pairs).T; err=np.abs(p-y)
    return {'n':len(y),'mape':float(np.mean(err/y)),'wape':float(err.sum()/y.sum()),'hit20':float(np.mean(err/y<=.2))}

def run(shrink=.5,half_life=None):
    out=[]; primary=[]; strict=[]; allpairs=[]; future=[]; flat=[]; raw=[]
    for r in panel():
        a,b=float(r['r1998']),float(r['r1999']); p=predict(a,b,shrink,half_life=half_life); y=[float(r[f'r{i}']) if r[f'r{i}'] else None for i in range(2000,2005)]
        pairs=[(i,j) for i,j in zip(p,y) if j is not None]
        primary.append(pairs[0]); allpairs.extend(pairs); future.extend(pairs[1:]); flat.append((b,y[0])); raw.append((b*b/a,y[0]))
        if r['input_vintage']!='reconstructed': strict.append(pairs[0])
        out.append(dict(company=r['company'],r1999=b,forecast2000=p[0],actual2000=y[0],ape=abs(p[0]/y[0]-1),forecast2004=p[-1],actual2004=y[-1],vintage=r['input_vintage']))
    return dict(companies=out,fy2000=metrics(primary),verified_vintage_fy2000=metrics(strict),available_2000_04=metrics(allpairs),available_2001_04=metrics(future),flat2000=metrics(flat),raw_growth2000=metrics(raw))

# Pre-holdout 1997 data only; fit a shared persistence from growth in 1998
# to 1999, not using any future revenue or market prices. Some numbers are
# reconstructed from later publications (see panel source and source notes).
R97={'Cisco':6.452,'AOL':2.634,'Yahoo':.084108,'Amazon':.147787,
     'eBay':.04137,'Excite@Home':.007437,'Internet Capital Group':.000792}

def preperiod_persistence(excluded):
    x=[]; y=[]
    for r in panel():
        n=r['company']
        if n==excluded or n not in R97: continue
        a,b=float(r['r1998']),float(r['r1999'])
        x.append(np.log(a/R97[n])); y.append(np.log(b/a))
    # Constrained least squares, slope only, no intercept. The fitted coefficient
    # is a shared growth-persistence parameter, not a customer lifetime probability.
    return float(np.clip(np.dot(x,y)/np.dot(x,x),0,1))

def calibrated():
    results=[]; first=[]; later=[]
    for r in panel():
        n=r['company']; rho=preperiod_persistence(n)
        a,b=float(r['r1998']),float(r['r1999']); g=np.log(b/a)
        x=np.zeros((8,3,3,7)); x[7,0,0,0]=b; vs=np.tile(np.eye(7),(8,1,1)); p=[]
        for t in range(1,6):
            x=propagate(x,np.eye(72)*np.exp(g*rho**t),vs); p.append(float(x.sum()))
        y=[float(r[f'r{i}']) if r[f'r{i}'] else None for i in range(2000,2005)]
        first.append((p[0],y[0])); later.extend((i,j) for i,j in zip(p[1:],y[1:]) if j is not None)
        results.append(dict(company=n,rho=rho,forecast2000=p[0],actual2000=y[0],predictions=p,actuals=y))
    return dict(companies=results,fy2000=metrics(first),available_2001_04=metrics(later))

if __name__=='__main__':
    import json
    print(json.dumps({'fixed_fade':run(),'one_year_half_life_stress':run(half_life=1),'preperiod_loco':calibrated()},indent=2))
