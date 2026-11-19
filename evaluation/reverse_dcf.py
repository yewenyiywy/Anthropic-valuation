"""Reverse DCF: which single assumption would the production engine need to match
a given equity value? Diagnostic only. The market value is an input to read
off implied assumptions, never a training label (Anthropic is application-only).

Each lever moves alone from the base normal-regime case; all others stay base.
"""
import argparse
import json
from models.joint_customer_states import forecast_joint, initial_capture, draw_parameters

LEVERS = {
    'scenario_factor': ('factor', None, 0., 1., 'all scenario parameters moved together from base (0) to bull (1), as in simulate()'),
    # name: (kind, key, low, high, description)
    'terminal_capture': ('input', 'capture', .05, 3., 'effective capture of AI deployment spend at year 10'),
    'demand_growth': ('input', 'growth', .2, 6., 'multiplier on IDC sector growth rates'),
    'acquisition_rate': ('scenario', 'new', 0., 2., 'new-customer revenue as a share of existing (fades by year 8)'),
    'initial_volume': ('scenario', 'volume', 1., 6., 'initial token-volume growth multiplier (fades by year 8)'),
    'compute_cost_ratio': ('scenario', 'cost_ratio', .05, .9, 'variable compute cost / revenue'),
    'wacc': ('scenario', 'wacc', .05, .20, 'discount rate'),
    'terminal_growth': ('scenario', 'terminal_growth', -.05, .11, 'survivor long-run growth after year 10'),
}

def equity(kind, key, x):
    if kind == 'factor':
        scen, inp = draw_parameters(x)
        return forecast_joint(scenario_overrides=scen, input_overrides=inp)[2]
    if kind == 'input':
        return forecast_joint(input_overrides={key: x})[2]
    return forecast_joint(scenario_overrides={key: x})[2]

def solve(target, lever, tol=1e-4):
    kind, key, lo, hi, desc = LEVERS[lever]
    f_lo, f_hi = equity(kind, key, lo) - target, equity(kind, key, hi) - target
    out = dict(lever=lever, description=desc, bounds=(lo, hi),
               equity_at_bounds=(f_lo + target, f_hi + target))
    if f_lo * f_hi > 0:
        return dict(out, implied=None, note='target not reachable within bounds')
    for _ in range(60):
        mid = (lo + hi) / 2; f = equity(kind, key, mid) - target
        if abs(hi - lo) < tol: break
        if (f < 0) == (f_lo < 0): lo, f_lo = mid, f
        else: hi = mid
    return dict(out, implied=(lo + hi) / 2)

def run(target):
    base = forecast_joint()[2]
    ref = dict(scenario_factor=0., acquisition_rate=.20, initial_volume=1.65, terminal_capture=initial_capture(), demand_growth=1., compute_cost_ratio=.48, wacc=.12, terminal_growth=.03)
    return dict(status='diagnostic: implied single-lever assumptions, not a forecast',
                target_equity=target, base_equity=base,
                levers=[dict(solve(target, k), base_value=ref[k]) for k in LEVERS])

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--equity', type=float, required=True, help='equity value in USD B to reverse-engineer')
    print(json.dumps(run(ap.parse_args().equity), indent=2))
