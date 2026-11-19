"""Margin-at-scale and discount-rate estimation from comparables.

Development/diagnostic study registered in evaluation/margin_scale_preregistration.md.
Outputs replace the hand-set cost ratios and WACC of the valuation scenarios.
"""
import csv, json, math, sys, warnings
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / 'data' / 'margin_scale_panel.csv'
FAMILY = {'AWS': 'AMZN', 'GCLOUD': 'GOOGL', 'MSIC': 'MSFT'}
PLATFORM = {'MSFT', 'GOOGL', 'META', 'ORCL', 'ADBE', 'CRM', 'INTU', 'NFLX', 'AWS', 'GCLOUD', 'MSIC'}
SEED = 0


def load():
    rows = {}
    for r in csv.DictReader(open(PANEL)):
        rev = float(r['revenue_usd_b']); oi = float(r['operating_income_usd_b'])
        cor = float(r['cost_of_revenue_usd_b']) if r['cost_of_revenue_usd_b'] else None
        rows.setdefault(r['company'], []).append((r['fiscal_year_end'], rev, oi, cor))
    for k in rows: rows[k].sort()
    return rows


def examples(rows, h=5):
    X, y, g, names = [], [], [], []
    for c, s in rows.items():
        for i in range(1, len(s) - h):
            _, rev, oi, cor = s[i]; _, rp, oip, _ = s[i - 1]
            if rev < .05 or rp <= 0: continue
            m = oi / rev; mp = oip / rp
            growth = min(max(rev / rp - 1, -.5), 3.)
            gm = 1 - cor / rev if cor is not None else np.nan
            lab = s[i + h][2] / s[i + h][1]
            X.append([m, math.log(rev), growth, m - mp, gm]); y.append(lab)
            g.append(FAMILY.get(c, c)); names.append((c, s[i][0]))
    return np.array(X), np.array(y), np.array(g), names


class Hold:
    def fit(self, X, y): return self
    def predict(self, X): return X[:, 0]


class Mean:
    def fit(self, X, y): self.m = float(np.mean(y)); return self
    def predict(self, X): return np.full(len(X), self.m)


class Partial:
    def fit(self, X, y): self.b = np.polyfit(X[:, 0], y, 1); return self
    def predict(self, X): return np.polyval(self.b, X[:, 0])


class Convergence:
    """label = m + lam*(a + b*logrev - m); fit by least squares on (lam, lam*a, lam*b)."""
    def fit(self, X, y):
        A = np.column_stack([-X[:, 0], np.ones(len(X)), X[:, 1]])
        self.w, *_ = np.linalg.lstsq(A, y - X[:, 0], rcond=None); return self
    def predict(self, X):
        return X[:, 0] + np.column_stack([-X[:, 0], np.ones(len(X)), X[:, 1]]) @ self.w


def sk_models():
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import Ridge
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
    from sklearn.neural_network import MLPRegressor
    imp = lambda: SimpleImputer(strategy='median', add_indicator=True)
    return {
        'ridge': lambda: make_pipeline(imp(), StandardScaler(), Ridge(alpha=1.0)),
        'gbm': lambda: HistGradientBoostingRegressor(max_depth=3, max_iter=200, learning_rate=.05, random_state=SEED),
        'gp': lambda: make_pipeline(imp(), StandardScaler(), GaussianProcessRegressor(
            ConstantKernel(1.0) * RBF(1.0) + WhiteKernel(.01), normalize_y=True, random_state=SEED)),
        'mlp': lambda: make_pipeline(imp(), StandardScaler(), MLPRegressor(hidden_layer_sizes=(16, 16), early_stopping=True,
                                     max_iter=3000, random_state=SEED)),
    }


def loio(X, y, g, make):
    pred = np.empty(len(y))
    for fam in np.unique(g):
        tr, te = g != fam, g == fam
        pred[te] = make().fit(X[tr], y[tr]).predict(X[te])
    return pred


def score(p, y):
    return dict(mae_pp=float(100 * np.mean(np.abs(p - y))), bias_pp=float(100 * np.mean(p - y)))


def target_a(rows):
    X, y, g, names = examples(rows)
    cands = {'hold': Hold, 'mean': Mean, 'partial': Partial, 'convergence': Convergence}
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        cands.update(sk_models())
        res = {k: score(loio(X, y, g, f), y) for k, f in cands.items()}
    base = min(res[k]['mae_pp'] for k in ('hold', 'mean', 'partial'))
    best = min(res, key=lambda k: res[k]['mae_pp'])
    promoted = best if best not in ('hold', 'mean', 'partial') and res[best]['mae_pp'] <= base - 1.0 else None
    return dict(n=int(len(y)), issuers=int(len(np.unique(g))), scores=res, best=best,
                best_baseline_mae_pp=base, promoted=promoted)


def target_b(rows):
    ms = {}
    for c, s in rows.items():
        if c not in PLATFORM or s[-1][1] < 20: continue
        ms[c] = float(np.mean([oi / rev for _, rev, oi, _ in s[-3:]]))
    v = np.array(sorted(ms.values()))
    q = {k: float(np.quantile(v, p)) for k, p in (('p10', .1), ('p50', .5), ('p90', .9))}
    msic = [r for r in rows['MSIC'] if r[3] is not None]
    share = [cor / (rev - oi) for _, rev, oi, cor in msic]
    return dict(issuers=ms, m_star=q, m_star_values=[float(x) for x in v],
                compute_share=dict(values=share, bear=max(share), base=float(np.mean(share)), bull=min(share)))


def target_c():
    mk = {r['item']: float(r['value']) for r in csv.DictReader(open(ROOT / 'data' / 'wacc_market.csv'))}
    t = mk['tax_rate']; bu = []
    for r in csv.DictReader(open(ROOT / 'data' / 'wacc_inputs.csv')):
        bu.append(float(r['beta_5y']) / (1 + (1 - t) * float(r['debt_to_equity'])))
    bu = np.array(bu); de = mk['anthropic_debt_usd_b'] / mk['anthropic_equity_usd_b']
    we = 1 / (1 + de); kd = (mk['risk_free_10y'] + .01) * (1 - t)
    def wacc(b, erp=mk['implied_erp']):
        bl = b * (1 + (1 - t) * de); return we * (mk['risk_free_10y'] + bl * erp) + (1 - we) * kd
    q = {k: float(np.quantile(bu, p)) for k, p in (('p25', .25), ('p50', .5), ('p75', .75))}
    return dict(unlevered_betas=[float(x) for x in bu], beta_quantiles=q, de=de,
                wacc=dict(bear=wacc(q['p75']), base=wacc(q['p50']), bull=wacc(q['p25'])),
                wacc_erp_low=wacc(q['p50'], mk['implied_erp_low']), wacc_erp_high=wacc(q['p50'], mk['implied_erp_high']))


def estimates():
    rows = load(); b = target_b(rows); c = target_c()
    out = {}
    for n, m, s in (('bear', b['m_star']['p10'], b['compute_share']['bear']),
                    ('base', b['m_star']['p50'], b['compute_share']['base']),
                    ('bull', b['m_star']['p90'], b['compute_share']['bull'])):
        costs = 1 - m
        out[n] = dict(cost_ratio=costs * s, other_ratio=costs * (1 - s), wacc=c['wacc'][n], m_star=m)
    return out


def run():
    rows = load()
    return dict(status='development/diagnostic; labels were public before registration',
                target_a=target_a(rows), target_b=target_b(rows), target_c=target_c(), scenario_estimates=estimates())


if __name__ == '__main__':
    json.dump(run(), sys.stdout, indent=1)
