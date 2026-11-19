"""Open duration-dependent customer lifecycle stress; USD billions.

States are seed years 0,1,2,3,4+, funded scaleup, mature SME, large,
and closed. A separate commercial loss operates conditional on survival.
The company-count matrix is a proxy, not an observed Claude transition matrix.
Revenue migration assumes within-state transition independent of invoice size.
"""
import csv
from .customer_cohorts import (INPUTS, hazards, customer_retention, SCENARIOS,
    observations, commitment_floor, lifecycle_tail, overlap_factor, benchmark,
    enterprise_cap, MENLO_DEPLOYMENT, annual_probability, LARGE_DELIST_5Y,
    LARGE_US_FAILURE)
from .valuation import ROOT

STATES=('seed0','seed1','seed2','seed3','seed4plus','scaleup','sme','large','closed')
GROUP=(0,0,0,0,0,1,2,3)
# All parameters beyond the source anchors are assumptions; transitions to SME
# are operational maturation, not funding events. Large is not defined by valuation.
PARAM={
 'bear':dict(seed_cif=(.06,.18,.27,.31), bootstrap=.02, late_grad=.025, scale_sme=.08, scale_large=.01, sme_large=.002, large_down=.01, seed_spend=.03, market=1.3, unique=.65, capture=.15, birth_share=.20, upgrade=1.15),
 'base':dict(seed_cif=(.10,.22,.31,.36), bootstrap=.04, late_grad=.035, scale_sme=.12, scale_large=.02, sme_large=.005, large_down=.005, seed_spend=.05, market=2, unique=.75, capture=.25, birth_share=.20, upgrade=1.35),
 'bull':dict(seed_cif=(.129,.327,.40,.45), bootstrap=.06, late_grad=.05, scale_sme=.17, scale_large=.04, sme_large=.01, large_down=.003, seed_spend=.08, market=3, unique=.85, capture=.40, birth_share=.20, upgrade=1.60),
}

def anchors():
    with (ROOT/'data/markov_anchors.csv').open() as f:
        return {r['metric']:float(r['value']) for r in csv.DictReader(f)}

def transition(name, migration=True, seed_hazards=None, seed_cif=None):
    a=PARAM[name]; h=hazards(); P=[[0.]*9 for _ in range(9)]
    seed_hazards=[h[0]]*5 if seed_hazards is None else list(seed_hazards)
    cif=a['seed_cif'] if seed_cif is None else tuple(seed_cif)
    if len(seed_hazards)!=5 or any(not 0<=x<1 for x in seed_hazards) or len(cif)!=4 or any(not 0<=x<=1 for x in cif) or any(x>y for x,y in zip(cif,cif[1:])):
        raise ValueError('invalid seed competing risks')
    # Competing risks: incremental cumulative incidence / remaining eligible mass.
    # Bootstrap is a separate competing exit from seed, not a failure.
    risk=1.; previous=0.
    for i in range(5):
        g=(cif[i]-previous)/risk if i<4 else a['late_grad']
        b=a['bootstrap']; d=seed_hazards[i]
        if not migration: g=b=0.
        if g+b+d>1: raise ValueError('infeasible competing risks')
        P[i][min(i+1,4)]=1-g-b-d; P[i][5]=g; P[i][6]=b; P[i][8]=d
        if i<4:
            risk*=1-g-b-d; previous=cif[i]
    for i,j,k,x,y in [(5,6,7,a['scale_sme'],a['scale_large']), (6,7,7,a['sme_large'],0), (7,6,6,a['large_down'],0)]:
        if not migration: x=y=0.
        d=h[GROUP[i]]; P[i][i]=1-d-x-y; P[i][j]+=x; P[i][k]+=y; P[i][8]=d
    P[8][8]=1.
    return P

def step_count(n,P,birth=0):
    out=[sum(n[i]*P[i][j] for i in range(9)) for j in range(9)]
    out[0]+=birth
    return out

def seed_birth(name,t,birth_multiplier=1):
    # US pre-seed/seed deal counts are flows of deals, not unique new firms.
    # Apply explicit global coverage and uniqueness assumptions, then vendor capture.
    a=PARAM[name]; d=anchors(); deals=d['us_seed_deals']*a['market']
    firms=deals*a['unique']; paid=firms*a['capture']*birth_multiplier
    # Allocate a fraction of mean financing to yearly Claude invoices; a budget ceiling,
    # not observed ARPA. Unique adjustment applies to count and funding proxy.
    arpa=d['us_seed_capital']/d['us_seed_deals']*a['seed_spend']
    return paid,paid*arpa

def spread(w):
    return [w[0]*x for x in (.30,.25,.20,.15,.10)]+list(w[1:])

def migrate(values,P,name,commercial=True):
    a=PARAM[name]; h=hazards(); r=customer_retention(name)
    out=[0.]*8
    for i,v in enumerate(values):
        c=r[GROUP[i]]/(1-h[GROUP[i]]) if commercial else 1.
        for j in range(8):
            # Only upgrading firms have a spending jump. This is not a financing multiple.
            jump=a['upgrade'] if GROUP[j]>GROUP[i] else (.75 if GROUP[j]<GROUP[i] else 1.)
            out[j]+=v*P[i][j]*c*jump
    return out

def forecast_markov(name,o=None,migration=True,birth_multiplier=1):
    o=observations() if o is None else o; p=dict(SCENARIOS[name]); a=INPUTS[name]; b=PARAM[name]
    P=transition(name,migration); w=spread(a['weights']); r=customer_retention(name)
    p['exit']=dict(bear=annual_probability(LARGE_DELIST_5Y,5),base=hazards()[-1],bull=LARGE_US_FAILURE)[name]
    api=o['run_rate']*o['consumption_9m26']/o['revenue_9m26']; sub=o['run_rate']-api
    personal0=sub*p['personal']; personal_raw=personal0
    trial=[api*x*p['trial'] for x in w]; live=[api*x*(1-p['trial']) for x in w]; seats=[(sub-personal0)*x for x in w]
    initial=(api+sum(seats))/MENLO_DEPLOYMENT; personal_cap=benchmark(a['personal_ratio'])['annual_revenue']; rows=[]
    for t in range(1,11):
        fade=max(0,1-(t-1)/7); mult=(1-(1-p['price'])*fade)*(1+(p['volume']-1)*fade)
        pa=sum(trial)+sum(live); ps=sum(seats)
        loss_api=sum((trial[i]+live[i])*(1-r[GROUP[i]]) for i in range(8)); loss_seat=sum(seats[i]*(1-r[GROUP[i]]) for i in range(8))
        new_api=pa*p['new']*fade+loss_api*a['replacement']*(1-fade)
        new_seat=ps*p['new']*fade+loss_seat*a['replacement']*(1-fade)
        potential_count,birth_budget=seed_birth(name,t,birth_multiplier)
        # Replace part of planned new API sales with distinct young-firm births.
        # Remaining new sales are acquisition of existing firms, not new births.
        birth=min(new_api*b['birth_share'],birth_budget)
        new_api*=1-b['birth_share']; pilot=.1+.5*fade
        funded=[1+(p['funding']-1)*fade if GROUP[i]<2 else 1 for i in range(8)]
        live=migrate([(live[i]+trial[i]*p['conversion']*p['rollout'])*funded[i]*mult for i in range(8)],P,name)
        seats=migrate([seats[i]*funded[i]*(1+p['subscription_growth']*fade) for i in range(8)],P,name)
        trial=[new_api*x*pilot for x in w]; live=[v+new_api*w[i]*(1-pilot) for i,v in enumerate(live)]
        seats=[v+new_seat*w[i] for i,v in enumerate(seats)]; trial[0]+=birth*pilot; live[0]+=birth*(1-pilot)
        personal_raw*=1+p['subscription_growth']*fade
        employer=p['employer0']+(p['employer_end']-p['employer0'])*min(t/10,1)
        overlap=overlap_factor(employer,p['cannibal'])/overlap_factor(p['employer0'],p['cannibal'])
        personal=min(personal_raw*overlap,personal_cap+max(0,personal0-personal_cap)*max(0,1-t/5)); personal_raw=personal/overlap
        cap=enterprise_cap(t,a['growth'],a['capture'],initial); scale=min(1,cap/(sum(trial)+sum(live)+sum(seats)))
        trial=[v*scale for v in trial]; live=[v*scale for v in live]; seats=[v*scale for v in seats]
        group=[sum(trial[i]+live[i]+seats[i] for i in range(8) if GROUP[i]==g) for g in range(4)]
        revenue=sum(group)+personal; compute=max(commitment_floor(t,o),revenue*p['cost_ratio'])
        pretax=revenue-compute-revenue*(p['other_ratio']+p['capex']); fcf=pretax-.25*max(0,pretax)
        rows.append(dict(year=t,revenue=revenue,group=group,birth_budget=birth_budget,birth_revenue=birth*scale,potential_birth_count=potential_count,fcf=fcf))
    tail,_=lifecycle_tail(rows[-1]['revenue'],p,o)
    ev=sum(x['fcf']/(1+p['wacc'])**x['year'] for x in rows)+tail
    return rows,ev,ev+o['proforma_cash']-o['proforma_convertibles']

if __name__=='__main__':
    for name in PARAM:
        P=transition(name); n=[1000]+[0]*8
        for t in range(10): n=step_count(n,P)
        rows,ev,eq=forecast_markov(name)
        print(name,'10y seed cohort', [round(x,1) for x in n], 'births',seed_birth(name,1),'rev 1/5/10',[round(rows[i]['revenue'],2) for i in (0,4,9)], 'EV/equity',round(ev,2),round(eq,2),'no migration',round(forecast_markov(name,migration=False)[2],2),'no births',round(forecast_markov(name,birth_multiplier=0)[2],2))
