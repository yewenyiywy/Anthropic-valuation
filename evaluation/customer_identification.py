"""Point-in-time partial identification, not a reduced-model equity score."""
import csv
import json
from datetime import date
from models.valuation import ROOT

ORIGIN=date(2020,12,31)
REQUIRED=('customer_lifecycle_mix','financial_health','gross_acquisition','logo_retention',
          'vendor_switching','personal_enterprise_overlap','pilot_conversion','price_volume',
          'demand_ceiling','commitment_schedule','cashflow_bridge','capital_structure')

def stock_flow_bounds(old,new):
    """For same-scope stocks, N1=r*N0+A; no assumptions on r beyond [0,1].

    A includes activation/reactivation or threshold crossings as appropriate,
    not necessarily new companies. This is an identified set, not a fitted prior.
    """
    if old<=0 or new<0: raise ValueError('invalid stocks')
    return dict(retention_min=0.,retention_max=min(1.,new/old),gross_entries_min=max(0.,new-old),gross_entries_max=new)

def evidence():
    out={}
    with (ROOT/'data/cloud_customer_vintage_evidence.csv').open() as f:
        for r in csv.DictReader(f):
            if date.fromisoformat(r['available_date'])>ORIGIN: raise ValueError('future feature')
            if date.fromisoformat(r['period_end'])>date.fromisoformat(r['available_date']): raise ValueError('publication precedes observation')
            if not r['source'].startswith('https://www.sec.gov/'): raise ValueError('non-primary source')
            out.setdefault(r['company'],{})[r['metric']]=float(r['value'])
    return out

def report():
    x=evidence(); rows=[]
    with (ROOT/'data/cloud_equity_cohort.csv').open() as f:
        for raw in csv.DictReader(f):
            n=raw['company']; v=x[n]; bounds={}
            if n=='PayPal': bounds=stock_flow_bounds(v['active_accounts_prior'],v['active_accounts'])
            elif n=='ServiceNow': bounds=stock_flow_bounds(v['large_acv_accounts_prior'],v['large_acv_accounts'])
            # Do not apply count-flow identity to ARR: continuing ARR may expand.
            rows.append(dict(company=n,origin_cap=float(raw['cap20']),actual_cap5=float(raw['cap25']),
                             vintage_anchors=len(v),partial_bounds=bounds,missing_or_unidentified=list(REQUIRED),
                             status='not eligible for full-model equity scoring'))
    # No historical forecast is constructed from incomplete profiles.
    return dict(status='BLOCKED',scope='previously exposed development cohort; no eligible full profile',
                origin=str(ORIGIN),rows=rows,eligible=0,total=len(rows),equity_wape=None,
                flat_market_cap_reference_wape=sum(abs(r['origin_cap']-r['actual_cap5']) for r in rows)/sum(r['actual_cap5'] for r in rows))

if __name__=='__main__': print(json.dumps(report(),indent=2))
