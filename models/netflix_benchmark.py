"""Paid-account benchmark, not an estimated AI conversion rate. USD billions."""
from .valuation import SCENARIOS, forecast

# Netflix 2024 10-K; year-end memberships (millions), full-year monthly ARM.
REGIONS = ((89.625,17.20),(101.133,10.96),(53.327,8.24),(57.541,7.29))
ACCOUNTS = 325.0  # million, rounded 2025 milestone
AUDIENCE = 1000.0  # million, approximate upper reference (Netflix: approaching 1bn)

def benchmark(account_ratio, north_america_price=20):
    """Ratio of Claude paid individual accounts to Netflix paid accounts.

    Regional mix assumed unchanged; relative regional price index is a proxy
    for willingness to pay, not actual Claude regional pricing.
    """
    total = sum(n for n, _ in REGIONS)
    arm = north_america_price*sum(n*p/17.20 for n,p in REGIONS)/total
    paid = ACCOUNTS*account_ratio
    return dict(paid_millions=paid, audience_fraction=paid/AUDIENCE,
                monthly_arm=arm, annual_revenue=paid*arm*12/1000)

if __name__ == '__main__':
    for name,ratio in zip(SCENARIOS,(.05,.15,.30)):
        b=benchmark(ratio)
        rows,ev,equity=forecast(SCENARIOS[name],personal_ceiling=b['annual_revenue'])
        print(name,b, 'EV',round(ev,2),'equity',round(equity,2), 'year5 personal',round(rows[4]['personal'],2))
