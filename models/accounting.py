"""Reconciled accrual-to-economic-FCFF candidate; not a fitted forecast."""
import csv
from .valuation import ROOT

def anthropic_anchor():
    with (ROOT/'data/anthropic_accounting_audit.csv').open() as f:
        d={r['metric']:float(r['value_usd_b']) for r in csv.DictReader(f) if r['status'].startswith('verified')}
    r=d['revenue']; other=d['total_operating_expenses']-d['compute_infrastructure']
    if abs(r-other-d['compute_infrastructure']-d['operating_income'])>1e-8: raise ValueError('EBIT bridge')
    return dict(compute=d['compute_infrastructure']/r,other=other/r,da=d['depreciation_amortization']/r,
                capex=d['capex']/r,ebit=d['operating_income']/r)

def ratios(anchor,scenario,t,fade_years=5,terminal_da=.03):
    if fade_years<2: raise ValueError('fade must include anchor and endpoint')
    f=min(1,max(0,(t-1)/(fade_years-1)))
    end=dict(compute=scenario['cost_ratio'],other=scenario['other_ratio'],da=terminal_da,capex=scenario['capex'])
    return {k:anchor[k]*(1-f)+end[k]*f for k in end}

def cashflow(revenue,previous_revenue,commitment,costs,nwc_ratio=0.,da_compute_share=.5,tax_rate=.25):
    """CapEx is not tax deductible. Economic SBC remains in operating expense.

    Compute commitment shortfall is modeled as incremental cash, not an
    immediately deductible accrual expense. No separate lease prepayment is
    subtracted; contractual timing and D&A allocation are assumptions.
    """
    if not 0<=da_compute_share<=1 or not 0<=tax_rate<=1 or nwc_ratio<0: raise ValueError('invalid accounting assumption')
    if min(revenue,previous_revenue,commitment,*costs.values())<0: raise ValueError('negative input')
    compute=costs['compute']*revenue; other=costs['other']*revenue; da=costs['da']*revenue; capex=costs['capex']*revenue
    if da_compute_share*da>compute or (1-da_compute_share)*da>other: raise ValueError('D&A allocation exceeds accrual expense')
    ebit=revenue-compute-other; tax=tax_rate*max(0,ebit)
    compute_cash=compute-da*da_compute_share; shortfall=max(0,commitment-compute_cash)
    nwc=nwc_ratio*(revenue-previous_revenue)
    return dict(ebit=ebit,tax=tax,da=da,capex=capex,nwc=nwc,commitment_shortfall=shortfall,
                compute_cash=compute_cash+shortfall,fcf=ebit-tax+da-capex-nwc-shortfall)
