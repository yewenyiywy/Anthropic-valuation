from evaluation.cloud_equity import inputs,evaluate

def test_future_values_not_used():
    rows=inputs()
    a=evaluate(rows)
    b=evaluate([dict(r,cap25='9999',r2025='9999') for r in rows])
    assert [r['pred'] for r in a['rows']]==[r['pred'] for r in b['rows']]
