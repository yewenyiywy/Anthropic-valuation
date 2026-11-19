# Final-test cohort cloud2018: roster rule (frozen before the source was opened)

Registered 2026-11-19, before loading the ranking source and before looking at
any post-2018 outcome for any candidate.

- Source: Wayback Machine snapshot 20180628204913 of
  https://www.bvp.com/strategy/cloud-computing/index (BVP Cloud Index page,
  market caps as displayed on that date). If the snapshot does not show market
  caps, use the nearest earlier snapshot that does, no earlier than 20180503.
- Ranking date: the snapshot date. Origin 2018-12-31. Target 2023-12-31.
- Eligibility: rank all listed constituents by displayed market cap; take the
  top 10 whose corporate family is not in validation_gate.EXPOSED and not in
  data/stage4_candidate_universe.csv (cloud2015, cloud2020). Ties: earlier
  listing order on the page.
- Every selected issuer stays in the cohort regardless of later acquisition,
  delisting or bankruptcy (acquired issuers use the approved acquisition
  endpoint policy). No replacement after selection.
- Role: untouched final test. Equity outcomes (2023-12-31 market caps, deal
  values) must not be fetched until the production model, its trained
  parameters and all ten origin profiles are frozen and hashed.
