# Release candidate evidence schema

The manifest is deliberately absent until a real candidate exists. Never copy
synthetic test fixtures into it. Use `evaluation/release_manifest.json` for CI.
All dates are ISO 8601; timestamps include timezone. All amounts are USD B.

Required manifest fields:

- `target`: `equity_market_cap_usd_b`
- `model_entrypoint`: `models.joint_customer_states.forecast_joint`
- `model_scope`: `full_company_profile`
- `evidence_tier`: `observed_historical` (validated imputations are a separate
  empirical development tier; synthetic labels are simulation only)
- `training_objective`: `equity_log1p_mae`
- `horizon_years`: 5
- `thresholds`: max_wape 0.30, max_abs_bias 0.15, min_families 10, min_cycles 2
- `source_fingerprint`: output of `source_fingerprint(ROOT)` in validation_gate
- `registered_at`, `frozen_at`, `labels_opened_at`, `reviewed_at`
- `trainer`, `reviewer`: distinct accountable persons
- `artifacts`: mapping from each required artifact name to repository-relative
  path and SHA-256 (`path`, `sha256`).

Artifact names and evidence:

| Artifact | Contents |
|---|---|
| preregistration | universe/source, dates, target definition, hyperparameter search budget, metric/threshold and censoring plans |
| splits | CSV: sample_id, company, family_id, split, cycle, origin, target_date, label_available, origin_market_cap, origin_revenue |
| provenance | CSV: sample_id, component, available_date, status, source, reconciliation, document_section, units; link the actual immutable input row/value and assumptions in reconciliation evidence |
| predictions | CSV: sample_id, equity_market_cap_usd_b, revenue5; freeze before labels are revealed |
| labels | CSV: sample_id, target_date, equity_market_cap_usd_b, outcome, source; outcome listed/wipeout/acquired_documented; document M&A comparability |
| parameters | fitted checkpoint, all preprocessing transforms and state parameters, seeds, dependency lock and uncertainty |
| training_log | fold-level losses, feature selection, covariance shrinkage, hyperparameter trials, ablations, revenue and matched FCFF forecasts, reproducible commands |
| freeze_attestation | independent timestamped evidence of preregistration and checkpoint/prediction hashes before label access |
| review | independent source and execution review, sample coverage, corporate actions, label comparability, calibration and uncertainty, signed decision |
| engine | models/joint_customer_states.py |
| model_contract | JSON: entrypoint, source_fingerprint, mechanisms (exact MECHANISMS set in gate); document architecture, state dimensions and allowed structural zeros |
| execution_trace | CSV: sample_id, mechanism, status, architecture_sha256, checkpoint_sha256, trace_evidence, input_evidence, ablation_evidence, structural_zero_source; one row per mechanism per issuer including `anthropic_application`; status active or evidence_supported_structural_zero only |

Use stable family IDs reflecting mergers and predecessor/rebranded entities;
the exposed-name list is a safeguard, not a substitute for resolving aliases.
The reviewer must reconcile the claimed universe against the outcome roster,
including mergers, delistings and bankruptcies. A merger price is not an
ordinary year-five market cap: if no comparable target can be constructed under
the preregistered methodology, report the distinct exit outcome and block the
full equity claim rather than silently deleting the firm.

The machine gate verifies structural evidence, hashes, timing, coverage and
the primary numerical test, not document authenticity, independent custody,
whether training really used the stated loss, or whether all evidence is true.
Those require authenticated independent review. Even a machine pass is named
`GATE_PASS_REQUIRES_AUTHENTICATED_REVIEW`; it is never an automatic publication approval.
