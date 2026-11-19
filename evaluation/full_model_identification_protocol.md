# Full-model synthetic parameter recovery (development; not an empirical backtest)

Freeze the following design before fitting: use the full `forecast_joint` engine
with no callbacks or disabled mechanisms, entirely invented issuer financials,
and nine positive scenario parameters. Generate labels from a declared synthetic
truth with normal/winter/boom constant regime paths as training and two distinct
mixed paths as test. Fit scaled first-five-year revenue, FCF and year-five equity
residuals by bounded nonlinear least squares. Compare to the same loss augmented
with synthetic direct conversion, price, usage, capex and unit-cost observations.
Use three deterministic initial points; no selection by test loss. Record the
full Jacobian SVD in normalized log-parameter coordinates and relative parameter
error, plus year-five synthetic equity error. The truth is not a historical
company, and the synthetic test is a recovery check, not empirical accuracy.
Do not transfer fitted values to Anthropic. Exact structural nonidentification
may be removed by a one-to-one composite coordinate without deleting economic
mechanisms; report which external measurements are necessary to recover each
factor separately. No real equity labels are read or used.
