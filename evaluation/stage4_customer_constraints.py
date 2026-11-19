"""Vintage-only identified bounds; no synthetic labels or equity scoring."""
from collections import defaultdict
import json
from .validation_gate import ROOT, read_csv, day
from .customer_identification import stock_flow_bounds

def audit():
    roster={r['company']:r for r in read_csv(ROOT/'data/stage4_candidate_universe.csv') if r['eligibility']=='candidate'}
    evidence=read_csv(ROOT/'data/stage4_customer_anchors.csv')
    groups=defaultdict(dict)
    for r in evidence:
        assert day(r['period_end'])<=day(r['available_by'])<=day(roster[r['company']]['origin'])
        assert r['source'].startswith('https://www.sec.gov/')
        key=(r['company'],r['scope']); assert r['metric'] not in groups[key]
        groups[key][r['metric']]=r
    bounds=[]
    for (company,scope),g in groups.items():
        if not {'prior_count','current_count'}<=g.keys(): continue
        a,b=g['prior_count'],g['current_count']; x,y=float(a['value']),float(b['value'])
        z=stock_flow_bounds(x,y)
        if b['qualifier']=='lower_bound': z['gross_entries_max']=None
        bounds.append(dict(company=company,scope=scope,growth_floor_or_point=y/x-1,qualifiers=[a['qualifier'],b['qualifier']],**z))
    return dict(status='partial identification only',observations=len(evidence),companies=len({r['company'] for r in evidence}),candidate_companies=len(roster),bounds=bounds,validated_profiles=0)

if __name__=='__main__': print(json.dumps(audit(),indent=2))
