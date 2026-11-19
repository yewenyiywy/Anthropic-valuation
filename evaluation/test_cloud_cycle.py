from evaluation.cloud_cycle import cohort,evaluate

def test_cloud_endpoints_do_not_change_forecasts():
    rows=cohort()
    a=evaluate(rows)
    b=evaluate([dict(r,r2025=str(float(r['r2025'])*3)) for r in rows])
    assert len(a['rows'])==5
    assert a['theta']==b['theta']
    assert a['endpoint_prior']==b['endpoint_prior']
    assert [r['pred'] for r in a['rows']]==[r['pred'] for r in b['rows']]
