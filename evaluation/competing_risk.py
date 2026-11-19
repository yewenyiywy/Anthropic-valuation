"""Competing issuer exit states and acquisition scope diagnostics.

Original cohort estimates exit probabilities; external cohort scores are
retrospective (already inspected) and not a fresh holdout. Acquired firms
are not bankrupt firms. No zero-revenue or zero-equity imputation.
"""
import csv
import numpy as np
from evaluation.fundamental_growth import panel
from evaluation.external_validation import load, evaluate
from models.valuation import ROOT

STATES=('standalone','bankruptcy','merger')

def events():
    with (ROOT/'data/dotcom_exit_events.csv').open() as f:
        return {r['company']:r for r in csv.DictReader(f)}

def estimate(names, event_map, alpha=.5):
    if alpha<=0: raise ValueError('positive prior required')
    counts=np.array([sum(event_map.get(n,{}).get('event','standalone')==s for n in names) for s in STATES])
    posterior=counts+alpha
    return counts,posterior/posterior.sum(),posterior

def transition(p5):
    """Constant annual hazard matching five-year cumulative incidences."""
    p5=np.asarray(p5)
    s=p5[0]**.2
    q=(1-s)*p5[1:]/p5[1:].sum()
    return np.array([[s,*q],[0,1,0],[0,0,1]])

def score(p, labels):
    y=np.eye(3)[[STATES.index(s) for s in labels]]
    return dict(brier=float(np.mean(np.sum((p-y)**2,axis=1))),
                log_loss=float(-np.mean(np.log(np.maximum(y@p,1e-15)))))

def acquisition_npv(p, acquired_revenue, margin, cost, discount, years):
    """Finite flat acquired revenue, paid upfront if deal closes; no terminal."""
    if not 0<=p<=1 or acquired_revenue<0 or cost<0 or discount<=-1 or years<1:
        raise ValueError('invalid deal inputs')
    return p*(sum(acquired_revenue*margin/(1+discount)**t for t in range(1,years+1))-cost)

def run():
    em=events(); train=[r['company'] for r in panel()]
    ext=[r['company'] for r in load()]
    counts,p,posterior=estimate(train,em)
    labels=[em.get(n,{}).get('event','standalone') for n in ext]
    rng=np.random.default_rng(42)
    intervals=np.quantile(rng.dirichlet(posterior,size=100000),[.025,.975],axis=0)
    pred={r['company']:r for r in evaluate()['rows']}
    scope=[]
    with (ROOT/'data/dotcom_acquisition_components.csv').open() as f:
        for r in csv.DictReader(f):
            total=float(r['reported_revenue']); component=float(r['component_revenue'])
            item=dict(r,component_share=component/total,revenue_ex_component=total-component)
            if r['company'] in pred and r['year']=='2004':
                forecast=pred[r['company']]['pred']['saturation']
                item.update(consolidated_ape=abs(forecast/total-1),
                            ex_component_ape=abs(forecast/(total-component)-1))
            scope.append(item)
    return dict(states=STATES,counts=counts.tolist(),probabilities=p.tolist(),
                posterior_95=intervals.tolist(),annual_transition=transition(p).tolist(),
                external_counts=[labels.count(s) for s in STATES],
                external_score=score(p,labels),always_standalone=score(np.array([1,0,0]),labels),
                uniform=score(np.ones(3)/3,labels),acquisition_scope=scope)

if __name__=='__main__':
    import json
    print(json.dumps(run(),indent=2))
