"""Transparent scenario engine. Currency: USD billions, unless specified."""
import csv
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def observations():
    with (ROOT / "data/observations.csv").open() as file:
        return {r["id"]: float(r["value"]) for r in csv.DictReader(file)}

def consumer_revenue(population, internet, adoption, paid, market_share, monthly_price):
    """Population in billions, probabilities conditional on previous stage."""
    return population * internet * adoption * paid * market_share * monthly_price * 12

def enterprise_revenue(employees, adoption, monthly_spend, market_share):
    """Employees in billions; spend must be mean, not sample median."""
    return employees * adoption * monthly_spend * 12 * market_share

def survival(s5, years):
    return s5 ** (years / 5)

def cohort(start, survival_probability, expansion, price_factor, share_factor):
    return start * survival_probability * expansion * price_factor * share_factor

def pilot(start, conversion, expansion, residual=0):
    return start * (conversion * expansion + (1-conversion) * residual)

def reverse_dcf(ev, wacc, growth, margin):
    """Steady-state next-year revenue needed to support EV, no interim years."""
    return ev * (wacc-growth) / margin

# All entries here are illustrative stresses, not measured customer mix or forecasts.
SCENARIOS = {
    "bear": dict(startup=.55, trial=.25, s5=.40, funding=.70, conversion=.20,
                 rollout=2, volume=1.45, price=.65, share=.90, new=.10,
                 subscription_growth=.03, cost_ratio=.65, other_ratio=.35, capex=.06,
                 wacc=.15, terminal_growth=.025),
    "base": dict(startup=.40, trial=.30, s5=.54, funding=.90, conversion=.35,
                 rollout=3, volume=1.65, price=.78, share=.96, new=.20,
                 subscription_growth=.12, cost_ratio=.48, other_ratio=.25, capex=.06,
                 wacc=.12, terminal_growth=.03),
    "bull": dict(startup=.25, trial=.20, s5=.65, funding=1.05, conversion=.50,
                 rollout=4, volume=1.85, price=.88, share=1.0, new=.30,
                 subscription_growth=.22, cost_ratio=.35, other_ratio=.20, capex=.05,
                 wacc=.10, terminal_growth=.035),
}

# Illustrative effective demand ceilings (not observed TAM), subscription overlap,
# and corporate lifecycle transition probabilities. No empirical calibration implied.
# Exit = zero-recovery DISTRESS exit only (acquisitions pay shareholders; see
# evaluation/saas_exit.py). Same annual values in every model and backtest:
#   hazard = BCG large-firm all-cause delisting (8%/5y) x distress share
#   base: Daepp et al. distress share 4.5%+3.5% = 8%
#   bear: dot-com distress share = bankruptcies / exits in data/dotcom_exit_events.csv (2/4 = 50%)
#   bull: historical large-US outright failure 0.09%/yr
LARGE_DELIST_ANNUAL = 1-(1-.08)**(1/5)
DOTCOM_DISTRESS_SHARE = .5
EXIT_HAZARD = dict(bear=LARGE_DELIST_ANNUAL*DOTCOM_DISTRESS_SHARE, base=LARGE_DELIST_ANNUAL*(.045+.035), bull=.0009)
for name, extra in {
    'bear': dict(ceiling=2, personal=.5, employer0=.4, employer_end=.8, cannibal=.8, exit=EXIT_HAZARD['bear'], decline=.30, renew=.03),
    'base': dict(ceiling=4, personal=.5, employer0=.4, employer_end=.7, cannibal=.5, exit=EXIT_HAZARD['base'], decline=.20, renew=.08),
    'bull': dict(ceiling=8, personal=.5, employer0=.4, employer_end=.6, cannibal=.2, exit=EXIT_HAZARD['bull'], decline=.10, renew=.15),
}.items():
    SCENARIOS[name].update(extra)

COST_HALF_LIFE = 3.0  # years; development estimate, evaluation/margin_development.py

def cost_ratios(p, t, half_life=COST_HALF_LIFE):
    """(compute, other, capex) ratios in forecast year t for the Anthropic run.

    Starts from the reported nine-month accrual ratios (models/accounting.py)
    and converges to the scenario's steady-state ratios with the given
    half-life. half_life=None jumps to the scenario ratios at t=1 (the
    pre-2026-11-19 behaviour). Applied identically in every reduced and joint
    model so that model nesting is preserved.
    """
    if half_life is None:
        return p['cost_ratio'], p['other_ratio'], p['capex']
    from .accounting import anthropic_anchor
    a=anthropic_anchor(); w=2**(-t/half_life)
    return tuple(p[k]+(a[ak]-p[k])*w for k,ak in (('cost_ratio','compute'),('other_ratio','other'),('capex','capex')))

def tail_margins(p, tax=.25):
    """Steady-state after-tax cash margins (mature, declining, renewed, exited).

    Derived from the SAME scenario cost ratios used in years 1-10 instead of a
    hard-coded 15%, so the tail cannot silently flip a loss-making scenario into
    a profitable one. Declining/renewed keep the previous 0.2x / 4/3x ratios.
    """
    pre=1-p['cost_ratio']-p['other_ratio']-p['capex']
    m=pre-tax*max(pre,0)
    return (m,.2*m,min(.60,4*m/3) if m>0 else m,0.)

def overlap_factor(employer, cannibal):
    return 1-employer*cannibal

def commitment_floor(t, o):
    # Annualized approximation: allocate the entire reported total exactly over 19 years.
    if t == 1: return o['commit_next12m']
    if t <= 4: return (o['commit_to_2030']-o['commit_next12m'])/3
    if t <= 19: return (o['commit_total']-o['commit_to_2030'])/15
    return 0

def lifecycle_tail(revenue, p, o, start=10, horizon=30, margins=None, continuation=True, recenter=True):
    """Markov reward continuation: mature, declining, renewed, exited.

    Revenue mass tracks E[revenue * 1(state)], preserving path-dependent growth.
    Mature revenue grows at the scenario's terminal_growth (previously 0%).
    Years start+1..horizon are explicit (trace + commitment schedule); after the
    horizon the same chain continues in closed form, PV = a B (I-B)^-1 mu, with
    B = P diag(growth)/(1+W). This replaces the former zero-value truncation.
    Limited liability: exited mass earns zero and equity no longer pays the
    commitment shortfall after exit (shortfall is weighted by survival).
    recenter: the raw state growth (1, .85, 1.08) with decline/renew rates implied
    perpetual survivor shrinkage (base -4.1%/yr, bear -9.8%/yr) that no scenario
    states. With recenter=True the growth vector is scaled so the survivor
    long-run growth equals terminal_growth; states then carry dispersion and
    timing only, and exit remains an explicit separate loss.
    """
    import numpy as np
    e,d,u=p['exit'],p['decline'],p['renew']; w=p['wacc']; g=p.get('terminal_growth',0.)
    if margins is None: margins=tail_margins(p)
    P=np.array(((1-e-d-u,d,u,e),(.10,1-e-.10-u,u,e),(.40,d,1-e-.40-d,e),(0,0,0,1)))
    growth=np.array((1+g,.85,1.08*(1+g),0.))
    if recenter:
        rho=max(abs(np.linalg.eigvals(P[:3,:3]*growth[None,:3])))
        growth[:3]*=(1+g)*(1-e)/rho
    A=P*growth[None,:]; mu=np.array(margins)
    mass=np.array([revenue,0.,0.,0.]); prob=np.array([1.,0.,0.,0.]); pv=0.; tail=[]
    for t in range(start+1,horizon+1):
        mass=mass@A; prob=prob@P
        alive=1-prob[3]; expected_rev=float(mass.sum())
        # Survivor-conditional shortfall times survival (Jensen lower bound kept).
        shortfall=alive*max(0,commitment_floor(t,o)-p['cost_ratio']*expected_rev/alive) if alive>0 else 0.
        fcf=float(mass@mu)-shortfall
        pv+=fcf/(1+w)**t
        tail.append(dict(year=t,revenue=expected_rev,fcf=fcf,alive=float(alive),shortfall=shortfall))
    if continuation:
        if any(commitment_floor(t,o)>0 for t in range(horizon+1,horizon+40)):
            raise ValueError('commitments extend past explicit horizon')
        B=A/(1+w)
        if max(abs(np.linalg.eigvals(B)))>=1: raise ValueError('tail growth must be below discount rate')
        cont=float(mass@B@np.linalg.solve(np.eye(4)-B,mu))/(1+w)**horizon
        pv+=cont
        tail.append(dict(year='continuation',pv=cont))
    return pv,tail

def forecast(p, o=None, years=10, personal_ceiling=None, enterprise_ceiling=None, cost_half_life=COST_HALF_LIFE):
    o = observations() if o is None else o
    # October run rate is a starting intensity; segment split is September historical proxy.
    api = o["run_rate"] * o["consumption_9m26"] / o["revenue_9m26"]
    sub = o["run_rate"] - api
    startup, trial = api*p["startup"], api*p["trial"]
    personal=sub*p['personal']; enterprise_sub=sub-personal
    sub_start_personal=personal
    personal_raw=personal
    mature = api-startup-trial
    rows = []
    for t in range(1, years+1):
        # Fade net growth drivers toward maturity rather than compound hypergrowth indefinitely.
        fade = max(0, 1-(t-1)/7)
        price = 1-(1-p["price"])*fade
        share = 1-(1-p["share"])*fade
        volume = 1+(p["volume"]-1)*fade
        multiplier = price*share*volume
        previous_api = startup+trial+mature
        startup = startup * survival(p["s5"], 1) * (1+(p["funding"]-1)*fade) * multiplier
        # Successful pilots move into mature cohort, unsuccessful ones are extinguished.
        mature = (mature + pilot(trial,p["conversion"],p["rollout"])) * multiplier
        new = previous_api * p["new"] * fade
        startup += new*.4
        trial = new*.6
        # Personal and employer invoices are disjoint; overlap modifies personal demand only.
        personal_raw *= 1+p['subscription_growth']*fade
        employer=p['employer0']+(p['employer_end']-p['employer0'])*min(t/10,1)
        personal=personal_raw*overlap_factor(employer,p['cannibal'])/overlap_factor(p['employer0'],p['cannibal'])
        if personal_ceiling is not None:
            # Stress only: converge to the benchmark by year 5; do not rewrite the observed baseline.
            cap = personal_ceiling + max(0, sub_start_personal-personal_ceiling)*max(0,1-t/5)
            personal = min(personal, cap)
            personal_raw = personal * overlap_factor(p['employer0'],p['cannibal'])/overlap_factor(employer,p['cannibal'])
        enterprise_sub *= 1+p['subscription_growth']*fade
        sub=personal+enterprise_sub
        # Conditional revenue ceiling, gradually reaching the assumed ceiling by year 10.
        if enterprise_ceiling is None:
            limit=o['run_rate']*(1+(p['ceiling']-1)*min(t/10,1))
            scale=min(1,limit/(startup+trial+mature+sub))
            startup*=scale; trial*=scale; mature*=scale
            personal*=scale; personal_raw*=scale; enterprise_sub*=scale
        else:
            # Independent demand envelope: no second aggregate ceiling.
            # Consumption includes non-enterprise use, so this is a scope proxy.
            budget=enterprise_ceiling(t)
            scale=min(1,budget/(startup+trial+mature+enterprise_sub))
            startup*=scale; trial*=scale; mature*=scale; enterprise_sub*=scale
            limit=budget+personal
        sub=personal+enterprise_sub
        revenue = startup+trial+mature+sub
        # Cash expense model: commitments are a floor, not added atop variable compute.
        # This allocates aggregate commitments evenly in two buckets (timing proxy).
        floor = commitment_floor(t,o)
        c_t, o_t, x_t = cost_ratios(p, t, cost_half_life)
        compute = max(floor, revenue*c_t)
        other = revenue*o_t
        capex = revenue*x_t
        pretax = revenue-compute-other-capex
        # Simplified cash-tax proxy; no tax benefit for loss; no separate WC forecast.
        fcf = pretax - max(0,pretax)*.25
        rows.append(dict(year=t,revenue=revenue,startup=startup,trial=trial,mature=mature,
                         subscription=sub,personal=personal,enterprise_subscription=enterprise_sub,ceiling=limit,compute=compute,commitment_floor=floor,
                         other=other,capex=capex,fcf=fcf))
    w = p['wacc']
    tail_pv,_ = lifecycle_tail(rows[-1]['revenue'],p,o,start=years)
    ev = sum(r['fcf']/(1+w)**r['year'] for r in rows)+tail_pv
    # Convertible liability treatment is illustrative (carrying value, not payoff),
    # do not add IPO cash twice or report a per-share value without a diluted cap table.
    bridge = o["proforma_cash"]-o["proforma_convertibles"]
    return rows, ev, ev+bridge

def monte_carlo(n=2000, seed=42):
    """Common-factor scenario interpolation; not a statistically estimated distribution."""
    rng=random.Random(seed)
    values=[]
    for _ in range(n):
        z=rng.triangular(-1,1,0)
        side=SCENARIOS["bull" if z>=0 else "bear"]
        p={k:v+(side[k]-v)*abs(z) for k,v in SCENARIOS["base"].items()}
        values.append(forecast(p)[2])
    return sorted(values)

if __name__ == "__main__":
    for name,p in SCENARIOS.items():
        rows,ev,equity=forecast(p)
        print(f"{name}: year 1 revenue {rows[0]['revenue']:.2f}, year 5 {rows[4]['revenue']:.2f}, EV {ev:.2f}, illustrative equity {equity:.2f}")
    v=monte_carlo()
    print("Scenario simulation quantiles P10/P50/P90:",*[round(v[int(q*(len(v)-1))],2) for q in (.1,.5,.9)])
