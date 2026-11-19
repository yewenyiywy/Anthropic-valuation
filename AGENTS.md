# Mandatory research protocol

Every change to valuation, data, calibration, or evaluation MUST follow
[MODEL_VALIDATION_PROTOCOL.md](MODEL_VALIDATION_PROTOCOL.md). This is a
repository instruction, not an optional recommendation.

- Before training, register the target, vintage, issuer groups, split, baseline,
  loss, thresholds, model entrypoint and data/parameter provenance.
- Train and select hyperparameters on development data only. Never select a
  model or fit a correction using final holdout outcomes.
- Evaluate the actual production model, not a reduced surrogate. Report revenue,
  cash flow and equity separately; equity market cap is the primary observable
  target, not intrinsic value ground truth.
- Run `python -m unittest discover -s evaluation -p 'test_*.py'` and
  `python -m evaluation.validation_gate --audit`. For a claimed validated
  valuation, `python -m evaluation.validation_gate --manifest PATH` MUST pass.
- Missing, proxy, or unverified company-specific information must be labeled;
  never silently substitute Anthropic assumptions. Do not publish a new
  validated Anthropic estimate when the gate is blocked.
- Update the English and Chinese README with actual measured results, limitations,
  and gate status. Do not call an already examined cohort a blind test.
