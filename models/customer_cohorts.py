"""Customer type x billing type x deployment status; separate distress and commercial churn.

All USD billions. Customer revenue weights and revenue-weighted cancellation
rates are scenario assumptions, NOT estimated from published customer counts.
"""
import csv
from .valuation import ROOT, SCENARIOS, observations, commitment_floor, lifecycle_tail, overlap_factor
from .industry_calibration import enterprise_cap, MENLO_DEPLOYMENT, annual_probability, LARGE_DELIST_5Y, DISTRESS_EXIT_FRACTION, LARGE_US_FAILURE
from .netflix_benchmark import benchmark

GROUPS=('early_startup','scaleup','mature_sme','large')
INPUTS={
 'bear':dict(weights=(.30,.30,.25,.15), churn_factors=(1,.8,.65,.35), growth=.7,capture=.15,personal_ratio=.05,replacement=.5),
 'base':dict(weights=(.15,.25,.30,.30), churn_factors=(.8,.55,.45,.20), growth=1,capture=.30,personal_ratio=.15,replacement=1),
 'bull':dict(weights=(.05,.15,.30,.50), churn_factors=(.5,.35,.25,.10), growth=1.5,capture=.50,personal_ratio=.30,replacement=1.25),
}

def risk_data():
    with (ROOT/'data/customer_risk.csv').open() as f:
        return {r['metric']:float(r['value']) for r in csv.DictReader(f)}

def hazards(d=None):
    d=risk_data() if d is None else d
    return (annual_probability(1-d['information_new_survival5'],5),
            annual_probability(1-d['information_survival10']/d['information_new_survival5'],5),
            annual_probability(1-d['all_survival10']/d['all_new_survival5'],5),
            annual_probability(LARGE_DELIST_5Y,5)*DISTRESS_EXIT_FRACTION)

def customer_retention(scenario,d=None):
    d=risk_data() if d is None else d
    # Ramp is all-cause count cancellation; stress transfer to revenue by group.
    logo_loss=annual_probability(d['ramp_monthly_logo_cancel'],1/12)
    h=hazards(d)
    target=[logo_loss*f for f in INPUTS[scenario]['churn_factors']]
    # Conditional commercial loss is residual, never add closure twice.
    conditional=[max(0,(q-p)/(1-p)) for p,q in zip(h,target)]
    return [(1-p)*(1-c) for p,c in zip(h,conditional)]

def forecast_cohorts(name, o=None, no_commercial_loss=False, top5_cut=0):
    o=observations() if o is None else o
    p=dict(SCENARIOS[name]); a=INPUTS[name]; w=a['weights']
    p['exit']=dict(bear=annual_probability(LARGE_DELIST_5Y,5),base=hazards()[-1],bull=LARGE_US_FAILURE)[name]
    planned_r=customer_retention(name)
    r=planned_r if not no_commercial_loss else [1-x for x in hazards()]
    api=o['run_rate']*o['consumption_9m26']/o['revenue_9m26']; sub=o['run_rate']-api
    personal0=sub*p['personal']; personal_raw=personal0
    # Type is independent of deployment status; weights applied once to each invoice type.
    trial=[api*x*p['trial'] for x in w]; live=[api*x*(1-p['trial']) for x in w]
    seats=[(sub-personal0)*x for x in w]
    initial=(api+sum(seats))/MENLO_DEPLOYMENT
    personal_cap=benchmark(a['personal_ratio'])['annual_revenue']; rows=[]
    for t in range(1,11):
        fade=max(0,1-(t-1)/7)
        # Price and token intensity conditional on continuing customers; switching is
        # modeled in retention, so do not additionally apply the old share factor.
        mult=(1-(1-p['price'])*fade)*(1+(p['volume']-1)*fade)
        pa=sum(trial)+sum(live); ps=sum(seats)
        api_loss=sum((trial[i]+live[i])*(1-r[i]) for i in range(4))
        seat_loss=sum(seats[i]*(1-r[i]) for i in range(4))
        losses=api_loss+seat_loss
        # At maturity gross new sales need not vanish when net growth slows.
        # Replacement fraction is an explicit scenario, not an observed acquisition rate.
        planned_api_loss=sum((trial[i]+live[i])*(1-planned_r[i]) for i in range(4))
        planned_seat_loss=sum(seats[i]*(1-planned_r[i]) for i in range(4))
        new_api=pa*p['new']*fade+planned_api_loss*a['replacement']*(1-fade)
        new_seats=ps*p['new']*fade+planned_seat_loss*a['replacement']*(1-fade)
        pilot_fraction=.1+.5*fade
        for i in range(4):
            funding=1+(p['funding']-1)*fade if i<2 else 1
            # Pilot resolution only after survival and retention; failed pilots extinct.
            live[i]=(live[i]+trial[i]*p['conversion']*p['rollout'])*r[i]*funding*mult+new_api*w[i]*(1-pilot_fraction)
            trial[i]=new_api*w[i]*pilot_fraction
            seats[i]=seats[i]*r[i]*funding*(1+p['subscription_growth']*fade)+new_seats*w[i]
        personal_raw*=1+p['subscription_growth']*fade
        employer=p['employer0']+(p['employer_end']-p['employer0'])*min(t/10,1)
        overlap=overlap_factor(employer,p['cannibal'])/overlap_factor(p['employer0'],p['cannibal'])
        personal=min(personal_raw*overlap,personal_cap+max(0,personal0-personal_cap)*max(0,1-t/5))
        personal_raw=personal/overlap
        cap=enterprise_cap(t,a['growth'],a['capture'],initial)
        scale=min(1,cap/(sum(trial)+sum(live)+sum(seats)))
        trial=[x*scale for x in trial]; live=[x*scale for x in live]; seats=[x*scale for x in seats]
        if t==1 and top5_cut:
            # Incremental shock after ordinary churn; nine-month concentration proxy.
            # Unknown customer-type allocation -> proportional enterprise reduction.
            enterprise=sum(trial)+sum(live)+sum(seats)
            shock=min(enterprise,.25*(enterprise+personal)*top5_cut)
            shock_scale=1-shock/enterprise
            trial=[x*shock_scale for x in trial]; live=[x*shock_scale for x in live]; seats=[x*shock_scale for x in seats]
        group=[trial[i]+live[i]+seats[i] for i in range(4)]
        revenue=sum(group)+personal
        compute=max(commitment_floor(t,o),revenue*p['cost_ratio'])
        pretax=revenue-compute-revenue*(p['other_ratio']+p['capex'])
        fcf=pretax-.25*max(0,pretax)
        rows.append(dict(year=t,revenue=revenue,personal=personal,enterprise=sum(group),group=dict(zip(GROUPS,group)),
                         losses=losses,new=new_api+new_seats,cap=cap,fcf=fcf))
    tail,_=lifecycle_tail(rows[-1]['revenue'],p,o)
    ev=sum(x['fcf']/(1+p['wacc'])**x['year'] for x in rows)+tail
    return rows,ev,ev+o['proforma_cash']-o['proforma_convertibles']

if __name__=='__main__':
    for n in INPUTS:
        rows,ev,eq=forecast_cohorts(n)
        print(n, 'customer retention',*[round(x,3) for x in customer_retention(n)],'revenue 1/5/10',*[round(rows[i]['revenue'],2) for i in (0,4,9)],'first loss',round(rows[0]['losses'],2),'EV',round(ev,2),'equity',round(eq,2),'closure only equity',round(forecast_cohorts(n,no_commercial_loss=True)[2],2))
