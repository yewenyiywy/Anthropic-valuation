"""Revenue-growth persistence on the 18-observation cloud panel (DEVELOPMENT ONLY).

All 18 observations are exposed: the 7 exposed-family rows by design and the
11 stage-4 rows because target-year revenue was collected with the margin
labels. Nothing here is an out-of-sample claim.

Model: log growth decays geometrically toward a long-run rate,
    g_t = g_inf + (g_0 - g_inf) * 2**(-t/H),   g_0 = ln(R_0 / R_-1),
    ln(R_h / R_0) = sum_{t=1..h} g_t   (fractional final year pro rata).
Reported revenue includes acquisitions (e.g. Salesforce-Slack, Twilio-Segment),
so fitted persistence is an upper bound for organic growth.
"""
import json
import math
from evaluation.margin_path import ROOT, features, read

GRID_H = [x / 4 for x in range(2, 41)]        # 0.5..10 years
GRID_G = [x / 200 for x in range(-10, 41)]    # -5%..20% log growth

def panel():
    rows = []
    for r in read(ROOT / 'data/margin_dev_panel.csv'):
        x = features(r)
        rows.append(dict(family=r['family'], origin=r['origin'], g0=x['g0'], h=x['h'],
                         y=math.log(float(r['target_revenue']) / float(r['revenue'])), source='exposed'))
    inp = {r['family']: r for r in read(ROOT / 'data/stage4_origin_inputs.csv')}
    for r in read(ROOT / 'data/stage4_margin_labels.csv'):
        if not r['revenue']: continue
        i = inp[r['family']]; x = features(i)
        rows.append(dict(family=r['family'], origin=i['origin'], g0=x['g0'], h=x['h'],
                         y=math.log(float(r['revenue']) / float(i['revenue'])), source='stage4 (retired)'))
    return rows

def cum(g0, h, ginf, H):
    n = int(h); frac = h - n
    s = sum(ginf + (g0 - ginf) * 2 ** (-t / H) for t in range(1, n + 1))
    return s + frac * (ginf + (g0 - ginf) * 2 ** (-(n + 1) / H))

def fit(rows, ginf=None):
    best = None
    for H in GRID_H:
        for g in (GRID_G if ginf is None else [ginf]):
            L = sum(abs(cum(r['g0'], r['h'], g, H) - r['y']) for r in rows)
            if best is None or L < best[0]: best = (L, H, g)
    return dict(half_life=best[1], g_inf=best[2])

def engine_fade(g0, h, years=7):
    """The engine's linear fade applied to the same g0 (diagnostic comparator)."""
    n = int(h); frac = h - n
    f = lambda t: g0 * max(0, 1 - (t - 1) / years)
    return sum(f(t) for t in range(1, n + 1)) + frac * f(n + 1)

def loo(rows):
    fams = sorted({r['family'] for r in rows}); out = {}
    models = {
        'flat': lambda tr, r: 0.,
        'hold_growth': lambda tr, r: r['g0'] * r['h'],
        'engine_linear7': lambda tr, r: engine_fade(r['g0'], r['h']),
        'decay_fit': lambda tr, r: (lambda th: cum(r['g0'], r['h'], th['g_inf'], th['half_life']))(fit(tr)),
        'decay_fit_ginf0': lambda tr, r: (lambda th: cum(r['g0'], r['h'], 0., th['half_life']))(fit(tr, 0.)),
    }
    for name, f in models.items():
        err = []
        for fam in fams:
            tr = [x for x in rows if x['family'] != fam]
            err += [f(tr, r) - r['y'] for r in rows if r['family'] == fam]
        # error in log revenue at the endpoint; report as % via exp
        out[name] = dict(loo_mae_log=sum(map(abs, err)) / len(err), loo_bias_log=sum(err) / len(err))
    return out

def run():
    rows = panel(); th = fit(rows); th0 = fit(rows, 0.)
    return dict(status='development only; all 18 observations exposed', n=len(rows),
                families=len({r['family'] for r in rows}), fit=th, fit_ginf0=th0, loo=loo(rows),
                g0_range=(min(r['g0'] for r in rows), max(r['g0'] for r in rows)), rows=rows)

if __name__ == '__main__':
    print(json.dumps(run(), indent=2))

def engine_equivalent_g0(years=(5, 10)):
    """Starting log growth a panel-fitted SaaS decay would need to reproduce the
    engine's base revenue path from the 81B run rate (diagnostic only)."""
    from models.joint_customer_states import forecast_joint
    from models.valuation import observations
    th = fit(panel()); r0 = observations()['run_rate']; rows = forecast_joint()[0]
    out = {}
    for h in years:
        target = math.log(rows[h - 1]['revenue'] / r0); lo, hi = -.5, 5.
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if cum(mid, h, th['g_inf'], th['half_life']) < target else (lo, mid)
        out[h] = (lo + hi) / 2
    g0s = sorted(r['g0'] for r in panel())
    return dict(fit=th, equivalent_g0=out, panel_g0_percentile={h: sum(g <= v for g in g0s) / len(g0s) for h, v in out.items()},
                anthropic_observed_g0=math.log(33.242 / 2.545), note='observed g0 is far outside the panel range; not extrapolated')
