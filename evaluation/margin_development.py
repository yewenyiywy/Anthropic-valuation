"""Post-stage-4 margin development panel (DEVELOPMENT ONLY, no test claim).

The stage-4 roster was scored once under its preregistration (see
stage4_margin_score.json) and is now retired to development. This module pools
it with the exposed-family panel (18 observations, 16 families) to estimate
margin convergence for use in the engine and its diagnostics. Any new claim of
out-of-sample accuracy needs a new roster.

Two margin definitions:
  cfo : (CFO - capex - capitalized software) / revenue   (SBC not deducted)
  econ: cfo margin - SBC / revenue                         (SBC as a real cost,
        the definition the valuation engine's cost ratios correspond to)
"""
import csv
import json
import statistics as st
from evaluation.margin_path import ROOT, features, read

HALF_LIVES = (1.5, 2., 3., 4., 6.)

def panel():
    rows = []
    for r in read(ROOT / 'data/margin_dev_panel.csv'):
        x = features(r); R, Rt = float(r['revenue']), float(r['target_revenue'])
        f = float(r['cfo']) - float(r['capex_ppe'] or 0) - float(r['capex_software'] or 0)
        ft = float(r['target_cfo']) - float(r['target_capex_ppe']) - float(r['target_capex_software'] or 0)
        rows.append(dict(family=r['family'], origin=r['origin'], h=x['h'], g0=x['g0'], source='exposed',
                         cfo0=f / R, econ0=(f - float(r['sbc'])) / R, cfo=ft / Rt, econ=(ft - float(r['target_sbc'])) / Rt))
    inp = {r['family']: r for r in read(ROOT / 'data/stage4_origin_inputs.csv')}
    for r in read(ROOT / 'data/stage4_margin_labels.csv'):
        if not r['target_margin']: continue
        i = inp[r['family']]; x = features(i); R, Rt = float(i['revenue']), float(r['revenue'])
        f = float(i['cfo']) - float(i['capex_ppe']) - float(i['capex_software'] or 0)
        ft = float(r['cfo']) - float(r['capex_ppe']) - float(r['capex_software'] or 0)
        rows.append(dict(family=r['family'], origin=i['origin'], h=x['h'], g0=x['g0'], source='stage4 (retired)',
                         cfo0=f / R, econ0=(f - float(i['sbc'])) / R, cfo=ft / Rt, econ=(ft - float(r['sbc'])) / Rt))
    return rows

def converge(m0, h, mstar, hl):
    return mstar + (m0 - mstar) * 2 ** (-h / hl)

def fit(rows, kind, hl=None):
    """Minimize MAE over m* (and half-life from a fixed grid if hl is None)."""
    grid = [i / 1000 for i in range(-200, 501)]
    best = None
    for H in (HALF_LIVES if hl is None else (hl,)):
        for m in grid:
            loss = sum(abs(converge(r[kind + '0'], r['h'], m, H) - r[kind]) for r in rows)
            if best is None or loss < best[0]: best = (loss, m, H)
    return dict(mstar=best[1], half_life=best[2])

def loo(rows, kind):
    out = {}
    fams = sorted({r['family'] for r in rows})
    for name in ('hold', 'pooled', 'converge3', 'converge_fit'):
        err = []
        for fam in fams:
            tr = [r for r in rows if r['family'] != fam]; te = [r for r in rows if r['family'] == fam]
            for r in te:
                if name == 'hold': p = r[kind + '0']
                elif name == 'pooled': p = sum(x[kind] for x in tr) / len(tr)
                else:
                    th = fit(tr, kind, 3. if name == 'converge3' else None)
                    p = converge(r[kind + '0'], r['h'], th['mstar'], th['half_life'])
                err.append(p - r[kind])
        out[name] = dict(loo_mae_pp=100 * sum(map(abs, err)) / len(err), loo_bias_pp=100 * sum(err) / len(err))
    return out

def run():
    rows = panel()
    res = dict(status='development only; stage-4 roster retired after one preregistered scoring',
               n=len(rows), families=len({r['family'] for r in rows}))
    for kind in ('cfo', 'econ'):
        y = sorted(r[kind] for r in rows)
        res[kind] = dict(loo=loo(rows, kind), fit_all=fit(rows, kind), fit_all_hl3=fit(rows, kind, 3.),
                         target_median=st.median(y), target_mean=st.mean(y), target_sd=st.stdev(y),
                         target_p10=y[int(.1 * (len(y) - 1))], target_p90=y[int(.9 * (len(y) - 1) + .5)])
    res['rows'] = rows
    return res

def percentile(value, kind='econ'):
    """Share of panel target margins at or below value (empirical CDF)."""
    y = [r[kind] for r in panel()]
    return sum(v <= value for v in y) / len(y)

if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
