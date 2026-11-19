"""Joint duration, latent health, macro regime and vendor state DCF.

USD billions. Scenario model, not fitted HMM or empirically estimated joint matrix.
The state tensor holds potential invoice mass, not unique customers. Vendor reward
maps that mass to Claude revenue; rival/dormant mass earns zero until reacquisition.
"""
import numpy as np
from .customer_markov import *
from .valuation import EXIT_HAZARD

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

def forecast_joint(name='base',regime_path=None,health=True,duration=True,competition=True,o=None,scenario_overrides=None,profile=None,growth_half_life=None,seed_hazards=None,seed_cif=None,accounting=None,input_overrides=None,cost_half_life=3.0):
    if growth_half_life is not None and growth_half_life<=0: raise ValueError('positive half life required')
    if profile is not None and (o is None or scenario_overrides is not None or seed_hazards is not None or seed_cif is not None):
        raise ValueError('company profile requires explicit company observations and scenario')
    if accounting is not None and profile is not None and 'cashflow' in profile:
        raise ValueError('accounting candidate cannot be combined with custom cashflow')
    o=observations() if o is None else o; p=dict(SCENARIOS[name]); a=INPUTS[name]; b=PARAM[name]
    path=[1]*10 if regime_path is None else list(regime_path)
    if len(path)!=10 or any(k not in (0,1,2) for k in path): raise ValueError('need ten macro states')
    p['exit']=EXIT_HAZARD[name]
    if scenario_overrides:
        if set(scenario_overrides)-set(p): raise ValueError('unknown scenario parameter')
        p.update(scenario_overrides)
    if input_overrides:
        if profile is not None: raise ValueError('input overrides apply to the Anthropic run only')
        if set(input_overrides)-set(a): raise ValueError('unknown input parameter')
        a=dict(a); a.update(input_overrides)
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
    # Cost path: start from the reported nine-month accrual ratios and converge to
    # the scenario's steady-state ratios with half-life cost_half_life (years).
    # 3 years is the development estimate from 18 cloud-software margin paths
    # (evaluation/margin_development.py); None = jump to scenario ratios at t=1
    # (pre-2026-11-19 behaviour). Historical company profiles are unaffected.
    from .valuation import cost_ratios
    anthropic_costs=profile is None and accounting is None
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
        floor_t=commitment_floor(t,o) if profile is None else profile['commitment_floor'](t)
        c_t,o_t,x_t=cost_ratios(p,t,cost_half_life if anthropic_costs else None)
        revenue=earn(live+trial+seats)+personal; compute=max(floor_t,revenue*c_t)
        pretax=revenue-compute-revenue*(o_t+x_t); fcf=pretax-.25*max(0,pretax)
        accounting_trace={}
        if accounting is not None:
            from .accounting import cashflow, ratios
            ar=ratios(accounting['anchor'],p,t,accounting.get('fade_years',5),accounting.get('terminal_da',.03))
            accounting_trace=cashflow(revenue,rows[-1]['revenue'] if rows else o['run_rate'],commitment_floor(t,o) if profile is None else profile['commitment_floor'](t),ar,accounting.get('nwc_ratio',0.),accounting.get('da_compute_share',.5))
            fcf=accounting_trace['fcf']
            compute=accounting_trace['compute_cash']
        elif profile is not None and 'cashflow' in profile:
            fcf=profile['cashflow'](revenue,t)
        rows.append(dict(year=t,revenue=revenue,fcf=fcf,regime=reg,vendor_mass=(live+trial+seats).sum(axis=(0,1,2)).tolist(),
                         price_factor=1-(1-p['price'])*fade,volume_factor=1+(p['volume']-1)*fade,
                         pilot_conversion=p['conversion'],compute_cost=compute,capex=accounting_trace.get('capex',revenue*x_t),cost_ratios=(c_t,o_t,x_t),accounting=accounting_trace,
                         personal_revenue=personal,enterprise_revenue=earn(live+trial+seats),
                         enterprise_ceiling=cap,ceiling_binding=scale<1-1e-10,
                         # Diagnostics only: commitments are a cash floor and do NOT
                         # create demand, so no revenue is credited to idle capacity.
                         commitment_floor=floor_t,
                         commitment_implied_revenue=floor_t/c_t if c_t>0 else float('inf'),
                         idle_commitment_cost=max(0.,floor_t-revenue*c_t)))
    tail_p=dict(p)
    if accounting is not None:
        # Tail margins already include D&A/CapEx; use the consistent cash compute
        # ratio only for the separate committed-capacity shortfall.
        tail_p['cost_ratio']-=accounting.get('terminal_da',.03)*accounting.get('da_compute_share',.5)
    tail,_=lifecycle_tail(rows[-1]['revenue'],tail_p,o) if profile is None else profile['tail'](rows[-1]['revenue'],tail_p,o)
    ev=sum(x['fcf']/(1+p['wacc'])**x['year'] for x in rows)+tail
    return rows,ev,ev+o['proforma_cash']-o['proforma_convertibles']

BLEND_INPUTS=('growth','capture','replacement','personal_ratio')

def initial_capture(o=None,name='base'):
    o=observations() if o is None else o; p=SCENARIOS[name]
    api=o['run_rate']*o['consumption_9m26']/o['revenue_9m26']; sub=o['run_rate']-api
    return (api+sub*(1-p['personal']))/MENLO_DEPLOYMENT

def draw_parameters(z,o=None):
    """Common-factor interpolation between base and bear (z<0) or bull (z>0).

    Same convention as valuation.monte_carlo: one factor moves every scenario
    parameter together, so this is a wide (comonotone) stress band, not an
    estimated joint posterior. Kernel-level PARAM values stay at base.
    """
    side='bull' if z>=0 else 'bear'; w=abs(z)
    scen={k:v+(SCENARIOS[side][k]-v)*w for k,v in SCENARIOS['base'].items() if isinstance(v,(int,float))}
    scen['exit']=EXIT_HAZARD['base']+(EXIT_HAZARD[side]-EXIT_HAZARD['base'])*w
    c0=initial_capture(o)
    val=lambda n,k: (c0 if INPUTS[n][k] is None else INPUTS[n][k])
    inp={k:val('base',k)+(val(side,k)-val('base',k))*w for k in BLEND_INPUTS}
    return scen,inp

COST_KEYS=('cost_ratio','other_ratio','capex'); DISC_KEYS=('wacc',); LIFE_KEYS=('terminal_growth','exit','decline','renew')

def _block(k):
    return 'cost' if k in COST_KEYS else 'disc' if k in DISC_KEYS else 'life' if k in LIFE_KEYS else 'rev'

def draw_blocks(zr=0.,zc=0.,zw=0.,zl=0.,o=None):
    """Block-wise draw (margin_scale addendum). Each block moves from base toward
    bear (z<0) or bull (z>0) with its own factor; cost and discount blocks are
    estimated quantiles and may extrapolate linearly to |z|<=2."""
    z=dict(rev=max(-1.,min(1.,zr)),cost=max(-2.,min(2.,zc)),disc=max(-2.,min(2.,zw)),life=max(-1.,min(1.,zl)))
    base=SCENARIOS['base']; scen={}
    for k,v in base.items():
        if not isinstance(v,(int,float)): continue
        w=z[_block(k)]; side='bull' if w>=0 else 'bear'
        scen[k]=v+(SCENARIOS[side][k]-v)*abs(w)
    w=z['life']; side='bull' if w>=0 else 'bear'
    scen['exit']=EXIT_HAZARD['base']+(EXIT_HAZARD[side]-EXIT_HAZARD['base'])*abs(w)
    scen['cost_ratio']=max(scen['cost_ratio'],.05); scen['other_ratio']=max(scen['other_ratio'],.05); scen['capex']=max(scen['capex'],0.)
    scen['wacc']=max(scen['wacc'],scen['terminal_growth']+.02)
    w=z['rev']; side='bull' if w>=0 else 'bear'
    c0=initial_capture(o); val=lambda n,k: (c0 if INPUTS[n][k] is None else INPUTS[n][k])
    inp={k:val('base',k)+(val(side,k)-val('base',k))*abs(w) for k in BLEND_INPUTS}
    return scen,inp

def _rev_multiple(zr):
    scen,inp=draw_blocks(zr=zr); r=forecast_joint(scenario_overrides=scen,input_overrides=inp)[0]
    return r[4]['revenue']/r[0]['revenue']

_REV_BOUNDS=None
def revenue_bounds():
    """Revenue factor at the 10th/90th percentile: model year-5/year-1 multiple
    equals base x (q10/q50, q90/q50) of the >=$50B comparables' 4-year multiple."""
    global _REV_BOUNDS
    if _REV_BOUNDS is None:
        from evaluation.margin_scale import load,target_d
        q=target_d(load())['revenue_multiple']; m0=_rev_multiple(0.)
        def solve(target,lo,hi):
            for _ in range(30):
                mid=(lo+hi)/2
                if (_rev_multiple(mid)-target)*(_rev_multiple(lo)-target)>0: lo=mid
                else: hi=mid
            return (lo+hi)/2
        _REV_BOUNDS=(solve(m0*q['q10']/q['q50'],-1.,0.),solve(m0*q['q90']/q['q50'],0.,1.))
    return _REV_BOUNDS

def _phi(x):
    from math import erf,sqrt
    return .5*(1+erf(x/sqrt(2)))

def draw_costs(u_margin,u_wacc):
    from evaluation.margin_scale import draw_costs as dc
    return dc(u_margin,u_wacc)

def copula_rho():
    from evaluation.margin_scale import load,target_d
    rs=target_d(load())['spearman_growth_margin']; return 2*np.sin(np.pi*rs/6)

def block_factors(nr,nc,nw,zl):
    lo,hi=revenue_bounds(); q=1.2815515655446004
    zr=nr/q*(hi if nr>=0 else -lo)
    return zr,nc/q,nw/0.6744897501960817,zl

def simulate(name='base',n=256,seed=42,parameters=True,comonotone=False):
    """Macro regime paths plus parameter uncertainty.

    Default: block-wise draws (margin_scale addendum). Revenue factor calibrated to
    comparables' 4-year revenue-multiple quantiles; steady margin, compute share
    and WACC drawn from their empirical comparable distributions; Gaussian copula
    between revenue and margin; lifecycle block keeps its triangular factor. comonotone=True
    reproduces the former single-factor stress band; parameters=False is
    macro-only.
    """
    rng=np.random.default_rng(seed); equity=[]; rho=copula_rho() if parameters and not comonotone else 0.
    for _ in range(n):
        path=[]; current=1
        for t in range(10):
            current=int(rng.choice(3,p=MACRO[current])); path.append(current)
        if parameters and comonotone:
            z=float(rng.triangular(-1,0,1)); scen,inp=draw_parameters(z)
            equity.append(forecast_joint(name,path,scenario_overrides=scen,input_overrides=inp)[2])
        elif parameters:
            nr,e2,nw=rng.standard_normal(3); nc=rho*nr+np.sqrt(1-rho**2)*e2
            zr,_,_,zl=block_factors(nr,0.,0.,float(rng.triangular(-1,0,1)))
            scen,inp=draw_blocks(zr=zr,zl=zl)
            scen.update(draw_costs(_phi(nc),_phi(nw))); scen['wacc']=max(scen['wacc'],scen['terminal_growth']+.02)
            equity.append(forecast_joint(name,path,scenario_overrides=scen,input_overrides=inp)[2])
        else:
            equity.append(forecast_joint(name,path)[2])
    e=np.array(equity)
    return dict(mean=float(e.mean()),p05=float(np.quantile(e,.05)),p10=float(np.quantile(e,.10)),median=float(np.median(e)),
                p90=float(np.quantile(e,.90)),p95=float(np.quantile(e,.95)),negative=float(np.mean(e<0)))

if __name__=='__main__':
    for n in INPUTS:
        rows,ev,eq=forecast_joint(n); print(n,'revs', [round(rows[i]['revenue'],2) for i in (0,4,9)],'EV/EQ',round(ev,2),round(eq,2))
    for k in ('health','duration','competition'):
        print('without',k,forecast_joint(**{k:False})[2])
    for k in range(3): print(REGIMES[k],forecast_joint(regime_path=[k]*10)[2])
    print('revenue factor bounds',revenue_bounds(),'copula rho',copula_rho())
    print('comonotone stress band',simulate(n=1024,comonotone=True))
    print(simulate(n=1024))
