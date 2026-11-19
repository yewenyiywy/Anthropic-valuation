"""Evidence-anchored enterprise demand and competing-risk proxy stresses.

IDC projections are broad AI spending, not foundation model spending. Their
sector weights and growth shape are transferred to a Menlo deployment proxy.
Neither source observes Anthropic invoices by sector. Currency USD billions.
"""
import csv
from .valuation import ROOT, SCENARIOS, forecast, observations
from .netflix_benchmark import benchmark

MENLO_DEPLOYMENT = 176.8  # 2026 annualized estimate; US survey, market model
MENLO_MODEL_INFERENCE = 94.2
MENLO_API_SHARE = .55  # survey-derived share, not directly comparable to combined inference
LARGE_DELIST_5Y = .08  # BCG 2026, all causes, revenue > $3.5bn
DISTRESS_EXIT_FRACTION = .045 + .035  # Daepp et al., bankruptcy and liquidation share
LARGE_US_FAILURE = .0009  # historical top-1000 US, quoted in UK study
def annual_probability(p, years):
    return 1-(1-p)**(1/years)

def sector_inputs():
    with (ROOT/'data/industry_spending.csv').open() as f:
        return [(r['sector'],float(r['ai_2024_billion']),float(r['ai_2028_billion'])) for r in csv.DictReader(f)]

def sector_budget(t, growth_multiplier=1):
    raw=sector_inputs()
    weights=[(a*b)**.5 for _,a,b in raw] # 2026 interpolated midpoint, geometric
    ans={}
    for (name,a,b),w in zip(raw,weights):
        g=(b/a)**.25-1
        value=MENLO_DEPLOYMENT*w/sum(weights)
        for y in range(1,t+1):
            fade=max(0,1-max(0,y-2)/8)
            value*=1+.03+(g*growth_multiplier-.03)*fade
        ans[name]=value
    return ans

def enterprise_cap(t, growth_multiplier, terminal_capture, initial_capture):
    # Effective capture includes geography, netting upstream/downstream spend,
    # vendor share and price effects; scenario, NOT an observed market share.
    # terminal_capture=None holds the observed starting capture (no assumed share
    # change). The former base value 0.30 silently implied a fall from ~41%.
    if terminal_capture is None: terminal_capture=initial_capture
    capture=initial_capture+(terminal_capture-initial_capture)*min(t/10,1)
    return sum(sector_budget(t,growth_multiplier).values())*capture

def run():
    from .valuation import EXIT_HAZARD
    o=observations()
    baseline=o['run_rate']*(1-(1-o['consumption_9m26']/o['revenue_9m26'])*.5)
    initial=baseline/MENLO_DEPLOYMENT
    # Transferring the historical distress share to the large-company delisting
    # rate is an explicitly cross-sample proxy, not a fitted company hazard.
    proxy=annual_probability(LARGE_DELIST_5Y,5)*DISTRESS_EXIT_FRACTION
    for name,mult,capture,exit_p,ratio in zip(SCENARIOS,(.7,1,1.5),(.15,None,.50),  # base holds observed capture
            (EXIT_HAZARD['bear'],proxy,LARGE_US_FAILURE),(.05,.15,.30)):
        p=dict(SCENARIOS[name],exit=exit_p)
        cap=lambda t: enterprise_cap(t,mult,capture,initial)
        rows,ev,equity=forecast(p,personal_ceiling=benchmark(ratio)['annual_revenue'],enterprise_ceiling=cap)
        yield name,exit_p,cap(5),cap(10),rows,ev,equity

if __name__=='__main__':
    for name,e,c5,c10,rows,ev,eq in run():
        print(name, 'exit',round(e*100,3),'enterprise cap', round(c5,2),round(c10,2),
              'revenue 1/5/10',*[round(rows[x]['revenue'],2) for x in (0,4,9)],'EV',round(ev,2),'equity',round(eq,2))
