"""Joint duration, latent health, macro regime and vendor state DCF.

USD billions. Scenario model, not fitted HMM or empirically estimated joint matrix.
The state tensor holds potential invoice mass, not unique customers. Vendor reward
maps that mass to Claude revenue; rival/dormant mass earns zero until reacquisition.
"""
import numpy as np
from .customer_markov import *

VENDORS=('claude_only','multi_with_claude','openai','google','self_hosted','other','none')
HEALTH=('distressed','funded_unprofitable','self_sustaining')
REGIMES=('winter','normal','boom')
REWARD=np.array([1.,.60,0,0,0,0,0])
MACRO=np.array([[.60,.35,.05],[.18,.67,.15],[.08,.42,.50]])
HEALTH_P=np.array([[.67,.23,.10],[.18,.62,.20],[.04,.10,.86]])
# P(observed recent funding | latent state); assumed, not profitability data.
EMISSION=np.array([.15,.75,.25])
PRIOR=np.array([[.25,.60,.15],[.15,.55,.30],[.10,.15,.75],[.04,.10,.86]])
MACRO_DEATH=np.array([1.5,1.,.75]); MACRO_GROW=np.array([.65,1.,1.25])
HEALTH_DEATH=np.array([1.6,1.,.55]); HEALTH_SPEND=np.array([.75,1.,1.10])
DWELL_PROMOTE=np.array([.55,1.,1.20])

def posterior(prior, funded):
    likelihood=EMISSION if funded else 1-EMISSION
    x=np.asarray(prior)*likelihood
    return x/x.sum()

def health_matrix(regime):
    p=HEALTH_P.copy()
    if regime==0:
        p[:,0]*=1.45
    elif regime==2:
        p[:,0]*=.70; p[:,2]*=1.15
    return p/p.sum(axis=1,keepdims=True)

def lifecycle_kernel(name,regime,health=True,duration=True,seed_hazards=None,seed_cif=None):
    """Substochastic live transition; residual is absorbing business closure."""
    P=np.array(transition(name,seed_hazards=seed_hazards,seed_cif=seed_cif)); out=np.zeros((8,3,3,8,3,3))
    H=health_matrix(regime) if health else np.eye(3)
    for i in range(8):
      for d in range(3):
       for q in range(3):
        row=P[i].copy(); stay=min(i+1,4) if i<5 else i
        death=min(.95,row[8]*MACRO_DEATH[regime]*(HEALTH_DEATH[q] if health else 1))
        row[8]=death
        for j in range(8):
            if GROUP[j]>GROUP[i]:
                row[j]*=MACRO_GROW[regime]*(DWELL_PROMOTE[d] if duration and i>=5 else 1)
        row[stay]=0
        total=row.sum()
        if total>1: row[:8]*=(1-death)/(total-death)
        row[stay]=1-row.sum()
        for j in range(8):
            nd=min(d+1,2) if GROUP[i]==GROUP[j] else 0
            jump=PARAM[name]['upgrade'] if GROUP[j]>GROUP[i] else (.75 if GROUP[j]<GROUP[i] else 1.)
            # Reward weighted kernel, not row-stochastic after spending jump.
            out[i,d,q,j,nd,:]=row[j]*H[q]*jump
    return out.reshape(72,72)

def vendor_matrix(name,group,regime,competition=True):
    """Conditional on company survival. Commercial exit is modeled ONCE."""
    h=hazards()[group]; r=customer_retention(name)[group]
    c=1-r/(1-h); c=min(.95,c*(1.3 if regime==0 else .85 if regime==2 else 1))
    M=np.eye(7)
    # In the comparison without explicit competition, equivalent cancellation is
    # retained as an absorbing zero-reward state (no reactivation).
    if not competition:
        for i in (0,1): M[i,i]=1-c; M[i,6]=c
        return M
    # Split exit among rival-only and nonpurchase. Conditional splits assumptions.
    dest=np.array([.35,.25,.15,.10,.15])
    for i in (0,1):
        M[i]=0; M[i,2:]=c*dest
        # Maintain multi-homing dynamics; initial overlap is a count proxy only.
        switch=.12 if i==0 else .04
        M[i,1-i]=(1-c)*switch; M[i,i]=(1-c)*(1-switch)
    for i in range(2,7):
        regain=(.035 if i==6 else .06)*MACRO_GROW[regime]
        M[i,i]=1-regain; M[i,0]=regain*.25; M[i,1]=regain*.75
    return M

def initial_tensor(values,competition=True,health=True):
    x=np.zeros((8,3,3,7)); mix=np.array([.21,.79]) if competition else np.array([1.,0.])
    # Approximate equal gross budget per logo; normalize to disclosed Claude revenue.
    mix=mix/(mix@REWARD[:2]);
    for i,v in enumerate(values):
        q=posterior(PRIOR[GROUP[i]],i<6) if health else np.array([0.,1.,0.])
        x[i,0,:,:2]=v*q[:,None]*mix[None,:]
    return x

def reward(x): return float(np.sum(x*REWARD))

def propagate(x,K,vs):
    # Vendor loss conditional on survival in source group; then business migration.
    x=np.einsum('idqv,ivw->idqw',x,vs)
    return (x.reshape(72,7).T@K).T.reshape(8,3,3,7)

def forecast_joint(name='base',regime_path=None,health=True,duration=True,competition=True,o=None,scenario_overrides=None,profile=None,growth_half_life=None,seed_hazards=None,seed_cif=None):
    if growth_half_life is not None and growth_half_life<=0: raise ValueError('positive half life required')
    if profile is not None and (o is None or scenario_overrides is not None or seed_hazards is not None or seed_cif is not None):
        raise ValueError('company profile requires explicit company observations and scenario')
    o=observations() if o is None else o; p=dict(SCENARIOS[name]); a=INPUTS[name]; b=PARAM[name]
    path=[1]*10 if regime_path is None else list(regime_path)
    if len(path)!=10 or any(k not in (0,1,2) for k in path): raise ValueError('need ten macro states')
    p['exit']=dict(bear=annual_probability(LARGE_DELIST_5Y,5),base=hazards()[-1],bull=LARGE_US_FAILURE)[name]
    if scenario_overrides:
        if set(scenario_overrides)-set(p): raise ValueError('unknown scenario parameter')
        p.update(scenario_overrides)
    if profile is not None:
        # No Anthropic defaults for a foreign company. An explicitly incomplete
        # profile must fail rather than silently borrow Claude's parameters.
        required={'scenario','inputs','birth_share','weights','retention','start','initialize','kernel','vendor','birth_budget','enterprise_cap','personal_cap','reward','macro_growth','health_spend','tail','commitment_floor'}
        if not required<=set(profile) or set(profile)-required-{'cashflow'} or set(profile['scenario'])!=set(p) or set(profile['inputs'])!=set(a):
            raise ValueError('incomplete company profile; no cross-company default allowed')
        p=dict(profile['scenario']); a=dict(profile['inputs']); b={'birth_share':profile['birth_share']}
        w=profile['weights']; r=profile['retention']; api,sub,personal0=profile['start']; init=profile['initialize']
        if len(w)!=8 or len(r)!=4 or not np.isclose(sum(w),1) or not 0<=personal0<=sub or min(api,sub)<0:
            raise ValueError('invalid company initial state')
        if not np.isclose(api+sub,o['run_rate']): raise ValueError('company revenue reconciliation')
    else:
        w=spread(a['weights']); r=customer_retention(name)
        api=o['run_rate']*o['consumption_9m26']/o['revenue_9m26']; sub=o['run_rate']-api; personal0=sub*p['personal']
        init=lambda v:initial_tensor(v,competition,health)
    personal_raw=personal0
    earn=reward if profile is None else profile['reward']
    growth=MACRO_GROW if profile is None else profile['macro_growth']
    trial=init([api*v*p['trial'] for v in w]); live=init([api*v*(1-p['trial']) for v in w]); seats=init([(sub-personal0)*v for v in w])
    initial=(api+earn(seats))/MENLO_DEPLOYMENT if profile is None else None
    pc=benchmark(a['personal_ratio'])['annual_revenue'] if profile is None else profile['personal_cap']; rows=[]
    cache={}
    for t,reg in enumerate(path,1):
        fade=max(0,1-(t-1)/7) if growth_half_life is None else 2**(-(t-1)/growth_half_life); mult=(1-(1-p['price'])*fade)*(1+(p['volume']-1)*fade)
        if reg not in cache:
            cache[reg]=(lifecycle_kernel(name,reg,health,duration,seed_hazards,seed_cif),np.array([vendor_matrix(name,g,reg,competition) for g in GROUP])) if profile is None else (profile['kernel'](reg),profile['vendor'](reg))
        K,vs=cache[reg]; pa=earn(trial)+earn(live); ps=earn(seats)
        loss=lambda x:sum(earn(x[i])*(1-r[GROUP[i]]) for i in range(8))
        new_api=(pa*p['new']*fade+loss(trial+live)*a['replacement']*(1-fade))*growth[reg]
        new_seat=(ps*p['new']*fade+loss(seats)*a['replacement']*(1-fade))*growth[reg]
        budget=seed_birth(name,t,MACRO_GROW[reg])[1] if profile is None else profile['birth_budget'](t,reg)
        birth=min(new_api*b['birth_share'],budget); new_api*=1-b['birth_share']
        pilot=.1+.5*fade
        funding=np.array([1+(p['funding']-1)*fade if g<2 else 1 for g in GROUP])[:,None,None,None]
        spend=(HEALTH_SPEND[None,None,:,None] if health else 1.) if profile is None else profile['health_spend']
        live=propagate((live+trial*p['conversion']*p['rollout'])*funding*mult*spend,K,vs)
        seats=propagate(seats*funding*(1+p['subscription_growth']*fade)*spend,K,vs)
        add=np.array(w)*new_api; add[0]+=birth
        trial=init(add*pilot); live+=init(add*(1-pilot)); seats+=init(np.array(w)*new_seat)
        personal_raw*=1+p['subscription_growth']*fade
        employer=p['employer0']+(p['employer_end']-p['employer0'])*min(t/10,1)
        overlap=overlap_factor(employer,p['cannibal'])/overlap_factor(p['employer0'],p['cannibal'])
        personal=min(personal_raw*overlap,pc+max(0,personal0-pc)*max(0,1-t/5)); personal_raw=personal/overlap
        ent=earn(live+trial+seats); cap=enterprise_cap(t,a['growth'],a['capture'],initial) if profile is None else profile['enterprise_cap'](t)
        scale=min(1,cap/ent) if ent else 1
        # Proportional scaling applies to retained opportunity mass too.
        live*=scale; trial*=scale; seats*=scale
        revenue=earn(live+trial+seats)+personal; compute=max(commitment_floor(t,o) if profile is None else profile['commitment_floor'](t),revenue*p['cost_ratio'])
        pretax=revenue-compute-revenue*(p['other_ratio']+p['capex']); fcf=pretax-.25*max(0,pretax)
        if profile is not None and 'cashflow' in profile:
            fcf=profile['cashflow'](revenue,t)
        rows.append(dict(year=t,revenue=revenue,fcf=fcf,regime=reg,vendor_mass=(live+trial+seats).sum(axis=(0,1,2)).tolist()))
    tail,_=lifecycle_tail(rows[-1]['revenue'],p,o) if profile is None else profile['tail'](rows[-1]['revenue'],p,o)
    ev=sum(x['fcf']/(1+p['wacc'])**x['year'] for x in rows)+tail
    return rows,ev,ev+o['proforma_cash']-o['proforma_convertibles']

def simulate(name='base',n=256,seed=42):
    rng=np.random.default_rng(seed); equity=[]
    for _ in range(n):
        path=[]; current=1
        for t in range(10):
            current=int(rng.choice(3,p=MACRO[current])); path.append(current)
        equity.append(forecast_joint(name,path)[2])
    return dict(mean=float(np.mean(equity)),p05=float(np.quantile(equity,.05)),median=float(np.median(equity)),p95=float(np.quantile(equity,.95)),negative=float(np.mean(np.array(equity)<0)))

if __name__=='__main__':
    for n in INPUTS:
        rows,ev,eq=forecast_joint(n); print(n,'revs', [round(rows[i]['revenue'],2) for i in (0,4,9)],'EV/EQ',round(ev,2),round(eq,2))
    for k in ('health','duration','competition'):
        print('without',k,forecast_joint(**{k:False})[2])
    for k in range(3): print(REGIMES[k],forecast_joint(regime_path=[k]*10)[2])
    print(simulate(n=1024))
