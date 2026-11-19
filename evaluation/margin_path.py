"""Stage-4 margin-path component: development selection and frozen predictions.

See evaluation/stage4_margin_preregistration.md. This module never reads
stage-4 outcome labels. `score()` refuses to run unless the frozen record
matches the current predictions, inputs, code and preregistration.
"""
import csv
import hashlib
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / 'data/stage4_origin_inputs.csv'
DEV = ROOT / 'data/margin_dev_panel.csv'
PREREG = ROOT / 'evaluation/stage4_margin_preregistration.md'
PREDICTIONS = ROOT / 'evaluation/stage4_margin_predictions.csv'
FREEZE = ROOT / 'evaluation/stage4_margin_freeze.json'
HALF_LIFE = 3.0
SIMPLICITY_PP = 1.0
TARGET_YEAR = {'cloud2015': 2020, 'cloud2020': 2025}
CANDIDATES = ('hold', 'fade15', 'pooled', 'converge', 'leverage')

def read(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def margin(cfo, ppe, sw, rev):
    return (float(cfo) - float(ppe or 0) - float(sw or 0)) / float(rev)

def features(r):
    end = date.fromisoformat(r['fy_end']); y = TARGET_YEAR[r['episode']]
    try: tgt = end.replace(year=y)
    except ValueError: tgt = end.replace(year=y, day=28)
    if r['capex_ppe'] == '': raise ValueError('missing capex: ' + r['family'])
    return dict(m0=margin(r['cfo'], r['capex_ppe'], r['capex_software'], r['revenue']),
                g0=math.log(float(r['revenue']) / float(r['revenue_prior'])),
                h=(tgt - end).days / 365.25)

def target(r):
    return margin(r['target_cfo'], r['target_capex_ppe'], r['target_capex_software'], r['target_revenue'])

def predict(model, theta, x):
    m0, g0, h = x['m0'], x['g0'], x['h']
    if model == 'hold': return m0
    if model == 'fade15': return m0 + (.15 - m0) * min(h / 10, 1)
    if model == 'pooled': return theta
    if model == 'converge': return theta + (m0 - theta) * 2 ** (-h / HALF_LIFE)
    if model == 'leverage': return m0 + theta * max(0., g0)
    raise ValueError(model)

def fit(model, X, y):
    """One parameter at most; minimize MAE by dense grid (no outcome but dev)."""
    if model in ('hold', 'fade15'): return None
    if model == 'pooled': return sum(y) / len(y)
    grid = [i / 1000 for i in range(-200, 601)]
    loss = lambda t: sum(abs(predict(model, t, x) - v) for x, v in zip(X, y))
    return min(grid, key=loss)

def development():
    rows = read(DEV); X = [features(r) for r in rows]; y = [target(r) for r in rows]
    fams = sorted({r['family'] for r in rows}); out = {}
    for m in CANDIDATES:
        errs = [None] * len(rows)
        for fam in fams:
            tr = [i for i, r in enumerate(rows) if r['family'] != fam]
            th = fit(m, [X[i] for i in tr], [y[i] for i in tr])
            for i, r in enumerate(rows):
                if r['family'] == fam: errs[i] = predict(m, th, X[i]) - y[i]
        out[m] = dict(loo_mae_pp=100 * sum(map(abs, errs)) / len(errs),
                      loo_bias_pp=100 * sum(errs) / len(errs),
                      theta_all=fit(m, X, y))
    best = min(CANDIDATES, key=lambda m: out[m]['loo_mae_pp'])
    selected = best if out['hold']['loo_mae_pp'] - out[best]['loo_mae_pp'] >= SIMPLICITY_PP else 'hold'
    detail = [dict(family=r['family'], origin=r['origin'], m0=x['m0'], g0=x['g0'], h=x['h'], target=v)
              for r, x, v in zip(rows, X, y)]
    return dict(candidates=out, best_by_loss=best, selected=selected, n=len(rows), families=len(fams), rows=detail)

def freeze():
    dev = development(); rows = read(INPUTS)
    with PREDICTIONS.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['family', 'episode', 'origin', 'fy_end', 'h', 'm0', 'g0'] + [f'pred_{m}' for m in CANDIDATES] + ['primary'])
        for r in rows:
            x = features(r)
            preds = [predict(m, dev['candidates'][m]['theta_all'], x) for m in CANDIDATES]
            w.writerow([r['family'], r['episode'], r['origin'], r['fy_end'], f"{x['h']:.4f}", f"{x['m0']:.6f}", f"{x['g0']:.6f}"]
                       + [f'{p:.6f}' for p in preds] + [dev['selected']])
    record = dict(status='frozen before stage-4 margin labels were opened; labels not accessed by this code',
                  selected=dev['selected'], development=dev['candidates'],
                  sha256={p.name: sha(p) for p in (PREDICTIONS, INPUTS, DEV, PREREG, Path(__file__))})
    FREEZE.write_text(json.dumps(record, indent=2) + '\n')
    return record

def verify():
    rec = json.loads(FREEZE.read_text())
    cur = {p.name: sha(p) for p in (PREDICTIONS, INPUTS, DEV, PREREG, Path(__file__))}
    bad = [k for k in rec['sha256'] if rec['sha256'][k] != cur.get(k)]
    if bad: raise ValueError('frozen artifacts changed: ' + ', '.join(bad))
    return rec

def score(labels_path):
    """Score frozen predictions against a labels CSV (family, target_margin or blank = no endpoint)."""
    rec = verify(); preds = {r['family']: r for r in read(PREDICTIONS)}
    labels = {r['family']: r for r in read(Path(labels_path))}
    if set(labels) != set(preds): raise ValueError('labels must cover every frozen issuer (blank = no endpoint)')
    res = {}
    for scope in ('all', 'cloud2015', 'cloud2020'):
        fam = [f for f in preds if labels[f]['target_margin'] != '' and (scope == 'all' or preds[f]['episode'] == scope)]
        y = [float(labels[f]['target_margin']) for f in fam]
        res[scope] = dict(n=len(fam), coverage=len(fam) / sum(1 for f in preds if scope == 'all' or preds[f]['episode'] == scope))
        for m in CANDIDATES:
            p = [float(preds[f][f'pred_{m}']) for f in fam]
            res[scope][m] = dict(mae_pp=100 * sum(abs(a - b) for a, b in zip(p, y)) / len(y) if y else None,
                                 bias_pp=100 * sum(a - b for a, b in zip(p, y)) / len(y) if y else None)
    s = rec['selected']
    promote = res['all']['n'] >= 8 and all(res[k][s]['mae_pp'] is not None and res[k][s]['mae_pp'] < min(res[k]['hold']['mae_pp'], res[k]['pooled']['mae_pp'])
                                           for k in ('all', 'cloud2015', 'cloud2020') if res[k]['n'])
    return dict(selected=s, promoted=bool(promote) and s not in ('hold', 'pooled'), scores=res)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--development', action='store_true'); g.add_argument('--freeze', action='store_true')
    g.add_argument('--verify', action='store_true'); g.add_argument('--score', metavar='LABELS_CSV')
    a = ap.parse_args()
    print(json.dumps(development() if a.development else freeze() if a.freeze else verify() if a.verify else score(a.score), indent=2))
