# Stage 4 candidate roster — outcome-sealed preflight

The candidate selection rule is contemporaneous, not survivor-selected. Use the 2015 Bessemer State of the Cloud ranking (May 29 market capitalization; [original slide deck](https://www.slideshare.net/slideshow/bessemer-venture-partners-2015-state-of-the-cloud/135025215)) and the ten largest June 30 2020 WCLD positions from the SEC-filed annual report. The latter is a holdings ranking, not a market capitalization ranking. Exclude previously exposed issuer families before examining any target labels. Origins are December 31 of each vintage, and targets are five calendar years later. The two cloud episodes are not established to be distinct technology cycles; independent approval or a replacement ex-ante cohort is needed.

Primary target remains observed equity market capitalization under MODEL_VALIDATION_PROTOCOL.md. Acquisitions, bankruptcies and delistings must be tracked, never silently dropped or assigned zero equity absent legal evidence. An acquisition payoff is a distinct endpoint; if the same target cannot be observed, the release gate remains blocked pending an independently approved endpoint policy. Do not open labels to resolve these decisions.

This freezes the selection rule only, not the fitted model or inputs. Before opening any target, collect vintage public company evidence, validate state reconstruction by masking observed fields, fit on separate development families with five-year label embargo, freeze the exact full-model code, parameters and predictions, and arrange independent custody. No market-cap accuracy has been measured on this roster. Run `python -m evaluation.stage4_readiness` for the preflight. Release must pass the separate validation gate.

The first evidence batch is `data/stage4_customer_anchors.csv`: 20 observations covering nine candidates. `available_by` is a conservative publication cutoff rather than necessarily the exact filing date. Five issuers have comparable year-over-year stock counts, which identify the following interval conditional on comparable scope: $A=N_1-rN_0$, $0\le r\le1$. Thus $A\ge\max(0,N_1-N_0)$, and $A\le N_1$ if the ending count is exact. Approximate counts give approximate bounds; lower-bounded counts do not establish an upper bound. Entries include threshold crossings and reactivation. Acquisitions can also add accounts, so these bounds do not identify organic births. NRR is the product of retention and conditional expansion, not a standalone survival probability. No labels were consulted in deriving these constraints.

## Accounting candidate

The opt-in accounting bridge retains the joint customer architecture. For revenue R, accrual compute C, other operating expense O, D&A D, capital expenditure K, working capital change W and incremental cash commitment shortfall H:

$$ EBIT=R-C-O $$

$$ FCFF=EBIT-\tau\max(EBIT,0)+D-K-W-H $$

Economic stock-based compensation remains in operating expenses. Compute commitment shortfall uses compute expense net of allocated D&A; the allocation and working-capital coefficients remain assumptions. Anthropic anchors are from the verified accounting evidence CSV, not from target valuations. This is an untrained candidate, not a production release or new valuation.
