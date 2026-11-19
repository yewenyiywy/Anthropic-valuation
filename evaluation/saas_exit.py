"""Five-year competing exits for the two cloud-software rosters (development).

Universe = every member of the frozen stage-4 rosters, including the exposed
families (no survivor selection): cloud2015 = Bessemer May-2015 top ten;
cloud2020 = top-ten WCLD positions June 2020 plus the five Bessemer 2020
$50B+ issuers used in the exposed cloud backtest (Shopify is in both).
States within the 5-year window: standalone / acquired / bankrupt.
Acquired issuers keep their deal value (data/stage4_exit_events.csv); they are
never scored as zero equity. Uses the same Dirichlet(0.5) convention as
evaluation/competing_risk.py (dot-com cohort) so the two eras are comparable.
"""
import csv
import json
import numpy as np
from models.valuation import ROOT

STATES = ('standalone', 'acquired', 'bankrupt')

def read(name):
    with (ROOT / 'data' / name).open(newline='') as f:
        return list(csv.DictReader(f))

def universe():
    rows = {}
    for r in read('stage4_candidate_universe.csv'):
        rows[(r['episode'], r['family'])] = dict(episode=r['episode'], family=r['family'], origin=r['origin'], target=r['target'])
    for r in read('cloud_cycle_cohort.csv'):
        fam = r['company'].lower()
        rows.setdefault(('cloud2020', fam), dict(episode='cloud2020', family=fam, origin='2020-12-31', target='2025-12-31'))
    ev = {(r['episode'], r['family']): r for r in read('stage4_exit_events.csv')}
    for k, r in rows.items():
        e = ev.get(k)
        r['state'] = 'acquired' if e and e['close_date'] <= r['target'] else 'standalone'
        r['event'] = e
    return list(rows.values())

def posterior(rows, alpha=.5, draws=100000, seed=42):
    n = np.array([sum(r['state'] == s for r in rows) for s in STATES], float)
    a = n + alpha; p = a / a.sum()
    sample = np.random.default_rng(seed).dirichlet(a, size=draws)
    lo, hi = np.quantile(sample, [.05, .95], axis=0)
    annual_acq = 1 - (1 - p[1]) ** (1 / 5)  # constant hazard reproducing 5y incidence (single-risk approx.)
    return dict(n=int(n.sum()), counts=dict(zip(STATES, n.astype(int).tolist())), p5=dict(zip(STATES, p.tolist())),
                p5_90=dict(zip(STATES, zip(lo.tolist(), hi.tolist()))), annual_acquisition_hazard=annual_acq)

def run():
    rows = universe(); out = dict(status='development; rosters retired after margin scoring', episodes={})
    for ep in ('cloud2015', 'cloud2020'):
        out['episodes'][ep] = posterior([r for r in rows if r['episode'] == ep])
    out['pooled'] = posterior(rows)
    vals = [r for r in rows if r['event'] and r['event']['origin_ranking_value_usd_b']]
    out['deal_value_to_may2015_cap'] = {r['family']: float(r['event']['headline_value_usd_b']) / float(r['event']['origin_ranking_value_usd_b']) for r in vals}
    out['note'] = ('Deal values are headline figures with mixed equity/enterprise bases; May-2015 market caps predate the '
                   'Dec-2015 origin. Ratios are descriptive, not a premium estimate. No bankruptcy occurred in either roster '
                   '(the dot-com cohort had 2 of 18), so the bankrupt share is prior-driven.')
    out['rows'] = [dict(r, event=bool(r['event'])) for r in rows]
    return out

if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
