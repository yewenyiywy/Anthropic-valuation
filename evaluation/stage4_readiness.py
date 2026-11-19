"""Stage 4 roster preflight; never read outcome labels or grant release."""
from collections import Counter
import json
from .validation_gate import ROOT, EXPOSED, MIN_FAMILIES, MIN_CYCLES, day, read_csv, sha

def audit(path=ROOT/'data/stage4_candidate_universe.csv'):
    rows=read_csv(path)
    eligible=[]
    for r in rows:
        assert day(r['ranking_date'])<=day(r['origin'])
        a,b=day(r['origin']),day(r['target'])
        assert b==a.replace(year=a.year+5)
        expected='exposed' if r['family'] in EXPOSED else 'candidate'
        assert r['eligibility']==expected
        if expected=='candidate': eligible.append(r)
    assert len({r['family'] for r in rows})==len(rows)
    episodes=Counter(r['episode'] for r in eligible)
    for e in episodes:
        cohort=[r for r in rows if r['episode']==e]
        assert [int(r['rank']) for r in cohort]==list(range(1,11))
        assert [float(r['ranking_value']) for r in cohort]==sorted((float(r['ranking_value']) for r in cohort),reverse=True)
    return dict(status='BLOCKED',roster_sha256=sha(path),total=len(rows),candidates=len(eligible),excluded=len(rows)-len(eligible),episodes=dict(episodes),numerical_roster_minimum=len(eligible)>=MIN_FAMILIES and len(episodes)>=MIN_CYCLES,validated_profiles=0,independent_labels_opened=0,equity_wape=None,blockers=['company profiles and masking validation not completed','distinct technology cycles and family independence require reviewer confirmation','frozen trained parameters and independent label custody absent'])

if __name__=='__main__': print(json.dumps(audit(),indent=2))
